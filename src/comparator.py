import yaml

from labeler import load_folder, save_folder
import validater

import utility

config = utility.load_config()
PREPROCESSED_PATH = config["paths"]["preprocessed"]
COMPARED_PATH = config["paths"]["compared"]

DEFAULT_FILE_COUNT = 100


def compare(
    preprocessed_path: str = PREPROCESSED_PATH,
    compared_path: str = COMPARED_PATH,
    file_count: int = DEFAULT_FILE_COUNT,
) -> None:
    """
    Load preprocessed data, estimate parameters, and compare them.

    Args:
        preprocessed_path: Path to the folder with preprocessed data files.
        compared_path: Path to the folder where comparison results will be saved.
        file_count: Number of data files to process.
    """

    # load preprocessed data. They don't have estimated parameters.
    preprocessed_data = load_folder(path=preprocessed_path, file_count=file_count)

    # Initialize compared data list
    compared_data = [{"map_list": []} for _ in range(file_count)]

    # Update parameters and prepare compared data
    for i, data in enumerate(preprocessed_data):
        for map_item in data["map_list"]:
            try:
                examples = map_item["example_maps"]
            except KeyError:
                examples = None
            map = map_item["map"]
            before_params = map_item["params"]
            after_params = validater.validate(map)
            compared_data[i]["map_list"].append(
                {
                    "example_maps": examples,
                    "map": map,
                    "before_params": before_params,
                    "after_params": after_params,
                }
            )
    save_folder(data=compared_data, path=compared_path, file_count=file_count)

    return


if __name__ == "__main__":
    compare(
        preprocessed_path=PREPROCESSED_PATH,
        compared_path=COMPARED_PATH,
        file_count=1,
    )
