import re

def preprocess_text(data):
    """
    Preprocess the input text data to normalize it and prepare for ASCII art extraction.

    Args:
    - data (str): The input text data.

    Returns:
    - list: A list of preprocessed lines.
    """
    # Normalize whitespace
    data = re.sub(r'\s+', ' ', data)

    # Split into lines and strip leading/trailing whitespace
    lines = [line.strip() for line in data.splitlines() if line.strip()]

    return lines

def extract_ascii_art(data):
    """
    Extract the ASCII art section from the preprocessed text data.

    Args:
    - data (str): The input text data.

    Returns:
    - str: The extracted ASCII art.
    """
    # Preprocess the text data
    lines = preprocess_text(data)

    # Define patterns to detect the start and end of the ASCII art
    start_pattern = re.compile(r'^#+.*#+$')  # Lines with # symbols at the start and end
    end_pattern = re.compile(r'^#+.*#+$')

    # Variables to hold the start and end indices of the ASCII art
    start_idx = None
    end_idx = None
    map_started = False

    # Detect the start and end of the ASCII art
    for idx, line in enumerate(lines):
        if start_pattern.match(line):
            if not map_started:
                start_idx = idx
                map_started = True
                print(f"Start detected at line {idx}: {line}")
            else:
                end_idx = idx
                print(f"End detected at line {idx}: {line}")

    # If start or end index is not found, return an empty string
    if start_idx is None or end_idx is None:
        print("Start or end index not found.")
        return ""

    # Extract the ASCII art lines
    ascii_art_lines = lines[start_idx:end_idx + 1]

    # Join the lines to form the final ASCII art
    ascii_art = "\n".join(ascii_art_lines)

    return ascii_art

# Example input data
input_data = """
You are a game map design expert. Your task is to generate an ASCII map for a game based on the following parameters: map size, number of rooms, number of monsters, number of treasures, and linearity. Here is how you will develop the map:

Define the Map Layout:
Use the map size to determine the overall dimensions of the map.
Represent the map using # for walls, . for open space, and + for doors connecting rooms.
Place the Rooms:
Divide the map into the specified number of rooms.
Ensure rooms are separated by walls and connected by doors (+).
Distribute Monsters and Treasures:
Randomly place the specified number of monsters (M) and treasures (T) within the rooms.
Determine Linearity:
Adjust the layout based on the linearity parameter, where a higher linearity value means a more straightforward path between rooms.
Generate the ASCII Map:
Combine all the elements to create a coherent and visually clear ASCII map.
Parameters:

MAP_SIZE: (18, 31)
ROOM_COUNT: Let's assume 4 rooms for simplicity.
MONSTER_COUNT: 13
TREASURE_COUNT: 2
LINEARITY: Let's assume a linearity of 5 (moderate linearity).
Example 1:

Parameters:
ENEMY_GROUP: 4
ENEMY_GROUP_SIZE: 3~4
ENEMY_IDEAL: 13
REWARD: 2
BOSS: 1
DENSITY: 0.026881720430107527
EMPTY_RATIO: 0.4874551971326165
EXPLORATION_REQUIREMENT: 515
DIFFICULTY_CURVE: 0.0
NONLINEARITY: 1.0317524933848972
REWARD_NUM: 2
ENEMY_NUM: 13
MAP_SIZE: (18, 31)

Generated Map:
##################### #######  
#.........#.........# #.....#  
#.EE......#.........# #...P.#  
#E........#.........# #.....#  
#######/###.........# ####/##  
    #.....#.........#   #...#  
#####.....#....E....#   #...#  
#...#.....#.........#   #...#  
#...#.....#......E..#   #...#  
#.B./E.E..#...E.E...#   #...#  
#...#E....##/############...#  
#...#...../.........#.../R..#  
###########.........#.E.#####  
  #.......#.........#E..#      
  #......./........./..E#      
  #.......#.....R...#...#      
  #.......###############      
  #.......#                    
  #########                    

Take a deep breath and let's work this out in a step-by-step way to be sure we have the right answer.
"""

# Extract and print the ASCII art from the example input
ascii_art = extract_ascii_art(input_data)
print("Extracted ASCII Art:")
print(ascii_art)