# menus for adding tasks

import time

from user_interface_menus.utils._menu_display import *
from user_interface_menus._menu_helper import *

def add_new_r_script_menu(self):
    if not self.commands_queue:
        print_menu_header("tasks add rscript")
    r_scripts = self.api("GET", "system/get_r_script_tasks")
    if not r_scripts:
        error("No R scripts available.", self)
        return
    print("Available R Scripts:")
    for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
        print(f"{i}: {name}")
    script_idx = get_input(self, prompt = "Select R script index: ")
    r_script_dict = r_scripts['r_script_tasks']
    script_names = list(r_script_dict.keys())
    if not script_idx.isdigit() or not (1 <= int(script_idx) <= len(script_names)):
        error("Invalid index.", self)
        return
    selected_script_name = script_names[int(script_idx) - 1]
    r_script_path = f"{r_script_dict[selected_script_name]}.R"
    task_time = get_input(self, prompt = "Task time (HH:MM:SS) ", default_value = "00:00:00")
    if not task_time:
        print("No time provided, using default 00:00:00.")
        task_time = "00:00:00"
    else:
        try:
            time.strptime(task_time, '%H:%M:%S')
        except ValueError:
            print("Invalid time format, using default 00:00:00.")
            task_time = "00:00:00"
    if self.api("POST", f"system/add_r_script_task/{r_script_path}/{task_time}"):
        success(f"R script task {r_script_path} scheduled at {task_time}.", self)
    else:
        error(f"Failed to schedule R script task {selected_script_name}.", self)

def add_new_task_menu(self):
    if not self.commands_queue:
        print_menu_header("tasks add system")
    task_types = self.get_task_types()
    if not task_types:
        error("No task types available.")
        return
    print("Available Tasks:")
    for i, (k,v) in enumerate(task_types.items(),1):
        print(f"{yellow(i)}: {v} ({k})")
    idx = get_input(self, prompt = "Task index to add: ")
    if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
        error("Invalid index.", self)
        return
    
    task_type = list(task_types.keys())[int(idx)-1]
    if task_type == 'RUN_R_SCRIPT':
        add_new_r_script_menu(self)
    else:
        task_time = get_input(self, prompt = "Task time (HH:MM:SS) ", default_value = "00:00:00")
        if not task_time:
            print("No time provided, using default 00:00:00.")
            task_time = "00:00:00"
        else:
            try:
                time.strptime(task_time, '%H:%M:%S')
            except ValueError:
                print("Invalid time format, using default 00:00:00.")
                task_time = "00:00:00"
        if self.api("POST", f"system/add_system_task/{task_type}/{task_time}"):
            success("Task added.", self)
        else:
            error("Failed to add task.", self)

def add_task_menu(self):
    menu_options = {
        'system': {'description': 'Add New System Task', 'menu_caller': add_new_task_menu},
        'rscript': {'description': 'Add New R Script Task', 'menu_caller': add_new_r_script_menu},
    }
    while True:
        if not self.commands_queue:
            print_menu_header("tasks add")
        if print_menu_options(self, menu_options, submenu = True):
            break