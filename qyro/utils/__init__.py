# qyro/utils/__init__.py

from rich.console import Console
import sys
import logging

console = Console(stderr=True)

class EngineMessage:
    """
    Class to display formatted messages in the console.
    Separates the printing logic from exception handling.
    """

    LEVEL_STYLES = {
        "error": ("❌", "bold red"),
        "warning": ("⚠️", "bold yellow"),
        "info": ("ℹ️", "bold cyan"),
        "debug": ("🛠️", "bold magenta"),
        "critical": ("🚨", "bold red on white"),
        "hot": ("🔥", "bold red"),
    }

    @classmethod
    def show(cls, message: str, level: str = "error"):
        """
        Display a message with rich formatting based on its level.
        """
        emoji, style = cls.LEVEL_STYLES.get(level, ("❌", "bold red"))
        console.print(f"{emoji} [{style}]{level.upper()}:[/{style}] {message}")


class EngineError(Exception):
    """
    Base exception for the Qyro Engine.
    Used only to be raised as an error; display is handled via EngineMessage.
    """
    def __init__(self, message: str):
        super().__init__(message)
        EngineMessage.show(message, level="error")