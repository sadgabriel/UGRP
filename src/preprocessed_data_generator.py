import logging
import glob
import os
import json
import yaml

from prompt_generator import generate_prompt
from param_generator import generate_param
from sampler import (
    load_random_examples_from_folder,
    generate_example_prompt,
    generate_example_map_list,
)
from preprocessor import preprocess
from unstructured_data_generator import unstructured_data_generate


def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def setup_logging(log_path: str) -> None:
    """Set up logging to record the process in a log file."""
    logging.basicConfig(filename=log_path, level=logging.INFO)


def create_preprocessed_directory(path: str) -> None:
    """Create the preprocessed data directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def find_existing_files(path: str) -> list:
    """Find existing JSON files in the preprocessed data directory."""
    return glob.glob(path)


def find_or_create_file(existing_files: list, path: str) -> tuple:
    """
    Find an appropriate file to use based on file size and dataset length.
    If all files have 100 or more entries, create a new file.

    Returns:
    tuple: (current_file, batch_number, dataset)
    """
    if existing_files:
        # Sort files by size, from smallest to largest
        files_sorted_by_size = sorted(existing_files, key=lambda x: os.path.getsize(x))

        # Iterate over sorted files to find one with less than 100 map entries
        for file_path in files_sorted_by_size:
            with open(file_path, "r") as infile:
                dataset = json.load(infile)
                if len(dataset.get("map_list", [])) < 100:
                    # Use the first file found with less than 100 map entries
                    batch_number = int(file_path.split("batch")[-1].split(".json")[0])
                    print(
                        f"Loading file: {file_path} with size: {os.path.getsize(file_path)} bytes and batch number: {batch_number}"
                    )
                    print(
                        f"Loading dataset: {len(dataset['map_list'])} data exist in file."
                    )
                    return file_path, batch_number, dataset

        # If all files have 100 or more entries, create a new batch file
        max_batch_number = max(
            int(x.split("batch")[-1].split(".json")[0]) for x in existing_files
        )
        new_batch_number = max_batch_number + 1
        new_file = f"{path}batch{new_batch_number}.json"
        dataset = {"map_list": []}  # Initialize empty dataset for the new file
        with open(new_file, "w") as outfile:
            json.dump(dataset, outfile)
        print(f"Created new file: {new_file} with batch number: {new_batch_number}")
        return new_file, new_batch_number, dataset
    else:
        # If no existing files are found, create the first batch file
        first_batch_number = 1
        new_file = f"{path}batch{first_batch_number}.json"
        dataset = {"map_list": []}  # Initialize empty dataset for the first file
        with open(new_file, "w") as outfile:
            json.dump(dataset, outfile)
        print(f"Created first file: {new_file} with batch number: {first_batch_number}")
        return new_file, first_batch_number, dataset


def save_dataset_to_file(dataset: dict, file_path: str) -> None:
    """Save the dataset to the specified JSON file."""
    with open(file_path, "w") as outfile:
        json.dump(dataset, outfile)
    print(f"Successfully saved {file_path}")


def generate_and_preprocess_data(
    data_count: int,
    example_count: int,
    prompt_style: str,
    current_file: str,
    dataset: dict,
) -> dict:
    """Generate and preprocess data, appending it to the dataset."""
    for i in range(data_count):
        # Generate parameters for the prompt
        parameters = generate_param()
        # Load a specified number of random examples from the folder
        examples = load_random_examples_from_folder(example_count)
        example_prompt = generate_example_prompt(examples)
        example_maps = generate_example_map_list(examples)
        # Generate the prompt based on the parameters
        system, prompt = generate_prompt(example_prompt, parameters, prompt_style)
        # Generate unstructured data from the prompt
        raw_text = unstructured_data_generate(system, prompt)
        # Preprocess the unstructured data into an ASCII map
        ascii_map = preprocess(raw_text)

        # Append the processed data and parameters to the dataset
        dataset["map_list"].append(
            {"params": parameters, "map": ascii_map, "example_maps": example_maps}
        )

        # Log the text and its corresponding ASCII map
        logging.info(f"Data #{i}:")
        logging.info(f"Text:\n{raw_text}")
        logging.info(f"ASCII Map:\n{ascii_map}")

        # Check if the dataset length exceeds 100 after adding the new data
        if len(dataset["map_list"]) > 100:
            # Save the current dataset to the current file
            save_dataset_to_file(dataset, current_file)

            # Start a new file for the next batch
            return None

    return dataset


def generate_preprocessed_data(
    data_count: int, example_count: int, prompt_style: str
) -> None:
    """Main function to generate and preprocess data, saving it in batches."""
    config = load_config("config.yaml")
    preprocessed_path = config["paths"]["preprocessed"]

    create_preprocessed_directory(preprocessed_path)
    setup_logging(f"{preprocessed_path}.log")

    existing_files = find_existing_files(f"{preprocessed_path}batch*.json")
    current_file, batch_number, dataset = find_or_create_file(
        existing_files, preprocessed_path
    )

    while data_count > 0:
        dataset = generate_and_preprocess_data(
            data_count, example_count, prompt_style, current_file, dataset
        )
        if dataset is None:
            # If a new batch file is required, update file paths and continue processing
            batch_number += 1
            current_file = f"{preprocessed_path}batch{batch_number}.json"
            dataset = {"map_list": []}  # Reset dataset for the next batch

        # Reduce data count by the number of processed items
        data_count -= example_count

    # Save any remaining data to the final file
    if dataset and dataset["map_list"]:
        save_dataset_to_file(dataset, current_file)
        print(f"Successfully saved {current_file} with remaining data")


# Example usage (should be removed in production code)
# generate_preprocessed_data(data_count=150, example_count=10, prompt_style="style1")
