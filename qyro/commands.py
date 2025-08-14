import sys
from .cli_engine import CLI
from .utils import EngineMessage

__version__ = "2.1.0"

@CLI(help='Show the engine version.')
def version():
    """
    Displays the current version of the Qyro CLI.
    """
    EngineMessage.show(f"[Qyro] version: {__version__}", level="info")
    sys.exit(0)