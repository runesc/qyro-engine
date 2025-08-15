def to_camel_case(app_name: str) -> str:
    """
    Convierte un nombre de aplicación en formato snake_case o kebab-case a CamelCase.
    """
    parts = app_name.strip().replace('-', ' ').replace('_', ' ').split()
    return ''.join(word.capitalize() for word in parts)
