
import json



def load_examples(input_path: str) -> str:
    with open(input_path, 'r') as file:
        examples_data = json.load(file)

    example_prompts = ""

    for i, example in enumerate(examples_data['map_list']):
        params = example['params']
        map_size = params.get('map_size', 'N/A')
        room_num = params.get('room_num', 'N/A')  # 'room_num'이 실제 데이터에 없다면 다른 적절한 키를 사용해야 합니다.
        enemy_num = params.get('enemy_num', 'N/A')
        treasure_num = params.get('reward_num', 'N/A')  # 'treasure_num' 대신 'reward_num' 사용

        selected_params = {
            'MAP_SIZE': map_size,
            'ROOM_COUNT': room_num,
            'ENEMY_COUNT': enemy_num,
            'TREASURE_COUNT': treasure_num
        }
        params_str = "\n".join([f"{key.upper()}: {value}" for key, value in params.items()])

        example_prompt = f"""

Example {i + 1}:

Parameters:
{params_str}

Generated Map:
{example['map']}
"""
        example_prompts += example_prompt
    return example_prompts