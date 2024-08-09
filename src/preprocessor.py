from unstructured_data_generator import unstructured_data_generator
from config import PROMPT_FILE_PATH


def has_two_or_more_hashes(line: str) -> bool:
    """
    Checks if the given line contains two or more '#' characters.

    Parameters:
    line (str): Line to check

    Returns:
    bool: True if the line contains two or more '#' characters, False otherwise
    """
    count = line.count("#")
    result = count >= 2
    return result


def _is_ascii_art_line(line: str) -> bool:
    """
    Checks if the given line consists only of ASCII art characters ('#', ' ', etc.).

    Parameters:
    line (str): Line to check

    Returns:
    bool: True if the line consists only of ASCII art characters, False otherwise
    """
    result = has_two_or_more_hashes(line)

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
    print("Cannot find the 'Final Map' keyword. Scanning the entire text from bottom.")

    start_index = None
    end_index = None

    # Check all lines from the end to start
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
