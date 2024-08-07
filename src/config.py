PROMPT_STYLE = 'AutoCOT1'
example_count = 10
params = {
    'MAP_SIZE': [20, 20],
    'ROOM_COUNT': 7,
    'ENEMY_COUNT': 2,
    'TREASURE_COUNT': 1
}

base_prompt_path = f'../data/4. prompt/base_prompt/{PROMPT_STYLE}.txt'
example_folder_path = f'../data/3. labelled'
prompt_path = f'../data/4. prompt/{PROMPT_STYLE}.txt'
unstructured_data_path = f'../data/5. preprocessed/unstructured_data/{PROMPT_STYLE}.txt'