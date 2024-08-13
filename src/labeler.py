from collections import deque
import json
import os

from utility import load_config

config = load_config()

PLACED_PATH = config["paths"]["placed"]
LABELLED_PATH = config["paths"]["labelled"]

# Define constants
DEFAULT_FILE_COUNT = 100
DEFAULT_DIFFICULTY_CURVE_INTERVAL = 5

# Input parameter names list
input_parameter_names = [
    "enemy_group",
    "enemy_group_size",
    "enemy_ideal",
    "treasure",
    "boss",
]

# Output parameter names list
"""
Caution: The names of the output parameters are currently hard-coded in labeler.py.
If the output parameters need to be modified in the current state, they must be changed one by one.
"""
output_parameter_names = [
    "density",
    "empty_ratio",
    "exploration_requirement",
    "difficulty_curve",
    "treasure_count",
    "enemy_count",
    "map_size",
    "nonlinearity",
    "room_count",
]

# Tile icons
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
    placed_path: str = PLACED_PATH,
    labelled_path: str = LABELLED_PATH,
    file_count: int = DEFAULT_FILE_COUNT,
    difficulty_curve_interval: int = DEFAULT_DIFFICULTY_CURVE_INTERVAL,
) -> None:
    """
    Labels level data by estimating and updating parameters.

    Args:
        placed_path: Path to the input files.
        labelled_path: Path to the output files.
        file_count: Number of files to process.
        difficulty_curve_interval: Interval for difficulty curve calculation.
    """

    # Load data. input_data is a list of batches = { "map_list": [] }
    data = load_folder(path=placed_path, file_count=file_count)

    # Estimate each level data
    for i, data_i in enumerate(data):
        for j, map_list_j in enumerate(data_i["map_list"]):
            new_params = estimate(map_list_j["map"], difficulty_curve_interval)
            data[i]["map_list"][j]["params"].update(new_params)

    # Save data
    save_folder(data=data, path=labelled_path, file_count=file_count)


def estimate(
    level: str, difficulty_curve_interval: int = DEFAULT_DIFFICULTY_CURVE_INTERVAL
) -> dict[str, float]:
    """
    Estimate level parameters and return them as a dictionary.

    Args:
        level: Level data in string format.
        difficulty_curve_interval: Interval for difficulty curve calculation.

    Returns:
        Dictionary of estimated parameters.
    """
    # Convert string level to list level it
    list_level = str_level_to_list_level(level)

    # Count parameters
    counts = _calculate_counts(list_level)

    # Find positions of objects and calculate distances
    positions = _find_positions(list_level)
    distances = _calculate_distances(list_level, positions["entry"], positions["exit"])

    # Calculate and store output parameters
    output_parameters = _calculate_output_parameters(
        counts, positions, distances, difficulty_curve_interval, list_level
    )

    return output_parameters


def _calculate_counts(list_level: list) -> dict:
    """Calculate and return the count-related parameters."""
    (
        treasure_count,
        enemy_count,
        empty_tile_count,
        map_size,
        total_object_count,
        total_passable_tile_count,
        total_tile_count,
    ) = _set_count_param(list_level)

    return {
        "treasure_count": treasure_count,
        "enemy_count": enemy_count,
        "empty_tile_count": empty_tile_count,
        "map_size": map_size,
        "total_object_count": total_object_count,
        "total_passable_tile_count": total_passable_tile_count,
        "total_tile_count": total_tile_count,
    }


def _find_positions(list_level: list) -> dict:
    """Find and return the positions of objects."""
    object_positions, enemy_positions, exit_position, entry_position = _set_object_dict(
        list_level
    )

    return {
        "object_positions": object_positions,
        "enemy_positions": enemy_positions,
        "exit": exit_position,
        "entry": entry_position,
    }


def _calculate_distances(list_level: list, entry_pos: tuple, exit_pos: tuple) -> dict:
    """Calculate and return the distance dictionaries."""
    distance_dict_entry, distance_dict_exit = _set_distance_dict(
        list_level, entry_pos, exit_pos
    )

    return {
        "entry": distance_dict_entry,
        "exit": distance_dict_exit,
    }


