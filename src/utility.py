import os
import json

import yaml


def load_json_files(path: str) -> list[dict]:
    """Load all json data from directory.

    Args:
        path (str): The path of directory which has files.

    Returns:
        list[dict]: The list of contents

    Raises:
        FileNotFoundError: Raised when the path is not vaild."""
    if not os.path.exists(path):
        raise FileNotFoundError(f"The specified directory does not exist: {path}")

    filename_list = [
        filename
        for filename in os.listdir(path)
        if filename.endswith(".json") and os.path.isfile(os.path.join(path, filename))
    ]
    path_list = [os.path.join(path, filename) for filename in filename_list]

    content_list = list()
    for file_path in path_list:
        with open(file_path, "r") as file:
            batch = json.load(file)
            for content in batch["map_list"]:
                content_list.append(content)

    return content_list


def load_yaml_file(path: str) -> dict:
    """
    Loads and returns the content of a YAML file located at the specified path.

    Args:
        path (str): The file path of the YAML file to be loaded.

    Returns:
        dict: A dictionary containing the loaded YAML content.
    """
    with open(path, "r") as file:
        content = yaml.safe_load(file)

        return content


def load_config() -> dict:
    """
    Loads and returns the content of the 'config.yaml' file.

    Returns:
        dict: A dictionary containing the configuration settings from 'config.yaml'.
    """
    return load_yaml_file(os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.yaml"))
