from labeler import estimate, load_folder, save_folder  # 한 줄로 묶어 임포트 정리

from config import *

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

    # Load preprocessed data that lacks estimated parameters.
    preprocessed_data = load_folder(
        path=preprocessed_path, file_count=file_count
    )  # 변수명 수정 불필요

    # Estimate parameters and update preprocessed data.
    compared_data = []  # 리스트 초기화 위치를 변경하여 논리적 순서에 맞게 수정

    for file_data in preprocessed_data:
        map_list = file_data["map_list"]
        data_count = len(map_list)

        temp_map_list = {"map_list": []}  # 파일 단위로 데이터를 저장할 리스트

        for map_data in map_list:
            before_params = map_data["params"]
            after_params = estimate(map_data["map"])

            # Store before and after parameters in the comparison data structure
            temp_map_list["map_list"].append(
                {"before_params": before_params, "after_params": after_params}
            )

        compared_data.append(temp_map_list)  # 파일 단위 데이터를 비교 리스트에 추가

    # Save the comparison result data.
    save_folder(data=compared_data, path=compared_path, file_count=file_count)

    return


if __name__ == "__main__":
    compare(
        preprocessed_path=PREPROCESSED_PATH,
        compared_path=COMPARED_PATH,
        file_count=1,
    )
