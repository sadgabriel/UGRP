import random as rd
from season1.labeler import save_file

target_range = {
    "enemy_count": (10, 26),
    "treasure_count": (1, 4),
    "room_count": (5, 13),
    "map_size": (16, 26),
    "exploration": (0.4, 0.7),
    "winding_path": (0.3, 0.9),
}


def output_target_param(
    map_list: list, path: str, file_count: int = 10, param_count: int = 100
) -> None:
    for i in range(file_count):
        save_file({"param_list": _generate_target_params_for(param_count)}, path)


def _generate_target_params_for(repeatition: int = 100) -> list:
    result_list = []
    for i in range(repeatition):
        result_list.append(_generate_target_param())
    return result_list


def _generate_target_param() -> dict:
    return {
        "enemy_count": rd.randint(
            target_range["enemy_count"][0], target_range["enemy_count"][1]
        ),
        "treasure_count": rd.randint(
            target_range["treasure_count"][0], target_range["treasure_count"][1]
        ),
        "room_count": rd.randint(
            target_range["room_count"][0], target_range["room_count"][1]
        ),
        "map_size": rd.randint(
            target_range["map_size"][0], target_range["map_size"][1]
        ),
        "exploration": rd.uniform(
            target_range["exploration"][0], target_range["exploration"][1]
        ),
        "winding_path": rd.uniform(
            target_range["winding_path"][0], target_range["winding_path"][1]
        ),
    }


if __name__ == "__main__":
    pass
