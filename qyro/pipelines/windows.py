import sys
import os
import struct
import shutil
from shutil import copy
from pathlib import Path
from os.path import join, exists
from importlib import resources
from qyro import path
from qyro._store import QYRO_INTERNAL_STATE
from qyro_engine._source import default_path
from qyro.utils.fs import _copy_and_filter
from qyro.pipelines import compile_with_pyinstaller
from qyro._exceptions import EngineError
from qyro.utils.platform import mac_based


def build_for_windows(debug=False, bundle=False):
    """
    Builds the application for Windows using PyInstaller.

    Args:
        debug (bool or str): Enables debug mode. Can be a boolean
                             or a string ('dev', 'development', 'true', '1').
        bundle (bool): Bundles the executable into a single file.

    Returns:
        list: A list of command-line arguments for PyInstaller.
    """
    arguments = ['pyinstaller']
    is_debug = (
        debug.lower() in ('dev', 'development', 'true', '1')
        if isinstance(debug, str)
        else bool(debug)
    )

    arguments += ['--console',
                  '--log-level=DEBUG'] if is_debug else ['--noconsole']

    if bundle:
        arguments.append('--onefile')

    for path_callback in [path]:
        _copy_and_filter(
            path_callback,
            default_path('src/build/compilers/win32/metadata.py'),
            path('target/PyInstaller')
        )

    arguments += [
        '--icon', path('src/main/icons/Icon.ico'),
        '--version-file', path('target/PyInstaller/metadata.py'),
        *(['--debug', 'all'] if is_debug else [])
    ]

    freeze_path = compile_with_pyinstaller(arguments, is_debug)
    _generate_resources()
    embed_qyro_cli_commands()
    copy(path('src/main/icons/Icon.ico'), path('${freeze_dir}'))
    restore_essential_dlls(freeze_path)


def embed_qyro_cli_commands():
    """
    Moves the QYRO CLI commands into the application bundle.
    Works both in development and in the compiled (PyInstaller) version.
    """
    settings = QYRO_INTERNAL_STATE.get_config('settings')

    # Directorio destino dentro del bundle
    output_dir = path(
        f'target/{settings["app_name"]}/_internal/qyro/cli_commands/')
    os.makedirs(output_dir, exist_ok=True)

    try:
        with resources.path('qyro.cli_commands', 'package.json') as pkg_path:
            cli_commands_path = Path(pkg_path)
    except Exception:
        default_dir = os.path.normpath(os.path.join(
            os.path.dirname(__file__), '..', 'qyro'))
        cli_commands_path = Path(default_dir) / 'cli_commands' / 'package.json'

    shutil.copy(cli_commands_path, output_dir)


def restore_essential_dlls(freeze_path: str):
    """
    Ensures that critical Visual C++ and UCRT DLLs are present
    in the frozen application's directory.
    """
    # DLLs from Visual C++ Redistributables
    vc_dlls = [
        'msvcr100.dll', 'msvcr110.dll', 'msvcp110.dll',
        'vcruntime140.dll', 'msvcp140.dll', 'concrt140.dll', 'vccorlib140.dll'
    ]
    for dll in vc_dlls:
        _copy_dll_to_freeze_dir(
            dll_name=dll,
            freeze_path=freeze_path,
            install_desc="Visual C++ Redistributable 2012",
            install_url="https://www.microsoft.com/en-us/download/details.aspx?id=30679"
        )

    # UCRT DLLs (required on Windows 10+)
    ucrt_dlls = ['api-ms-win-crt-multibyte-l1-1-0.dll']
    bitness = struct.calcsize("P") * 8  # 32-bit or 64-bit Python interpreter
    for dll in ucrt_dlls:
        _copy_dll_to_freeze_dir(
            dll_name=dll,
            freeze_path=freeze_path,
            install_desc="Windows 10 SDK or KB2999226",
            install_url="https://developer.microsoft.com/en-us/windows/downloads/windows-10-sdk",
            bitness=bitness
        )


def _copy_dll_to_freeze_dir(dll_name: str, freeze_path: str, install_desc: str, install_url: str, bitness: int = None):
    """
    Copies a DLL to the freeze directory if found in PATH.
    Raises EngineError if the DLL cannot be found.
    """
    dst_path = join(freeze_path, dll_name)
    if exists(dst_path):
        return  # Already present

    src_path = _locate_dll(dll_name)
    if not src_path:
        msg = f"Could not find {dll_name}. Please install {install_desc}.\nURL: {install_url}"
        if bitness:
            msg += f"\nUse the {bitness}-bit version of the DLL that matches your Python interpreter."
        raise EngineError(msg)

    shutil.copy(src_path, freeze_path)


def _locate_dll(dll_name: str) -> str | None:
    """
    Searches for a DLL in all PATH directories.
    Returns the full path if found, or None if not found.
    """
    search_paths = os.environ.get("PATH", os.defpath).split(os.pathsep)

    # Ensure current directory is checked first on Windows
    if sys.platform == "win32" and os.curdir not in search_paths:
        search_paths.insert(0, os.curdir)

    seen_dirs = set()
    for directory in search_paths:
        norm_dir = os.path.normcase(directory)
        if norm_dir in seen_dirs:
            continue
        seen_dirs.add(norm_dir)

        candidate = join(directory, dll_name)
        if exists(candidate):
            return candidate

    return None


def _generate_resources():
    """
    Copy the data files from src/main/resources to freeze_dir.
    Works both in development and frozen builds.
    Automatically filters files mentioned in the settings files_to_filter.
    """
    # Determinar freeze_dir dinámicamente
    freeze_dir = Path(sys._MEIPASS) if getattr(sys, 'frozen', False) else path('${freeze_dir}')

    # En macOS, los recursos van a Contents/Resources
    from qyro.utils.platform import mac_based
    resources_dest_dir = freeze_dir / 'Contents' / 'Resources' if mac_based() else freeze_dir

    # Copiar recursos de todos los perfiles cargados
    for path_fn in (default_path, path):
        for profile in QYRO_INTERNAL_STATE._loaded_profiles:
            # Filtrado automático usando _copy_and_filter
            _copy_and_filter(
                path_fn,
                f'src/main/resources/{profile}',
                resources_dest_dir
            )
            _copy_and_filter(
                path_fn,
                f'src/compilers/{profile}',
                freeze_dir
            )
