from collections import deque
import json
import os


# input parameters name list
input_parameters_name = [
    "enemy_group",
    "enemy_group_size",
    "enemy_ideal",
    "reward",
    "boss",
]

# output parameters name list
"""
Caution: the names of the output parameter are currently hard-coded in labeler.py .
If the output parameter needs to be modified in the current state, it needs to be changed one by one.
"""
output_parameters_name = [
    "density",
    "empty_ratio",
    "exploration_requirement",
    "difficulty_curve",
    "nonlinearity",
    "reward_num",
    "enemy_num",
    "map_size",
]

# tile icons
icons = {
    "enemy": "E",
    "reward": "R",
    "entry": "P",
    "exit": ">",
    "boss": "B",
    "empty": ".",
    "wall": "#",
}


def label(
    input_file_num: int = 100,
    output_file_num: int = 100,
    difficulty_curve_interval: int = 5,
) -> None:
    """
    label level data.
    Load.
    Estimate each level.
    Save.
    """

    # Load data. input_data is a list of batch = { map_list: [] }
    # input_data = [batch0, batch1, ...]
    input_data = load_folder()

    # estimate each level data
    output_data = input_data
    for i in len(input_data):
        map_list = input_data[i]["map_list"]

        for j in len(map_list):
            new_params = estimate(map_list[j]["map"])
            output_data[i]["map_list"][j]["params"].update(new_params)

    # Save data
    save_folder(output_data)

    return


def estimate(list_level: list, difficulty_curve_interval: int = 5) -> dict:
    # num parameters
    (
        reward_num,
        enemy_num,
        empty_tile_num,
        map_size,
        total_object_num,
        total_passible_tile_num,
        total_tile_num,
    ) = _set_num_param(list_level)

    # set object positions
    (
        object_positions,
        enemy_positions,
        reward_positions,
        exit_position,
        entry_position,
    ) = _set_object_dict(list_level)

    # set distance dict
    distance_dict_entry, distance_dict_exit = _set_distance_dict(
        list_level, entry_position, exit_position
    )

    # Make a result dict
    output_parameters = dict()
    output_parameters["density"] = str(_density(reward_num + enemy_num, total_tile_num))
    output_parameters["empty_ratio"] = str(_empty_ratio(empty_tile_num, total_tile_num))
    output_parameters["exploration_requirement"] = str(
        _exploration_requirement(distance_dict_entry, object_positions)
    )
    output_parameters["difficulty_curve"] = str(
        _difficulty_curve(
            distance_dict_entry, enemy_positions, difficulty_curve_interval
        )
    )
    output_parameters["nonlinearity"] = str(
        _nonlinearity(
            distance_dict_entry,
            distance_dict_exit,
            object_positions,
            total_object_num,
            total_passible_tile_num,
        )
    )
    output_parameters["reward_num"] = str(reward_num)
    output_parameters["enemy_num"] = str(enemy_num)
    output_parameters["map_size"] = str(map_size)

    return output_parameters


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


def load_folder(path: str = "..\\data\\placed", file_num: int = 100) -> list:
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

    for i in range(file_num):
        _path = os.path.join(cur_dir, path, "batch" + str(i) + ".json")
        data_list.append(load_file(_path))

    return data_list


def save_file(data: list, path: str) -> None:
    """
    Save map data into json file.

    Args:
        path: relative path of data file.
        data: 100 map data for a file.
    """

    # temporary script xxx
    with open(path, "w") as f:
        json.dump(data, f)

    return


def save_folder(
    data: list, path: str = "..\\data\\labelled", file_num: int = 100
) -> None:
    """
    Save map data into data folder.

    Args:
        path: relative path of data folder.
        data: 100 map data for the folder.
        file_num: the number of files in a labelled data folder
    """

    # directory
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    for i in range(file_num):
        _path = os.path.join(cur_dir, path, "batch" + str(i) + ".json")
        save_file(data[i], _path)

    return


