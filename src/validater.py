import labeler

param_names = ("playability", "other_ASCII_count", "empty_validation")


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

    # Count parameters
    counts = labeler._calculate_counts(list_level)

    # Find positions of objects and calculate distances
    positions = labeler._find_positions(list_level)
    distances = labeler._calculate_distances(
        list_level, positions["entry"], positions["exit"]
    )

    # Calculate and store output parameters
    output_parameters = _calculate_parameters(
        counts, positions, distances, difficulty_curve_interval, list_level
    )

    return output_parameters


def _prepare_level(level: str) -> list:
    list_level = labeler.str_level_to_list_level(level)
    list_level = _standardize(list_level)
    return list_level


def _calculate_parameters(
    counts: dict,
    positions: dict,
    distances: dict,
    difficulty_curve_interval: int,
    list_level: list,
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
            distances["entry"], positions["object_positions"]
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
        output_parameters[labeler.output_parameter_names[7]] = labeler._nonlinearity(
            distances["entry"],
            distances["exit"],
            positions["object_positions"],
            counts["total_object_count"],
            counts["total_passable_tile_count"],
        )
    else:
        output_parameters[labeler.output_parameter_names[7]] = None

    output_parameters[labeler.output_parameter_names[8]] = labeler._count_rooms(
        list_level
    )

    return output_parameters


def _standardize(list_level: list) -> list:
    """
    Standardize the level by ensuring consistent formatting of spaces and empty tiles.
    """

    # Find the maximum length of rows.
    row_max_len = max(len(row) for row in list_level)
    new_list_level = list()

    icon_outside = labeler.icons["outside"]

    # Fill shorter rows with spaces.
    for row in list_level:
        for i in range(row_max_len - len(row)):
            row.append(icon_outside)
        new_list_level.append(row)

    return new_list_level


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


def _is_in_icons(tile: str) -> bool:
    return any(tile == icon for icon in labeler.icons.values())


def _validate_empty(list_level: list) -> float:
    """After distinguishing between the outside and the inside,
    Calculate the correct percentage of tiles.
    Outside, only ASCII " " is considered as a right tile,
    Inside, only ASCII " " is considered as a wrong tile.

        Calculate the percentage of correctly placed empty tiles in the level, differentiating between inside and outside areas.

    Args:
        list_level (list): The level represented as a list of lists.

    Returns:
        float: The percentage of correctly placed empty tiles.
    """
    icon_inner_empty = labeler.icons["empty"]
    icon_outer_empty = labeler.icons["outside"]
    icon_obstacles = set(labeler.icons["wall"])

    x_boundary = len(list_level)
    y_boundary = len(list_level[0])

    def is_accessible_tile(x, y):
        return labeler._is_accessible(list_level[x][y], icon_obstacles)

    outer_set = set()
    # Find outer
    # (0, 0) ~ (n-1, 0), (0, m-1) ~ (n-1, m-1)
    for x in range(x_boundary):
        for y in (0, y_boundary - 1):
            if (x, y) not in outer_set and is_accessible_tile(x, y):
                _visit(
                    list_level, x, y, x_boundary, y_boundary, icon_obstacles, outer_set
                )

    # (0, 1) ~ (0, m-2), (n-1, 1) ~ (n-1, m-2)
    for x in (0, x_boundary - 1):
        for y in range(1, y_boundary - 1):
            if (x, y) not in outer_set and is_accessible_tile(x, y):
                _visit(
                    list_level, x, y, x_boundary, y_boundary, icon_obstacles, outer_set
                )

    # Count right and wrong outer tiles.
    outer_right_count = sum(
        1 for x, y in outer_set if list_level[x][y] == icon_outer_empty
    )
    outer_wrong_count = len(outer_set) - outer_right_count

    # Identify wall and total sets
    wall_set = {
        (x, y)
        for x in range(x_boundary)
        for y in range(y_boundary)
        if list_level[x][y] in icon_obstacles
    }
    total_set = {(x, y) for x in range(x_boundary) for y in range(y_boundary)}

    # Determine inner set and count right and wrong inner tiles
    inner_set = total_set - wall_set - outer_set
    inner_wrong_count = sum(1 for x, y in inner_set if list_level[x][y] == " ")
    inner_right_count = len(inner_set) - inner_wrong_count

    # Return the percentage of correct tiles
    total_right = inner_right_count + outer_right_count
    total_tiles = total_right + outer_wrong_count + inner_wrong_count

    return total_right / total_tiles if total_tiles > 0 else 0.0


def _visit(
    list_level: list,
    x: int,
    y: int,
    x_boundary: int,
    y_boundary: int,
    icon_obstacles: set,
    visited: set,
) -> None:
    directions = ((1, 0), (-1, 0), (0, 1), (0, -1))
    que = labeler.deque([(x, y)])
    while que:
        cur_x, cur_y = que.popleft()
        for dx, dy in directions:
            new_x = cur_x + dx
            new_y = cur_y + dy
            if (
                (new_x, new_y) not in visited
                and labeler._is_in_bounds(new_x, new_y, x_boundary, y_boundary)
                and labeler._is_accessible(list_level[new_x][new_y], icon_obstacles)
            ):
                visited.add((new_x, new_y))
                que.append((new_x, new_y))
