from labeler import estimate
from labeler import output_parameters_name
import json
import os


def compare(file_num: int = 100, data_num: int = 100) -> None:
    """
    Load labelled data and preprocessed data.
    Estimate preprocessed data.
    Make a result list that it contains parameters from two datasets.
    Save the result list.

    Args:
        file_num: The number of data files in a data folder.
        data_num: The number of map data in a data file.
    """

    # load labelled data. They already have estimated parameters.
    labelled_data = load_folder("..\\data\\labelled")
    # load preprocessed data. They don't have estimated parameters.
    preprocessed_data = load_folder("..\\data\\preprocessed")

    # Make scores of preprocessed data by estimating preprocessed_data.
    preprocessed_scores = list()
    for _100_levels in preprocessed_data:
        preprocessed_scores.append(list())
        cur = len(preprocessed_scores) - 1
        for level in _100_levels:
            preprocessed_scores[cur].appned(estimate(level))

    # Make a list that it contains parameters from two datasets.
    result = list()

    for i in range(file_num):
        result.append(list())
        cur = i - 1

        for j in range(data_num):
            temp = dict()
            for param_name in output_parameters_name:
                temp[param_name] = tuple(
                    labelled_data[i][j][param_name],
                    preprocessed_scores[i][i][param_name],
                )
            result[cur].append(temp)

    # Save the result list.
    save_folder(result)

    return


def load_file(path: str) -> list:
    """
    Load map data from json file.

    Args:
        path: relative path of data file.
    Returns:
        a list of 100 map data.
    """

    with open(path, "r") as f:
        data = json.load(f)

    return data


def load_folder(path: str = "..\\data\\labelled", file_num: int = 100) -> list:
    """
    Load map data from data folder.

    Args:
        path: relative path of data folder.
        file_num: the number of data files in the placed folder.
    Returns:
        a list of 100 lists of 100 map data.
    """
    data_list = list()

    # dicrectory
    cur_dir = os.path.dirname(os.path.abspath(__file__))

    for i in range(1, 1 + file_num):
        _path = os.path.join(cur_dir, path, "data" + str(i) + ".json")
        data_list.append(load_file(_path))

    return data_list


def save_folder(path: str = "..\\data\\compared") -> None:
    pass
