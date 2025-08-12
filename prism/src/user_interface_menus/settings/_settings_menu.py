# system settings for the user interface

from user_interface_menus._menu_helper import *

# ------------------------------------------------------------

def window_width_settings(self):
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    print("Current PRISM window width:", WINDOW_WIDTH)
    new_width = get_input(self, prompt = "Enter new width between 80 and 200: ")
    if not new_width.isdigit():
        error("Window width must be an integer.")
        return 0
    if int(new_width) > 200 or int(new_width) < 80:
        error("Window width cannot exceed 200 characters.")
        return 0
    set_window_width(int(new_width))

def window_height_settings(self):
    from user_interface_menus._menu_helper import WINDOW_HEIGHT
    print("Current PRISM window height:", WINDOW_HEIGHT)
    new_height = get_input(self, prompt = "Enter new height between 5 and 15: ")
    if not new_height.isdigit():
        error("Window height must be an integer.")
        return 0
    if int(new_height) < 5 or int(new_height) > 15:
        error("Window height must be between 5 and 15 lines.")
        return 0
    set_window_height(int(new_height))

def print_display_params(self):
    if not self.commands_queue:
        from user_interface_menus._menu_helper import WINDOW_WIDTH, RIGHT_ALIGN, COLOR_ON
        print()
        print(f"PRISM window width: {WINDOW_WIDTH}")
        print(f"Right alignment of menu options: {'enabled' if RIGHT_ALIGN else 'disabled'}")
        print(f"Color output in terminal: {'enabled' if COLOR_ON else 'disabled'}")
        exit_menu()

def display_settings(self):
    menu_options = {
        'print': {'description': 'Print current system parameters', 'menu_caller': print_display_params},
        'width': {'description': 'Adjust PRISM window width', 'menu_caller': window_width_settings},
        'height': {'description': 'Adjust PRISM window height', 'menu_caller': window_height_settings},
        'align': {'description': 'Toggle right alignment of menu options', 'menu_caller': toggle_right_align},
        'color': {'description': 'Toggle color output in terminal', 'menu_caller': toggle_color_output},
    }

    while True:
        if not self.commands_queue:
            print_menu_header("settings display")
        if print_menu_options(self, menu_options, submenu = True, recommended_actions = ['color']):
            break

# ------------------------------------------------------------

def related_parameter(self):
    from user_interface_menus._menu_helper import RELATED_OPTIONS_THRESHOLD
    print("Current threshold:", RELATED_OPTIONS_THRESHOLD)
    new_threshold = get_input(self, prompt = "Enter new threshold (ranges 0.0 to 1.0): ")
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
    new_threshold = get_input(self, prompt = "Enter new threshold (ranges 0.0 to 1.0): ")
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
    new_temperature = get_input(self, prompt = "Enter new temperature (ranges 0.0 to 1.0): ")
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
    new_tokens = get_input(self, prompt = "Enter new max tokens (must be a positive integer): ")
    if new_tokens == '':
        return 0
    try:
        if int(new_tokens) <= 0:
            error("Max tokens must be a positive integer.")
            return 0
    except Exception as e:
        error("Invalid input. Please try again.")
    set_assistant_tokens(int(new_tokens))

def menu_delay_parameter(self):
    from user_interface_menus._menu_helper import MENU_DELAY
    print("Current menu delay:", MENU_DELAY)
    new_delay = get_input(self, prompt = "Enter new menu delay (must be a positive number): ")
    if new_delay == '':
        return 0
    try:
        if float(new_delay) <= 0:
            error("Menu delay must be a positive number.")
            return 0
    except Exception as e:
        error("Invalid input. Please try again.")
        return 0
    set_menu_delay(float(new_delay))

def timeout_parameter(self):
    from user_interface_menus._menu_helper import TIMEOUT
    print("Current timeout:", TIMEOUT)
    new_timeout = get_input(self, prompt = "Enter new timeout (must be a positive integer): ")
    if new_timeout == '':
        return 0
    try:
        if int(new_timeout) <= 0:
            error("Timeout must be a positive integer.")
            return 0
    except Exception as e:
        error("Invalid input. Please try again.")
        return 0
    set_timeout(int(new_timeout))

def param_set_type_speed(self):
    from user_interface_menus._menu_helper import ASSISTANT_TYPE_SPEED
    print("Current assistant type speed:", ASSISTANT_TYPE_SPEED)
    new_speed = get_input(self, prompt = "Enter new type speed (must be a positive number recommended 0.015): ")
    print(f"New type speed: {new_speed}")
    if new_speed == '':
        return 0
    try:
        if float(new_speed) < 0.001 or float(new_speed) > 0.03:
            error(f"Type speed must be a positive number between 0.001 and 0.03: {new_speed}")
            return 0
    except Exception as e:
        error("Invalid input. Please try again.")
    set_assistant_type_speed(float(new_speed))

