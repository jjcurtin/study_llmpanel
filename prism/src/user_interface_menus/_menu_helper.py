import os

# ------------------------------------------------------------

_menu_options = None

global WINDOW_WIDTH
WINDOW_WIDTH = 155

global RIGHT_ALIGN
RIGHT_ALIGN = True

global RELATED_OPTIONS_THRESHOLD
RELATED_OPTIONS_THRESHOLD = 0.3

global BEST_OPTIONS_THRESHOLD
BEST_OPTIONS_THRESHOLD = 0.7

global ASSISTANT_TEMPERATURE
ASSISTANT_TEMPERATURE = 0.7

global SHOW_README
SHOW_README = True

global COLOR_ON
COLOR_ON = True

# ------------------------------------------------------------

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu_header(title):
    clear()
    padding = (WINDOW_WIDTH - len(title)) // 2
    print_equals()
    if COLOR_ON:
        print(" " * padding + f"\033[31m{title}\033[0m")
    else:
        print(" " * padding + title)
    print_equals()
    print()

def toggle_color_output(self):
    global COLOR_ON
    COLOR_ON = not COLOR_ON
    save_params()

def print_fixed_terminal_prompt():
    if COLOR_ON:
        choice = input("\n\033[36mprism> \033[0m").strip()
    else:
        choice = input("\nprism> ").strip()
    return choice

def print_assistant_terminal_prompt():
    if COLOR_ON:
        choice = input("\n\033[31massistant> \033[0m").strip()
    else:
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
    save_params()

def toggle_right_align(self = None):
    global RIGHT_ALIGN
    RIGHT_ALIGN = not RIGHT_ALIGN
    save_params()

def set_related_options_threshold(new_threshold):
    global RELATED_OPTIONS_THRESHOLD
    RELATED_OPTIONS_THRESHOLD = new_threshold
    save_params()

def set_best_options_threshold(new_threshold):
    global BEST_OPTIONS_THRESHOLD
    BEST_OPTIONS_THRESHOLD = new_threshold
    save_params()

def set_assistant_temperature(temperature):
    global ASSISTANT_TEMPERATURE
    ASSISTANT_TEMPERATURE = temperature
    save_params()

def set_show_readme(show):
    global SHOW_README
    SHOW_README = show
    save_params()

# ------------------------------------------------------------

