from user_interface_menus._menu_helper import *

# ------------------------------------------------------------

def window_width_settings(self):
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    print("Current PRISM window width:", WINDOW_WIDTH)
    new_width = input("Enter new width (default 80): ").strip()
    if not new_width.isdigit():
        error("Window width must be an integer.")
        return 0
    if int(new_width) > 200:
        error("Window width cannot exceed 200 characters.")
        return 0
        
    set_window_width(int(new_width))

def display_settings(self):
    menu_options = {
        'width': {'description': 'Adjust PRISM window width', 'menu_caller': window_width_settings},
        'align': {'description': 'Toggle right alignment of menu options', 'menu_caller': toggle_right_align},
        'color': {'description': 'Toggle color output in terminal', 'menu_caller': toggle_color_output},
    }

    while True:
        print_menu_header("settings display")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

def related_parameter(self):
    from user_interface_menus._menu_helper import RELATED_OPTIONS_THRESHOLD
    print("Current threshold:", RELATED_OPTIONS_THRESHOLD)
    new_threshold = input("Enter new threshold (ranges 0.0 to 1.0): ").strip()
    if new_threshold == '':
        return 0
    try:
        if float(new_threshold) > 1.0 or float(new_threshold) < 0.0:
            error("Threshold must be within the range 0.0 to 1.0.")
            return 0
    except Exception as e:
        error("Invalid input. Please try again.")
        return 0
    set_related_options_threshold(float(new_threshold))


def best_related_parameter(self):
    from user_interface_menus._menu_helper import BEST_OPTIONS_THRESHOLD
    print("Current threshold:", BEST_OPTIONS_THRESHOLD)
    new_threshold = input("Enter new threshold (ranges 0.0 to 1.0): ").strip()
    if new_threshold == '':
        return 0
    try:
        if float(new_threshold) > 1.0 or float(new_threshold) < 0.0:
            error("Threshold must be within the range 0.0 to 1.0.")
            return 0
    except Exception as e:
        error("Invalid input. Please try again.")
        return 0
    set_best_options_threshold(float(new_threshold))

def temperature_parameter(self):
    from user_interface_menus._menu_helper import ASSISTANT_TEMPERATURE
    print("Current assistant temperature:", ASSISTANT_TEMPERATURE)
    new_temperature = input("Enter new temperature (ranges 0.0 to 1.0): ").strip()
    if new_temperature == '':
        return 0
    try:
        if float(new_temperature) > 1.0 or float(new_temperature) < 0.0:
            error("Temperature must be within the range 0.0 to 1.0.")
            return 0
    except Exception as e:
        error("Invalid input. Please try again.")
        return 0
    set_assistant_temperature(float(new_temperature))

def tokens_parameter(self):
    from user_interface_menus._menu_helper import ASSISTANT_TOKENS
    print("Current assistant max tokens:", ASSISTANT_TOKENS)
    new_tokens = input("Enter new max tokens (must be a positive integer): ").strip()
    if new_tokens == '':
        return 0
    try:
        if int(new_tokens) <= 0:
            error("Max tokens must be a positive integer.")
            return 0
    except Exception as e:
        error("Invalid input. Please try again.")
    set_assistant_tokens(int(new_tokens))

def parameter_settings(self):
    menu_options = {
        'threshold': {'description': 'Adjust the minimum command prediction similarity tolerance', 'menu_caller': related_parameter},
        'best threshold': {'description': 'Adjust the prioritized "best" command prediction similarity tolerance', 'menu_caller': best_related_parameter},
        'temperature': {'description': 'Adjust the temperature of the PRISM Assistant', 'menu_caller': temperature_parameter},
        'tokens': {'description': 'Adjust the maximum tokens for the PRISM Assistant', 'menu_caller': tokens_parameter}
    }

    while True:
        print_menu_header("settings system params")
        if print_menu_options(self, menu_options, submenu = True):
            break

def readme(self):
    from user_interface_menus._menu_helper import SHOW_README
    if SHOW_README:
        print("PRISM Readme is currently enabled.")
    else:
        print("PRISM Readme is currently disabled.")
    
    choice = input("Show README on startup? (y/n): ").strip().lower()
    if choice == 'y':
        set_show_readme(True)
        success("Readme will be shown on startup.")
    elif choice == 'n':
        set_show_readme(False)
        success("Readme will not be shown on startup.")
    else:
        print("No changes made to Readme display setting.")
        exit_menu()

def system_settings(self):
    menu_options = {
        'params': {'description': 'Adjust system parameters', 'menu_caller': parameter_settings},
        'readme': {'description': 'Toggle display of the PRISM Readme on startup', 'menu_caller': readme},
    }

    while True:
        print_menu_header("settings system")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

def settings_menu(self):
    menu_options = {
        'system': {'description': 'System Settings', 'menu_caller': system_settings},
        'display': {'description': 'Manage Display settings', 'menu_caller': display_settings}
    }

    while True:
        print_menu_header("settings")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

global DISPLAY 
DISPLAY = display_settings
global WINDOW_WIDTH_SETTINGS
WINDOW_WIDTH_SETTINGS = window_width_settings

global SYSTEM_SETTINGS
SYSTEM_SETTINGS = system_settings

global PARAMETER_SETTINGS
PARAMETER_SETTINGS = parameter_settings

global PARAM_RELATED_THRESHOLD
PARAM_RELATED_THRESHOLD = related_parameter

global PARAM_BEST_OPTIONS_THRESHOLD
PARAM_BEST_OPTIONS_THRESHOLD = best_related_parameter

global PARAM_ASSISTANT_TEMPERATURE
PARAM_ASSISTANT_TEMPERATURE = temperature_parameter

global PARAM_ASSISTANT_TOKENS
PARAM_ASSISTANT_TOKENS = tokens_parameter

global READ_ME_SET
READ_ME_SET = readme