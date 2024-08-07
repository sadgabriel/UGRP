from labeler import estimate
from labeler import load_folder
from labeler import save_folder
import json
import os


def compare(
    prompt_path: str = "../data/4. prompt",
    preprocessed_path: str = "../data/5. preprocessed",
    compared_path="../data/6. compared",
    file_num: int = 100,
) -> None:
    """
    Load prompt data and preprocessed data.
    Estimate preprocessed data.
    Make a result list that it contains parameters from two datasets.
    Save the result list.

    Args:
        file_num: The number of data files in a data folder.
        data_num: The number of map data in a data file.
    """

    # load prompt data. They already have estimated parameters.
    prompt_data = load_folder(path=prompt_path, file_num=file_num)
    # load preprocessed data. They don't have estimated parameters.
    preprocessed_data = load_folder(path=preprocessed_path, file_num=file_num)

    # Update parameters of preprocessed data by estimating preprocessed_data.
    for i in range(len(preprocessed_data)):
        map_list = preprocessed_data[i]["map_list"]
        data_num = len(map_list)
        for j in range(data_num):
            new_params = estimate(map_list[j]["map"])
            preprocessed_data[i]["map_list"][j]["params"].update(new_params)

    # Make a list that it contains parameters from two datasets.
    compared_data = list()

    for i in range(file_num):
        temp_map_list = {"map_list": []}
        compared_data.append(temp_map_list)

        prompt_map_list = prompt_data[i]["map_list"]
        preprocessed_map_list = preprocessed_data[i]["map_list"]

        for j in range(data_num):
            temp_compared_data = {"before_params": {}, "after_params": {}}
            compared_data[i]["map_list"].append(temp_compared_data)

            compared_data[i]["map_list"][j]["before_params"] = prompt_map_list[j][
                "params"
            ]
            compared_data[i]["map_list"][j]["after_params"] = preprocessed_map_list[j][
                "params"
            ]

    # Save the result list.
    save_folder(data=compared_data, path=compared_path, file_num=file_num)

    return


if __name__ == "__main__":
    compare(
        prompt_path="../data/3. labelled",
        preprocessed_path="../data/5. preprocessed",
        compared_path="../data/6. compared",
        file_num=1,
    )
