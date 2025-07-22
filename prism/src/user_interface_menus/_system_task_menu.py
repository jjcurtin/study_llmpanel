import time
from user_interface_menus._menu_helper import *

# ------------------------------------------------------------

def print_task_schedule(self):
    tasks = self.api("GET", "system/get_task_schedule")
    if tasks and "tasks" in tasks:
        self.scheduled_tasks = tasks["tasks"]
        if self.scheduled_tasks:
            print("Scheduled Tasks")
            print_dashes()
            for i, t in enumerate(self.scheduled_tasks, 1):
                print(f"{i}: {t['task_type']} @ {t['task_time']}{f" {t['r_script_path']}" if t['r_script_path'] else ""} - Run Today: {t.get('run_today', False)}")
            print_dashes()
        else:
            print("No tasks scheduled.")
    else:
        from user_interface_menus._menu_helper import COLOR_ON
        if COLOR_ON:
            print("\033[31mNo tasks scheduled.\033[0m")
        else:
            print("No tasks scheduled.")

# ------------------------------------------------------------

def add_new_r_script_menu(self):
    print_menu_header("Add New R Script Task")
    r_scripts = self.api("GET", "system/get_r_script_tasks")
    if not r_scripts:
        error("No R scripts available.")
        return
    print("Available R Scripts:")
    for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
        print(f"{i}: {name}")
    script_idx = input("Select R script index: ").strip()
    r_script_dict = r_scripts['r_script_tasks']
    script_names = list(r_script_dict.keys())
    if not script_idx.isdigit() or not (1 <= int(script_idx) <= len(script_names)):
        error("Invalid index.")
        return
    selected_script_name = script_names[int(script_idx) - 1]
    r_script_path = f"{r_script_dict[selected_script_name]}.R"
    task_time = input("Task time (HH:MM:SS, default 00:00:00): ").strip()
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
        success(f"R script task {r_script_path} scheduled at {task_time}.")
    else:
        error(f"Failed to schedule R script task {selected_script_name}.")