def _calculate_output_parameters(
    counts: dict,
    positions: dict,
    distances: dict,
    difficulty_curve_interval: int,
    list_level: list,
) -> dict:
    """Calculate and return the output parameters."""
    output_parameters = {
        output_parameter_names[0]: _density(
            counts["treasure_count"] + counts["enemy_count"], counts["total_tile_count"]
        ),
        output_parameter_names[1]: _empty_ratio(
            counts["empty_tile_count"], counts["total_tile_count"]
        ),
        output_parameter_names[2]: _exploration_requirement(
            distances["entry"], positions["object_positions"]
        ),
        output_parameter_names[3]: _difficulty_curve(
            distances["entry"], positions["enemy_positions"], difficulty_curve_interval
        ),
        output_parameter_names[4]: counts["treasure_count"],
        output_parameter_names[5]: counts["enemy_count"],
        output_parameter_names[6]: counts["map_size"],
    }

    # Calculate nonlinearity only if the level is playable
    output_parameters[output_parameter_names[7]] = _nonlinearity(
        distances["entry"],
        distances["exit"],
        positions["object_positions"],
        counts["total_object_count"],
        counts["total_passable_tile_count"],
    )

    output_parameters[output_parameter_names[8]] = _count_rooms(list_level)

    return output_parameters


def load_file(path: str) -> list:
    """
    Load map data from a JSON file.

    Args:
        path: Relative path of the data file.

    Returns:
        A list of 100 map data items.
    """
    with open(path, "r") as f:
        data = json.load(f)

    return data


def load_folder(path: str = PLACED_PATH, file_count: int = DEFAULT_FILE_COUNT) -> list:
    """
    Load map data from a folder containing multiple files.

    Args:
        path: Relative path of the data folder.
        file_count: Number of data files in the placed folder.

    Returns:
        A list of lists containing map data.
    """
    data_list = []

    # Directory
    cur_dir = os.path.dirname(os.path.abspath(__file__))

    for i in range(file_count):
        _path = os.path.join(cur_dir, path, f"batch{i}.json")  # f-string 사용으로 수정
        data_list.append(load_file(_path))

    return data_list


def save_file(data: list, path: str) -> None:
    """
    Save map data into a JSON file.

    Args:
        path: Relative path of the data file.
        data: Map data to save.
    """
    with open(path, "w") as f:
        json.dump(data, f, indent=4)


def save_folder(
    data: list, path: str = LABELLED_PATH, file_count: int = DEFAULT_FILE_COUNT
) -> None:
    """
    Save map data into a folder containing multiple files.

    Args:
        path: Relative path of the data folder.
        data: Map data to save.
        file_count: Number of files in the labelled data folder.
    """
    if not os.path.exists(path):
        os.makedirs(path)

    # Directory
    cur_dir = os.path.dirname(os.path.abspath(__file__))
    for i in range(file_count):
        _path = os.path.join(cur_dir, path, f"batch{i}.json")
        save_file(data[i], _path)


def _set_count_param(list_level: list) -> tuple:
    treasure_count, enemy_count, empty_tile_count, map_size = _tile_count(list_level)

    total_object_count = treasure_count + enemy_count + 2
    total_passable_tile_count = total_object_count + empty_tile_count
    total_tile_count = map_size[0] * map_size[1]

    return (
        treasure_count,
        enemy_count,
        empty_tile_count,
        map_size,
        total_object_count,
        total_passable_tile_count,
        total_tile_count,
    )


