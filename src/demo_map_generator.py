import os
import subprocess

import numpy as np

import season1.placer as placer
import season1.utility as util
import season1.validater as validator

config = util.load_config()


def create_map_dataset() -> list:
    data = [
        [[[[] for _ in range(3)] for _ in range(3)] for _ in range(3)] for _ in range(3)
    ]

    for map_idx, map_size in enumerate((16, 20, 26)):
        for room_idx, room_count in enumerate((5, 8, 13)):
            for enemy_idx, enemy_count in enumerate((10, 16, 26)):
                for treasure_idx, treasure_count in enumerate((1, 2, 4)):
                    while True:
                        print(map_idx, room_idx, enemy_idx, treasure_idx)

                        maps = [
                            placer.Map(map_dict)
                            for map_dict in generate_node_maps(
                                map_size, room_count, 500
                            )
                        ]

                        for map in maps:
                            map.params["enemy_group_min"] = enemy_count
                            map.params["enemy_group_max"] = enemy_count

                            map.params["group_size_min"] = 1
                            map.params["group_size_max"] = 1

                            map.params["enemy_ideal_min"] = enemy_count
                            map.params["enemy_ideal_max"] = enemy_count

                            map.params["boss"] = 1
                            map.params["treasure"] = treasure_count

                            placer.modify_map(map, 0, 10, 0)

                            params_dict = validator.get_label(map.get_ascii_map())
                            map.params = params_dict

                        explorations = [map.params["exploration"] for map in maps]
                        winding_paths = [map.params["winding_path"] for map in maps]

                        exploration_20line = np.percentile(explorations, 20)
                        exploration_40line = np.percentile(explorations, 40)
                        exploration_60line = np.percentile(explorations, 60)
                        exploration_80line = np.percentile(explorations, 80)
                        winding_path_20line = np.percentile(winding_paths, 20)
                        winding_path_40line = np.percentile(winding_paths, 40)
                        winding_path_60line = np.percentile(winding_paths, 60)
                        winding_path_80line = np.percentile(winding_paths, 80)

                        sublist = [[[] for _ in range(3)] for _ in range(3)]

                        for map in maps:
                            exploration = map.params["exploration"]
                            winding_path = map.params["winding_path"]

                            if exploration < exploration_20line:
                                i = 0
                            elif exploration_40line < exploration < exploration_60line:
                                i = 1
                            elif exploration_80line < exploration:
                                i = 2
                            else:
                                i = None

                            if winding_path < winding_path_20line:
                                j = 0
                            elif (
                                winding_path_40line < winding_path < winding_path_60line
                            ):
                                j = 1
                            elif winding_path_80line < winding_path:
                                j = 2
                            else:
                                j = None

                            if (
                                i is not None
                                and j is not None
                                and len(sublist[i][j]) < 3
                            ):
                                sublist[i][j].append(
                                    {"params": map.params, "map": map.get_ascii_map()}
                                )

                        OK = True
                        for i in range(3):
                            for j in range(3):
                                if len(sublist[i][j]) != 3:
                                    OK = False

                        if OK:
                            data[map_idx][room_idx][enemy_idx][treasure_idx] = sublist
                            break

    return data


def generate_node_maps(
    map_size: int, room_count_ideal: int, map_count: int
) -> list[dict]:
    node_map_generator_path = os.path.join(
        os.path.dirname(__file__), "node_map_generator.js"
    )

    subprocess.run(
        [
            "node",
            node_map_generator_path,
            str(map_size),
            str(room_count_ideal),
            str(map_count),
        ]
    )

    raw_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), config["paths"]["raw"])
    )
    return util.load_json_files(raw_path)


if __name__ == "__main__":
    dir_path = os.path.normpath(
        os.path.join(os.path.dirname(__file__), config["paths"]["labelled"])
    )
    file_path = os.path.join(dir_path, "DemoMapDataset.json")

    util.create_directory(dir_path)
    util.empty_directory(dir_path)
    util.write_json_file(file_path, create_map_dataset())
