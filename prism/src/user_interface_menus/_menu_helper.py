from user_interface_menus.utils._display import *
from user_interface_menus.utils._menu_display import *

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

global ASSISTANT_TOKENS
ASSISTANT_TOKENS = 600

global SHOW_README
SHOW_README = True

global COLOR_ON
COLOR_ON = True

global RECENT_COMMANDS
RECENT_COMMANDS = []

# ------------------------------------------------------------

def toggle_color_output(self):
    global COLOR_ON
    COLOR_ON = not COLOR_ON
    save_params()

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

def set_assistant_tokens(tokens):
    global ASSISTANT_TOKENS
    ASSISTANT_TOKENS = tokens
    save_params()

def set_show_readme(show):
    global SHOW_README
    SHOW_README = show
    save_params()

def add_recent_command(command):
    global RECENT_COMMANDS
    if command != 'recent' and command != 'command' and command not in RECENT_COMMANDS:
        RECENT_COMMANDS.append(command)
        if len(RECENT_COMMANDS) > 10:
            RECENT_COMMANDS.pop(0)

# ------------------------------------------------------------

def load_params():
    global RIGHT_ALIGN, RELATED_OPTIONS_THRESHOLD, ASSISTANT_TEMPERATURE, \
           BEST_OPTIONS_THRESHOLD, ASSISTANT_TOKENS, WINDOW_WIDTH, SHOW_README, COLOR_ON

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
                            WINDOW_WIDTH = int(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "RELATED_OPTIONS_THRESHOLD":
                    try:
                        if float(val) > 1.0 or float(val) < 0.0:
                            print(global_var, "INVALID, please update")
                        else:
                            RELATED_OPTIONS_THRESHOLD = float(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "BEST_OPTIONS_THRESHOLD":
                    try:
                        if float(val) > 1.0 or float(val) < 0.0:
                            print(global_var, "INVALID, please update")
                        else:
                            BEST_OPTIONS_THRESHOLD = float(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "ASSISTANT_TEMPERATURE":
                    try:
                        if float(val) > 1.0 or float(val) < 0.0:
                            print(global_var, "INVALID, please update")
                        else:
                            ASSISTANT_TEMPERATURE = float(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "SHOW_README":
                    if val == "True":
                        SHOW_README = True
                        print(global_var, val)
                    elif val == "False":
                        SHOW_README = False
                        print(global_var, val)
                    else:
                        print(global_var, "INVALID, please update")
                elif global_var == "COLOR_ON":
                    if val == "True":
                        COLOR_ON = True
                        print(global_var, val)
                    elif val == "False":
                        COLOR_ON = False
                        print(global_var, val)
                    else:
                        print(global_var, "INVALID, please update")
                elif global_var == "ASSISTANT_TOKENS":
                    try:
                        if int(val) <= 0:
                            print(global_var, "INVALID, please update")
                        else:
                            ASSISTANT_TOKENS = int(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
    import time
    time.sleep(1)
    save_params()

def save_params():
    global RIGHT_ALIGN, RELATED_OPTIONS_THRESHOLD, ASSISTANT_TEMPERATURE, \
           BEST_OPTIONS_THRESHOLD, ASSISTANT_TOKENS, WINDOW_WIDTH, SHOW_README, COLOR_ON

    file_path = "../config/uiconfig.txt"
    with open(file_path, 'w') as file:
        file.write(f"RIGHT_ALIGN={RIGHT_ALIGN}\n")
        file.write(f"RELATED_OPTIONS_THRESHOLD={RELATED_OPTIONS_THRESHOLD}\n")
        file.write(f"BEST_OPTIONS_THRESHOLD={BEST_OPTIONS_THRESHOLD}\n")
        file.write(f"ASSISTANT_TEMPERATURE={ASSISTANT_TEMPERATURE}\n")
        file.write(f"ASSISTANT_TOKENS={ASSISTANT_TOKENS}\n")
        file.write(f"WINDOW_WIDTH={WINDOW_WIDTH}\n")
        file.write(f"SHOW_README={SHOW_README}\n")
        file.write(f"COLOR_ON={COLOR_ON}\n")

def load_menus():
    global _menu_options

    clear()
    print("Now loading menus...")
    from user_interface_menus.utils._commands import init_commands
    _menu_options = init_commands()

# ------------------------------------------------------------

def get_menu_options():
    global _menu_options
    if _menu_options is None:
        load_menus()
    return _menu_options

def get_relevant_menu_options(query = None):
    global RELATED_OPTIONS_THRESHOLD
    def sort(iterable):
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