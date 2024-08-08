import json
import random
import os

from config import (
    EXAMPLE_COUNT,
    PARAMS,
    BASE_PROMPT_FILE_PATH,
    EXAMPLE_PATH,
    PROMPT_FILE_PATH,
)


"""
used prompt to creat autoCOT:
Given the ENEMY_GROUP, ENEMY_GROUP_SIZE, ENEMY_IDEAL, REWARD,BOSS, DENSITY, EMPTY_RATIO, EXPLORATION_REQUIREMENT, DIFFICULTY_CURVE, NONLINEARITY, REWARD_NUM, ENEMY_NUM, MAP_SIZE, and several example of Parameters-Generated map pairs, please create a prompt to generate a map in ASCII. prompt structure should be {start_prompt, example_prompt, end_prompt}.
"""


def _load_examples_from_file(input_path: str, example_count: int) -> str:

    with open(input_path, "r") as file:
        examples_data = json.load(file)

    selected_examples = random.sample(examples_data["map_list"], example_count)

    example_prompts = ""

    for i, example in enumerate(selected_examples):
        params = example["params"]
        map_size = params.get("map_size", "N/A")
        room_count = params.get("room_num", "N/A")
        enemy_count = params.get("enemy_num", "N/A")
        treasure_count = params.get(
            "reward_num", "N/A"
        )  # 'treasure_num' 대신 'reward_num' 사용

        selected_params = {
            "MAP_SIZE": map_size,
            "ROOM_COUNT": room_count,
            "ENEMY_COUNT": enemy_count,
            "TREASURE_COUNT": treasure_count,
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


def prompt_generator(
    example_count: int,
    params: dict,
    base_prompt_file_path: str,
    example_path: str,
    prompt_file_path: str,
) -> None:
    with open(base_prompt_file_path, "r") as file:
        content = file.read()

    start_prompt, end_prompt = _split_prompts(content)
    example = _load_examples_from_folder(example_path, example_count)

    complete_prompt = start_prompt + example + _format_parameters(params) + end_prompt

    with open(prompt_file_path, "w", encoding="utf-8") as file:
        file.write(complete_prompt)

    print(f"Complete prompt saved to {prompt_file_path}")


if __name__ == "__main__":

    prompt_generator(
        EXAMPLE_COUNT, PARAMS, BASE_PROMPT_FILE_PATH, EXAMPLE_PATH, PROMPT_FILE_PATH
    )
