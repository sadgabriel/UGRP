import json
import random
import os

from config import *


def _load_examples_from_file(input_path: str, example_count: int) -> str:

    with open(input_path, "r") as file:
        examples_data = json.load(file)

    selected_examples = random.sample(examples_data["map_list"], example_count)

    example_prompts = ""

    for i, example in enumerate(selected_examples):
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

Example {i + 1}:

Parameters:
{params_str}

Generated Map:
{example['map']}
"""
        example_prompts += example_prompt
    return example_prompts


def _split_prompts(content: str) -> tuple[str]:
    start_prompt_key = "Start Prompt:"
    end_prompt_key = "End Prompt:"

    start_prompt_start = content.find(start_prompt_key) + len(start_prompt_key)
    end_prompt_start = content.find(end_prompt_key)

    start_prompt = content[start_prompt_start:end_prompt_start].strip()
    end_prompt = content[end_prompt_start + len(end_prompt_key) :].strip()

    return start_prompt, end_prompt


def _load_examples_from_folder(folder_path: str, example_count: int) -> str:
    files = [
        f
        for f in os.listdir(folder_path)
        if os.path.isfile(os.path.join(folder_path, f)) and f != "dummy.txt"
    ]

    if not files:
        return "The folder is empty or only contains dummy.txt."

    # 랜덤으로 파일 하나 선택
    selected_file = random.choice(files)
    selected_file_path = os.path.join(folder_path, selected_file)

    return _load_examples_from_file(selected_file_path, example_count)


def _format_parameters(params: dict) -> str:
    params_str = "\n".join([f"{key.upper()}: {value}" for key, value in params.items()])
    return f"""
Parameters:
{params_str}

"""


def prompt_generator(example_count: int, params: dict, prompt_style: str) -> str:

    base_prompt_file_path = BASE_PROMPT_PATH + f"{prompt_style}.txt"
    prompt_file_path = PROMPT_PATH + f"{prompt_style}.txt"

    with open(base_prompt_file_path, "r") as file:
        content = file.read()

    start_prompt, end_prompt = _split_prompts(content)
    example = _load_examples_from_folder(LABELLED_PATH, example_count)

    complete_prompt = start_prompt + example + _format_parameters(params) + end_prompt

    return complete_prompt
