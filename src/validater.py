import labeler

param_names = ("playability", "other_ASCII_count")


def validate(
    level: str,
    difficulty_curve_interval: int = labeler.DEFAULT_DIFFICULTY_CURVE_INTERVAL,
) -> dict[str, float]:
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


def _validate_empty():
    pass
