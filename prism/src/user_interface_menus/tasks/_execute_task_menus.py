from user_interface_menus.utils._menu_display import *
from user_interface_menus._menu_helper import *

def execute_r_script_menu(self):
    clear_recommended_actions()
    if not self.commands_queue:
        print_menu_header("tasks execute rscript")
    r_scripts = self.api("GET", "system/get_r_script_tasks")
    if not r_scripts:
        error("No R scripts available.", self)
        return
    print("Available R Scripts:")
    for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
        print(f"{yellow(i)}: {name}")
    script_idx = get_input(self, prompt = "Select R script index: ")
    r_script_dict = r_scripts['r_script_tasks']
    script_names = list(r_script_dict.keys())

    if not script_idx.isdigit() or not (1 <= int(script_idx) <= len(script_names)):
        error("Invalid index.", self)
        return
    selected_script_name = script_names[int(script_idx) - 1]
    r_script_path = f"{r_script_dict[selected_script_name]}.R"
    print(f"Executing R script: {selected_script_name} at {r_script_path}")
    if self.api("POST", f"system/execute_r_script_task/{r_script_path}"):
        success(f"R script task {selected_script_name} executed.", self)
    else:
        error(f"Failed to execute R script task {selected_script_name}.", self)

def execute_task_menu(self):
    clear_recommended_actions()
    if not self.commands_queue:
        print_menu_header("tasks execute system")
    task_types = self.get_task_types()
    if not task_types:
        error("No task types available.", self)
        return
    print("Available Tasks:")
    for i, (k,v) in enumerate(task_types.items(),1):
        print(f"{yellow(i)}: {v} ({k})")
    idx = get_input(self, prompt = "Task index to execute: ")
    if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
        error("Invalid index.", self)
        return
    task_type = list(task_types.keys())[int(idx)-1]

    if task_type == 'RUN_R_SCRIPT':
        execute_r_script_menu(self)
    elif self.api("POST", f"system/execute_task/{task_type}"):
        success(f"Task {task_type} executed.", self)
    else:
        data = self.api("GET", f"system/get_transcript/{15}")
        if data and "transcript" in data:
            for entry in data["transcript"]:
                print(f"{entry['timestamp']} - {entry['message']}")
        else:
            print("No transcript found or failed to retrieve.")
        error("Failed to execute task.", self)

def execute_menu(self):
    menu_options = {
        'system': {'description': 'Execute System Task', 'menu_caller': execute_task_menu},
        'rscript': {'description': 'Execute R Script Task', 'menu_caller': execute_r_script_menu},
    }
    while True:
        clear_recommended_actions()
        if not self.commands_queue:
            print_menu_header("tasks execute")
        if print_menu_options(self, menu_options, submenu = True):
            break