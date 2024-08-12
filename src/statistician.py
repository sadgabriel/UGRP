import numpy as np

import utility

config = utility.load_config()
COMPARED_PATH = config["paths"]["compared"]

default_diff_param_name_list = [
    "map_size",
    "room_count",
    "enemy_count",
    "treasure_count",
]

default_after_param_name_list = ["playability", "other_ASCII_count", "empty_validation"]


def calc_abs_diff_mean_std_from_path(
    path: str = COMPARED_PATH,
    param_name_list: list[str] = default_diff_param_name_list,
) -> tuple[dict]:
    """
    Calculates the mean and standard deviation of absolute differences from JSON files at the specified path.

    Args:
        path (str): The directory path where the JSON files are stored.
        param_name_list (list[str]): List of parameter names to calculate differences for.

    Returns:
        tuple[dict]: A tuple containing dictionaries of means and standard deviations for the absolute differences.
    """
    compared_list = utility.load_json_files(path)
    return _calc_abs_diff_mean_std(compared_list, param_name_list)


def calc_after_mean_std_from_path(
    path: str = COMPARED_PATH,
    param_name_list: list[str] = default_after_param_name_list,
) -> tuple[dict]:
    """
    Calculates the mean and standard deviation of parameters from 'after' states in JSON files at the specified path.

    Args:
        path (str): The directory path where the JSON files are stored.
        param_name_list (list[str]): List of parameter names to calculate statistics for.

    Returns:
        tuple[dict]: A tuple containing dictionaries of means and standard deviations for the parameters.
    """
    compared_list = utility.load_json_files(path)
    return _calc_after_mean_std(compared_list, param_name_list)


def _calc_abs_diff_mean_std(
    compared_list: list[dict],
    param_name_list: list[str],
) -> tuple[dict]:
    """
    Calculates the mean and standard deviation of absolute differences for specified parameters

    Args:
        compared_list (list[dict]): List of dictionaries with parameters before and after changes.
        param_name_list (list[str]): List of parameter names for which to calculate statistics.

    Returns:
        tuple[dict]: A tuple containing two dictionaries, one for the means and one for the standard deviations of the absolute differences.
    """
    diff_dict = _calc_abs_diff(compared_list, param_name_list)

    mean_dict = dict()
    std_dict = dict()

    for param_name in param_name_list:
        try:
            mean_dict[param_name] = np.mean(np.array(diff_dict[param_name]), axis=0)
            std_dict[param_name] = np.std(np.array(diff_dict[param_name]), axis=0)
        except:
            mean_dict[param_name] = np.mean(diff_dict[param_name])
            std_dict[param_name] = np.std(diff_dict[param_name])

    return mean_dict, std_dict


def _calc_after_mean_std(
    compared_list: list[dict], param_name_list: list[str]
) -> tuple[dict]:
    """
    Calculates the mean and standard deviation for specified parameters from the 'after_params' of each item in compared_list.

    Args:
        compared_list (list[dict]): List of dictionaries containing 'after_params' with game level parameters.
        param_name_list (list[str]): List of parameter names to compute statistics for.

    Returns:
        tuple[dict]: A tuple containing two dictionaries, one for the mean and one for the standard deviation of each parameter.
    """
    mean_dict = dict()
    std_dict = dict()

    for param_name in param_name_list:
        value_list = [
            compared["after_params"][param_name] for compared in compared_list
        ]

        mean_dict[param_name] = np.mean(value_list)
        std_dict[param_name] = np.std(value_list)

    return mean_dict, std_dict


def _calc_abs_diff(
    compared_list: list[dict],
    param_name_list: list[str],
) -> dict:
    """
    Calculates absolute differences for specified parameters between 'before' and 'after' states in a list of dictionaries.

    Args:
        compared_list (list[dict]): List of dictionaries, each containing 'before_params' and 'after_params' for game levels.
        param_name_list (list[str]): List of parameter names to calculate differences for.

    Returns:
        dict: A dictionary where each key is a parameter name and each value is a list of absolute differences.

    Note:
        Handles both list and single numeric parameter differences.
    """
    diff_dict = dict()
    for param_name in param_name_list:
        diff_dict[param_name] = list()

    for compared in compared_list:
        for param_name in param_name_list:
            try:
                diff_dict[param_name].append(
                    [
                        abs(
                            float(compared["after_params"][param_name][i])
                            - float(compared["before_params"][param_name][i])
                        )
                        for i in range(len(compared["after_params"][param_name]))
                    ]
                )
            except:
                diff_dict[param_name].append(
                    abs(
                        float(compared["after_params"][param_name])
                        - float(compared["before_params"][param_name])
                    )
                )

    return diff_dict
