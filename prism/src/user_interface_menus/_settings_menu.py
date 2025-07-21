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
        'align': {'description': 'Toggle right alignment of menu options', 'menu_caller': lambda self: toggle_right_align(self)}
    }

    while True:
        print_menu_header("PRISM Display Settings")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

def related_parameter(self):
    from user_interface_menus._menu_helper import RELATED_OPTIONS_THRESHOLD
    print("Current threshold:", RELATED_OPTIONS_THRESHOLD)
    new_threshold = input("Enter new threshold (default 0.3, ranges 0.0 to 1.0): ").strip()
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

def temperature_parameter(self):
    from user_interface_menus._menu_helper import ASSISTANT_TEMPERATURE
    print("Current assistant temperature:", ASSISTANT_TEMPERATURE)
    new_temperature = input("Enter new temperature (default 0.7, ranges 0.0 to 1.0): ").strip()
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

def parameter_settings(self):
    menu_options = {
        'related': {'description': 'Adjust the related command prediction tolerance for similarity', 'menu_caller': related_parameter},
        'temperature': {'description': 'Adjust the temperature of the PRISM Assistant', 'menu_caller': temperature_parameter}
    }

    while True:
        print_menu_header("PRISM System Settings")
        if print_menu_options(self, menu_options, submenu = True):
            break

def system_settings(self):
    menu_options = {
        'parameters': {'description': 'Adjust system parameters', 'menu_caller': parameter_settings},
    }

    while True:
        print_menu_header("PRISM System Settings")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

def settings_menu(self):
    menu_options = {
        'system': {'description': 'System Settings', 'menu_caller': system_settings},
        'display': {'description': 'Manage Display settings', 'menu_caller': display_settings}
    }

    while True:
        print_menu_header("PRISM Settings Menu")
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

global PARAM_ASSISTANT_TEMPERATURE
PARAM_ASSISTANT_TEMPERATURE = temperature_parameter