from collections import deque
import json
import os
from tqdm import tqdm

from season1.validater import _is_playable


# 데이터 파일들이 있는 폴더 경로 지정 (예: "./data_files")
folder_path = "../data/result"


def read_json_from_file(file_path):
    """
    주어진 파일 경로에서 JSON 데이터를 읽어 반환합니다.
    확장자가 없는 파일도 JSON 형식으로 파싱합니다.

    :param file_path: 읽을 파일의 경로
    :return: 파싱된 JSON 데이터 또는 None (파싱 실패 시)
    """
    try:
        with open(file_path, "r") as file:
            return json.load(file)
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON from {file_path}: {e}")
        return None
    except FileNotFoundError:
        print(f"File not found: {file_path}")
        return None


def read_all_json_files_without_extension(folder_path):
    """
    지정된 폴더 경로에서 확장자가 없는 모든 파일을 읽어 JSON 데이터를 반환합니다.

    :param folder_path: 폴더 경로
    :return: 파싱된 JSON 데이터의 리스트
    """
    maps = []
    for filename in os.listdir(folder_path):
        # 파일에 확장자가 없는지 확인
        if "." not in filename:
            file_path = os.path.join(folder_path, filename)
            data = read_json_from_file(file_path)
            if data is not None:
                maps.append(data)
    return maps


def find_start_and_end_positions(map_data):
    """
    맵에서 'P'와 'B'의 위치를 찾습니다.

    :param map_data: 맵 문자열
    :return: (p_position, b_position) 각각 (row, col) 형태의 튜플 또는 None
    """
    p_position = None
    b_position = None
    lines = map_data.split("\n")

    for r, line in enumerate(lines):
        for c, char in enumerate(line):
            if char == "P":
                p_position = (r, c)
            elif char == "B":
                b_position = (r, c)

    return p_position, b_position


def is_path_exists(map_data, wall_symbols):
    """
    'P'에서 'B'까지의 경로가 존재하는지 검사합니다.
    '#'은 벽으로 간주하며, 지나갈 수 없습니다.

    :param map_data: 맵 문자열
    :return: 경로가 존재하면 True, 아니면 False
    """
    p_position, b_position = find_start_and_end_positions(map_data)

    # P와 B가 없으면 경로가 성립되지 않음
    if not p_position or not b_position:
        return False

    # BFS를 위한 초기 설정
    queue = deque([p_position])
    visited = set([p_position])
    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]  # 상, 하, 좌, 우

    # 맵을 줄 단위로 나눔
    lines = map_data.split("\n")
    row_count = len(lines)

    # BFS 탐색 시작
    while queue:
        current_position = queue.popleft()
        r, c = current_position

        # 'B'에 도달하면 경로가 존재
        if current_position == b_position:
            return True

        # 네 방향으로 이동
        for dr, dc in directions:
            nr, nc = r + dr, c + dc

            # 맵 범위 내에 있어야 함
            if 0 <= nr < row_count and 0 <= nc < len(lines[nr]):
                new_position = (nr, nc)

                # 벽('#')이 아니며, 방문한 적이 없어야 함
                if lines[nr][nc] not in wall_symbols and new_position not in visited:
                    visited.add(new_position)
                    queue.append(new_position)

    # BFS 탐색 종료 후 'B'에 도달하지 못하면 경로가 없음
    return False


def analyze_maps(data_list):
    """
    JSON 데이터 리스트에서 각 맵에 'P'와 'B'의 존재 여부를 검사하고,
    조건에 맞는 개수를 세어 비율을 계산하여 출력합니다.

    :param data_list: JSON 데이터의 리스트
    """
    total_maps = 0
    one_or_both_missing = 0
    both_present = 0
    both_present_with_path_only_hash = 0
    both_present_with_path_is_playable = 0

    has_path1 = False
    has_path2 = False

    # tqdm을 사용하여 진행률 표시
    total_entries = sum(len(data) for data in data_list)
    with tqdm(total=total_entries, desc="Analyzing maps") as progress_bar:
        for data in data_list:
            for entry in data:
                # 메인 맵 검사
                main_map = entry["map"]
                p_exists = "P" in main_map
                b_exists = "B" in main_map

                if p_exists and b_exists:
                    both_present += 1
                    has_path1 = is_path_exists(main_map, wall_symbols=["#"])
                    has_path2 = _is_playable(main_map)

                    if has_path1 != has_path2:
                        print(f"is_path_exists: {has_path1}")
                        print(f"_is_playable: {has_path2}")
                        print(main_map)
                    # 'P'와 'B'가 모두 존재할 때 경로가 있는지 검사
                    if has_path1:
                        both_present_with_path_only_hash += 1
                    if has_path2:
                        both_present_with_path_is_playable += 1

                else:
                    one_or_both_missing += 1

                total_maps += 1
                progress_bar.update(1)

    # 비율 계산
    if total_maps > 0:
        both_present_ratio = both_present / total_maps * 100
        path_only_hash_ratio = both_present_with_path_only_hash / total_maps * 100
        path_is_playable_ratio = both_present_with_path_is_playable / total_maps * 100
    else:
        both_present_ratio = 0
        path_only_hash_ratio = 0
        path_is_playable_ratio = 0

    # 결과 출력
    print(f"Total maps: {total_maps}")
    print(f"Maps with both 'P' and 'B': {both_present} ({both_present_ratio:.2f}%)")
    print(
        f"Maps with paths ('#' as walls): {both_present_with_path_only_hash} ({path_only_hash_ratio:.2f}%)"
    )
    print(
        f"Maps with paths (_is_playable): {both_present_with_path_is_playable} ({path_is_playable_ratio:.2f}%)"
    )


# JSON 파일들을 읽고 분석 수행
# data_list = read_all_json_files_without_extension(folder_path)
# analyze_maps(data_list)

maps = []
maps.append(read_json_from_file(folder_path + "/enemy_count_0"))
analyze_maps(maps)