def add_new_task_menu(self):
    print_menu_header("Add New System Task")
    task_types = self.get_task_types()
    if not task_types:
        error("No task types available.")
        return
    print("Available Tasks:")

    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        for i, (k,v) in enumerate(task_types.items(),1):
            print(f"{f"\033[33m{i}\033[0m"}: {v} ({k})")
    else:
        for i, (k,v) in enumerate(task_types.items(),1):
            print(f"{i}: {v} ({k})")
    idx = input("Task index to add: ").strip()
    if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
        error("Invalid index.")
        return
    
    task_type = list(task_types.keys())[int(idx)-1]
    if task_type == 'RUN_R_SCRIPT':
        add_new_r_script_menu(self)
    else:
        task_time = input("Task time (HH:MM:SS, default 00:00:00): ").strip()
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
            success("Task added.")
        else:
            error("Failed to add task.")

def add_task_menu(self):
    menu_options = {
        'system': {'description': 'Add New System Task', 'menu_caller': add_new_task_menu},
        'rscript': {'description': 'Add New R Script Task', 'menu_caller': add_new_r_script_menu},
    }
    while True:
        print_menu_header("Add New Task")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

def remove_task_menu(self):
    print_menu_header("Remove System Task")
    print_task_schedule(self)
    try:
        idx = int(input("Task index to remove: ")) - 1
        if 0 <= idx < len(self.scheduled_tasks):
            t = self.scheduled_tasks[idx]
            if self.api("DELETE", f"system/remove_system_task/{t['task_type']}/{t['task_time']}"):
                success("Task removed.")
            else:
                error("Failed to remove task.")
        else:
            error("Invalid index.")
    except Exception:
        error("Invalid input.")

# ------------------------------------------------------------
    
def execute_r_script_menu(self):
    print_menu_header("Execute R Script Task")
    r_scripts = self.api("GET", "system/get_r_script_tasks")
    if not r_scripts:
        error("No R scripts available.")
        return
    print("Available R Scripts:")
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
            print(f"{f"\033[33m{i}\033[0m"}: {name}")
    else:
        for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
            print(f"{i}: {name}")
    script_idx = input("Select R script index: ").strip()
    r_script_dict = r_scripts['r_script_tasks']
    script_names = list(r_script_dict.keys())

    if not script_idx.isdigit() or not (1 <= int(script_idx) <= len(script_names)):
        error("Invalid index.")
        return
    selected_script_name = script_names[int(script_idx) - 1]
    r_script_path = f"{r_script_dict[selected_script_name]}.R"
    print(f"Executing R script: {selected_script_name} at {r_script_path}")
    if self.api("POST", f"system/execute_r_script_task/{r_script_path}"):
        success(f"R script task {selected_script_name} executed.")
    else:
        error(f"Failed to execute R script task {selected_script_name}.")

def execute_task_menu(self):
    print_menu_header("Execute System Task")
    task_types = self.get_task_types()
    if not task_types:
        error("No task types available.")
        return
    print("Available Tasks:")
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        for i, (k,v) in enumerate(task_types.items(),1):
            print(f"{f"\033[33m{i}\033[0m"}: {v} ({k})")
    else:
        for i, (k,v) in enumerate(task_types.items(),1):
            print(f"{i}: {v} ({k})")
    idx = input("Task index to execute: ").strip()
    if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
        error("Invalid index.")
        return
    task_type = list(task_types.keys())[int(idx)-1]

    if task_type == 'RUN_R_SCRIPT':
        execute_r_script_menu(self)
    elif self.api("POST", f"system/execute_task/{task_type}"):
        success(f"Task {task_type} executed.")
    else:
        data = self.api("GET", f"system/get_transcript/{15}")
        if data and "transcript" in data:
            for entry in data["transcript"]:
                print(f"{entry['timestamp']} - {entry['message']}")
        else:
            print("No transcript found or failed to retrieve.")
        error("Failed to execute task.")

def execute_menu(self):
    menu_options = {
        'system': {'description': 'Execute System Task', 'menu_caller': execute_task_menu},
        'rscript': {'description': 'Execute R Script Task', 'menu_caller': execute_r_script_menu},
    }
    while True:
        print_menu_header("Execute Task")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

def clear_task_schedule_menu(self):
    choice = input("Are you sure you want to clear the task schedule? (yes/no): ").strip().lower()
    if choice == 'yes' or choice == 'y':
        if self.api("DELETE", "system/clear_task_schedule"):
            success("Task schedule cleared.")
        else:
            error("Failed to clear task schedule.")
    else:
        print("Task schedule not cleared.")
        exit_menu()

# ------------------------------------------------------------
        
def system_task_menu(self):
    menu_options = {
        'add': {'description': 'Add New Task', 'menu_caller': add_task_menu},
        'remove': {'description': 'Remove Task', 'menu_caller': remove_task_menu},
        'execute': {'description': 'Execute Task Now', 'menu_caller': execute_menu},
        'clear': {'description': 'Clear Task Schedule', 'menu_caller': clear_task_schedule_menu},
    }

    while True:
        print_menu_header("PRISM System Task Menu")
        print_task_schedule(self)
        print()
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

global ADD_TASK
global ADD_SYSTEM_TASK
global ADD_R_SCRIPT
global REMOVE_TASK
global EXECUTE_TASK
global EXECUTE_SYSTEM_TASK
global EXECUTE_R_SCRIPT
global CLEAR_TASKS

ADD_TASK = add_task_menu
ADD_SYSTEM_TASK = add_new_task_menu
ADD_R_SCRIPT = add_new_r_script_menu
REMOVE_TASK = remove_task_menu
EXECUTE_TASK = execute_menu
EXECUTE_SYSTEM_TASK = execute_task_menu
EXECUTE_R_SCRIPT = execute_r_script_menu
CLEAR_TASKS = clear_task_schedule_menu