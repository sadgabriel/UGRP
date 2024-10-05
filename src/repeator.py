from season1.utility import *
from season1.llm_utils import generate_data_block, generate_and_save_data

from season1.validater import get_label


def get_data_from_map(map: str) -> dict:

    data = {"params": get_label(map), "map": map}
    return data


def repeat_process(data_count: int, prompt_style: str) -> None:
    """Repeat the process of generating and saving data using existing goal and map data."""
    config = load_config()
    preprocessed_path = config["paths"]["preprocessed"]
    repeated_path = config["paths"]["repeated"]

    create_directory(repeated_path)
    setup_logging(f"{repeated_path}.log")

    current_file, batch_number, dataset = find_or_create_dataset(path=repeated_path)

    data_block = None
    # Use the general function with a new parameter generation function
    while data_count > 0:

        first_step_data = get_last_element_of_largest_batch_file(preprocessed_path)

        parameters = first_step_data["params"]
        examples = [get_data_from_map(first_step_data["map"])]

        # Step 3: Pass the data block to generate_and_save_data
        dataset = generate_and_save_data(data_block, current_file, dataset)

        # Step 4: Check if a new file is needed based on dataset size
        if len(dataset["map_list"]) == 0:
            # Create a new batch file and reset the dataset
            batch_number += 1
            current_file = f"{preprocessed_path}batch{batch_number}.json"
            dataset = {"map_list": []}

        data_count -= 1
        for iteration in range(2):
            data_block = generate_data_block(parameters, examples, prompt_style)
            examples = [get_data_from_map(data_block["map"])]

        # Step 3: Pass the data block to generate_and_save_data
        dataset = generate_and_save_data(data_block, current_file, dataset)

        # Step 4: Check if a new file is needed based on dataset size
        if len(dataset["map_list"]) == 0:
            # Create a new batch file and reset the dataset
            batch_number += 1
            current_file = f"{repeated_path}batch{batch_number}.json"
            dataset = {"map_list": []}

        data_count -= 1

    if dataset and dataset["map_list"]:
        save_dataset_to_file(dataset, current_file)
        print(f"Successfully saved {current_file} with remaining data")


# Example usage (should be removed in production code)
repeat_process(1, "AutoCOT1")