def _set_num_param(list_level: list) -> tuple:
    reward_num, enemy_num, empty_tile_num, map_size = _tile_count(list_level)

    total_object_num = reward_num + enemy_num + 2
    total_passible_tile_num = total_object_num + empty_tile_num
    total_tile_num = map_size[0] * map_size[1]

    return (
        reward_num,
        enemy_num,
        empty_tile_num,
        map_size,
        total_object_num,
        total_passible_tile_num,
        total_tile_num,
    )


def _set_object_dict(list_level: list) -> tuple:
    entry_position = _find_objects_position(list_level, icons["entry"])[0]
    for i in range(len(list_level)):
        row = list_level[0]
        if icons["boss"] in row:
            exit_position = _find_objects_position(list_level, icons["boss"])[0]
            break
        elif icons["exit"] in row:
            exit_position = _find_objects_position(list_level, icons["exit"])[0]
            break
    reward_positions = _find_objects_position(list_level, icons["reward"])
    enemy_positions = _find_objects_position(list_level, icons["enemy"])
    object_positions = (
        [entry_position] + [exit_position] + reward_positions + enemy_positions
    )

    return (
        object_positions,
        enemy_positions,
        reward_positions,
        exit_position,
        entry_position,
    )


def _set_distance_dict(list_level: list, entry_pos: tuple, exit_pos: tuple) -> tuple:
    entry_distance_dict = _shortest_distances(list_level, entry_pos)
    exit_distance_dict = _shortest_distances(list_level, exit_pos)

    return entry_distance_dict, exit_distance_dict


def _density(total_object_num: int, total_tile_num: int) -> float:
    """Returns the ratio of object tiles to total tiles."""
    return total_object_num / total_tile_num


def _empty_ratio(empty_num: int, total_tile_num: int) -> float:
    """Returns the ratio of empty tiles to total tiles."""
    return empty_num / total_tile_num


def _exploration_requirement(distance_dict_entry: dict, object_positoins: list) -> int:
    """
    Return the amount of movement required to meet all objects from the entrance

    Args:
        distance_dict_entry: dict of amount of movement btw entry and accessible tile.
        object_positoins: list of positions of all objects in the level.

    Return:
        the amount of movement required to meet all objects from the entrance

    Raise:
        KeyError: If there are objects on inaccessible location, it dismiss that and print message 'Object may be on inaccessible location.'
    """

    sum = 0
    for obj_pos in object_positoins:
        try:
            sum += distance_dict_entry[obj_pos]
        except KeyError:
            print("Object may be on inaccessible location.")

    return sum


