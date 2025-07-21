import os

_menu_options = None
_previous_menu = None

global WINDOW_WIDTH
WINDOW_WIDTH = 155

global RIGHT_ALIGN
RIGHT_ALIGN = True

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu_header(title):
    clear()
    padding = (WINDOW_WIDTH - len(title)) // 2
    print_equals()
    print(" " * padding + title)
    print_equals()
    print()

def print_fixed_terminal_prompt():
    choice = input("\nprism> ").strip()
    return choice

def print_assistant_terminal_prompt():
    choice = input("\nassistant> ").strip()
    return choice

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

def toggle_right_align(self):
    global RIGHT_ALIGN
    RIGHT_ALIGN = not RIGHT_ALIGN

def load_menus():
    clear()
    print("Now loading menus...")
    global _menu_options
    from user_interface_menus._commands import init_commands
    _menu_options = init_commands()

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

def print_menu_options(self, menu_options, submenu = False, index_and_text = False, choice = None):

    def print_key_line(margin_width, key, item):
        if not RIGHT_ALIGN:
            print(f"{key:<{int(margin_width)}} {item['description']:<{int(margin_width - 1)}}")
        else:
            print(f"{key:<{int(margin_width)}} {item['description']:>{int(margin_width - 1)}}")

    def print_keys():
        margin_width = WINDOW_WIDTH / 2
        if index_and_text:
            for key, item in menu_options.items():
                if key.isdigit():
                    print_key_line(margin_width, key, item)
            print_dashes()
            print()
            for key, item in menu_options.items():
                if not key.isdigit():
                    print_key_line(margin_width, key, item)
        else:
            for key, item in menu_options.items():
                print_key_line(margin_width, key, item)
        if submenu:
            print("\nENTER: Back to Previous Menu")

    if choice is None:
        print_keys()
        choice = print_fixed_terminal_prompt()
    
    selected = menu_options.get(choice)
    if selected:
        try:
            menu_caller = selected['menu_caller']
            if goto_menu(menu_caller, self):
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
        invalid_choice_menu(self, menu_options, choice)
    return 0

def invalid_choice_menu(self, menu_options, choice = None):
    def sort(iterable):
        from difflib import get_close_matches
        return get_close_matches(choice, iterable, n = 5, cutoff = 0.3)

    potential_local_choices = ', '.join(menu_options.keys())
    potential_glocal_choices = ', '.join(_menu_options.keys())
    combined_choices = potential_local_choices + ', ' + potential_glocal_choices
    combined_choices = ', '.join(sort(set(combined_choices.split(', '))))

    diagnosis = "Invalid choice."

    if combined_choices == '':
        diagnosis += " Please use 'command' to see a list of commands or 'help' to view documentation."
        print(diagnosis)
    else:    
        diagnosis += " Did you mean one of these?"
        print(diagnosis)
        for potential_choice in combined_choices.split(', ')[:5]:
            print(f"- {potential_choice}")
    choice = print_fixed_terminal_prompt()
    print_menu_options(self, menu_options, submenu = False, index_and_text = False, choice = choice)

def error(message = "An unexpected error occurred."):
    print(f"Error: {message}")
    input("Press Enter to continue...")

def success(message = "Operation completed successfully."):
    print(f"Success: {message}")
    input("Press Enter to continue...")
    
def exit_menu():
    input("Press Enter to continue...")