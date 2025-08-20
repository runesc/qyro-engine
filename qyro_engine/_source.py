import os
from pathlib import Path
from qyro._exceptions import EngineError
from qyro_engine._qyro import generate_core_profiles, get_config_path, extract_public_settings
from qyro_engine._settings import load_json_configs


def find_project_root_directory():
    start_path = Path(os.getcwd())
    while start_path != start_path.parent:
        if (start_path / 'src' / 'main' / 'python').is_dir():
            return str(start_path)
    raise EngineError(
        "Could not determine the project base directory. Expected 'src/main/python'.")


def get_project_resource_locations(project_base_dir):

    icons_dir = Path(project_base_dir) / 'src' / 'main' / 'icons'
    resources_base = Path(project_base_dir) / 'src' / 'main' / 'resources'

    resource_dirs = [str(icons_dir)]
    profiles = generate_core_profiles()

    for profile in reversed(profiles):
        resource_dirs.append(str(resources_base / profile))

    return resource_dirs

def load_build_configurations(project_base_dir):
    core_settings = get_config_path(project_base_dir)
    profiles = generate_core_profiles()

    json_config_paths = _get_settings_paths(project_base_dir, profiles)
    settings = load_json_configs(json_config_paths, core_settings)
    filtered_settings = extract_public_settings(settings)

    if not filtered_settings:
       return settings

    return filtered_settings


def _get_settings_paths(project_base_dir, profiles):

    paths = []
    default_settings_dir = Path(os.path.dirname(
        __file__)) / '..' / 'qyro' / '_default_settings'

    for profile in profiles:
        # Ruta predeterminada del sistema
        default_path = default_settings_dir / 'src' / \
            'build' / 'settings' / f'{profile}.json'
        if default_path.exists():
            paths.append(str(default_path))

        # Ruta específica del proyecto
        project_path = Path(project_base_dir) / 'src' / \
            'build' / 'settings' / f'{profile}.json'
        if project_path.exists():
            paths.append(str(project_path))

        release_path = Path(project_base_dir) / 'src' / \
            'build' / 'settings' / f'release.json'
        if release_path.exists():
            paths.append(str(release_path))

    return paths


def default_path(path_):
    default_directory = os.path.normpath(os.path.join(
        os.path.dirname(__file__), '..', 'qyro', '_default_settings'))
    return path(default_directory, path_)

def env_root_path(path_):
    default_directory = os.path.normpath(os.path.join(
        os.path.dirname(__file__), '..', 'qyro'))
    return path(default_directory, path_)

def path(base_directory_path, path_):
    return os.path.normpath(os.path.join(base_directory_path, *path_.split('/')))
