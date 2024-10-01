RAW_PATH = "../../data/1. raw/"
PLACED_PATH = "../../data/2. placed/"
LABELLED_PATH = "../../data/3. labelled/"
PROMPT_PATH = "../../data/4. prompt/"
PREPROCESSED_PATH = "../../data/5. preprocessed/"
COMPARED_PATH = "../../data/6. compared/"

BASE_PROMPT_PATH = f"../base_prompt/"

"""
yaml로 불러오는 방법
pip install pyyaml




import yaml

# YAML 파일을 읽어옵니다
with open("config.yaml", "r") as file:
    config = yaml.safe_load(file)

# 필요한 값을 가져옵니다
PREPROCESSED_PATH = config['paths']['preprocessed']
COMPARED_PATH = config['paths']['compared']

"""