def print_params(self):
    if not self.commands_queue:
        from user_interface_menus._menu_helper import RELATED_OPTIONS_THRESHOLD, BEST_OPTIONS_THRESHOLD, \
                                                    ASSISTANT_TEMPERATURE, ASSISTANT_TOKENS, \
                                                    MENU_DELAY, TIMEOUT, ASSISTANT_TYPE_SPEED
        print(f"RELATED_OPTIONS_THRESHOLD: {RELATED_OPTIONS_THRESHOLD}")
        print(f"BEST_OPTIONS_THRESHOLD: {BEST_OPTIONS_THRESHOLD}")
        print(f"ASSISTANT_TEMPERATURE: {ASSISTANT_TEMPERATURE}")
        print(f"ASSISTANT_TOKENS: {ASSISTANT_TOKENS}")
        print(f"ASSISTANT_TYPE_SPEED: {ASSISTANT_TYPE_SPEED}")
        print(f"MENU_DELAY: {MENU_DELAY}")
        print(f"TIMEOUT: {TIMEOUT}")
        exit_menu()

def parameter_settings(self):
    menu_options = {
        'print': {'description': 'Print current system parameters', 'menu_caller': print_params},
        'threshold': {'description': 'Adjust the minimum command prediction similarity tolerance', 'menu_caller': related_parameter},
        'best threshold': {'description': 'Adjust the prioritized "best" command prediction similarity tolerance', 'menu_caller': best_related_parameter},
        'temperature': {'description': 'Adjust the temperature of the PRISM Assistant', 'menu_caller': temperature_parameter},
        'tokens': {'description': 'Adjust the maximum tokens for the PRISM Assistant', 'menu_caller': tokens_parameter},
        'type speed': {'description': 'Adjust the typing speed of the PRISM Assistant', 'menu_caller': param_set_type_speed},
        'delay': {'description': 'Adjust the delay between menu displays', 'menu_caller': menu_delay_parameter}, 
        'timeout': {'description': 'Adjust the user interface timeout for API calls', 'menu_caller': timeout_parameter},
    }

    while True:
        if not self.commands_queue:
            print_menu_header("settings system params")
        if print_menu_options(self, menu_options, submenu = True, recommended_actions = ['print']):
            break

def readme(self):
    from user_interface_menus._menu_helper import SHOW_README
    if SHOW_README:
        print("PRISM Readme is currently enabled.")
    else:
        print("PRISM Readme is currently disabled.")
    
    show_on_startup = prompt_confirmation(self, prompt = "Show README on startup?")
    set_show_readme(show_on_startup)
    success(f"PRISM Readme on startup {'enabled' if show_on_startup else 'disabled'}.", self)

def system_settings(self):
    menu_options = {
        'params': {'description': 'Adjust system parameters', 'menu_caller': parameter_settings},
        'readme': {'description': 'Toggle display of the PRISM Readme on startup', 'menu_caller': readme},
    }

    while True:
        if not self.commands_queue:
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
        if not self.commands_queue:
            print_menu_header("settings")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

global DISPLAY 
DISPLAY = display_settings

global READ_ME_SET
READ_ME_SET = readme

global WINDOW_WIDTH_SETTINGS
WINDOW_WIDTH_SETTINGS = window_width_settings

global PARAM_WINDOW_HEIGHT
PARAM_WINDOW_HEIGHT = window_height_settings

# ------------------------------------------------------------

global SYSTEM_SETTINGS
SYSTEM_SETTINGS = system_settings

global PARAMETER_SETTINGS
PARAMETER_SETTINGS = parameter_settings

global PRINT_PARAMS
PRINT_PARAMS = print_params

global PARAM_MENU_DELAY
PARAM_MENU_DELAY = menu_delay_parameter

global PARAM_TIMEOUT
PARAM_TIMEOUT = timeout_parameter

global PARAM_RELATED_THRESHOLD
PARAM_RELATED_THRESHOLD = related_parameter

global PARAM_BEST_OPTIONS_THRESHOLD
PARAM_BEST_OPTIONS_THRESHOLD = best_related_parameter

global PARAM_ASSISTANT_TEMPERATURE
PARAM_ASSISTANT_TEMPERATURE = temperature_parameter

global PARAM_ASSISTANT_TOKENS
PARAM_ASSISTANT_TOKENS = tokens_parameter

global PARAM_ASSISTANT_TYPE_SPEED
PARAM_ASSISTANT_TYPE_SPEED = param_set_type_speed