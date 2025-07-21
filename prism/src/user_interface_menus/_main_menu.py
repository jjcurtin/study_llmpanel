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
    def exit_interface(self):
        print("Exiting PRISM Interface.")
        exit(0)

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
        print_menu_header("PRISM Interface Menu")
        print_menu_options(self, menu_options)

def read_me(self):
    print_menu_header("PRISM User Interface Readme")
    print("Welcome to the PRISM User Interface!")
    print("This interface allows you to manage and interact with the PRISM system.")
    print("Use the following commands to navigate:")
    print("- 'help': Access help documentation.")
    print("- 'command': View global command menu.")
    print("- 'assistant': Interact with the PRISM Assistant.")
    print("- 'check': Perform system status checks and diagnostics.")
    print("- 'tasks': Manage system tasks and R scripts.")
    print("- 'participants': Manage study participants.")
    print("- 'logs': View system logs.")
    print("- 'settings': Adjust system settings.")
    print("- 'shutdown': Safely shutdown the PRISM system.")
    print("- 'exit': Exit the PRISM User Interface.\n")
    
    input("Press Enter to return to the main menu...")

global README
README = read_me