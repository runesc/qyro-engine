from pathlib import Path
from qyro_engine.exceptions import EngineError

class FileLocator:
    """
    Handles searching for files across multiple base directories.
    """

    def __init__(self, directories):
        """
        Initialize the locator with a list of base directories.

        Args:
            directories (list[Path | str]): List of directories to search in.
        """
        # Convert all to Path objects
        self.directories = [Path(d) for d in directories]

    def find(self, *relative_parts):
        """
        Locate a file by combining base directories with the given relative path.

        Args:
            *relative_parts: Components of the file's relative path.

        Returns:
            Path: Absolute path to the located file.

        Raises:
            FileNotFoundError: If the file cannot be found in any base directory.
        """
        target_path = Path(*relative_parts)
        for base in self.directories:
            candidate = base / target_path
            if candidate.exists():
                return str(candidate.resolve())

        raise EngineError(f"Cannot find file: {target_path}")
