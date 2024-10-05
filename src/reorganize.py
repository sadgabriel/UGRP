import glob
import json
import os
from typing import Any

from season1.utility import load_config

    # 이 스크립트는 다음 두 가지 주요 기능을 수행합니다:
    # 1. 메인 디렉토리와 서브디렉토리 내의 batch*.json 파일들을 재정리합니다.
    #    - 메인 디렉토리에 batch*.json 파일이 있을 경우, 이 파일들만 취합하여 새로 정리합니다.
    #    - 메인 디렉토리에 batch*.json 파일이 없을 경우, 서브디렉토리의 파일들을 취합하여 정리합니다.
    # 2. 데이터가 재정리된 후, 메인 디렉토리에서 처리된 기존의 batch*.json 파일들을 삭제하고, 100개의 항목으로 구성된 새로운 batch 파일들을 메인 디렉토리에 생성합니다.
    #    - 서브디렉토리의 파일들은 삭제되지 않습니다.
    #    - 최종적으로, 어느 경로에서 파일들이 처리되었는지를 출력합니다.
    

def load_data_from_directory(directory_path: str) -> tuple[list[Any], list[str]]:
    """Load all data from all batch files in the specified directory into a single list."""
    all_data = []
    file_paths = glob.glob(f"{directory_path}batch*.json")

    for file_path in file_paths:
        with open(file_path, "r") as infile:
            dataset = json.load(infile)
            all_data.extend(dataset.get("map_list", []))

    return all_data, file_paths


def save_data_in_batches(all_data: list, directory_path: str) -> None:
    """Save all data into batch files with exactly 100 items each."""
    batch_number = 0
    total_data_count = len(all_data)

    for i in range(0, total_data_count, 100):
        batch_data = all_data[i : i + 100]
        batch_file = f"{directory_path}batch{batch_number}.json"
        dataset = {"map_list": batch_data}

        with open(batch_file, "w") as outfile:
            json.dump(dataset, outfile)

        print(f"Saved {batch_file} with {len(batch_data)} items")
        batch_number += 1


def reorganize_batches(directory_path: str) -> None:
    """Main function to reorganize existing batch files from preprocessed and its subdirectories into proper sizes."""

    # Load all data from the main preprocessed directory
    main_dir_data, main_dir_files = load_data_from_directory(directory_path)

    if main_dir_files:
        # If there are files in the main directory, process only those files
        all_data = main_dir_data
        file_paths_to_delete = main_dir_files
        processed_from = "Main Directory"
    else:
        # If no files in the main directory, load from subdirectories
        all_data = []
        subdirs = [d for d in glob.glob(f"{directory_path}*/") if os.path.isdir(d)]
        file_paths_to_delete = []

        for subdir in subdirs:
            subdir_data, subdir_files = load_data_from_directory(subdir)
            all_data.extend(subdir_data)
            file_paths_to_delete.extend([])  # 서브디렉토리의 파일은 삭제하지 않음

        processed_from = "Sub Directories"

    # Remove the files that were loaded (only from main directory)
    if processed_from == "Main Directory":
        for file_path in file_paths_to_delete:
            os.remove(file_path)

    # Save the data into new batch files with 100 items each in the main preprocessed directory
    save_data_in_batches(all_data, directory_path)

    # Output detailed information about the processing
    print(f"Data processing completed.")
    print(f"Processed from: {processed_from}")


# Run the reorganization
config = load_config()
path = config["paths"]["preprocessed"]
reorganize_batches(path)
