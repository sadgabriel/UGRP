import os
import json
import logging
import glob

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
    return load_yaml_file(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "../config.yaml")
    )


def setup_logging(log_path: str) -> None:
    """Set up logging to record the process in a log file."""
    logging.basicConfig(filename=log_path, level=logging.INFO)


def create_directory(path: str) -> None:
    """Create the data directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def find_existing_files(directory: str, file_pattern: str = "*.json") -> list:
    """
    Find existing files in the specified directory that match the given file pattern.

    Args:
        directory (str): The directory to search for files.
        file_pattern (str): The pattern to search for files. Defaults to '*.json'.

    Returns:
        list: A list of file paths that match the given pattern.
    """
    if not os.path.exists(directory):
        raise FileNotFoundError(f"The specified directory does not exist: {directory}")

    # Use glob to find files matching the pattern in the directory
    return glob.glob(os.path.join(directory, file_pattern))


def read_json_file(file_path: str) -> dict:
    """Read JSON data from a file."""
    with open(file_path, "r") as infile:
        return json.load(infile)


def write_json_file(file_path: str, data: dict) -> None:
    """Write JSON data to a file."""
    with open(file_path, "w") as outfile:
        json.dump(data, outfile)


def sort_files_by_size(files: list) -> list:
    """Sort files by their size, from smallest to largest."""
    return sorted(files, key=lambda x: os.path.getsize(x))


def find_available_dataset(files_sorted_by_size: list) -> tuple:
    """Find the first dataset with less than 100 entries."""
    for file_path in files_sorted_by_size:
        dataset = read_json_file(file_path)
        if len(dataset.get("map_list", [])) < 100:
            batch_number = int(file_path.split("batch")[-1].split(".json")[0])
            print(
                f"Loading file: {file_path} with size: {os.path.getsize(file_path)} bytes and batch number: {batch_number}"
            )
            print(
                f"Loading dataset: {len(dataset['map_list'])} data exist in the dataset."
            )
            return file_path, batch_number, dataset
    return None, None, None


def create_new_dataset(path: str, batch_number: int) -> tuple:
    """Create a new batch file and initialize it with an empty dataset."""
    new_file = f"{path}batch{batch_number}.json"
    dataset = {"map_list": []}  # Initialize empty dataset for the new file
    write_json_file(new_file, dataset)
    print(f"Created new dataset file: {new_file} with batch number: {batch_number}")
    return new_file, batch_number, dataset


def find_or_create_dataset(
    path: str,
    file_pattern: str = "batch*.json",
    max_entries: int = 100,
    create_new: bool = False,
) -> tuple:
    """
    Find an appropriate dataset file based on file size and dataset length.
    If no file matches the criteria or if create_new is True, a new file is created.

    Args:
        path (str): Directory path to search for files.
        file_pattern (str): The pattern to search for files. Defaults to 'batch*.json'.
        max_entries (int): The maximum number of entries allowed in a file before creating a new one. Defaults to 100.
        create_new (bool): If True, a new dataset file is created regardless of existing files. Defaults to False.

    Returns:
        tuple: (current_file, batch_number, dataset)
    """
    # Search for existing files in the specified path with the given pattern
    existing_files = find_existing_files(path, file_pattern)

    if existing_files and not create_new:
        # Sort files by size, from smallest to largest
        files_sorted_by_size = sort_files_by_size(existing_files)

        # Find an available dataset with less than max_entries
        file_path, batch_number, dataset = find_available_dataset(files_sorted_by_size)
        if file_path and len(dataset.get("map_list", [])) < max_entries:
            return file_path, batch_number, dataset

    # If no valid file found or create_new is True, create a new one
    if existing_files:
        max_batch_number = max(
            int(x.split("batch")[-1].split(".json")[0]) for x in existing_files
        )
        new_batch_number = max_batch_number + 1
    else:
        new_batch_number = 0

    return create_new_dataset(path, new_batch_number)


def save_dataset_to_file(dataset: dict, file_path: str) -> None:
    """Save the dataset to the specified JSON file."""
    with open(file_path, "w") as outfile:
        json.dump(dataset, outfile)
    print(f"Successfully saved {file_path}")
