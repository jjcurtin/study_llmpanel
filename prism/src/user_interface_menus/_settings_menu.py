from user_interface_menus._menu_helper import *

def window_width_settings(self):
    print("Current PRISM window width:", WINDOW_WIDTH)
    new_width = input("Enter new width (default 80): ").strip()
    if not new_width.isdigit():
        new_width = '80'
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
        'display': {'description': 'View Today\'s Transcript', 'menu_caller': display_settings}
    }

    while True:
        print_menu_header("PRISM Settings Menu")
        if print_menu_options(self, menu_options, submenu = True):
            break