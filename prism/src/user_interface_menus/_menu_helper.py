# globals and global editing functions

from user_interface_menus.utils._display import *
from user_interface_menus.utils._menu_display import *

# ------------------------------------------------------------

_menu_options = None

global local_menu_options
local_menu_options = {}

global current_menu
current_menu = None

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

global MENU_DELAY
MENU_DELAY = 0.5

global TIMEOUT
TIMEOUT = 10

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

def set_menu_delay(delay):
    global MENU_DELAY
    if isinstance(delay, (int, float)) and delay >= 0:
        MENU_DELAY = delay
    else:
        error("Menu delay must be a non-negative number.")
    save_params()

def set_timeout(timeout):
    global TIMEOUT
    if isinstance(timeout, int) and timeout > 0:
        TIMEOUT = timeout
    else:
        error("Timeout must be a positive integer.")
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

def load_saved_macros(self):
    try:
        with open("../config/saved_macros.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip():
                    identifier, command_string, description = line.strip().split('|')
                    add_user_defined_global_command(identifier, command_string, description, self)
    except FileNotFoundError:
        print("No saved macros found. Please run the system tests to create macros.")
    except Exception as e:
        error(f"Error loading saved macros: {e}", self)
    try:
        with open("user_interface_menus/utils/system_tests.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip():
                    identifier, command_string, description = line.strip().split('|')
                    add_user_defined_global_command(identifier, command_string, description, self)
    except FileNotFoundError:
        print("No system tests found. Please run the system tests to create macros.")
    except Exception as e:
        error(f"Error loading system tests: {e}", self)
    try:
        with open("user_interface_menus/utils/system_utils.txt", 'r') as file:
            lines = file.readlines()
            for line in lines:
                if line.strip():
                    identifier, command_string, description = line.strip().split('|')
                    add_user_defined_global_command(identifier, command_string, description, self)
    except FileNotFoundError:
        print("No system tests found. Please run the system tests to create macros.")
    except Exception as e:
        error(f"Error loading system tests: {e}", self)

def save_macro(self, identifier, command_string, description = None):
    with open("../config/saved_macros.txt", 'a') as file:
        if description is None:
            description = command_string
        file.write(f"{identifier}|{command_string}|{description}\n")
    success("Macro saved successfully.", self)

def remove_macro(self, choice):
    global _menu_options
    identifier = choice[1:].strip()
    if _menu_options and identifier in _menu_options:
        del _menu_options[identifier]
        try:
            with open("../config/saved_macros.txt", 'r') as file:
                lines = file.readlines()
            with open("../config/saved_macros.txt", 'w') as file:
                for line in lines:
                    if not line.startswith(f"{identifier}|"):
                        file.write(line)
            success(f"Macro '{identifier}' removed successfully.", self)
            try:
                with open("../config/saved_macros.txt", "r") as f:
                    saved_macros = f.readlines()
                    for macro in saved_macros:
                        print(macro.strip())
                identifier = choice[1:].strip()
            except FileNotFoundError:
                error(f"No saved macros found. Check {green('config/saved_macros.txt')}.", self)
            except Exception as e:
                error(f"Error removing command: {e}", self)
        except Exception as e:
            error(f"Error removing macro from file: {e}", self)

def macro_search(self, query, all = False):
    from difflib import get_close_matches

    def sort(iterable):
        global RELATED_OPTIONS_THRESHOLD
        return get_close_matches(query, iterable, n = 10, cutoff = RELATED_OPTIONS_THRESHOLD)
    
    query = query[1:].strip() if len(query) > 1 else ''
    try:
        with open("../config/saved_macros.txt", "r") as f:
            saved_macros = f.readlines()
            matches = []
            print(f"\nSearching {"all" if all else "matching"} macros{f" for '{yellow(query)}'" if query else ""}:")
            if all:
                matches = [macro.strip() for macro in saved_macros if macro.strip()]
            elif query:
                for macro in saved_macros:
                    if query in macro:
                        matches.append(macro.strip())
                close_matches = sort([macro.split('|')[0] for macro in saved_macros])
                for match in close_matches:
                    if match not in matches:
                        for macro in saved_macros:
                            if macro.startswith(f"{match}|") and macro.strip() not in matches:
                                matches.append(macro.strip())
                matches = matches[:10]
            if matches:
                print()
                for match in matches:
                    print(yellow(left_align(match.split('|')[0])) + " " * 2 + align(match.split('|')[2]))
                print()
                success(f"Found {cyan(len(matches))} matching macros:", self)
            else:
                print()
                error(f"No saved macros found." if not query else f"No matching macros found for '{yellow(query)}'.", self)
    except FileNotFoundError:
        error(f"No saved macros found. Check {green('config/saved_macros.txt')}.", self)
    except Exception as e:
        error(f"Error searching macros: {e}", self)

def add_user_defined_global_command(identifier, command_string, description = None, self = None):
    global _menu_options
    if _menu_options is None:
        _menu_options = {}

    banned_characters = ['/', '?']
    banned_identifiers = ['yes', 'y', 'no', 'n']
    banned_identifiers.extend(map(str, range(0, 1000)))
    
    if identifier not in _menu_options:
        if identifier in banned_identifiers:
            error(f"Identifier '{identifier}' is reserved and cannot be used.", self)
            return False
        if any(char in identifier for char in banned_characters):
            error(f"Identifier '{identifier}' contains a banned character and cannot be used.", self)
            return False
        _menu_options[identifier] = {
            'description': command_string if description is None else description,
            'menu_caller': CommandInjector(command_string)
        }
        return True
    else:
        error(f"Command '{identifier}' already exists.", self if self else None)
        return False

def set_local_menu_options(menu_name, menu_options):
    global current_menu, local_menu_options
    current_menu = menu_name
    local_menu_options = menu_options

def print_local_menu_options(self = None):
    global local_menu_options
    if local_menu_options:
        print(f"\nLocal menu options ({yellow('/<command>')} to access):\n")
        for key, value in local_menu_options.items():
            print(f"{yellow(key)}")
    print()

def get_local_menu_options():
    global local_menu_options
    return local_menu_options

# ------------------------------------------------------------

def load_params():
    import time
    global RIGHT_ALIGN, RELATED_OPTIONS_THRESHOLD, ASSISTANT_TEMPERATURE, \
           BEST_OPTIONS_THRESHOLD, ASSISTANT_TOKENS, WINDOW_WIDTH, SHOW_README, COLOR_ON, \
           MENU_DELAY, TIMEOUT

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
                elif global_var == "MENU_DELAY":
                    try:
                        if float(val) < 0:
                            print(global_var, "INVALID, please update")
                        else:
                            MENU_DELAY = float(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
                elif global_var == "TIMEOUT":
                    try:
                        if int(val) <= 0:
                            print(global_var, "INVALID, please update")
                        else:
                            TIMEOUT = int(val)
                            print(global_var, val)
                    except Exception as e:
                        print(global_var, "INVALID, please update")
    time.sleep(MENU_DELAY * 2)
    save_params()

def save_params():
    global RIGHT_ALIGN, RELATED_OPTIONS_THRESHOLD, ASSISTANT_TEMPERATURE, \
           BEST_OPTIONS_THRESHOLD, ASSISTANT_TOKENS, WINDOW_WIDTH, SHOW_README, COLOR_ON, \
           MENU_DELAY, TIMEOUT

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
        file.write(f"MENU_DELAY={MENU_DELAY}\n")
        file.write(f"TIMEOUT={TIMEOUT}\n")

def load_menus():
    global _menu_options

    clear()
    print("Now loading menus...")
    from user_interface_menus.utils._commands import init_commands
    _menu_options = init_commands()

def write_to_interface_log(message):
    try:
        with open("../logs/interface_logs/test_interface_log.txt", "a") as file:
            file.write(f"{message}\n")
    except Exception as e:
        print(f"Error: Could not write to log file: {e}")

def read_from_interface_log():
    try:
        with open("../logs/interface_logs/test_interface_log.txt", "r") as file:
            content = file.read()
        return content
    except FileNotFoundError:
        print("Interface log file not found.")
        return ""
    except Exception as e:
        print(f"An unexpected error occurred while reading the interface log: {e}")
        return ""