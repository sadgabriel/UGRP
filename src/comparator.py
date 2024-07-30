from labeler import estimate
from labeler import output_parameters_name
from labeler import load_folder
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
    labelled_data = load_folder(path="..\\data\\labelled", file_num=file_num)
    # load preprocessed data. They don't have estimated parameters.
    preprocessed_data = load_folder(path="..\\data\\preprocessed", file_num=file_num)

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
    save_folder(data=result)

    return


def save_folder(data, path: str = "..\\data\\compared") -> None:
    pass


if __name__ == "__main__":
    compare(file_num=1)
    pass
