from user_interface_menus._menu_helper import *
from user_interface_menus._system_check_menu import system_check_menu
from user_interface_menus._system_task_menu import system_task_menu
from user_interface_menus._participant_management_menus import participant_management_menu
from user_interface_menus._log_menu import log_menu
from user_interface_menus._shutdown_menu import shutdown_menu
from user_interface_menus.help_menu._help_menu import help_menu
from user_interface_menus._settings_menu import settings_menu
from user_interface_menus.assistant._assistant_menu import assistant_menu

# ------------------------------------------------------------

def main_menu(self):
    menu_options = {
        'help': {'description': 'Help', 'menu_caller': help_menu},
        'command': {'description': 'Global Command Menu; "command <query>" to search', 'menu_caller': print_global_command_menu},
        'assistant': {'description': 'PRISM Assistant', 'menu_caller': assistant_menu},
        'check': {'description': 'System Status and Diagnostics', 'menu_caller': system_check_menu},
        'tasks': {'description': 'Manage System Tasks and R Scripts', 'menu_caller': system_task_menu},
        'participants': {'description': 'Manage Participants', 'menu_caller': participant_management_menu},
        'logs': {'description': 'View Logs', 'menu_caller': log_menu},
        'settings': {'description': 'Settings', 'menu_caller': settings_menu},
        'shutdown': {'description': 'Shutdown PRISM', 'menu_caller': shutdown_menu},
        'exit': {'description': 'Exit PRISM User Interface', 'menu_caller': exit_interface}
    }

    from user_interface_menus._menu_helper import SHOW_README
    if SHOW_README == True:
        read_me(self)

    while True:
        print_menu_header("PRISM Interface Main Menu")
        print_menu_options(self, menu_options)

def read_me(self):
    print_menu_header("README")
    print("I recommend looking through the help section and then looking through the commands.")
    print("You can search for commands by typing 'command <query>' or '/<query>'.")
    print("Most commands are globally accessible but some are only available in specific menus.")
    print("\nENTER: Return")
    print_fixed_terminal_prompt()

global README
README = read_me