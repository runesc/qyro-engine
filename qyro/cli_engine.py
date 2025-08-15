import argparse
import sys
import inspect
from typing import Callable
from .utils import EngineMessage, QYRO_METADATA


COMMANDS = {}  # Dictionary to store dynamically registered commands

class DynamicCommand:
    """Internal class to encapsulate a registered command with metadata."""

    def __init__(self, func, **kwargs):
        self.func = func
        self.name = func.__name__
        self.help = kwargs.get(
            'help', func.__doc__ or f'Executes the {self.name} command')
        self.params = {}


def CLI(**kwargs) -> Callable[[Callable], Callable]:
    """
    Decorator to register a CLI command dynamically.
    Usage: @CLI(help='Description of the command')
    """
    def decorator(func: Callable) -> Callable[[argparse.ArgumentParser], None]:
        cmd = DynamicCommand(func, **kwargs)
        COMMANDS[cmd.name] = cmd
        return func
    return decorator


def _create_arg_parser() -> argparse.ArgumentParser:
    """
    Creates and returns the argparse parser, configuring subparsers
    for each dynamically registered command, and also a global --version flag.
    """
    prog_name = 'python -m qyro' if sys.argv[0].endswith(
        'qyro') and '-m' in sys.argv else sys.argv[0]

    parser = argparse.ArgumentParser(
        prog=prog_name,
        description='Executes CLI/Engine framework commands.',
        epilog='Use <command> --help for more information about a specific command.'
    )

    class RichVersionAction(argparse.Action):
        def __call__(self, parser, namespace, values, option_string=None):
            EngineMessage.show(f"Qyro v{QYRO_METADATA['version']}", level="info")
            sys.exit(0)

    parser.add_argument(
        '--version',
        action=RichVersionAction,
        nargs=0,
        help='Show program\'s version number and exit.'
    )

    subparsers = parser.add_subparsers(
        dest='command', help='Available commands')
    subparsers.required = True

    for name, cmd in COMMANDS.items():
        subparser = subparsers.add_parser(name, help=cmd.help)

        sig = inspect.signature(cmd.func)
        for param_name, param in sig.parameters.items():
            kwargs = {}
            if param.default is not inspect.Parameter.empty:
                kwargs['default'] = param.default
                kwargs['nargs'] = '?'
                if isinstance(param.default, bool):
                    kwargs['action'] = 'store_true' if not param.default else 'store_false'
                    del kwargs['default']
                    del kwargs['nargs']

            subparser.add_argument(f'--{param_name}', **kwargs)
            cmd.params[param_name] = param

    return parser


def _execute_command(parser: argparse.ArgumentParser) -> None:
    """
    Parses the command line, finds the command, and executes the associated function.
    """
    args = parser.parse_args()
    cmd_name = args.command

    if cmd_name not in COMMANDS:
        parser.print_help()
        sys.exit(1)

    cmd_func = COMMANDS[cmd_name].func

    cmd_args = {k: v for k, v in vars(
        args).items() if k in COMMANDS[cmd_name].params}

    cmd_func(**cmd_args)
