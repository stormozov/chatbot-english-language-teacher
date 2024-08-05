import os


def get_absolute_path(path_parts: list[str]) -> str:
	"""Creates absolute path from path parts."""
	file_path = os.path.join(*path_parts)
	absolute_file_path = os.path.abspath(file_path)

	return absolute_file_path
