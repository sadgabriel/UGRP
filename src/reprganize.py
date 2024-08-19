import glob
import json
import os
import yaml


def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def load_all_data(preprocessed_path: str) -> list:
    """Load all data from all batch files in preprocessed and its subdirectories into a single list."""
    all_data = []

    # Load files from preprocessed directory
    file_paths = glob.glob(f"{preprocessed_path}batch*.json")

    # Load files from subdirectories
    subdirs = [d for d in glob.glob(f"{preprocessed_path}*/") if os.path.isdir(d)]
    for subdir in subdirs:
        file_paths.extend(glob.glob(f"{subdir}batch*.json"))

    for file_path in file_paths:
        with open(file_path, "r") as infile:
            dataset = json.load(infile)
            all_data.extend(dataset.get("map_list", []))

    return all_data, file_paths


def save_data_in_batches(all_data: list, preprocessed_path: str) -> None:
    """Save all data into batch files with exactly 100 items each."""
    batch_number = 0
    total_data_count = len(all_data)

    for i in range(0, total_data_count, 100):
        batch_data = all_data[i : i + 100]
        batch_file = f"{preprocessed_path}batch{batch_number}.json"
        dataset = {"map_list": batch_data}

        with open(batch_file, "w") as outfile:
            json.dump(dataset, outfile)

        print(f"Saved {batch_file} with {len(batch_data)} items")
        batch_number += 1


def reorganize_batches():
    """Main function to reorganize existing batch files from preprocessed and its subdirectories into proper sizes."""
    config = load_config("config.yaml")
    preprocessed_path = config["paths"]["preprocessed"]

    # Load all data from preprocessed directory and subdirectories
    all_data, file_paths = load_all_data(preprocessed_path)

    # Remove all existing batch files in the preprocessed directory
    for file_path in file_paths:
        os.remove(file_path)

    # Save the data into new batch files with 100 items each in the main preprocessed directory
    save_data_in_batches(all_data, preprocessed_path)


# Run the reorganization
reorganize_batches()
