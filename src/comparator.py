from labeler import estimate
from labeler import load_folder
from labeler import save_folder
import json
import os


def compare(
    preprocessed_path: str = "../data/5. preprocessed",
    compared_path="../data/6. compared",
    file_count: int = 100,
) -> None:
    """
    Load prompt data and preprocessed data.
    Estimate preprocessed data.
    Make a result list that it contains parameters from two datasets.
    Save the result list.

    Args:
        file_count: The number of data files in a data folder.
        data_count: The number of map data in a data file.
    """

    # load preprocessed data. They don't have estimated parameters.
    preprocessed_data = load_folder(path=preprocessed_path, file_count=file_count)

    # Update parameters of preprocessed data by estimating preprocessed_data.
    for i in range(len(preprocessed_data)):
        map_list = preprocessed_data[i]["map_list"]
        data_count = len(map_list)
        for j in range(data_count):
            before_params = map_list[j]["params"]
            after_params = estimate(map_list[j]["map"])

    # Make a list that it contains parameters from two datasets.
    compared_data = list()

    for i in range(file_count):
        temp_map_list = {"map_list": []}
        compared_data.append(temp_map_list)

        for j in range(data_count):
            compared_data[i]["map_list"].append(dict())
            compared_data[i]["map_list"][j]["before_params"] = before_params
            compared_data[i]["map_list"][j]["after_params"] = after_params

    # Save the result list.
    save_folder(data=compared_data, path=compared_path, file_count=file_count)

    return


if __name__ == "__main__":
    compare(
        preprocessed_path="../data/5. preprocessed",
        compared_path="../data/6. compared",
        file_count=1,
    )
