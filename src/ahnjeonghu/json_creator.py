import json
from config import base_prompt_path, json_base_prompt_path

def split_prompts(content):
    start_prompt_key = 'Start Prompt:'
    end_prompt_key = 'End Prompt:'

    start_prompt_start = content.find(start_prompt_key) + len(start_prompt_key)
    end_prompt_start = content.find(end_prompt_key)

    start_prompt = content[start_prompt_start:end_prompt_start].strip()
    end_prompt = content[end_prompt_start + len(end_prompt_key):].strip()

    return start_prompt, end_prompt

def prompt_data_to_json(base_prompt_path, output_json_path):

    with open(base_prompt_path, 'r') as file:
        content = file.read()

    start_prompt, end_prompt = split_prompts(content)

    prompt_data = {
        "start_prompt": start_prompt,
        "end_prompt": end_prompt
    }

    with open(output_json_path, 'w') as json_file:
        json.dump(prompt_data, json_file, indent=4)


prompt_data_to_json(base_prompt_path, json_base_prompt_path)