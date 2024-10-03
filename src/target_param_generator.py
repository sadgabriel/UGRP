import random as rd

target_range = {
    "enemy_count": (10, 36),
    "treasure_count": (1, 4),
    "room_count": (4, 16),
    "map_size": (16, 30),
    "exploration": (0.4, 0.7),
    "winding_path": (0.3, 0.9),
}


def json_process(data):
    return


def generate_target_param() -> dict:
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
