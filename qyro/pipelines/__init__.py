import os
from pathlib import Path
import subprocess
from os.path import join, dirname
from os import rename, makedirs
from functools import lru_cache
from qyro.utils.platform import mac_based, windows_based, linux_based, _get_linux_distribution
from qyro._exceptions import EngineError
from qyro._store import QYRO_INTERNAL_STATE
from qyro import path
from qyro_engine._qyro import extract_public_settings


FREEZER_MAP = {
    "mac": ("qyro.pipelines.mac", "build_for_mac"),
    "windows": ("qyro.pipelines.windows", "build_for_windows"),
    "ubuntu": ("qyro.pipelines.ubuntu", "build_for_ubuntu"),
    "linuxmint": ("qyro.pipelines.ubuntu", "build_for_ubuntu"),
    "Pop!_os": ("qyro.pipelines.ubuntu", "build_for_ubuntu"),
    "arch": ("qyro.pipelines.arch", "build_for_arch"),
    "fedora": ("qyro.pipelines.fedora", "build_for_fedora"),
    "linux": ("qyro.pipelines.linux", "build_for_linux"),
}


@lru_cache(maxsize=1)
def get_freezer():
    """
    Returns a tuple (os_key, module_name, func_name)
    for the current platform/distro.
    """
    if mac_based():
        return "mac", *FREEZER_MAP["mac"]

    if windows_based():
        return "windows", *FREEZER_MAP["windows"]

    if linux_based():
        distro = _get_linux_distribution()
        if distro in FREEZER_MAP:
            return distro, *FREEZER_MAP[distro]
        return "linux", *FREEZER_MAP["linux"]

    raise EngineError("Unsupported OS")
from pathlib import PurePath

def compile_with_pyinstaller(arguments: list, debug: bool):
    """
    Compiles the application using PyInstaller with the given arguments.

    Args:
        arguments (list): A list of command-line arguments for PyInstaller.

    Returns:
        None
    """
    settings = QYRO_INTERNAL_STATE.get_config('settings')
    arguments += [
        '--name', settings['app_name'],
        '--noupx',
        '--noconfirm',
        '--distpath', path('target'),
        '--specpath', path('target/PyInstaller'),
        '--workpath', path('target/PyInstaller'),
        '--additional-hooks-dir', join(dirname(__file__), 'hooks'),
        *settings.get('extra_pyinstaller_args', []),
        *(item for hi in settings['hidden_imports'] for item in ['--hidden-import', hi]),
        '--runtime-hook', create_pyinstaller_runtime_hook()
    ]
    arguments.append(path(settings['main_module']))
    log_file_path = Path("build.log")
    if debug:
        # Ejecuta y muestra la salida en tiempo real mientras la guarda
        with log_file_path.open("w", encoding="utf-8") as log_file:
            process = subprocess.Popen(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
            for line in process.stdout:
                print(line, end="")
                log_file.write(line)
            process.wait()
            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, arguments)
    else:

        result = subprocess.run(arguments, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, check=True)
        log_file_path.write_text(result.stdout, encoding="utf-8")

    output_dir = path(f'target/{settings["app_name"]}' + ('.app' if mac_based() else ''))
    freeze_dir = path('${freeze_dir}')
    # In most cases, rename(src, dst) silently "works" when src == dst. But on
    # some Windows drives, it raises a FileExistsError. So check src != dst:
    if PurePath(output_dir) != PurePath(freeze_dir):
        rename(output_dir, freeze_dir)

    return path('${freeze_dir}')


def create_pyinstaller_runtime_hook():
    """
    Creates a PyInstaller runtime hook file for the qyro_engine,
    injecting public settings and ensuring PySide6 GUI works properly.

    Returns:
        str: The full path to the generated hook file.
    """
    import os
    from qyro._store import QYRO_INTERNAL_STATE
    from qyro_engine._qyro import extract_public_settings
    from qyro import path
    from os import makedirs

    # Ruta del hook
    hook_dir = path('target/PyInstaller')
    makedirs(hook_dir, exist_ok=True)
    hook_file_path = os.path.join(hook_dir, 'qyro_runtime_hook.py')

    # Obtener settings
    settings = QYRO_INTERNAL_STATE.get_config('settings')
    build_settings_repr = repr(extract_public_settings(settings))

    # Contenido del hook
    hook_content = f"""
import importlib
from PySide6 import QtCore, QtGui, QtWidgets, QtNetwork
import os

# Ensure PySide6 plugins (platforms, etc.) are found
QtCore.QCoreApplication.addLibraryPath(
    os.path.join(os.path.dirname(__file__), "_internal", "PySide6", "plugins")
)

# Inject public settings into the frozen module
try:
    module = importlib.import_module('qyro_engine._frozen')
except ImportError as e:
    raise RuntimeError(f"Could not import the frozen module: {{e}}")

module.BUILD_SETTINGS = {build_settings_repr}
"""

    # Escribir el hook
    with open(hook_file_path, 'w', encoding='utf-8') as f:
        f.write(hook_content)

    return hook_file_path
