# first menu shown on startup of the user interface

from user_interface_menus._menu_helper import *
from user_interface_menus.check._system_check_menu import system_check_menu
from user_interface_menus.tasks._system_task_menu import system_task_menu
from user_interface_menus.participants._participant_management_menus import participant_management_menu
from user_interface_menus.logs._log_menu import log_menu
from user_interface_menus._shutdown_menu import shutdown_menu
from user_interface_menus.help._help_menu import help_menu
from user_interface_menus.settings._settings_menu import settings_menu
from user_interface_menus.assistant._assistant_menu import assistant_menu

# ------------------------------------------------------------

def main_menu(self):
    menu_options = {
        'help': {'description': 'Help', 'menu_caller': help_menu},
        'command': {'description': 'Global Command Menu', 'menu_caller': print_global_command_menu},
        'assistant': {'description': 'PRISM Assistant', 'menu_caller': assistant_menu},
        'check': {'description': 'System Status and Diagnostics', 'menu_caller': system_check_menu},
        'tasks': {'description': 'Manage System Tasks/R Scripts', 'menu_caller': system_task_menu},
        'participants': {'description': 'Manage Participants', 'menu_caller': participant_management_menu},
        'logs': {'description': 'View Logs', 'menu_caller': log_menu},
        'settings': {'description': 'Settings', 'menu_caller': settings_menu},
        'shutdown': {'description': 'Shutdown PRISM', 'menu_caller': shutdown_menu},
        'exit': {'description': 'Exit PRISM User Interface', 'menu_caller': exit_interface}
    }

    menu_loop(self, menu_options, submenu = False, recommended_actions = ['help', 'participants', 'tasks'])