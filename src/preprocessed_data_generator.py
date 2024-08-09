from prompt_generator import prompt_generator
from param_generator import param_generator
from preprocessor import preprocessor
from unstructured_data_generator import unstructured_data_generator
import json
import logging


def preprocessed_data_generator(
    data_count: int,
    example_count: int,
    preprocessed_path: str,
    base_prompt_file_path: str,
    example_path: str,
    prompt_file_path: str,
) -> None:
    """
    Generates and preprocesses data, saving it in batches as JSON files and logging the process.

    Parameters:
    data_count (int): The number of data points to generate.
    example_count (int): The number of examples to generate per data point.
    preprocessed_path (str): The path where the preprocessed data will be saved.
    base_prompt_file_path (str): The file path for the base prompt template.
    example_path (str): The path where example data will be generated.
    prompt_file_path (str): The file path where prompts will be generated.

    Returns:
    None
    """

    # Set up logging to record process in a log file
    log_file_path = f"{preprocessed_path}.log"
    logging.basicConfig(filename=log_file_path, level=logging.INFO)

    file_count = 0
    dataset = {"map_list": []}

    for i in range(data_count):
        # Generate parameters for the prompt
        param = param_generator()

        # Generate the prompt based on the parameters
        prompt_generator(
            example_count, param, base_prompt_file_path, example_path, prompt_file_path
        )

        # Generate unstructured data from the prompt
        text = unstructured_data_generator(prompt_file_path)

        # Preprocess the unstructured data into an ASCII map
        askii_map = preprocessor(text)

        # Append the processed data and parameters to the dataset
        dataset["map_list"].append({"params": param, "map": askii_map})

        # Log the text and its corresponding ASCII map
        logging.info(f"Data #{i}:")
        logging.info(f"Text:\n{text}")
        logging.info(f"ASCII Map:\n{askii_map}")

        # Save the dataset to a new file every 100 data points
        if i % 100 == 0:
            with open(f"{preprocessed_path}batch{file_count}.json", "w") as outfile:
                json.dump(dataset, outfile)
            dataset = {"map_list": []}  # Reset dataset for the next batch
            print(f"Successfully saved {preprocessed_path}batch{file_count}.json")
            file_count += 1

    # If there is any remaining data, save it to a final file
    if dataset["map_list"]:
        with open(f"{preprocessed_path}batch{file_count}.json", "w") as outfile:
            json.dump(dataset, outfile)
            print(
                f"Successfully saved {preprocessed_path}batch{file_count}.json... left data"
            )
