from param_generator import generate_param
from sampler import load_random_examples_from_folder
from llm_utils import generate_and_save_data
from utility import *


# 최초 출력 파트에서 사용될 파라미터 생성 함수
def get_new_parameters_and_examples(example_count: int) -> tuple:
    """Generate new parameters and example maps."""
    parameters = generate_param()
    examples = load_random_examples_from_folder(example_count)  # examples 로드
    return parameters, examples


def generate_preprocessed_data(
    data_count: int, example_count: int, prompt_style: str
) -> None:
    """Generate the initial output and save it."""
    config = load_config()
    preprocessed_path = os.path.abspath(config["paths"]["preprocessed"])

    create_directory(preprocessed_path)
    setup_logging(f"{preprocessed_path}.log")

    current_file, batch_number, dataset = find_or_create_dataset(path=preprocessed_path)

    # get_new_parameters_and_examples 래핑
    def wrapped_get_new_parameters():
        return get_new_parameters_and_examples(example_count)

    # Use the general function with a new parameter generation function
    dataset = generate_and_save_data(
        data_count,
        prompt_style,
        current_file,
        dataset,
        wrapped_get_new_parameters,
    )

    if dataset is None:
        batch_number += 1
        current_file = f"{preprocessed_path}batch{batch_number}.json"
        dataset = {"map_list": []}

    if dataset and dataset["map_list"]:
        save_dataset_to_file(dataset, current_file)
        print(f"Successfully saved {current_file} with remaining data")


# Example usage (should be removed in production code)
generate_preprocessed_data(data_count=1, example_count=10, prompt_style="AutoCOT1")
