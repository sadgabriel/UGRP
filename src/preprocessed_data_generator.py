from prompt_generator import prompt_generator
from param_generator import param_generator
from preprocessor import preprocessor
from unstructured_data_generator import unstructured_data_generator
import json
import logging
import glob
from config import *


def preprocessed_data_generator(
    data_count: int, example_count: int, prompt_style: str
) -> None:
    """
    Generates and preprocesses data, saving it in batches as JSON files and logging the process.

    Parameters:
    data_count (int): The number of data points to generate.
    example_count (int): The number of examples to generate per data point.
    prompt_style (str): The style of prompt.

    Returns:
    None
    """

    # Set up logging to record process in a log file
    log_file_path = f"{PREPROCESSED_PATH}.log"
    logging.basicConfig(filename=log_file_path, level=logging.INFO)

    # Find the latest file with the highest file_count
    existing_files = glob.glob(f"{PREPROCESSED_PATH}batch*.json")
    if existing_files:
        latest_file = max(
            existing_files, key=lambda x: int(x.split("batch")[-1].split(".json")[0])
        )
        file_count = int(latest_file.split("batch")[-1].split(".json")[0])
        print(f"Loading latest file: {latest_file} with file_count: {file_count}")
        with open(latest_file, "r") as infile:
            dataset = json.load(infile)
    else:
        file_count = 0
        dataset = {"map_list": []}

    current_file_path = f"{PREPROCESSED_PATH}batch{file_count}.json"

    for i in range(data_count):

        # Generate parameters for the prompt
        param = param_generator()
        # Generate the prompt based on the parameters
        prompt = prompt_generator(example_count, param, prompt_style)
        # Generate unstructured data from the prompt
        text = unstructured_data_generator(prompt)
        # Preprocess the unstructured data into an ASCII map
        askii_map = preprocessor(text)

        # Append the processed data and parameters to the dataset
        dataset["map_list"].append({"params": param, "map": askii_map})

        # Log the text and its corresponding ASCII map
        logging.info(f"Data #{i}:")
        logging.info(f"Text:\n{text}")
        logging.info(f"ASCII Map:\n{askii_map}")

        # Check if the dataset length exceeds 100 after adding the new data
        if len(dataset["map_list"]) > 100:
            # Save the current dataset to the current file
            with open(current_file_path, "w") as outfile:
                json.dump(dataset, outfile)
            print(f"Successfully saved {current_file_path}")

            # Start a new file for the next batch
            file_count += 1
            current_file_path = f"{PREPROCESSED_PATH}batch{file_count}.json"
            dataset = {"map_list": []}  # Reset dataset for the next batch

    # If there is any remaining data, save it to a final file
    if dataset["map_list"]:
        with open(current_file_path, "w") as outfile:
            json.dump(dataset, outfile)
            print(f"Successfully saved {current_file_path}... left data")
