import labeler

param_names = ("playability", "other_ASCII_count", "empty_validation")


# =====================
# 1. Game level validation
# =====================
def validate(
    level: str,
    difficulty_curve_interval: int = labeler.DEFAULT_DIFFICULTY_CURVE_INTERVAL,
) -> dict[str, float]:
    """
    Validate the given level by calculating "treasure_count", "enemy_count", "map_size", "room_count","playability", "other_ASCII_count", "empty_validation"

    Args:
        level (str): The level represented as a string.
        difficulty_curve_interval (int, optional): Interval used for calculating the difficulty curve. Defaults to labeler.DEFAULT_DIFFICULTY_CURVE_INTERVAL.

    Returns:
        dict[str, float]: Dictionary of calculated parameters such as playability, exploration requirements, and other level metrics.
    """
    # Convert string level to list level and standardize it
    list_level = _prepare_level(level)
    if list_level is None:
        output_parameters = _set_none_parameters()
        return output_parameters

    # Count parameters
    counts = labeler._set_count_dict(list_level)

    # Find positions of objects and calculate distances
    positions = labeler._set_object_dict(list_level)
    distances, accessible_tile_count = labeler._set_distance_dict(
        list_level, positions["entry"], positions["exit"]
    )

    # Calculate and store output parameters
    output_parameters = _calculate_parameters(
        counts,
        positions,
        distances,
        difficulty_curve_interval,
        list_level,
        accessible_tile_count,
    )

    return output_parameters


def _prepare_level(level: str) -> list:
    list_level = labeler.str_level_to_list_level(level)
    if list_level is None:
        return None
    list_level = _standardize(list_level)
    return list_level


def _calculate_parameters(
    counts: dict,
    positions: dict,
    distances: dict,
    difficulty_curve_interval: int,
    list_level: list,
    accessible_tile_count: int,
) -> dict:
    """Calculate and return the output parameters."""
    output_parameters = {
        labeler.output_parameter_names[0]: labeler._density(
            counts["treasure_count"] + counts["enemy_count"], counts["total_tile_count"]
        ),
        labeler.output_parameter_names[1]: labeler._empty_ratio(
            counts["empty_tile_count"], counts["total_tile_count"]
        ),
        labeler.output_parameter_names[2]: labeler._exploration_requirement(
            list_level,
            distances["entry"],
            positions["object_positions"],
            accessible_tile_count,
        ),
        labeler.output_parameter_names[3]: labeler._difficulty_curve(
            distances["entry"], positions["enemy_positions"], difficulty_curve_interval
        ),
        labeler.output_parameter_names[4]: counts["treasure_count"],
        labeler.output_parameter_names[5]: counts["enemy_count"],
        labeler.output_parameter_names[6]: counts["map_size"],
    }

    # Playability
    output_parameters[param_names[0]] = _is_playable(list_level)

    # Count other ASCII
    output_parameters[param_names[1]] = _count_other_ASCII(list_level)

    # Empty validation
    output_parameters[param_names[2]] = _validate_empty(list_level)

    # Calculate nonlinearity only if the level is playable
    if output_parameters["playability"]:
        output_parameters[labeler.output_parameter_names[7]] = (
            labeler._exploration_requirement(
                list_level,
                distances["entry"],
                [positions["entry"], positions["exit"]],
                accessible_tile_count,
            )
        )
    else:
        output_parameters[labeler.output_parameter_names[7]] = None

    output_parameters[labeler.output_parameter_names[8]] = labeler._count_rooms(
        list_level
    )

    return output_parameters


# ===============================
# 2. Data Processing and Calculation
# ===============================
# ===============================
# 2-1. Object and Position Information
# ===============================
def _find_outer_tiles(
    list_level: list, x_boundary: int, y_boundary: int, icon_obstacles: set
) -> set:
    outer_set = set()

    # (0, 0) ~ (n-1, 0), (0, m-1) ~ (n-1, m-1)
    for x in range(x_boundary):
        for y in (0, y_boundary - 1):
            if (x, y) not in outer_set and labeler._is_accessible(
                list_level[x][y], icon_obstacles
            ):
                labeler._visit(
                    list_level, x, y, x_boundary, y_boundary, icon_obstacles, outer_set
                )

    # (0, 1) ~ (0, m-2), (n-1, 1) ~ (n-1, m-2)
    for x in (0, x_boundary - 1):
        for y in range(1, y_boundary - 1):
            if (x, y) not in outer_set and labeler._is_accessible(
                list_level[x][y], icon_obstacles
            ):
                labeler._visit(
                    list_level, x, y, x_boundary, y_boundary, icon_obstacles, outer_set
                )
    return outer_set


