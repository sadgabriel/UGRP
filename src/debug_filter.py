import glob
import json
from utility import load_config


def load_all_batches(preprocessed_path: str) -> list:  # TODO: move to utility
    """Load all batch files from the preprocessed directory."""
    file_paths = glob.glob(f"{preprocessed_path}batch*.json")
    batches = []
    for file_path in file_paths:
        with open(file_path, "r") as infile:
            dataset = json.load(infile)
            batches.append((file_path, dataset))
    return batches


def debug_batches():
    """Visit all files to find maps with exactly four lines."""
    config = load_config()
    preprocessed_path = config["paths"]["preprocessed"]

    # Load all batches
    batches = load_all_batches(preprocessed_path)

    # Find and print maps with exactly four lines
    for file_path, dataset in batches:
        for item in dataset.get("map_list", []):
            map_data = item.get("map", "").strip()
            lines = map_data.splitlines()
            if len(lines) == 5:
                print(f"Four-line map found in {file_path}: {map_data}")


debug_batches()
