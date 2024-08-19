import glob
import json
import os
import yaml


def load_config(config_path: str) -> dict:
    """Load configuration from a YAML file."""
    with open(config_path, "r") as file:
        return yaml.safe_load(file)


def load_all_data(file_paths: list) -> list:
    """Load all data from the given batch files into a single list."""
    all_data = []
    for file_path in file_paths:
        with open(file_path, "r") as infile:
            dataset = json.load(infile)
            all_data.extend(dataset.get("map_list", []))
    return all_data


def save_data_in_batches(all_data: list, preprocessed_path: str) -> None:
    """Save all data into batch files with exactly 100 items each."""
    batch_number = 1
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
    """Main function to reorganize existing batch files into proper sizes."""
    config = load_config("config.yaml")
    preprocessed_path = config["paths"]["preprocessed"]

    # Find all existing batch files
    existing_files = glob.glob(f"{preprocessed_path}batch*.json")

    if not existing_files:
        print("No batch files found.")
        return

    # Load all data from existing files
    all_data = load_all_data(existing_files)

    # Remove all existing batch files
    for file_path in existing_files:
        os.remove(file_path)

    # Save the data into new batch files with 100 items each
    save_data_in_batches(all_data, preprocessed_path)


# Run the reorganization
reorganize_batches()
