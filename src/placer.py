import os
import random
from collections import deque


class Map:
    """A class to represent ASCII map.

    Attributes:
        list_map (list[list[str]]): The 2-dimensional list of ASCII character.
        params (dict[str, str]): Parameters which describe map's features.
    """

    def __init__(self, path: str = None) -> None:
        self.filename = None
        self.list_map = list()
        self.params = dict()

        if path:
            self.load(path)

    def get_ascii_map(self) -> str:
        ascii_map = ""
        for row in self.list_map:
            ascii_map += "".join(row) + "\n"

        return ascii_map

    def load(self, path: str):
        self.filename = os.path.basename(path)

        with open(path, "r") as file:
            params_str = file.readline().strip().replace(" ", "")

            map = list()
            while True:
                line = file.readline()
                if not line:
                    break
                map.append(line[:-1])

        self.params = {
            param.split("=")[0]: param.split("=")[1] for param in params_str.split(",")
        }

        for i in range(len(map)):
            self.list_map.append(list())
            for j in range(len(map[i])):
                self.list_map[i].append(map[i][j])

    def save(self, path: str):
        with open(path, "w") as file:
            params_str = ",".join(
                [f"{key}={value}" for key, value in self.params.items()]
            )
            file.write(params_str + "\n")

            for row in self.list_map:
                file.write("".join(row) + "\n")


def load_maps(path: str = "input") -> list[Map]:
    """Load all maps from directory.

    Args:
        path (str, optional): The path of directory which has map files. Defaults to "input".

    Returns:
        list[Map]: The list of created Map objects.
    """
    filename_list = [
        filename
        for filename in os.listdir(path)
        if filename.endswith(".txt") and os.path.isfile(os.path.join(path, filename))
    ]

    return [Map(os.path.join(path, filename)) for filename in filename_list]


def save_maps(maps: list[Map], path: str = "output") -> None:
    """Save maps to directory.

    Args:
        maps (list[Map]): Maps to be saved.
        path (str, optional): The path of directory in which the maps will be saved. Defaults to "output".
    """
    for map in maps:
        map.save(os.path.join(path, map.filename))


def modify_map(map: Map, group_min_dist: int, flag_try_count: int, enemy_sparsity: int):
    """Modify map with its parameters.

    Args:
        map (Map): A Map to modify.
        group_min_dist (int): The minimum distance between enemy groups.
        flag_try_count (int): The number of trial to set enemy group flag.
        enemy_sparsity (int): Sparsity of enemies in a enemy group.
    """
    group_size_list = _calc_group_detail(map)

    _set_player_and_boss(map)
    _set_group_flag(map, len(group_size_list), group_min_dist, flag_try_count)
    _set_enemy(map, group_size_list, enemy_sparsity)
    _set_reward(map)


def _set_player_and_boss(map: Map):
    for line in map.list_map:
        for i in range(len(line)):
            if line[i] == "<":
                line[i] = "P"
            if line[i] == ">" and int(map.params["boss"]):
                line[i] = "B"


def _calc_group_detail(map: Map) -> tuple[int]:
    if "~" in map.params["enemy_group"]:
        group_min, group_max = (
            int(num) for num in map.params["enemy_group"].split("~")
        )
    else:
        group_min = group_max = int(map.params["enemy_group"])

    if "~" in map.params["enemy_group_size"]:
        group_size_min, group_size_max = (
            int(num) for num in map.params["enemy_group_size"].split("~")
        )
    else:
        group_size_min = group_size_max = int(map.params["enemy_group_size"])

    if "~" in map.params["enemy_ideal"]:
        ideal_min, ideal_max = (
            int(num) for num in map.params["enemy_ideal"].split("~")
        )
    else:
        ideal_min = ideal_max = int(map.params["enemy_ideal"])

    try_max = 10000
    try_count = 0
    while True:
        group_list = list()
        group = random.randrange(group_min, group_max + 1)

        for i in range(group):
            group_list.append(random.randrange(group_size_min, group_size_max + 1))

        if (
            group_min * group_size_min > ideal_max
            or group_max * group_size_max < ideal_min
            or try_count >= try_max
        ):
            return group_list

        if ideal_min <= sum(group_list) <= ideal_max:
            return group_list

        try_count += 1


def _set_group_flag(map: Map, group_count: int, min_dist: int, try_count: int):
    while min_dist >= 0:
        if _try_set_group_flag(map, group_count, min_dist, try_count):
            return
        else:
            min_dist -= 1

    raise ValueError("not enough empty space for enemy")


def _try_set_group_flag(
    map: Map, group_count: int, min_dist: int, try_count: int
) -> bool:
    empty_set = set()
    for i in range(len(map.list_map)):
        for j in range(len(map.list_map[i])):
            if map.list_map[i][j] == ".":
                empty_set.add((i, j))

    for _ in range(try_count):
        ok = True
        flag_list = list()

        for _ in range(group_count):
            if empty_set:
                flag = random.choice(list(empty_set))
                flag_list.append(flag)
            else:
                ok = False
                break

            enemy_region = dict()
            queue = deque()
            enemy_region[flag] = 0
            queue.append(flag)

            while queue:
                now = queue.popleft()

                for direction in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                    next = (now[0] + direction[0], now[1] + direction[1])

                    if (
                        0 <= next[0] < len(map.list_map)
                        and 0 <= next[1] < len(map.list_map[next[0]])
                        and map.list_map[next[0]][next[1]] == "."
                        and next not in enemy_region
                        and enemy_region[now] + 1 <= min_dist
                    ):

                        enemy_region[next] = enemy_region[now] + 1
                        queue.append(next)

            empty_set -= enemy_region.keys()

        if ok:
            for flag in flag_list:
                map.list_map[flag[0]][flag[1]] = "F"
            return True

    return False


def _set_enemy(map: Map, group_size_list: list[int], sparsity: int):
    group_num = 0
    for i in range(len(map.list_map)):
        for j in range(len(map.list_map[i])):
            if map.list_map[i][j] == "F":
                map.list_map[i][j] = "."
                empty_list = list()
                queue = deque()
                queue.append((i, j))

                while (
                    queue and len(empty_list) <= group_size_list[group_num] * sparsity
                ):
                    now = queue.popleft()
                    for direction in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                        next = (now[0] + direction[0], now[1] + direction[1])
                        if (
                            0 <= next[0] < len(map.list_map)
                            and 0 <= next[1] < len(map.list_map[i])
                            and map.list_map[next[0]][next[1]] == "."
                            and next not in empty_list
                        ):
                            empty_list.append(next)
                            queue.append(next)

                enemy_list = random.sample(empty_list, group_size_list[group_num])
                for enemy in enemy_list:
                    map.list_map[enemy[0]][enemy[1]] = "E"

                group_num += 1


def _set_reward(map: Map):
    empty_list = list()
    for i in range(len(map.list_map)):
        for j in range(len(map.list_map[i])):
            if map.list_map[i][j] == ".":
                empty_list.append((i, j))

    reward_list = random.sample(empty_list, int(map.params["reward"]))

    for reward in reward_list:
        map.list_map[reward[0]][reward[1]] = "R"


if __name__ == "__main__":
    maps = load_maps()
    for map in maps:
        modify_map(map, 10, 50, 3)
    save_maps(maps)