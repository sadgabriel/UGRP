from prompt_generator import prompt_generator
from param_generator import param_generator
from preprocessor import preprocessor
import json


def preprocessed_data_generator(
    data_count: int,
    example_count: int,
    preprocessed_path: str,
    base_prompt_file_path: str,
    example_path: str,
    prompt_file_path: str,
) -> None:

    file_count = 1
    dataset = {"map_list": []}

    for i in range(data_count):
        param = param_generator()
        prompt_generator(
            example_count, param, base_prompt_file_path, example_path, prompt_file_path
        )

        map = preprocessor()
        dataset["map_list"].append({"params": param, "map": map})

        # 데이터가 100개일 때마다 새로운 파일로 저장
        if i % 100 == 0:
            with open(f"{preprocessed_path}_{file_count}.json", "w") as outfile:
                json.dump(dataset, outfile)
            dataset = {"map_list": []}
            file_count += 1

    # 남아 있는 데이터가 있을 경우 마지막 파일로 저장
    if dataset["map_list"]:
        with open(f"{preprocessed_path}_{file_count}.json", "w") as outfile:
            json.dump(dataset, outfile)
