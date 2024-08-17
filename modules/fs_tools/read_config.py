import configparser


def read_config(file_path: str, section: str = 'engine') -> dict[str, str]:
    """Reads the specified section from the config file.

    Args:
        file_path (str): The path to the config file.
        section (str): The section to read. Defaults to 'engine'.

    Returns:
        dict: A dictionary with the section's parameters.
    """
    config = configparser.ConfigParser()
    config.read(file_path)

    return {key: value for key, value in config[section].items()}
