from .param_generator import generate_param
from .sampler import load_random_examples_from_folder
from .llm_utils import generate_and_save_data, generate_data_block
from .utility import *


def generate_preprocessed_data(
    data_count: int, example_count: int, prompt_style: str
) -> None:
    """Generate the initial output and save it."""
    config = load_config()
    preprocessed_path = config["paths"]["preprocessed"]

    create_directory(preprocessed_path)
    setup_logging(f"{preprocessed_path}.log")

    current_file, batch_number, dataset = find_or_create_dataset(path=preprocessed_path)

    # Use the general function with a new parameter generation function
    while data_count > 0:
        # Step 1: Generate parameters and examples
        parameters = generate_param()
        examples = load_random_examples_from_folder(example_count)

        # Step 2: Generate the data block
        data_block = generate_data_block(parameters, examples, prompt_style)

        # Step 3: Pass the data block to generate_and_save_data
        dataset = generate_and_save_data(data_block, current_file, dataset)

        # Step 4: Check if a new file is needed based on dataset size
        if len(dataset["map_list"]) == 0:
            # Create a new batch file and reset the dataset
            batch_number += 1
            current_file = f"{preprocessed_path}batch{batch_number}.json"
            dataset = {"map_list": []}

        data_count -= 1

    # Save any remaining data that wasn't saved due to not reaching the limit
    if dataset and dataset["map_list"]:
        save_dataset_to_file(dataset, current_file)
        print(f"Successfully saved {current_file} with remaining data")


# Example usage (should be removed in production code)
generate_preprocessed_data(data_count=1, example_count=10, prompt_style="AutoCOT1")
