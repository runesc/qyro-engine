import os

def clear_console():
    """
    Clears the console screen.
    Works on both Windows ('cls') and Unix/Linux/macOS ('clear') systems.
    """
    os.system('cls' if os.name == 'nt' else 'clear')