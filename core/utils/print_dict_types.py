from typing import Any


def print_dict_type(dict_obj: dict[Any, Any]):
	print({'dict_obg': dict_obj})
	for key, value in dict_obj.items():
		print(f"{key} ---> type ---> {type(value).__name__}")