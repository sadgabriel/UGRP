from season1.utility import load_config
from season1.utility import load_list_from_files
from src.preprocessed_data_generator import generate_preprocessed_data
from repeator import repeat_process

config = load_config()
goal_params_path = "../data/test/"

data_count = 1
prompt_style = "AutoCOT1"
param_names = ["map_size"]

# step 1
param_list = load_list_from_files(goal_params_path, "param_list")
for goal_params in param_list:
    generate_preprocessed_data(data_count, prompt_style, goal_params, param_names)

# step 2
repeat_process(prompt_style)