def _set_object_dict(list_level: list) -> tuple:
    # Get entry position
    entry_position = _find_objects_position(list_level, icons["entry"])

    # Check the existence of entry.
    entry_uniqueness = False  # 변수명 위치와 초기화 위치를 함께 수정
    if not entry_position:
        entry_position = None
    elif len(entry_position) > 1:
        entry_position = entry_position[0]
    else:
        entry_position = entry_position[0]
        entry_uniqueness = True

    # Exit position
    boss_exists = False  # boss_existance -> boss_exists 수정
    exit_exists = False  # exit_existance -> exit_exists 수정
    exit_uniqueness = False

    # Check if there is a boss or an exit.
    for row in list_level:
        if icons["boss"] in row:
            boss_exists = True
        elif icons["exit"] in row:
            exit_exists = True
            break

    # Assign list to exit_position.
    if boss_exists:
        exit_position = _find_objects_position(list_level, icons["boss"])
    elif exit_exists:
        exit_position = _find_objects_position(list_level, icons["exit"])
    else:
        exit_position = None

    if exit_position:
        if len(exit_position) == 1:
            exit_uniqueness = True
        exit_position = exit_position[0]

    # Treasure and enemy positions
    treasure_positions = _find_objects_position(list_level, icons["treasure"])
    enemy_positions = _find_objects_position(list_level, icons["enemy"])

    # Object positions
    object_positions = treasure_positions + enemy_positions
    if entry_position is not None:
        object_positions.append(entry_position)
    if exit_position is not None:
        object_positions.append(exit_position)

    # Print existence and uniqueness
    if entry_position is None:
        print("Entry doesn't exist.")
    if not entry_uniqueness:
        print("Entry is not unique.")
    if exit_position is None:
        print("Exit doesn't exist")
    if not exit_uniqueness:
        print("Exit is not unique")

    return (
        object_positions,
        enemy_positions,
        exit_position,
        entry_position,
    )


def _set_distance_dict(list_level: list, entry_pos: tuple, exit_pos: tuple) -> tuple:
    entry_distance_dict = (
        _shortest_distances(list_level, entry_pos) if entry_pos else {}
    )
    exit_distance_dict = _shortest_distances(list_level, exit_pos) if exit_pos else {}

    return entry_distance_dict, exit_distance_dict


def _density(total_object_count: int, total_tile_count: int) -> float:
    """Returns the ratio of object tiles to total tiles."""
    return total_object_count / total_tile_count


def _empty_ratio(empty_count: int, total_tile_count: int) -> float:
    """Returns the ratio of empty tiles to total tiles."""
    return empty_count / total_tile_count


def _exploration_requirement(distance_dict_entry: dict, object_positions: list) -> int:
    """
    Returns the amount of movement required to meet all objects from the entrance.

    Args:
        distance_dict_entry: Dict of distances between entry and accessible tiles.
        object_positions: List of positions of all objects in the level.

    Returns:
        The amount of movement required to meet all objects from the entrance.

    Raises:
        KeyError: If objects are in inaccessible locations, dismisses that and prints a warning.
    """
    total_movement = 0  # 변수명 sum -> total_movement로 수정
    for obj_pos in object_positions:
        try:
            total_movement += distance_dict_entry[obj_pos]
        except KeyError:
            print("Object may be in an inaccessible location.")

    return total_movement


