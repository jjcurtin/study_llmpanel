from user_interface_menus._menu_helper import *

def window_width_settings(self):
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    print("Current PRISM window width:", WINDOW_WIDTH)
    new_width = input("Enter new width (default 80): ").strip()
    if not new_width.isdigit():
        new_width = '80'
    if int(new_width) > 200:
        error("Window width cannot exceed 200 characters.")
        return
        
    set_window_width(int(new_width))
    print("PRISM window width set to:", WINDOW_WIDTH)

def display_settings(self):
    menu_options = {
        'width': {'description': 'Adjust PRISM window width', 'menu_caller': window_width_settings}
    }

    while True:
        print_menu_header("PRISM Settings Menu")
        if print_menu_options(self, menu_options, submenu = True):
            break

def settings_menu(self):
    menu_options = {
        'display': {'description': 'Manage Display settings', 'menu_caller': display_settings}
    }

    while True:
        print_menu_header("PRISM Settings Menu")
        if print_menu_options(self, menu_options, submenu = True):
            break

global DISPLAY 
DISPLAY = display_settings
global WINDOW_WIDTH_SETTINGS
WINDOW_WIDTH_SETTINGS = window_width_settings