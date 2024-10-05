import re


def is_chapter_format(line: str) -> bool:
    """
    Checks if the given line follows the pattern of one or more '#' characters,
    followed by a space, and then a word.

    Parameters:
    line (str): The line of text to check.

    Returns:
    bool: True if the line matches the pattern, otherwise False.
    """
    pattern = r"^#+ [A-Za-z]+[^\#/\.]*$"
    result = bool(re.match(pattern, line))

    return result


def has_two_or_more_hashes(line: str) -> bool:
    """
    Checks if the given line contains two or more '#' characters.

    Parameters:
    line (str): The line of text to check.

    Returns:
    bool: True if the line contains two or more '#' characters, otherwise False.
    """
    count = line.count("#")
    result = count >= 2
    return result


def _is_ascii_art_line(line: str) -> bool:
    """
    Determines if the given line likely represents an ASCII art line,
    primarily by checking if it contains two or more '#' characters.

    Parameters:
    line (str): The line of text to check.

    Returns:
    bool: True if the line likely represents ASCII art, otherwise False.
    """
    result = has_two_or_more_hashes(line) and not is_chapter_format(line)

    print(f"is_ascii_art_line - Line to check: '{line}' Result: {result}")
    return result


def _extract_ascii_art_map(text: str) -> str:
    """
    Extracts the ASCII art map from the provided text by scanning from the bottom to the top.

    Parameters:
    text (str): The input text from which to extract the ASCII art map.

    Returns:
    str: The extracted ASCII art map, or an empty string if no map is found.
    """
    lines = text.split("\n")
    print("Scanning the entire text from bottom.")

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


def preprocess(text: str) -> str:
    """
    Preprocesses the text from the given prompt file path to extract the ASCII art map.

    Parameters:
    text (str): The prompt text.

    Returns:
    str: The extracted ASCII art map.
    """
    askii_map = _extract_ascii_art_map(text)
    print(askii_map)
    return askii_map
