from season1.utility import *
from season1.llm_utils import generate_data_block


def get_existing_parameters_and_maps() -> tuple:
    """Load the goal (parameters) and demonstrate data(map, param) from the stored file."""

    # return params, demonstrate_data


def repeat_process(data_count: int, prompt_style: str) -> None:
    """Repeat the process of generating and saving data using existing goal and map data."""
    config = load_config()
    repeated_path = config["paths"]["repeated"]

    create_directory(repeated_path)
    setup_logging(f"{repeated_path}.log")

    current_file, batch_number, dataset = find_or_create_dataset(path=repeated_path)

    # Use the general function with a new parameter generation function
    while data_count > 0:
        parameters, examples = None, None  # 루프 안에서 사용할 변수

        for iteration in range(2):
            if iteration == 0:
                parameters, examples = get_existing_parameters_and_maps()
            else:
                pass

            # 데이터 생성 및 처리
            dataset = generate_data_block(
                parameters, examples, prompt_style, dataset, current_file
            )

            if dataset is None:
                batch_number += 1
                current_file = f"{repeated_path}batch{batch_number}.json"
                dataset = {"map_list": []}

        data_count -= 1

    if dataset and dataset["map_list"]:
        save_dataset_to_file(dataset, current_file)
        print(f"Successfully saved {current_file} with remaining data")