def _difficulty_curve(distance_dict: dict, enemy_positions: tuple, n: int) -> float:
    """Returns the difficulty curve."""

    heights = []

    # find longest distance within accessible point.
    longest_distance = 0
    for dist in distance_dict.values():
        if longest_distance < dist:
            longest_distance = dist

    for i in range(longest_distance // n + 1):
        temp_height = 0
        for enemy_pos in enemy_positions:
            try:
                enemy_distance = distance_dict[enemy_pos]
                if i * n < enemy_distance <= (i + 1) * n:
                    temp_height += 1
            except KeyError:
                print("Enemy may be on inaccessible location.", enemy_pos)
        heights.append(temp_height)

    height_difference = heights[0] - heights[len(heights) - 1]
    interval_num = longest_distance // n + 1
    return (
        height_difference / interval_num
    )  # mean that variation of enemy number per interval n.


def _nonlinearity(
    entry_distance_dict: dict,
    exit_distance_dict: dict,
    object_positions: list,
    total_object_num: int,
    total_passible_tile_num: int,
) -> float:
    """Returns the nonlinearity."""

    entry_sum = 0
    exit_sum = 0
    for obj_pos in object_positions:
        # calculate flood coverage
        entry_obj_dist = entry_distance_dict[obj_pos]
        exit_obj_dist = exit_distance_dict[obj_pos]

        entry_counter = 0
        exit_counter = 0

        for dist in entry_distance_dict.values():
            if dist <= entry_obj_dist:
                entry_counter += 1

        for dist in exit_distance_dict.values():
            if dist <= exit_obj_dist:
                exit_counter += 1

        entry_sum += entry_counter
        exit_sum += exit_counter

    result = entry_sum + exit_sum

    return result / total_passible_tile_num / total_object_num


def _shortest_distances(list_level: list, pos: tuple) -> dict:
    """
    Find shortest distance btw pos1, pos2.

    Aruements
        pos1: (int, int)
        pos2: (int, int)
    """

    # flood fill algorithm by BFS
    # data
    que = deque()
    result = {}  # dict of {key: position, value: distance from pos}.

    # initial setting
    que.append(pos)
    visited = [pos]
    result[pos] = 0

    x_boundary = len(list_level)
    y_boundary = len(list_level[0])

    while len(que) != 0:
        current = que.popleft()

        # visit
        x = current[0]
        y = current[1]
        directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]

        for dx, dy in directions:
            new_x = x + dx
            new_y = y + dy
            if (new_x, new_y) not in visited:
                if (
                    new_x >= 0
                    and new_x < x_boundary
                    and new_y >= 0
                    and new_y < y_boundary
                ):
                    temp = list_level[new_x][new_y]
                    if temp != icons["wall"]:
                        que.append((new_x, new_y))
                        visited.append((new_x, new_y))
                        result[(new_x, new_y)] = result[current] + 1

    return result


def _find_objects_position(list_level: list, obj_icon: str) -> list:
    result = []

    for i in range(len(list_level)):
        for j in range(len(list_level[0])):
            if list_level[i][j] == obj_icon:
                result.append((i, j))

    return result


def str_level_to_list_level(level: str) -> tuple:
    result = []
    row = []

    parameters_result = []

    # take first line
    first_line = level[: level.find("\n") + 1]

    for name in input_parameters_name:
        index = first_line.find(
            name
        )  # "enemy_group=13~15,enemy_group_size=1,enemy_ideal=-1,reward=0,boss=0\n"
        temp = first_line[
            index:
        ]  # "enemy_group_size=1,enemy_ideal=-1,reward=0,boss=0\n"
        if "," in temp:
            temp = temp[: temp.find(",")]  # "enemy_group_size=1"
        else:
            temp = temp[: temp.find("\n")]
        temp = temp[temp.find("=") :].lstrip("=")  # '1'
        parameters_result.append(temp)

    # cutting first line (it means level.lstrip(first_line + "\n"))
    level = level[level.find("\n") :]
    level = level.lstrip("\n")

    for char in level:
        if char != "\n":
            row.append(char)
        else:
            result.append(row)
            row = []

    return result, tuple(parameters_result)


def _tile_count(list_level: list) -> tuple:
    reward_num = 0
    enemy_num = 0
    empty_tile_num = 0
    map_size = len(list_level), len(list_level[0])
    for row in list_level:
        for tile in row:
            if tile == icons["reward"]:
                reward_num += 1
            elif tile == icons["enemy"]:
                enemy_num += 1
            elif tile == icons["empty"]:
                empty_tile_num += 1

    return reward_num, enemy_num, empty_tile_num, map_size


def insert_level_parameter(level: str, output_parameters: dict) -> str:
    first_line = level[: level.find("\n")]
    result_level = level.lstrip(first_line)

    for param_name in output_parameters:
        value = output_parameters[param_name]

        type_value = type(value)
        if type_value == float:
            addition = param_name + "=" + format(value, ".3f") + ","
        elif type_value == tuple:
            addition = param_name + "=" + str(value[0]) + "*" + str(value[1]) + ","
        else:
            addition = param_name + "=" + str(value) + ","

        first_line += addition

    result_level = first_line.rstrip(",") + result_level

    return result_level


if __name__ == "__main__":
    label()
    pass
