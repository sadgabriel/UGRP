from prompt_generator import generate_prompt
from sampler import (
    generate_example_prompt,
    generate_example_map_list,
)
from preprocessor import preprocess
from unstructured_data_generator import unstructured_data_generate
from utility import *


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


def store_data(parameters, example_maps, ascii_map, dataset, current_file):
    """Store the processed data in the dataset and check for file size limits."""
    dataset["map_list"].append(
        {"params": parameters, "map": ascii_map, "example_maps": example_maps}
    )

    # Log the corresponding ASCII map
    logging.info(f"ASCII Map:\n{ascii_map}")

    # Check if the dataset length exceeds 100 after adding the new data
    if len(dataset["map_list"]) >= 100:
        # Save the current dataset to the current file
        save_dataset_to_file(dataset, current_file)
        return None  # Indicate a new file is needed

    return dataset


def generate_data_block(
    parameters, examples, prompt_style: str, dataset: dict, current_file: str
) -> dict:
    """Generate and process a data block, then store it."""
    # Generate the example prompt from the original examples (not from the maps)
    example_prompt = generate_example_prompt(examples)

    # Generate the ASCII map from the prompt
    ascii_map = generate_prompt_and_ascii_map(parameters, example_prompt, prompt_style)

    # Generate the example maps from the examples
    example_maps = generate_example_map_list(examples)

    # Store the generated data
    dataset = store_data(parameters, example_maps, ascii_map, dataset, current_file)

    return dataset


def generate_and_save_data(
    data_count: int,
    prompt_style: str,
    current_file: str,
    dataset: dict,
    get_parameters_fn,
) -> dict:
    """Main function to generate and save data blocks using a given parameters function."""
    while data_count > 0:
        # Use the provided function to get parameters and examples
        parameters, examples = get_parameters_fn()

        # Generate and process the data block with examples
        dataset = generate_data_block(
            parameters, examples, prompt_style, dataset, current_file
        )

        if dataset is None:
            # If dataset reaches limit, return None to signal the need for a new file
            return None

        # Decrease the data count by 1 as one block is processed
        data_count -= 1

    return dataset
