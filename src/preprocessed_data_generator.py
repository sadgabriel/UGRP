from src.season1.llm_utils import generate_and_save_data, generate_data_block
from src.season1.utility import *

from data_utility import get_demos_from_map_dataset


def generate_preprocessed_data(
    prompt_style: str,
    goal_params: str,
    param_names: list,
) -> None:
    """Generate the initial output and save it."""
    config = load_config()
    preprocessed_path = config["paths"]["preprocessed"]

    create_directory(preprocessed_path)
    setup_logging(f"{preprocessed_path}.log")

    current_file, batch_number, dataset = find_or_create_dataset(path=preprocessed_path)

    # Step 1: Generate examples
    examples = get_demos_from_map_dataset(param_names)

    # Step 2: Generate the data block
    data_block = generate_data_block(goal_params, examples, prompt_style, param_names)

    # Step 3: Pass the data block to generate_and_save_data
    dataset = generate_and_save_data(data_block, current_file, dataset)

    # Step 4: Check if a new file is needed based on dataset size
    if len(dataset["map_list"]) == 0:
        # Create a new batch file and reset the dataset
        batch_number += 1
        current_file = f"{preprocessed_path}batch{batch_number}.json"
        dataset = {"map_list": []}

    # Save any remaining data that wasn't saved due to not reaching the limit
    if dataset and dataset["map_list"]:
        save_dataset_to_file(dataset, current_file)
        print(f"Successfully saved {current_file} with remaining data")
