import glob
import json
import re
from utility import load_config


# 파일 단위로 이상한 데이터를 제거합니다.
# 실행 후 reorganize.py를 실행해 주세요.


def load_all_batches(preprocessed_path: str) -> list:  # TODO: move to utility
    """Load all batch files from the preprocessed directory."""
    file_paths = glob.glob(f"{preprocessed_path}batch*.json")
    batches = []
    for file_path in file_paths:
        with open(file_path, "r") as infile:
            dataset = json.load(infile)
            batches.append((file_path, dataset))
    return batches


def filter_maps(dataset: dict) -> dict:
    """Filter out entries in map_list where 'map' is empty, lacks 'P'/'B',
    or where the first and last line don't consist of # and spaces with at least three consecutive #s.
    """
    filtered_map_list = []
    removed_items = []

    for item in dataset.get("map_list", []):
        map_data = item.get("map", "").strip()
        lines = map_data.splitlines()

        # Check if the first and last line are valid
        def valid_border_line(line: str) -> bool:
            return bool(re.match(r"^\s*#{3,}\s*$", line))

        # Remove if map is empty, lacks P/B, or the first/last line are invalid
        if (
            not map_data
            or ("P" not in map_data or "B" not in map_data)
            or (
                lines
                and (
                    not valid_border_line(lines[0]) or not valid_border_line(lines[-1])
                )
            )
            or len(lines) < 5
        ):
            removed_items.append(map_data)
        else:
            filtered_map_list.append(item)

    return {"map_list": filtered_map_list}, removed_items


def save_batches(batches: list) -> None:
    """Save the filtered datasets back to their respective files."""
    for file_path, dataset in batches:
        with open(file_path, "w") as outfile:
            json.dump(dataset, outfile)
        print(f"Saved filtered dataset to {file_path}")


def clean_batches():
    """Main function to clean batch files based on the given conditions."""
    config = load_config()
    preprocessed_path = config["paths"]["preprocessed"]

    # Load all batches
    batches = load_all_batches(preprocessed_path)

    # Filter each batch dataset and print removed items
    for i, (file_path, dataset) in enumerate(batches):
        filtered_dataset, removed_items = filter_maps(dataset)
        batches[i] = (file_path, filtered_dataset)

        # Print removed items' map part only
        for map_data in removed_items:
            print(f"Removed from {file_path}: {map_data}")

    # Save the cleaned batches
    save_batches(batches)


# Run the cleaning process
clean_batches()
