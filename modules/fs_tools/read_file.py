import json


def read_file(path: str) -> dict:
	"""Read json file and return data"""
	with open(path, 'r', encoding='utf-8') as file:
		return json.load(file)