def _difficulty_curve(distance_dict: dict, enemy_positions: tuple, n: int) -> float:
    """Returns the difficulty curve."""

    heights = []

    # Find the longest distance within accessible points.
    longest_distance = max(distance_dict.values(), default=0)  # 코드 간소화

    for i in range(longest_distance // n + 1):
        temp_height = 0
        for enemy_pos in enemy_positions:
            try:
                enemy_distance = distance_dict[enemy_pos]
                if i * n < enemy_distance <= (i + 1) * n:
                    temp_height += 1
            except KeyError:
                print("Enemy may be in an inaccessible location.", enemy_pos)
        heights.append(temp_height)

    height_difference = heights[0] - heights[-1]
    interval_count = longest_distance // n + 1
    return (
        height_difference / interval_count
    )  # Mean variation of enemy number per interval.


def _nonlinearity(
    entry_distance_dict: dict,
    exit_distance_dict: dict,
    object_positions: list,
    total_object_count: int,
    total_passable_tile_count: int,
) -> float:
    """Returns the nonlinearity."""

    entry_sum = 0
    exit_sum = 0
    for obj_pos in object_positions:
        # Calculate flood coverage
        try:
            entry_obj_dist = entry_distance_dict[obj_pos]
        except KeyError:
            print("Object may be in an inaccessible location from entry.", obj_pos)
            entry_obj_dist = 0
        try:
            exit_obj_dist = exit_distance_dict[obj_pos]
        except KeyError:
            print("Object may be in an inaccessible location from exit.", obj_pos)
            exit_obj_dist = 0

        entry_counter = sum(
            1 for dist in entry_distance_dict.values() if dist <= entry_obj_dist
        )
        exit_counter = sum(
            1 for dist in exit_distance_dict.values() if dist <= exit_obj_dist
        )

        entry_sum += entry_counter
        exit_sum += exit_counter

    result = entry_sum + exit_sum

    return result / total_passable_tile_count / total_object_count


def _is_in_bounds(x: int, y: int, x_boundary: int, y_boundary: int) -> bool:
    """Check if the position is within the map boundaries."""
    return 0 <= x < x_boundary and 0 <= y < y_boundary


def _is_accessible(target_tile: str, icon_obstacles: set) -> bool:
    """Check if the tile at (x, y) is accessible."""
    return target_tile not in icon_obstacles


def _shortest_distances(list_level: list, pos: tuple) -> dict:
    """
    Find the shortest distances from pos to every tile in the map.

    Args:
        pos: Starting position (x, y).

    Returns:
        dict: A dictionary of shortest distances to each tile.
        Also logs inaccessible tiles for debugging.
    """
    que = deque([pos])
    result = {pos: 0}

    x_boundary = len(list_level)
    y_boundary = len(list_level[0])
    icon_obstacles = set(icons["wall"])

    directions = [(1, 0), (-1, 0), (0, 1), (0, -1)]
    while que:
        current = que.popleft()
        x, y = current

        for dx, dy in directions:
            new_x, new_y = x + dx, y + dy
            if (new_x, new_y) not in result:
                if _is_in_bounds(new_x, new_y, x_boundary, y_boundary):
                    if _is_accessible(list_level[new_x][new_y], icon_obstacles):
                        que.append((new_x, new_y))
                        result[(new_x, new_y)] = result[current] + 1

    return result


def _find_objects_position(list_level: list, obj_icon: str) -> list:
    """Find all positions of a specific object icon in the level."""
    return [
        (i, j)
        for i, row in enumerate(list_level)
        for j, tile in enumerate(row)
        if tile == obj_icon
    ]


def str_level_to_list_level(level: str) -> list:
    """
    Convert a string level into a 2D list level.
    """
    result = [[char for char in row] for row in level.split("\n")]
    if not result[-1]:
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


def _count_rooms(list_level: list) -> int:
    """
    Count the number of rooms in the level. A room is defined as a continuous space surrounded by walls.

    Args:
        list_level: 2D list representing the level.

    Returns:
        Number of rooms.
    """
    icon_wall = icons["wall"]

    closed_space_count = 0
    visited = set()
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    icon_obstacles = {icon_wall, icons["door"], icons["outside"]}

    x_boundary = len(list_level)
    y_boundary = len(list_level[0])

    for x in range(x_boundary):
        for y in range(y_boundary):
            if (x, y) not in visited and _is_accessible(
                list_level[x][y], icon_obstacles
            ):
                closed_space_count += 1
                que = deque([(x, y)])
                while que:
                    cur_x, cur_y = que.popleft()
                    for dx, dy in directions:
                        new_x = cur_x + dx
                        new_y = cur_y + dy
                        next_pos = (new_x, new_y)
                        if (
                            next_pos not in visited
                            and _is_in_bounds(new_x, new_y, x_boundary, y_boundary)
                            and _is_accessible(list_level[new_x][new_y], icon_obstacles)
                        ):
                            visited.add(next_pos)
                            que.append(next_pos)

    return closed_space_count


if __name__ == "__main__":
    label(file_count=1)
