import os

_menu_options = None
_previous_menu = None

global WINDOW_WIDTH
WINDOW_WIDTH = 80

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu_header(title):
    clear()
    padding = (WINDOW_WIDTH - len(title)) // 2
    print_equals()
    print(" " * padding + title)
    print_equals()
    print()

def print_dashes():
    print("-" * WINDOW_WIDTH)

def print_equals():
    print("=" * WINDOW_WIDTH)

def set_window_width(width):
    global WINDOW_WIDTH
    if isinstance(width, int) and width > 0:
        WINDOW_WIDTH = width
    else:
        error("Window width must be a positive integer.")

def load_menus():
    from user_interface_menus._main_menu import main_menu
    
    from user_interface_menus._system_check_menu import system_check_menu

    from user_interface_menus._system_task_menu import system_task_menu
    from user_interface_menus._system_task_menu import ADD_TASK, ADD_SYSTEM_TASK, ADD_R_SCRIPT, REMOVE_TASK, EXECUTE_TASK, EXECUTE_SYSTEM_TASK, EXECUTE_R_SCRIPT
    
    from user_interface_menus._participant_management_menus import participant_management_menu
    
    from user_interface_menus._log_menu import log_menu
    
    from user_interface_menus._shutdown_menu import shutdown_menu

    from user_interface_menus.help_menu._help_menu import help_menu
    from user_interface_menus.help_menu._help_menu import GENERAL_INFORMATION

    from user_interface_menus._settings_menu import settings_menu
    from user_interface_menus._settings_menu import DISPLAY, WINDOW_WIDTH_SETTINGS

    from user_interface_menus.help_menu._developer_documentation import developer_documentation
    from user_interface_menus.help_menu._research_assistant_documentation import research_assistant_documentation
    clear()
    print("Now loading menus...")

    # Store menu options in module-level variable
    global _menu_options
    _menu_options = {
        'main': {'description': 'Main Menu', 'menu_caller': main_menu},
        'check': {'description': 'System Status and Diagnostics', 'menu_caller': system_check_menu},

        'help': {'description': 'Help', 'menu_caller': help_menu},
        'help general': {'description': 'General Information', 'menu_caller': GENERAL_INFORMATION},
        'help ra': {'description': 'Research Assistant Documentation', 'menu_caller': research_assistant_documentation},
        'help dev': {'description': 'Developer Documentation', 'menu_caller': developer_documentation},

        'tasks': {'description': 'Manage System Tasks and R Scripts', 'menu_caller': lambda self: system_task_menu(self)},
        'tasks add': {'description': 'Add New Task', 'menu_caller': lambda self: ADD_TASK(self)},
        'tasks add system' : {'description': 'Add New Task', 'menu_caller': lambda self: ADD_SYSTEM_TASK(self)},
        'tasks add rscript': {'description': 'Add New R Script Task', 'menu_caller': lambda self: ADD_R_SCRIPT(self)},
        'tasks remove': {'description': 'Remove Task', 'menu_caller': lambda self: REMOVE_TASK(self)},
        'tasks execute': {'description': 'Execute Task Now', 'menu_caller': lambda self: EXECUTE_TASK(self)},
        'tasks execute system': {'description': 'Execute System Task Now', 'menu_caller': lambda self: EXECUTE_SYSTEM_TASK(self)},
        'tasks execute rscript': {'description': 'Execute R Script Task Now', 'menu_caller': lambda self: EXECUTE_R_SCRIPT(self)},
        
        'participants': {'description': 'Manage Participants', 'menu_caller': participant_management_menu},
        
        'logs': {'description': 'View Logs', 'menu_caller': log_menu},

        'settings': {'description': 'Settings', 'menu_caller': settings_menu},  
        'settings display': {'description': 'Manage Display settings', 'menu_caller': lambda self: DISPLAY(self)},
        'settings display width': {'description': 'Adjust PRISM window width', 'menu_caller': lambda self: WINDOW_WIDTH_SETTINGS(self)},
        
        'shutdown': {'description': 'Shutdown PRISM', 'menu_caller': shutdown_menu},
        
        'command': {'description': 'Global Command Menu', 'menu_caller': print_global_command_menu}
    }

def get_menu_options():
    global _menu_options
    if _menu_options is None:
        load_menus()
    return _menu_options

def check_global_menu_options(query = None):
    if query is None:
        return None
    
    menu_options = get_menu_options()
    result = menu_options.get(query)
    if result is None:
        return None
    return result['description'], result['menu_caller']

def goto_menu(menu_caller, self):
    try:
        if callable(menu_caller):
            return menu_caller(self)
        elif isinstance(menu_caller, str):
            result = check_global_menu_options(menu_caller)
            if result:
                description, caller = result
                return caller(self)
            else:
                error(f"Menu '{menu_caller}' not found.")
                return False
        else:
            error("Invalid menu caller.")
            return False
    except Exception as e:
        error(f"An error occurred while navigating to the menu: {e}")
        return False
    
def print_global_command_menu(self):
    print_menu_header("PRISM Global Command Menu")
    menu_options = get_menu_options()
    if print_menu_options(self, menu_options, submenu = True):
        return

def print_menu_options(self, menu_options, submenu = False, index_and_text = False):
    margin_width = WINDOW_WIDTH / 2
    if index_and_text:
        for key, item in menu_options.items():
            if key.isdigit():
                print(f"{key:<{int(margin_width)}} {item['description']:<{int(margin_width)}}")
        print_dashes()
        print()
        for key, item in menu_options.items():
            if not key.isdigit():
                print(f"{key:<{int(margin_width)}} {item['description']:<{int(margin_width)}}")
    else:
        for key, item in menu_options.items():
            print(f"{key:<{int(margin_width)}} {item['description']:<{int(margin_width)}}")
    if submenu:
        print("\nENTER: Back to Previous Menu")
    choice = input("\nprism> ").strip()
    
    selected = menu_options.get(choice)
    if selected:
        try:
            handler = selected['menu_caller']
            if handler(self): # if the submenu indicates to exit
                return 1
        except Exception as e:  
            error(f"Local menu option error: {e}")
            return 0
    elif choice.lower() in ['exit']:
        print("Exiting PRISM Interface.")
        exit(0)

    elif check_global_menu_options(choice):
        try:
            description, menu_caller = check_global_menu_options(choice)
            if goto_menu(menu_caller, self):
                return 1
        except Exception as e:
            error(f"Global menu option error: {e}")
            return 0
    elif choice == '' and submenu:
        return 1
    elif choice == '' and not submenu:
        pass
    else:
        error("Invalid choice.")
    return 0

def error(message = "An unexpected error occurred."):
        print(f"Error: {message}")
        input("Press Enter to continue...")

def success(message = "Operation completed successfully."):
    print(f"Success: {message}")
    input("Press Enter to continue...")
    
def exit_menu():
    input("Press Enter to continue...")