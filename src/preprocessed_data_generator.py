from prompt_generator import prompt_generator
from param_generator import param_generator
from preprocessor import preprocessor
from unstructured_data_generator import unstructured_data_generator
import json
import logging

# 로그 파일 설정
logging.basicConfig(filename="data_generation.log", level=logging.INFO)


def preprocessed_data_generator(
    data_count: int,
    example_count: int,
    preprocessed_path: str,
    base_prompt_file_path: str,
    example_path: str,
    prompt_file_path: str,
) -> None:
    file_count = 0
    dataset = {"map_list": []}

    for i in range(data_count):
        param = param_generator()
        prompt_generator(
            example_count, param, base_prompt_file_path, example_path, prompt_file_path
        )
        text = unstructured_data_generator(prompt_file_path)
        askii_map = preprocessor(text)

        dataset["map_list"].append({"params": param, "map": askii_map})

        # 로그 파일에 텍스트와 매핑 정보 기록
        logging.info(f"Data #{i}:")
        logging.info(f"Text:\n{text}")
        logging.info(f"ASCII Map:\n{askii_map}")

        # 데이터가 100개일 때마다 새로운 파일로 저장
        if i % 100 == 0:
            with open(f"{preprocessed_path}batch{file_count}.json", "w") as outfile:
                json.dump(dataset, outfile)
            dataset = {"map_list": []}
            print(f"Successfully saved {preprocessed_path}batch{file_count}.json")
            file_count += 1

    # 남아 있는 데이터가 있을 경우 마지막 파일로 저장
    if dataset["map_list"]:
        with open(f"{preprocessed_path}batch{file_count}.json", "w") as outfile:
            json.dump(dataset, outfile)
            print(
                f"Successfully saved {preprocessed_path}batch{file_count}.json... left data"
            )
