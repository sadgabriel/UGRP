import random
import json
import os

from .utility import load_config


config = load_config()
LABELLED_PATH = config["paths"]["labelled"]


def load_random_examples_from_folder(
    example_count: int, folder_path: str = LABELLED_PATH
) -> list:
    files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f != "dummy.txt"
    ]

    if not files:
        return "The folder is empty or only contains dummy.txt."

    # random file select
    selected_file = random.choice(files)
    selected_file_path = os.path.join(folder_path, selected_file)

    return _load_random_examples_from_file(example_count, selected_file_path)


def _load_random_examples_from_file(example_count: int, input_path: str) -> list:

    with open(input_path, "r") as file:
        examples_data = json.load(file)

    selected_examples = random.sample(examples_data["map_list"], example_count)

    return selected_examples


def generate_example_prompt(examples: list, prompt_style: str) -> str:
    if prompt_style == "AutoCOT1":
        example_prompts = ""

        for i, example in enumerate(examples):
            params = example["params"]

            selected_params = {
                "MAP_SIZE": params.get("map_size", "N/A"),
                "ROOM_COUNT": params.get("room_count", "N/A"),
                "ENEMY_COUNT": params.get("enemy_count", "N/A"),
                "TREASURE_COUNT": params.get("treasure_count", "N/A"),
            }
            params_str = "\n".join(
                [f"{key.upper()}: {value}" for key, value in selected_params.items()]
            )

            example_prompt = f"""
### Example {i + 1}:
**Parameters:**
```
{params_str}
```
**Generated Map:**
```
{example['map']}
```
"""
            example_prompts += example_prompt
    else:
        example_prompt = ""
    return example_prompts


def generate_example_map_list(examples: list) -> list:
    example_map_list = []
    for example in examples:
        example_map_list.append(example["map"])

    return example_map_list
