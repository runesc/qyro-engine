import sys


def app_is_frozen():
    """
    Check if the application is running in a frozen state (e.g., bundled with PyInstaller).
    """
    return getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS')
