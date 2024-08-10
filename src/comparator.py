from labeler import estimate, load_folder, save_folder  # 한 줄로 묶어 임포트 정리

from config import PREPROCESSED_PATH, COMPARED_PATH

DEFAULT_FILE_COUNT = 100


def compare(
    preprocessed_path: str = PREPROCESSED_PATH,
    compared_path: str = COMPARED_PATH,
    file_count: int = DEFAULT_FILE_COUNT,
) -> None:
    """
    Load preprocessed data, estimate parameters, and compare them.

    Args:
        preprocessed_path: Path to the folder with preprocessed data files.
        compared_path: Path to the folder where comparison results will be saved.
        file_count: Number of data files to process.
    """

    # load preprocessed data. They don't have estimated parameters.
    preprocessed_data = load_folder(path=preprocessed_path, file_count=file_count)

    # Initialize compared data list
    compared_data = [{"map_list": []} for _ in range(file_count)]

    # Update parameters and prepare compared data
    for i, data in enumerate(preprocessed_data):
        for map_item in data["map_list"]:
            before_params = map_item["params"]
            after_params = estimate(map_item["map"])
            compared_data[i]["map_list"].append(
                {
                    "before_params": before_params,
                    "after_params": after_params,
                }
            )
    save_folder(data=compared_data, path=compared_path, file_count=file_count)

    return


if __name__ == "__main__":
    compare(
        preprocessed_path=PREPROCESSED_PATH,
        compared_path=COMPARED_PATH,
        file_count=1,
    )
