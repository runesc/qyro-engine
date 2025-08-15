from ..utils import EngineMessage
from rich.prompt import Confirm
from rich.console import Console
from typing import Dict
import re
import pathlib
import shutil
import os
import json
from typing import Dict, List, Tuple, Union
from qyro.store import QYRO_INTERNAL_STATE

console = Console()

def _load_package_json() -> dict:
    """
        This function loads the package.json file for the Qyro project.

    Returns:
        dict: The contents of the package.json file.
    """
    utils_path = os.path.dirname(os.path.abspath(__file__))
    qyro_path = os.path.dirname(utils_path)
    package_json_path = os.path.join(qyro_path, "cli_commands", "package.json")
    with open(package_json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def _expand_placeholders(text: str, replacements: Dict[str, str]) -> str:
    """
    Replaces placeholders in a text using a dictionary of values.
    For example, ${VAR} is substituted with the value from replacements['VAR'].
    """
    pattern = r'\$\{([^}]+)\}'
    return re.sub(pattern, lambda m: replacements.get(m.group(1), m.group(0)), text)


def _get_files_to_replicate(
    source: pathlib.Path,
    destination: pathlib.Path,
    exclude: List[str]
) -> List[Tuple[pathlib.Path, pathlib.Path]]:
    """
    Generates a list of files to be copied, respecting exclusions.
    """
    files_to_copy = []
    # Ensure exclusions are absolute paths for accurate comparison
    exclude_paths = [pathlib.Path(p) for p in exclude]

    if source.is_file():
        if source not in exclude_paths:
            files_to_copy.append((source, destination / source.name))
    elif source.is_dir():
        for item in source.rglob('*'):
            if item.is_file():
                relative_path = item.relative_to(source)
                dest_path = destination / relative_path
                if item not in exclude_paths:
                    files_to_copy.append((item, dest_path))
    return files_to_copy


def replicate_and_filter(
    source_path: Union[str, pathlib.Path],
    destination_path: Union[str, pathlib.Path],
    replacements: Dict[str, str] = None,
    files_to_filter: List[str] = None,  # Ahora espera rutas relativas
    exclude: List[str] = None
) -> None:
    """
    Copies files and directories from a source to a destination, applying filters.
    :param source_path: The path of the source (file or directory).
    :param destination_path: The path of the destination.
    :param replacements: A dictionary for substituting placeholders.
    :param files_to_filter: A list of files in which text replacement will be applied (relative paths).
    :param exclude: A list of files or directories to exclude from the copy.
    """
    source = pathlib.Path(source_path).resolve()
    destination = pathlib.Path(destination_path).resolve()

    if replacements is None:
        replacements = {}
    if files_to_filter is None:
        files_to_filter = []
    if exclude is None:
        exclude = []

    files = _get_files_to_replicate(source, destination, exclude)

    # --- CAMBIO AQUÍ: Usar rutas relativas para la comparación ---
    relative_files_to_filter = [pathlib.Path(p) for p in files_to_filter]

    for src, dest in files:
        dest.parent.mkdir(parents=True, exist_ok=True)

        # Obtener la ruta relativa del archivo de origen
        relative_src_path = src.relative_to(source)

        # Comparar con la lista de archivos a filtrar
        if relative_src_path in relative_files_to_filter:
            with open(src, 'r') as f_in:
                content = f_in.read()
            filtered_content = _expand_placeholders(content, replacements)
            with open(dest, 'w') as f_out:
                f_out.write(filtered_content)
        else:
            shutil.copy2(src, dest)


def resolve_path(relative_path: str, replacements: Dict[str, str] = None) -> pathlib.Path:
    """
    Converts a relative path to an absolute path, expanding placeholders.
    :param relative_path: The relative path, with possible placeholders (e.g., '${VAR}/file.txt').
    :param replacements: A dictionary of values for substituting placeholders.
    :return: A pathlib.Path object with the resolved absolute path.
    """
    if replacements is None:
        # Use the global configuration if no dictionary is provided
        replacements = QYRO_INTERNAL_STATE.get_state_copy()[0]

    # 1. Expand placeholders in the path string
    expanded_path_str = _expand_placeholders(relative_path, replacements)

    # 2. Get the project's base directory
    project_dir = QYRO_INTERNAL_STATE.get_config('project_dir')
    if project_dir is None:
        raise ValueError(
            "The 'project_dir' must be set in the global state before calling this function.")

    # 3. Safely join and resolve the full path
    return pathlib.Path(project_dir) / expanded_path_str


def write_safely_from_template(
    file_path: pathlib.Path,
    code: str,
    item_name: str,
    item_type: str
) -> None:
    """
    Escribe el código en un archivo, solicitando confirmación si el archivo ya existe.

    Args:
        file_path (pathlib.Path): La ruta completa del archivo a crear.
        code (str): El contenido del archivo.
        item_name (str): El nombre del componente/vista.
        item_type (str): El tipo de item ('componente' o 'vista').
    """
    if file_path.exists():
        if not Confirm.ask(f"The file [bold]{file_path.name}[/bold] already exists. Overwrite?"):
            EngineMessage.show("Creation aborted by user.", level="warning")
            return

    try:
        file_path.parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, "w") as file:
            file.write(code)
        EngineMessage.show(
            f"{item_type.capitalize()} [bold]{item_name}[/bold] created in: [cyan]{file_path}[/cyan]",
            level="success"
        )
    except Exception as e:
        EngineMessage.show(
            f"An error occurred while writing the file: {e}",
            level="error"
        )


QYRO_METADATA = _load_package_json()
