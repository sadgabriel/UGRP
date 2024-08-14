import random

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


def calc_abs_diff_mean_std(
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
    return _calc_abs_diff_mean_std_from_list(compared_list, param_name_list)


def calc_after_mean_std(
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
    return _calc_after_mean_std_from_list(compared_list, param_name_list)


def _calc_abs_diff_mean_std_from_list(
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


def _calc_after_mean_std_from_list(
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


def calc_novelty(path: str = COMPARED_PATH, threshold: int = 5) -> float:
    """
    Calculate the novelty score for items stored in JSON files at the specified path.

    Args:
        path (str): The file path to the JSON files containing the data.
                    Defaults to COMPARED_PATH.
        threshold (int): The minimum Levenshtein distance required for a target string
                         to be considered novel. Defaults to 5.

    Returns:
        float: The average novelty score, where 1.0 indicates all target strings are novel,
               and 0.0 indicates none are novel.
    """
    compared_list = utility.load_json_files(path)
    return _calc_novelty_from_list(compared_list, threshold)


def _calc_novelty_from_list(compared_list: list[dict], threshold: int) -> float:
    """
    Calculate the average novelty of a list of items based on a given threshold.

    Args:
        compared_list (list[dict]): A list of dictionaries, each containing:
            - "examples" (list[str]): A list of example strings to compare against.
            - "map" (str): The target string to check for novelty.
        threshold (int): The minimum Levenshtein distance required for a target string
                         to be considered novel.

    Returns:
        float: The average novelty score, where 1.0 indicates all target strings are novel,
               and 0.0 indicates none are novel.
    """
    novelty_list = [
        _check_novelty(compared["examples"], compared["map"], threshold)
        for compared in compared_list
    ]

    return np.mean(novelty_list)


def _check_novelty(examples: list[str], target: str, threshold: int) -> bool:
    """
    Check if the target string is sufficiently novel compared to a list of example strings.

    Args:
        examples (list[str]): A list of strings to compare against.
        target (str): The target string to check for novelty.
        threshold (int): The minimum Levenshtein distance required for the target to be considered novel.

    Returns:
        bool: True if the target string is novel (i.e., sufficiently different from all examples),
              False if it is not.
    """
    for example in examples:
        if _calc_levenshtein_distance(example, target) < threshold:
            return False

    return True


def _calc_levenshtein_distance(A: str, B: str) -> int:
    """
    Calculate the Levenshtein distance between two strings A and B.

    The Levenshtein distance is a measure of the difference between two strings,
    defined as the minimum number of single-character edits (insertions, deletions,
    or substitutions) required to change one string into the other.

    Args:
        A (str): The first string.
        B (str): The second string.

    Returns:
        int: The Levenshtein distance between string A and string B.
    """
    len_A = len(A)
    len_B = len(B)

    dp = [[0] * (len_B + 1) for _ in range(len_A + 1)]

    for i in range(len_A + 1):
        dp[i][0] = i

    for j in range(len_B + 1):
        dp[0][j] = j

    for i in range(1, len_A + 1):
        for j in range(1, len_B + 1):
            if A[i - 1] == B[j - 1]:
                cost = 0
            else:
                cost = 1

            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)

    return dp[len_A][len_B]


def calc_diversity(path: str = COMPARED_PATH, threshold: int = 5) -> float:
    """
    Calculate the diversity score from JSON files at the specified path.

    Args:
        path (str): The file path to the JSON files containing the data. Defaults to COMPARED_PATH.
        threshold (int): The minimum Levenshtein distance required to create an edge between items. Defaults to 5.

    Returns:
        float: The diversity score, calculated as the ratio of the largest clique size to the total number of items.
    """
    compared_list = utility.load_json_files(path)
    return _calc_diversity_from_list(compared_list, threshold)


def _calc_diversity_from_list(compared_list: list[dict], threshold: int) -> float:
    """
    Calculate the diversity of a list of items based on the size of the largest clique found.

    Args:
        compared_list (list[dict]): A list of dictionaries, each containing a "map" key with a string to compare.
        threshold (int): The minimum Levenshtein distance required to create an edge between two items.

    Returns:
        float: The diversity score, calculated as the ratio of the largest clique size to the total number of items.
    """
    map_list = [compared["map"] for compared in compared_list]

    edges = _make_graph_from_map_list(map_list, threshold)

    U = set(range(len(edges)))

    clique_list = list()

    while U:
        vertex = random.choice(U)
        clique = _greedy_find_clique(edges, vertex)

        clique_list.append(clique)
        U.difference_update(clique)

    merged_clique_list = _merge_cliques(edges, clique_list)

    max_clique_len = max(len(clique) for clique in merged_clique_list)

    return max_clique_len / len(edges)


def _make_graph_from_map_list(map_list: list[str], threshold: int) -> list[list[int]]:
    """
    Create an adjacency list graph from a list of strings based on Levenshtein distance.

    Args:
        map_list (list[str]): A list of strings to be compared.
        threshold (int): The minimum Levenshtein distance required to create an edge between two strings.

    Returns:
        list[list[int]]: An adjacency list representing the graph, where each index contains a list of indices of connected nodes.
    """
    n = len(map_list)
    edges = [list() for _ in range(n)]

    for i in range(n - 1):
        for j in range(i + 1, n):
            if _calc_levenshtein_distance(map_list[i], map_list[j]) >= threshold:
                edges[i].append(j)
                edges[j].append(i)

    return edges


def _greedy_find_clique(edges: list[list[int]], start_vertex) -> set[int]:
    """
    Find a maximal clique in a graph using a greedy algorithm starting from a given vertex.

    Args:
        edges (list[list[int]]): The adjacency list representing the graph, where edges[i] contains a list of nodes connected to node i.
        start_vertex (int): The vertex to start the clique search from.

    Returns:
        set[int]: A set of vertices that form a maximal clique including the start_vertex.
    """
    clique = {start_vertex}

    candidates = set(edges[start_vertex])

    while candidates:
        for vertex in candidates:
            if all(vertex in edges[v] for v in clique):
                clique.add(vertex)
                candidates.intersection_update(edges[vertex])
                break
        else:
            break

    return clique


def _merge_cliques(
    edges: list[list[int]], clique_list: list[set[int]]
) -> list[set[int]]:
    """
    Merges cliques in a graph if the merged clique remains fully connected.

    Args:
        edges (list[list[int]]): The adjacency list representing the graph, where edges[i] contains a list of nodes connected to node i.
        clique_list (list[set[int]]): A list of cliques, where each clique is a set of nodes.

    Returns:
        list[set[int]]: A list of merged cliques that are fully connected.
    """
    merged_clique_list = list()

    while clique_list:
        clique = clique_list.pop(0)
        merged = False

        for i in range(len(merged_clique_list)):
            potential_clique = merged_clique_list[i] | clique

            if _check_fully_connected(edges, potential_clique):
                merged_clique_list[i] = potential_clique
                merged = True
                break

        if not merged:
            merged_clique_list.append(clique)

    return merged_clique_list


def _check_fully_connected(edges: list[list[int]], clique: set[int]) -> bool:
    """
    Checks if all nodes in the given clique are fully connected in the graph.

    Args:
        edges (list[list[int]]): The adjacency list representing the graph, where edges[i] contains a list of nodes connected to node i.
        clique (set[int]): A set of nodes that form the clique to check for full connectivity.

    Returns:
        bool: True if the clique is fully connected, False otherwise.
    """
    clique = list(clique)
    for i in range(len(clique)):
        for j in range(i + 1, len(clique)):
            if clique[j] not in edges[clique[i]]:
                return False

    return True
