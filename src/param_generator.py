import random
import numpy as np

config = {
    "small": {
        "map_min": 9,
        "map_max": 16,
        "room_count": {"mean": 3.245, "std_dev": 1.1510755839648412},
        "enemy_count": {"mean": 3.7425, "std_dev": 1.9751439820934573},
        "treasure_count": {"mean": 0.645, "std_dev": 0.4785133226985431},
    },
    "large": {
        "map_min": 16,
        "map_max": 30,
        "room_count": {"mean": 8.86, "std_dev": 2.6730881018028563},
        "enemy_count": {"mean": 14.255, "std_dev": 6.732382564887411},
        "treasure_count": {"mean": 2.255, "std_dev": 0.744966442197231},
    },
    "enemy_density": 0.05,
    "treasure_density": 0.01,
}


def generate_param() -> dict:

    size = "small" if random.random() < 0.5 else "large"

    map_config = config[size]

    map_width = np.random.randint(map_config["map_min"], map_config["map_max"] + 1)
    map_height = np.random.randint(map_config["map_min"], map_config["map_max"] + 1)

    counts = {"room_count": 0, "enemy_count": 0, "treasure_count": 0}

    counts = {}
    for key, min_value in zip(
        ["room_count", "enemy_count", "treasure_count"], [1, 0, 0]
    ):
        counts[key] = max(
            min_value,
            int(np.random.normal(map_config[key]["mean"], map_config[key]["std_dev"])),
        )

    return {"map_size": [map_width, map_height], **counts}
