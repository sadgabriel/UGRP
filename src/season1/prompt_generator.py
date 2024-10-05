import textwrap
from .utility import load_config

config = load_config()

BASE_PROMPT_PATH = config["paths"]["base_prompt"]


def _split_prompts(content: str) -> tuple[str, str]:
    start_prompt_key = "System Role:"
    end_prompt_key = "End Prompt:"

    start_prompt_start = content.find(start_prompt_key) + len(start_prompt_key)
    end_prompt_start = content.find(end_prompt_key)

    start_prompt = content[start_prompt_start:end_prompt_start].strip()
    end_prompt = content[end_prompt_start + len(end_prompt_key) :].strip()

    return start_prompt, end_prompt


def _format_parameters(params: dict) -> str:
    params_str = "\n".join([f"{key.upper()}: {value}" for key, value in params.items()])
    return f"""
Generate a map with the following parameters.
                
**Parameters:**
```
{params_str}
```
"""


def generate_prompt(example_prompt: str, params: dict, prompt_style: str) -> tuple:

    base_prompt_file_path = BASE_PROMPT_PATH + f"{prompt_style}.txt"

    with open(base_prompt_file_path, "r") as file:
        content = file.read()

    start_prompt, end_prompt = _split_prompts(content)

    system = start_prompt + example_prompt

    prompt = _format_parameters(params) + end_prompt

    return system, prompt
