# task management menu

from user_interface_menus._menu_helper import *
from user_interface_menus.tasks._add_task_menus import *
from user_interface_menus.tasks._execute_task_menus import *

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
            print(f"{red("No tasks scheduled.")}")
    else:
        print(f"{red("No tasks scheduled.")}")

# ------------------------------------------------------------

def remove_task_menu(self):
    print_menu_header("tasks remove")
    print_task_schedule(self)
    try:
        idx = int(get_input(self, prompt = "Task index to remove: ")) - 1
        if 0 <= idx < len(self.scheduled_tasks):
            t = self.scheduled_tasks[idx]
            if self.api("DELETE", f"system/remove_system_task/{t['task_type']}/{t['task_time']}"):
                success("Task removed.", self)
            else:
                error("Failed to remove task.", self)
        else:
            error("Invalid index.", self)
    except Exception:
        error("Invalid input.", self)

# ------------------------------------------------------------

def clear_task_schedule_menu(self):
    choice = get_input(self, prompt = "Are you sure you want to clear the task schedule? (yes/no): ").lower()
    if choice == 'yes' or choice == 'y':
        if self.api("DELETE", "system/clear_task_schedule"):
            success("Task schedule cleared.", self)
        else:
            error("Failed to clear task schedule.", self)
    else:
        success("Task schedule not cleared.", self)

# ------------------------------------------------------------
        
def system_task_menu(self):
    menu_options = {
        'add': {'description': 'Add New Task', 'menu_caller': add_task_menu},
        'remove': {'description': 'Remove Task', 'menu_caller': remove_task_menu},
        'execute': {'description': 'Execute Task Now', 'menu_caller': execute_menu},
        'clear': {'description': 'Clear Task Schedule', 'menu_caller': clear_task_schedule_menu},
    }

    while True:
        print_menu_header("tasks")
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