import os

class ResourceLocator:
    """
    A class to locate files within a list of base directories.
    """

    def __init__(self, base_paths):
        """
        Initializes ResourceLocator with a list of base paths.

        Args:
            base_paths (list): A list of base directory paths.
        """
        self.base_paths = base_paths

    def locate(self, *rel_path):
        """
        Searches for a file by combining the base paths with the relative path.

        Args:
            *rel_path (str): The components of the file's relative path.

        Returns:
            str: The real, absolute path of the file if found.

        Raises:
            FileNotFoundError: If the file is not found in any of the base paths.
        """
        combined_rel_path = os.path.join(*rel_path)
        for base_path in self.base_paths:
            full_path = os.path.join(base_path, combined_rel_path)
            if os.path.exists(full_path):
                return os.path.realpath(full_path)

        raise FileNotFoundError(
            f"The file '{combined_rel_path}' was not found in any of the base paths.")
