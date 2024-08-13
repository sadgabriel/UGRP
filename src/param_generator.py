import random
import math

config = {
    "small": {
        "map_min": 9,
        "map_max": 16,
    },
    "large": {
        "map_min": 16,
        "map_max": 30,
    },
    "enemy_density": 0.05,
    "treasure_density": 0.01,
}


def generate_param() -> dict:

    size = "small" if random.random() < 0.5 else "large"

    map_size_min = config[size]["map_min"]
    map_size_max = config[size]["map_max"]

    map_width = random.randint(map_size_min, map_size_max)
    map_height = random.randint(map_size_min, map_size_max)

    room_count_max = math.floor((map_width - 1) / 2) * math.floor((map_height - 1) / 2)
    room_count = random.randint(1, room_count_max)

    empty_space_predict = round(
        map_width * map_height
        - (math.sqrt(room_count) - 1) * (map_width + map_height)
        + (math.sqrt(room_count) - 1) * (math.sqrt(room_count) - 1)
    )
    enemy_count = round(empty_space_predict * config["enemy_density"])
    treasure_count = round(empty_space_predict * config["treasure_density"])

    return {
        "map_size": [
            map_width,
            map_height,
        ],
        "room_count": room_count,
        "enemy_count": enemy_count,
        "treasure_count": treasure_count,
    }
