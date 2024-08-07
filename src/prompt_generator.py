import json
from src.config import prompt_path, json_base_prompt_path

if __name__ == "__main__":

    with open(json_base_prompt_path, 'r') as file:
        prompts_data = json.load(file)

    complete_prompt = prompts_data['start_prompt'] + load_examples_from_json('../../data/3. labelled/batch0.json') + prompts_data['end_prompt']

    with open(prompt_path, 'w', encoding='utf-8') as file:
        file.write(complete_prompt)

    print(f'Complete prompt saved to {prompt_path}')


"""
used prompt to creat autoCOT:
Given the ENEMY_GROUP, ENEMY_GROUP_SIZE, ENEMY_IDEAL, REWARD,BOSS, DENSITY, EMPTY_RATIO, EXPLORATION_REQUIREMENT, DIFFICULTY_CURVE, NONLINEARITY, REWARD_NUM, ENEMY_NUM, MAP_SIZE, and several example of Parameters-Generated map pairs, please create a prompt to generate a map in ASCII. prompt structure should be {start_prompt, example_prompt, end_prompt}.
"""