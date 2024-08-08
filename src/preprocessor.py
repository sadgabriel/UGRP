from unstructured_data_generator import unstructured_data_generator
from config import PROMPT_FILE_PATH


def _find_final_map_keyword(text: str, keywords=["Final"]) -> list:
    """
    Finds the indices of lines containing keywords that indicate the final result.

    Parameters:
    text (str): Input text
    keywords (list): List of keywords indicating the final result

    Returns:
    list: List of indices where keywords are found
    """
    lines = text.split("\n")
    keyword_indices = []
    for i, line in enumerate(lines):
        if any(keyword in line for keyword in keywords):
            keyword_indices.append(i)
    print(f"find_final_map_keyword - Keyword positions: {keyword_indices}")
    return keyword_indices


def _is_ascii_art_line(line: str) -> bool:
    """
    Checks if the given line consists only of ASCII art characters ('#', ' ', etc.).

    Parameters:
    line (str): Line to check

    Returns:
    bool: True if the line consists only of ASCII art characters, False otherwise
    """
    result = line.strip() != "" and all(
        char in ["#", " ", ".", "/", "P", "B", "E", "R"] for char in line
    )
    print(f"is_ascii_art_line - Line to check: '{line}' Result: {result}")
    return result


def _extract_ascii_art_map(text: str) -> str:
    """
    Extracts the ASCII art map from the text.

    Parameters:
    text (str): Input text

    Returns:
    str: Extracted ASCII art map
    """
    lines = text.split("\n")
    keyword_indices = _find_final_map_keyword(text)

    if not keyword_indices:
        print(
            "Cannot find the 'Final Map' keyword. Scanning the entire text from bottom."
        )

    start_index = None
    end_index = None

    # If keywords are found, start scanning from the keyword positions
    if keyword_indices:
        indices_to_check = keyword_indices
    else:
        # If no keywords are found, check all lines from the end to start
        indices_to_check = reversed(range(len(lines)))

    # Scan from bottom to top
    for index in indices_to_check:
        if start_index is not None:
            break  # Stop if we've already found a valid map

        current_map = []
        for i in range(index, -1, -1):
            if _is_ascii_art_line(lines[i]):
                current_map.insert(0, lines[i])
                if end_index is None:
                    end_index = i
                start_index = i
            else:
                if start_index is not None and end_index is not None:
                    break

        # If a valid map is found, set the start and end index
        if start_index is not None and end_index is not None:
            break

    print(f"extract_ascii_art_map - Start index: {start_index}, End index: {end_index}")

    if start_index is not None and end_index is not None:
        ascii_art_map = "\n".join(lines[start_index : end_index + 1])
        return ascii_art_map
    else:
        print("Cannot find ASCII art.")
        return ""


def preprocessor(prompt_file_path: str) -> str:
    text = unstructured_data_generator(prompt_file_path)
    map = _extract_ascii_art_map(text)
    print(map)
    return map


preprocessor(PROMPT_FILE_PATH)