# ==========
# 2-2. Evaluation
# ==========
def _is_playable(list_level: list) -> bool:
    """
    Determine whether the level is playable by checking if the entry and exit points are accessible.

    Args:
        list_level (list): The level represented as a list of lists.

    Returns:
        bool: True if the level is playable, False otherwise.
    """
    entry_pos = labeler._find_objects_position(list_level, labeler.icons["entry"])
    if not entry_pos:
        return False
    entry_pos = entry_pos[0]

    exit_pos = labeler._find_objects_position(list_level, labeler.icons["boss"])
    if not exit_pos:
        exit_pos = labeler._find_objects_position(list_level, labeler.icons["exit"])
        if not exit_pos:
            return False
        exit_pos = exit_pos[0]
    else:
        exit_pos = exit_pos[0]

    entry_distance_dict = labeler._shortest_distances(list_level, entry_pos)

    # Check if exit is accessible from entry
    return exit_pos in entry_distance_dict


def _count_other_ASCII(list_level: list) -> int:
    """
    Count the number of unique ASCII characters in the level that are not defined as icons in the labeler.

    Args:
        list_level (list): The level represented as a list of lists.

    Returns:
        int: The number of unique non-icon ASCII characters present in the level.
    """
    other_ASCII_count = 0
    appeared = set()

    for row in list_level:
        for tile in row:
            if tile not in appeared and not _is_in_icons(tile):
                appeared.add(tile)
                other_ASCII_count += 1

    return other_ASCII_count


def _validate_empty(list_level: list) -> float:
    """
    Calculate the correct percentage of tiles.
    Outside, only ASCII " " is considered as a right tile,
    Inside, only ASCII " " is considered as a wrong tile.

    Args:
        list_level (list): The level represented as a list of lists.

    Returns:
        float: The percentage of correctly placed empty tiles.
    """
    # Initialization
    icon_inner_empty = labeler.icons["empty"]
    icon_outer_empty = labeler.icons["outside"]
    icon_obstacles = set(labeler.icons["wall"])

    x_boundary = len(list_level)
    y_boundary = len(list_level[0])

    # Make wall and total sets
    obstacles_set = {
        (x, y)
        for x in range(x_boundary)
        for y in range(y_boundary)
        if list_level[x][y] in icon_obstacles
    }
    total_set = {(x, y) for x in range(x_boundary) for y in range(y_boundary)}

    # Find inner and outer set
    outer_set = _find_outer_tiles(list_level, x_boundary, y_boundary, icon_obstacles)
    inner_set = total_set - obstacles_set - outer_set

    # Count right and wrong tiles
    inner_wrong_count = sum(
        1 for x, y in inner_set if list_level[x][y] == icon_inner_empty
    )
    inner_right_count = len(inner_set) - inner_wrong_count
    outer_right_count = sum(
        1 for x, y in outer_set if list_level[x][y] == icon_outer_empty
    )
    outer_wrong_count = len(outer_set) - outer_right_count

    # Return the percentage of correct tiles
    total_right = inner_right_count + outer_right_count
    total_tiles = total_right + outer_wrong_count + inner_wrong_count

    return total_right / total_tiles if total_tiles > 0 else 0.0


# =======
# Utility
# =======
def _is_in_icons(tile: str) -> bool:
    return any(tile == icon for icon in labeler.icons.values())


def _standardize(list_level: list) -> list:
    """
    Standardize the level by ensuring consistent formatting of spaces and empty tiles.
    """

    # Find the maximum length of rows.
    row_max_len = max(len(row) for row in list_level)

    icon_outside = labeler.icons["outside"]

    return [row + [icon_outside] * (row_max_len - len(row)) for row in list_level]


def _set_none_parameters():
    """Calculate and return the output parameters."""
    output_parameters = {
        labeler.output_parameter_names[0]: None,
        labeler.output_parameter_names[1]: None,
        labeler.output_parameter_names[2]: None,
        labeler.output_parameter_names[3]: None,
        labeler.output_parameter_names[4]: None,
        labeler.output_parameter_names[5]: None,
        labeler.output_parameter_names[6]: None,
        labeler.output_parameter_names[7]: None,
        labeler.output_parameter_names[8]: None,
    }

    # Playability
    output_parameters[param_names[0]] = None
    output_parameters[param_names[1]] = None
    output_parameters[param_names[2]] = None

    return output_parameters


# ========
# For TEST
# ========
def _make_list_level(x: int, y: int) -> list:
    return str([["#" for _ in range(y)] for _ in range(x)])


if __name__ == "__main__":
    for x in range(10):
        for y in range(10):
            test_map = _make_list_level(x, y)

            for tmp_interval in range(1, 10):
                validate(test_map, tmp_interval)
