import os

_menu_options = None

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu_header(title):
    clear()
    padding = (60 - len(title)) // 2
    print("=" * 60)
    print(" " * padding + title)
    print("=" * 60)
    print()

def load_menus():
    from user_interface_menus._main_menu import main_menu
    from user_interface_menus._system_check_menu import system_check_menu
    from user_interface_menus._system_task_menu import system_task_menu
    from user_interface_menus._participant_management_menus import participant_management_menu
    from user_interface_menus._log_menu import log_menu
    from user_interface_menus._shutdown_menu import shutdown_menu
    from user_interface_menus.help_menu._help_menu import help_menu
    from user_interface_menus.help_menu._developer_documentation import developer_documentation
    from user_interface_menus.help_menu._research_assistant_documentation import research_assistant_documentation
    print("Modules loaded successfully. Now loading menus...")

    # Store menu options in module-level variable
    global _menu_options
    _menu_options = {
        'main': {'description': 'Main Menu', 'menu_caller': main_menu},
        'check': {'description': 'System Status and Diagnostics', 'menu_caller': system_check_menu},
        'tasks': {'description': 'Manage System Tasks and R Scripts', 'menu_caller': system_task_menu},
        'participants': {'description': 'Manage Participants', 'menu_caller': participant_management_menu},
        'logs': {'description': 'View Logs', 'menu_caller': log_menu},
        'shutdown': {'description': 'Shutdown PRISM', 'menu_caller': shutdown_menu},
        'help': {'description': 'Help', 'menu_caller': help_menu},
        'dev': {'description': 'Developer Documentation', 'menu_caller': developer_documentation},
        'ra': {'description': 'Research Assistant Documentation', 'menu_caller': research_assistant_documentation},
        'commands': {'description': 'Global Command Menu', 'menu_caller': print_global_command_menu}
    }
    print("Menus loaded successfully.")

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
    
def print_global_command_menu(self):
    print_menu_header("PRISM Global Command Menu")
    menu_options = get_menu_options()
    if print_menu_options(None, menu_options, submenu = True):
        return

def print_menu_options(self, menu_options, submenu = False, index_and_text = False):
    if index_and_text:
        for key, item in menu_options.items():
            if key.isdigit():
                print(f"{key:<20}{item['description']:<20}")
        print("-" * 60)
        print()
        for key, item in menu_options.items():
            if not key.isdigit():
                print(f"{key:<20}{item['description']:<20}")
    else:
        for key, item in menu_options.items():
            print(f"{key:<20}{item['description']:<20}")
    if submenu:
        print("\nENTER: Back to Previous Menu")
    choice = input("\nprism> ").strip()
    selected = menu_options.get(choice)
    if selected:
        handler = selected['menu_caller']
        if handler(self): # if the submenu indicates to exit
            return 1
    elif check_global_menu_options(choice):
        description, menu_caller = check_global_menu_options(choice)
        if goto_menu(menu_caller, self):
            return 1
    elif choice.lower() in ['exit', 'quit', 'q']:
        if not submenu:
            exit_menu()
            exit(0)
        return 1
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