from .prompt_generator import generate_prompt
from .sampler import generate_example_prompt
from .preprocessor import preprocess
from .unstructured_data_generator import unstructured_data_generate
from .utility import *


def generate_prompt_and_ascii_map(
    parameters, example_prompt, prompt_style: str
) -> tuple:
    """Generate prompt based on parameters and example prompt, then return ASCII map."""
    # Generate the prompt
    system, prompt = generate_prompt(example_prompt, parameters, prompt_style)

    # Generate unstructured data from the prompt
    raw_text = unstructured_data_generate(system, prompt)

    # Preprocess the unstructured data into an ASCII map
    ascii_map = preprocess(raw_text)

    # Log the raw text
    logging.info(f"Text:\n{raw_text}")

    return ascii_map


def generate_data_block(
    parameters, examples: dict, prompt_style: str, param_names: list
) -> tuple:
    """Generate and return a single data block with parameters, ASCII map, and examples."""
    example_prompt = generate_example_prompt(examples, param_names)
    ascii_map = generate_prompt_and_ascii_map(parameters, example_prompt, prompt_style)

    data_block = {
        "params": parameters,
        "map": ascii_map,
        "examples": examples,
    }

    logging.info(f"Generated Data Block: {data_block}")

    return data_block


def generate_and_save_data(
    data_block: dict,
    current_file: str,
    dataset: dict,
) -> dict:
    """Append the provided data block to the dataset and save it if necessary."""

    # Step 1: Append the data block to the dataset
    dataset["map_list"].append(data_block)

    logging.info(f"Appending data block to dataset in file: {current_file}")

    # Step 2: Check if dataset size has reached the limit (e.g., 100 entries)
    if len(dataset["map_list"]) >= 100:
        save_dataset_to_file(dataset, current_file)
        dataset = {"map_list": []}  # Reset dataset after saving
        logging.info(f"Dataset saved and reset after reaching limit in {current_file}")

    return dataset
