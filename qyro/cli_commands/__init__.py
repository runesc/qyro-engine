import sys
import pathlib
from string import Template
from getpass import getuser
from os import makedirs, getcwd
from os.path import join, exists, abspath
from questionary import select, text, confirm
from prompt_toolkit.styles import Style
from rich.console import Console
from rich.prompt import Prompt, Confirm
from rich.panel import Panel
from rich.table import Table
from qyro.store import QYRO_INTERNAL_STATE
from ..cli_engine import CLI
from ..utils import EngineMessage, EngineError, module_exists
from ..utils.fs import QYRO_METADATA, replicate_and_filter, write_safely_from_template
from ..utils.parsers import to_camel_case
from ..utils.project_reader import get_project_settings
from .templates.component import COMPONENT_TEMPLATE

console = Console()

@CLI(help="Initialize a new Qyro project.")
def init(name: str = '.'):
    """
    Initializes a new Qyro project with a standard folder structure.
    """
    # Convert project name to CamelCase
    name = to_camel_case(name)
    project_path = abspath(name)

    # Check if the project already exists
    if exists(project_path + "/src"):
        raise EngineError(f"Project folder already exists at: [bold]{project_path}[/bold]")

    # Welcome message
    console.print(f"✨ Welcome to [bold green]{QYRO_METADATA['name']} v{QYRO_METADATA['version']}[/bold green] ✨\n")
    console.print(
        "Let's create a new project! This will create a [bold]src/[/bold] directory "
        "with the necessary files and folders.\n"
    )

    # Gather project details from the user
    app = to_camel_case(Prompt.ask("App name", default=name if name != '.' else "MyApp"))
    version = Prompt.ask("Version", default="1.0.0")
    default_author = getuser().title()
    author = Prompt.ask("Author", default=default_author)

    # Custom prompt styling
    custom_style = Style([
        ('qmark', 'fg:#ff00ff bold'),
        ('question', 'fg:#00ffff bold'),
        ('answer', 'fg:#00ffff bold'),
        ('pointer', 'fg:#ffff00 bold'),
        ('highlighted', 'fg:#2fe784 bold'),
        ('selected', 'fg:#2fe784 bold'),
    ])

    # Select Qt binding
    python_binding = select(
        "Select your Qt binding [PyQt5/PyQt6/PySide2/PySide6] (default: PySide6):",
        choices=["PyQt5", "PyQt6", "PySide2", "PySide6"],
        default="PySide6",
        style=custom_style
    ).ask()

    # Generate example macOS bundle identifier
    eg_bundle_id = f"com.{author.lower().split()[0]}.{''.join(app.lower().split())}"
    mac_bundle_identifier = Prompt.ask(
        f"Mac bundle identifier (e.g. {eg_bundle_id}, optional)",
        default=eg_bundle_id,
        show_default=False
    )
    if mac_bundle_identifier.strip() == "":
        mac_bundle_identifier = None

    # Display project configuration summary
    table = Table(title="Project Configuration", show_header=False, box=None)
    table.add_row("App name:", f"[cyan]{app}[/cyan]")
    table.add_row("Version:", f"[cyan]{version}[/cyan]")
    table.add_row("Author:", f"[cyan]{author}[/cyan]")
    table.add_row("Qt binding:", f"[cyan]{python_binding}[/cyan]")
    table.add_row("Mac bundle identifier:", f"[cyan]{mac_bundle_identifier or '(none)'}[/cyan]")

    console.print(Panel(table, title="[bold]Please confirm your settings[/bold]", border_style="blue"))

    # Confirm with the user
    if not Confirm.ask("Continue?"):
        console.print("[yellow]Operation aborted by user.[/yellow]")
        return

    # Check if the selected Qt binding is installed
    console.print(f"\n🔎 Checking if [bold cyan]{python_binding}[/bold cyan] is installed...")

    if not module_exists(python_binding):
        EngineMessage.show(f"Installing {python_binding}...", level="info")

    console.print(f"\n✅ [bold cyan]{python_binding}[/bold cyan] is installed!\n")

    # Create project directories
    if project_path != getcwd():
        makedirs(project_path, exist_ok=True)
    src_path = join(project_path, "src")
    makedirs(src_path, exist_ok=True)
    console.print(f"📂 Project folder '{name}/' created at: [bold]{project_path}[/bold]")

    # Set internal state
    QYRO_INTERNAL_STATE.set_config('project_dir', project_path)

    # Locate boilerplate templates
    template_dir = pathlib.Path(__file__).resolve().parent / 'boilerplate'
    if not template_dir.exists():
        raise EngineError(f"Template directory not found at: [bold]{template_dir}[/bold]")

    # Copy boilerplate files and apply placeholder replacements
    replicate_and_filter(
        source_path=template_dir,
        destination_path=project_path,
        replacements={
            'app_name': app,
            'author': author,
            'mac_bundle_identifier': mac_bundle_identifier,
            'python_bindings': python_binding,
            'binding': python_binding,
            'version': version
        },
        files_to_filter=[
            'src/build/settings/base.json',
            'src/build/settings/mac.json',
            'src/main/python/main.py'
        ]
    )

    # TODO: Mensaje que cambie dinámicamente si hay --name para indicar que primero se mueva a la carpeta del proyecto

    console.print(
        f"\n🎉 [bold green]Project created successfully at {project_path}/ directory 🎉[/bold green]\n"
        f"Now you can run:\n\n    [bold cyan]{QYRO_METADATA['name']} start[/bold cyan]"
    )

@CLI(help="Create a component or a new view in project")
def create(type: str = None, name: str = None, inherit: str = None):
    """Creates a new component or view in the project.

    Args:
        type (str, optional): The type of the item to create. Defaults to 'component'.
        name (str, optional): The name of the item to create. Defaults to None.
        inherit (str, optional): The name of the component to inherit from. Defaults to None.
    """

    # validate obligatory args (type, name)
    if not name:
        raise EngineError("The 'name' argument is required.")

    if type is None:
        raise EngineError("The 'type' argument is required and must be either 'component' or 'view'.")

    if type.lower() not in ['component', 'view']:
        raise EngineError("The 'type' argument must be either 'component' or 'view'.")

    name = to_camel_case(name)
    binding = get_project_settings('binding')

    if not inherit:
        inherit = text("Inherit from: ", default="QtWidget").ask()

    template = Template(COMPONENT_TEMPLATE)
    code = template.substitute(Binding=binding, Name=name, Widget=inherit)

    project_path = pathlib.Path.cwd()
    type_lower = type.lower()
    path = project_path / "src" / "main" / "python" / f"{type_lower}s"
    file_path = path / f"{name}.py"

    write_safely_from_template(
        file_path=file_path,
        code=code,
        item_name=name,
        item_type=type
    )

@CLI(help='Show the engine version.')
def version():
    """
    Displays the current version of the Qyro CLI.
    """
    EngineMessage.show(f"Qyro v{QYRO_METADATA['version']}", level="info")
    sys.exit(0)