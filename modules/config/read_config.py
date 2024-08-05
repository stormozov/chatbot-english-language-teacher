import configparser


def read_config(file_path, section: str = 'engine') -> dict:
	"""
		Reads a config file and returns a dictionary with the section's parameters.

		Args:
			file_path (str): The path to the config file.
			section (str): The section to read. Defaults to 'engine'.

		Returns:
			dict: A dictionary with the section's parameters.
	"""
	config = configparser.ConfigParser()
	config.read(file_path)
	result = {key: value for key, value in config[section].items()}

	return result
