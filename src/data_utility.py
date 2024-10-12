import random
import os

import season1.utility as util

config = util.load_config()


def get_demos_from_map_dataset(dataset, param_names) -> list[dict]:
    target_list = []
    map_size_range = range(3) if "map_size" in param_names else range(1, 2)
    room_count_range = range(3) if "room_count" in param_names else range(1, 2)
    enemy_count_range = range(3) if "enemy_count" in param_names else range(1, 2)
    treasure_count_range = range(3) if "treasure_count" in param_names else range(1, 2)
    exploration_range = range(3) if "exploration" in param_names else range(1, 2)
    winding_path_range = range(3) if "winding_path" in param_names else range(1, 2)

    if len(param_names) == 1 or len(param_names) == 6:
        last_range = range(3)
    elif len(param_names) == 2:
        last_range = range(0, 1)
    else:
        raise ValueError("param_names must contain 1, 2 or 6 entities.")

    for map_size_idx in map_size_range:
        for room_count_idx in room_count_range:
            for enemy_count_idx in enemy_count_range:
                for treasure_count_idx in treasure_count_range:
                    for exploration_idx in exploration_range:
                        for winding_path_idx in winding_path_range:
                            for last_idx in last_range:
                                target_list.append(
                                    dataset[map_size_idx][room_count_idx][
                                        enemy_count_idx
                                    ][treasure_count_idx][exploration_idx][
                                        winding_path_idx
                                    ][
                                        last_idx
                                    ]
                                )

    if len(target_list) >= 10:
        target_list = random.sample(target_list, 9)

    return target_list
