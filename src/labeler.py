from collections import deque
import json
import os

# input parameters name list
input_parameters_name = [
    "enemy_group",
    "enemy_group_size",
    "enemy_ideal",
    "treasure",
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
    "playability",
    "treasure_count",
    "enemy_count",
    "map_size",
    "nonlinearity",
    "room_count",
]


# tile icons
icons = {
    "enemy": "E",
    "treasure": "T",
    "entry": "P",
    "exit": ">",
    "boss": "B",
    "empty": ".",
    "wall": "#",
    "outside": " ",
    "door": "/",
}


def label(
    placed_file_path: str = "../data/2. placed",
    labelled_file_path: str = "../data/3. labelled",
    file_count: int = 100,
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
    input_data = load_folder(path=placed_file_path, file_count=file_count)

    # estimate each level data
    output_data = input_data
    for i in range(len(input_data)):
        map_list = input_data[i]["map_list"]

        for j in range(len(map_list)):
            new_params = estimate(map_list[j]["map"], difficulty_curve_interval)
            output_data[i]["map_list"][j]["params"].update(new_params)

    # Save data
    save_folder(data=output_data, path=labelled_file_path, file_count=file_count)

    return


def estimate(level: str, difficulty_curve_interval: int = 5) -> dict:
    """
    Make scores(it means parameters) by estimating level.
    """
    # str level to list level.
    list_level = str_level_to_list_level(level)
    _standardize(list_level)

    # count parameters
    (
        treasure_count,
        enemy_count,
        empty_tile_count,
        map_size,
        total_object_count,
        total_passible_tile_count,
        total_tile_count,
    ) = _set_count_param(list_level)

    # Find out the position information of all objects.
    # Here, object means enemy + treasure + exit + entry
    (
        object_positions,
        enemy_positions,
        exit_position,
        entry_position,
    ) = _set_object_dict(list_level)

    # set distance dict
    distance_dict_entry, distance_dict_exit = _set_distance_dict(
        list_level, entry_position, exit_position
    )

    # Make a result dict
    output_parameters = dict()
    output_parameters[output_parameters_name[0]] = _density(
        treasure_count + enemy_count, total_tile_count
    )
    output_parameters[output_parameters_name[1]] = _empty_ratio(
        empty_tile_count, total_tile_count
    )
    output_parameters[output_parameters_name[2]] = _exploration_requirement(
        distance_dict_entry, object_positions
    )
    output_parameters[output_parameters_name[3]] = _difficulty_curve(
        distance_dict_entry, enemy_positions, difficulty_curve_interval
    )
    output_parameters[output_parameters_name[4]] = _is_playable(list_level)
    output_parameters[output_parameters_name[5]] = treasure_count
    output_parameters[output_parameters_name[6]] = enemy_count
    output_parameters[output_parameters_name[7]] = map_size
    if output_parameters[output_parameters_name[4]] == True:
        output_parameters[output_parameters_name[8]] = _nonlinearity(
            distance_dict_entry,
            distance_dict_exit,
            object_positions,
            total_object_count,
            total_passible_tile_count,
        )
    else:
        output_parameters[output_parameters_name[8]] = None
    output_parameters[output_parameters_name[9]] = _count_room(list_level)

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


def load_folder(path: str = "../data/2. placed", file_count: int = 100) -> list:
    """
    Load map data from data folder.

    Args:
        path: relative path of data folder.
        file_count: the number of data files in the placed folder.
    Returns:
        a list of 100 lists of 100 map data.
    """
    data_list = list()

    # dicrectory
    cur_dir = os.path.dirname(os.path.abspath(__file__))

    for i in range(file_count):
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
        json.dump(data, f, indent=4)

    return


def save_folder(
    data: list, path: str = "../data/3. labelled", file_count: int = 100
) -> None:
    """
    Save map data into data folder.

    Args:
        path: relative path of data folder.
        data: 100 map data for the folder.
        file_count: the number of files in a labelled data folder
    """

    # directory
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    for i in range(file_count):
        _path = os.path.join(cur_dir, path, "batch" + str(i) + ".json")
        save_file(data[i], _path)

    return


def _set_count_param(list_level: list) -> tuple:
    treasure_count, enemy_count, empty_tile_count, map_size = _tile_count(list_level)

    total_object_count = treasure_count + enemy_count + 2
    total_passible_tile_count = total_object_count + empty_tile_count
    total_tile_count = map_size[0] * map_size[1]

    return (
        treasure_count,
        enemy_count,
        empty_tile_count,
        map_size,
        total_object_count,
        total_passible_tile_count,
        total_tile_count,
    )


def _set_object_dict(list_level: list) -> tuple:
    # Get entry position
    entry_position = _find_objects_position(list_level, icons["entry"])

    # Check the existance of entry.
    temp_len = len(entry_position)
    if temp_len == 0:
        entry_position = None
        entry_uniqueness = False
    elif temp_len > 1:
        entry_position = entry_position[0]
        entry_uniqueness = False
    else:
        entry_position = entry_position[0]
        entry_uniqueness = True

    # exit position
    boss_existance = False
    exit_existance = False
    exit_uniqueness = False

    # Check if there is a boss or an exit.
    for i in range(len(list_level)):
        row = list_level[i]
        if icons["boss"] in row:
            boss_existance = True
        elif icons["exit"] in row:
            exit_existance = True
            break

    # Assign list into exit_positions.
    if boss_existance:
        exit_position = _find_objects_position(list_level, icons["boss"])
    elif exit_existance:
        exit_position = _find_objects_position(list_level, icons["exit"])
    else:
        exit_position = None

    if exit_position is not None:
        # Check exit uniqueness.
        if len(exit_position) == 1:
            exit_uniqueness = True
        # Assign non-list exit_position.
        exit_position = exit_position[0]

    # treasure position
    treasure_positions = _find_objects_position(list_level, icons["treasure"])
    enemy_positions = _find_objects_position(list_level, icons["enemy"])

    # object position
    object_positions = treasure_positions + enemy_positions
    if entry_position != None:
        object_positions += [entry_position]
    if exit_position != None:
        object_positions += [exit_position]

    # Print existance & uniqueness
    if entry_position is None:
        print("Entry doesn't exist.")
    if not entry_uniqueness:
        print("Entry is not unique.")
    if exit_position is None:
        print("Exit doesn't exist")
    if not exit_uniqueness:
        print("Exit is not unique")

    # Also can use treasure pos.
    return (
        object_positions,
        enemy_positions,
        exit_position,
        entry_position,
    )


def _set_distance_dict(list_level: list, entry_pos: tuple, exit_pos: tuple) -> tuple:
    if entry_pos != None:
        entry_distance_dict = _shortest_distances(list_level, entry_pos)
    else:
        entry_distance_dict = dict()

    if exit_pos != None:
        exit_distance_dict = _shortest_distances(list_level, exit_pos)
    else:
        exit_distance_dict = dict()

    return entry_distance_dict, exit_distance_dict


def _density(total_object_count: int, total_tile_count: int) -> float:
    """Returns the ratio of object tiles to total tiles."""
    return total_object_count / total_tile_count


def _empty_ratio(empty_count: int, total_tile_count: int) -> float:
    """Returns the ratio of empty tiles to total tiles."""
    return empty_count / total_tile_count


def _exploration_requirement(distance_dict_entry: dict, object_positoins: list) -> int:
    """
    Return the amount of movement required to meet all objects from the entrance

    Args:
        distance_dict_entry: dict of amount of movement btw entry and accessible tile.
        object_positoins: list of positions of all objects in the level.

    Returns:
        the amount of movement required to meet all objects from the entrance

    Raises:
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
    interval_count = longest_distance // n + 1
    return (
        height_difference / interval_count
    )  # mean that variation of enemy number per interval n.


def _nonlinearity(
    entry_distance_dict: dict,
    exit_distance_dict: dict,
    object_positions: list,
    total_object_count: int,
    total_passible_tile_count: int,
) -> float:
    """Returns the nonlinearity."""

    entry_sum = 0
    exit_sum = 0
    for obj_pos in object_positions:
        # calculate flood coverage
        try:
            entry_obj_dist = entry_distance_dict[obj_pos]
        except KeyError:
            print("Objects may be on inaccessible location with entry.", obj_pos)
            entry_obj_dist = 0
        try:
            exit_obj_dist = exit_distance_dict[obj_pos]
        except KeyError:
            print("Objects may be on inaccessible location with exit.", obj_pos)
            exit_obj_dist = 0

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

    return result / total_passible_tile_count / total_object_count


def _shortest_distances(list_level: list, pos: tuple) -> dict:
    """
    Find shortest distances from pos to every tiles in the map.

    Aruements
        pos: (int, int)
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


def str_level_to_list_level(level: str) -> list:
    """
    Make str level into 2D list level.
    """
    result = []
    row = []

    result = [[char for char in row] for row in level.split("\n")]
    if result[-1] == []:
        result = result[:-1]
    return result


def _tile_count(list_level: list) -> tuple:
    treasure_count = 0
    enemy_count = 0
    empty_tile_count = 0
    map_size = len(list_level), len(list_level[0])
    for row in list_level:
        for tile in row:
            if tile == icons["treasure"]:
                treasure_count += 1
            elif tile == icons["enemy"]:
                enemy_count += 1
            elif tile == icons["empty"]:
                empty_tile_count += 1

    return treasure_count, enemy_count, empty_tile_count, map_size


def _is_playable(list_level: list) -> bool:
    entry_pos = _find_objects_position(list_level, icons["entry"])
    if entry_pos == []:
        return False
    else:
        entry_pos = entry_pos[0]

    exit_pos = _find_objects_position(list_level, icons["boss"])
    if exit_pos == []:
        exit_pos = _find_objects_position(list_level, icons["exit"])
        if exit_pos == []:
            return False
        else:
            exit_pos = exit_pos[0]
    else:
        exit_pos = exit_pos[0]

    entry_distance_dict = _shortest_distances(list_level, entry_pos)

    # entry_distance_dict only has info of accessible tiles.
    return exit_pos in entry_distance_dict


def _count_room(list_level: list) -> int:
    """
    (A) The number of room is defined as the number of discontinuous tunnels plus one.

    (B) The tunnel means that a passible tile surrounded by two opppsite walls.

    (C) The process is simple.
    1. find all tunnels.
    2. count discontinuous tunnels.
    """

    # Initialization.
    tunnels = []
    discontinuous_tunnels_count = 1

    x_boundary = len(list_level)
    y_boundary = len(list_level[0])

    icon_wall = icons["wall"]

    directions = {"up_down": ((1, 0), (-1, 0)), "right_left": ((0, 1), (0, -1))}

    # Find tunnels
    for x in range(len(list_level)):
        for y in range(len(list_level[x])):
            is_surround_wall = {"up_down": False, "right_left": False}
            for dir_name in directions:
                wall_count = 0
                for dx, dy in directions[dir_name]:
                    new_x = x + dx
                    new_y = y + dy

                    if (
                        new_x >= 0
                        and new_x < x_boundary
                        and new_y >= 0
                        and new_y < y_boundary
                        and list_level[new_x][new_y] == icon_wall
                    ):
                        wall_count += 1

                is_surround_wall[dir_name] = wall_count == 2

            # XOR test.
            ud = is_surround_wall["up_down"]  # ud means up down.
            rl = is_surround_wall["right_left"]  # rl means right left.
            if (ud == True and rl == False) or (ud == False and rl == True):
                # check passibility
                if (
                    list_level[x][y] != icon_wall
                    and list_level[x][y] != icons["outside"]
                ):
                    tunnels.append((x, y))

    # Count discontinuous tunnels.
    origin = dict()
    for cur in tunnels:
        origin[cur] = cur

    for x, y in tunnels:
        not_adjacent_tunnel_count = 0

        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            new_x = x + dx
            new_y = y + dy

            if (new_x, new_y) not in tunnels:
                not_adjacent_tunnel_count += 1
            elif origin[(new_x, new_y)] == (new_x, new_y):
                # Set the origin of this continuous tunnel to the origin of current tunnel.
                origin[(new_x, new_y)] = origin[(x, y)]

        if not_adjacent_tunnel_count == 4:
            discontinuous_tunnels_count += 1

    # Count the number of Count the number of different origins.
    org_count = 1
    org_exist = []
    for org in origin.values():
        if org not in org_exist:
            org_exist.append(org)
            org_count += 1

    # Find a closed space
    closed_space_count = 0
    visited = list()
    que = deque()
    que.append((0, 0))

    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    icon_obstacle = [icon_wall, icons["door"], icons["outside"]]

    for x in range(len(list_level)):
        row = list_level[x]
        for y in range(len(row)):

            tile = list_level[x][y]
            if (x, y) not in visited and tile not in icon_obstacle:
                closed_space_count += 1
                # Let's BFS
                que.append((x, y))
                while que:
                    cur = que.popleft()
                    for dx, dy in directions:
                        next = (cur[0] + dx, cur[1] + dy)
                        try:
                            if (
                                next not in visited
                                and list_level[next[0]][next[1]] not in icon_obstacle
                            ):
                                visited.append(next)
                                que.append(next)
                        except IndexError:
                            pass

    return closed_space_count


def _standardize(list_level: list) -> None:
    """
    Make list level standardized.
    It means
    ''''
    ###''
    # ##'
    ###''
    ''''

    -->>

    ''''
    ###''
    #.##'
    ###''
    ''''

    -->>

    '''''
    ### '
    #.##'
    ### '
    '''''

    Here, x means spacebar
    """

    # Change space ' ' into dot '.'
    for i in range(len(list_level)):
        row = list_level[i]
        for j in range(len(row)):
            if row[j] == icons["outside"]:
                list_level[i][j] = icons["empty"]

    # Find maximum length of rows.
    row_max_len = 0
    for row in list_level:
        cur_row_len = len(row)
        if cur_row_len > row_max_len:
            row_max_len = cur_row_len

    # Fill places not standardized into space bars.
    for i in range(len(list_level)):
        differnece = row_max_len - len(list_level[i])
        for j in range(differnece):
            list_level[i].append(" ")

    return


if __name__ == "__main__":
    label(file_count=1)

    pass
