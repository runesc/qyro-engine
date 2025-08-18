import re

def valid_version(version_str):
    """
    Validates and corrects a version string in X.Y.Z or X.Y format.

    Args:
        version_str (str): The version string to validate.

    Returns:
        str or None: The corrected version if valid, or None if the format is incorrect.
    """
    pattern = r'^(\d+)\.(\d+)(?:\.(\d+))?$'
    match = re.match(pattern, version_str)

    if match:
        parts = (match.group(1), match.group(2), match.group(3) or '0')

        return ".".join(parts)

    return None
