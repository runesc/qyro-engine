import os
import shutil
from importlib import resources
from qyro import path
from qyro._store import QYRO_INTERNAL_STATE
from qyro_engine._source import default_path, env_root_path
from qyro.utils.fs import _copy_and_filter
from qyro.pipelines import compile_with_pyinstaller
from pathlib import Path


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

    compile_with_pyinstaller(arguments, is_debug)
    embed_qyro_cli_commands()


def embed_qyro_cli_commands():
    """
    Moves the QYRO CLI commands into the application bundle.
    Works both in development and in the compiled (PyInstaller) version.
    """
    settings = QYRO_INTERNAL_STATE.get_config('settings')

    # Directorio destino dentro del bundle
    output_dir = path(f'target/{settings["app_name"]}/_internal/qyro/cli_commands/')
    os.makedirs(output_dir, exist_ok=True)

    # Obtener la ruta real de package.json, según el entorno
    try:
        # Funciona en versión congelada o instalada como paquete
        with resources.path('qyro.cli_commands', 'package.json') as pkg_path:
            cli_commands_path = Path(pkg_path)
    except Exception:
        # Fallback a entorno de desarrollo
        default_dir = os.path.normpath(os.path.join(
            os.path.dirname(__file__), '..', 'qyro'))
        cli_commands_path = Path(default_dir) / 'cli_commands' / 'package.json'

    # Copiar el archivo al directorio destino
    shutil.copy(cli_commands_path, output_dir)