def load_params():
    clear()
    print("Now loading parameters...")
    file_path = "../config/uiconfig.txt"
    with open(file_path, 'r') as file:
        lines = file.readlines()
        for line in lines:
            global_var = line.split("=")[0].strip()
            val = line.split("=")[1].strip()
            if global_var and val:
                if global_var == "RIGHT_ALIGN" and val == "False":
                    toggle_right_align()
                    print(global_var, val)
                elif global_var == "WINDOW_WIDTH":
                    try:
                        if int(val) and int(val) > 0 and int(val) < 200:
                            global WINDOW_WIDTH
                            WINDOW_WIDTH = int(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "RELATED_OPTIONS_THRESHOLD":
                    try:
                        if float(val) > 1.0 or float(val) < 0.0:
                            print(global_var, "INVALID, please update")
                        else:
                            global RELATED_OPTIONS_THRESHOLD
                            RELATED_OPTIONS_THRESHOLD = float(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "BEST_OPTIONS_THRESHOLD":
                    try:
                        if float(val) > 1.0 or float(val) < 0.0:
                            print(global_var, "INVALID, please update")
                        else:
                            global BEST_OPTIONS_THRESHOLD
                            BEST_OPTIONS_THRESHOLD = float(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "ASSISTANT_TEMPERATURE":
                    try:
                        if float(val) > 1.0 or float(val) < 0.0:
                            print(global_var, "INVALID, please update")
                        else:
                            global ASSISTANT_TEMPERATURE
                            ASSISTANT_TEMPERATURE = float(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "SHOW_README":
                    global SHOW_README
                    if val == "True":
                        SHOW_README = True
                        print(global_var, val)
                    elif val == "False":
                        SHOW_README = False
                        print(global_var, val)
                    else:
                        print(global_var, "INVALID, please update")
                elif global_var == "COLOR_ON":
                    global COLOR_ON
                    if val == "True":
                        COLOR_ON = True
                        print(global_var, val)
                    elif val == "False":
                        COLOR_ON = False
                        print(global_var, val)
                    else:
                        print(global_var, "INVALID, please update")
    save_params()

def save_params():
    file_path = "../config/uiconfig.txt"
    with open(file_path, 'w') as file:
        global RIGHT_ALIGN, RELATED_OPTIONS_THRESHOLD, ASSISTANT_TEMPERATURE
        file.write(f"RIGHT_ALIGN={RIGHT_ALIGN}\n")
        file.write(f"RELATED_OPTIONS_THRESHOLD={RELATED_OPTIONS_THRESHOLD}\n")
        file.write(f"BEST_OPTIONS_THRESHOLD={BEST_OPTIONS_THRESHOLD}\n")
        file.write(f"ASSISTANT_TEMPERATURE={ASSISTANT_TEMPERATURE}\n")
        file.write(f"WINDOW_WIDTH={WINDOW_WIDTH}\n")
        file.write(f"SHOW_README={SHOW_README}\n")
        file.write(f"COLOR_ON={COLOR_ON}\n")

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

def get_relevant_menu_options(query = None):
    def sort(iterable):
        global RELATED_OPTIONS_THRESHOLD
        from difflib import get_close_matches
        threshold = max(RELATED_OPTIONS_THRESHOLD, 0.1)
        return get_close_matches(query, iterable, n = 15, cutoff = threshold)

    menu_options = get_menu_options()
    potential_local_choices = ', '.join(menu_options.keys())
    potential_glocal_choices = ', '.join(_menu_options.keys())
    combined_choices = potential_local_choices + ', ' + potential_glocal_choices

    if query is not None:
        combined_choices = ', '.join(sort(set(combined_choices.split(', '))))
    
    combined_choices = {choice: menu_options[choice] for choice in combined_choices.split(', ') if choice in menu_options}
    return combined_choices

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
    
def print_global_command_menu(self, query = None):
    menu_options = get_relevant_menu_options(query)
    if query is None:
        menu_options = {k: v for k, v in sorted(menu_options.items(), key=lambda item: item[0])}

    while True:
        print_menu_header("PRISM Global Command Menu")

        if not menu_options:
            if COLOR_ON:
                print("\033[31mNo commands found matching your query.\033[0m")
            else:
                print("No commands found matching your query.")
        if print_menu_options(self, menu_options, submenu = True):
            break
    
# ------------------------------------------------------------

def print_menu_options(self, menu_options, submenu = False, index_and_text = False, choice = None):

    def print_key_line(margin_width, key, item):
        if not RIGHT_ALIGN:
            if COLOR_ON:
                print(f"\033[33m{key:<{int(margin_width)}}\033[0m {item['description']:<{int(margin_width - 1)}}")
            else:
                print(f"{key:<{int(margin_width)}} {item['description']:<{int(margin_width - 1)}}")
        else:
            if COLOR_ON:
                print(f"\033[33m{key:<{int(margin_width)}}\033[0m {item['description']:>{int(margin_width - 1)}}")
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
            if COLOR_ON:
                print("\n\033[33mENTER\033[0m: Back to Previous Menu")
            else:
                print("\nENTER: Back to Previous Menu")

    if choice is None:
        print_keys()
        choice = print_fixed_terminal_prompt()
    
    if choice.split(" ")[0] == "command":
        query = ' '.join(choice.split(" ")[1:]) if len(choice.split(" ")) > 1 else None
        print_global_command_menu(self, query)
        return 1
    elif choice.startswith("/"):
        query = choice[1:].strip()
        if query == '':
            query = None
        print_global_command_menu(self, query)
        return 1

    selected = menu_options.get(choice)
    if selected:
        try:
            menu_caller = selected['menu_caller']
            if goto_menu(menu_caller, self):
                return 1
        except Exception as e:  
            error(f"Local menu option error: {e}")
            return 0
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
        global RELATED_OPTIONS_THRESHOLD
        global BEST_OPTIONS_THRESHOLD
        from difflib import get_close_matches
        overall_matches = get_close_matches(choice, iterable, n = 5, cutoff = max(RELATED_OPTIONS_THRESHOLD, 0.1))
        best_matches = get_close_matches(choice, iterable, n = 5, cutoff = BEST_OPTIONS_THRESHOLD)
        if best_matches and RELATED_OPTIONS_THRESHOLD < BEST_OPTIONS_THRESHOLD:
            return best_matches
        return overall_matches

    potential_local_choices = ', '.join(menu_options.keys())
    potential_glocal_choices = ', '.join(_menu_options.keys())
    combined_choices = potential_local_choices + ', ' + potential_glocal_choices
    combined_choices = ', '.join(sort(set(combined_choices.split(', '))))

    if COLOR_ON:
        diagnosis = "\n\033[31mInvalid choice.\033[0m"
    else:
        diagnosis = "\nInvalid choice."

    if combined_choices == '':
        if COLOR_ON:
            diagnosis += " Please use \033[33mcommand\033[0m to see a list of commands or \033[33mhelp\033[0m to view documentation."
        else:
            diagnosis += " Please use 'command' to see a list of commands or 'help' to view documentation."
        print(diagnosis)
    else:    
        diagnosis += " Did you mean one of these?"
        print(diagnosis)
        
        if COLOR_ON:
            for potential_choice in combined_choices.split(', ')[:5]:
                print(f"- \033[33m{potential_choice}\033[0m")
            print("\nEnter \033[33myes\033[0m to select the first command, or enter a \033[33mdifferent command\033[0m.")
        else:
            for potential_choice in combined_choices.split(', ')[:5]:
                print(f"- {potential_choice}")
            print("Enter 'yes' to select the first command, or enter a different command.")
    
    choice = print_fixed_terminal_prompt()
    if choice.lower() == 'yes':
        first_choice = combined_choices.split(', ')[0]
        if first_choice in menu_options:
            menu_caller = menu_options[first_choice]['menu_caller']
            goto_menu(menu_caller, self)
        elif first_choice in _menu_options:
            menu_caller = _menu_options[first_choice]['menu_caller']
            goto_menu(menu_caller, self)
    else:
        print_menu_options(self, menu_options, submenu = True, index_and_text = False, choice = choice)

# ------------------------------------------------------------

def error(message = "An unexpected error occurred."):
    if COLOR_ON:
        print(f"\033[31mError\033[0m: {message}")
    else:
        print(f"Error: {message}")
    exit_menu()

def success(message = "Operation completed successfully."):
    if COLOR_ON:
        print(f"\033[32mSuccess\033[0m: {message}")
    else:
        print(f"Success: {message}")
    exit_menu()
    
def exit_menu():
    if COLOR_ON:
        input("\n\033[33mENTER to Continue> \033[0m")
    else:
        input("\nENTER to Continue> ")

def exit_interface(self):
    if COLOR_ON:
        print(f"\033[32mExiting PRISM Interface.\033[0m")
    else:
        print("Exiting PRISM Interface.")
    exit(0)