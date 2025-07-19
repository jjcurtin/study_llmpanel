from user_interface_menus._menu_helper import *
from user_interface_menus._system_check_menu import system_check_menu
from user_interface_menus._system_task_menu import system_task_menu
from user_interface_menus._participant_management_menus import participant_management_menu
from user_interface_menus._log_menu import log_menu
from user_interface_menus._shutdown_menu import shutdown_menu
from user_interface_menus._help_menu import help_menu

def main_menu(self):
    def exit_interface(self):
        print("Exiting PRISM Interface.")
        exit(0)

    menu_options = {
        'check': {'description': 'Get Status and Check System', 'menu_caller': system_check_menu},
        'tasks': {'description': 'Manage System Tasks and R Scripts', 'menu_caller': system_task_menu},
        'participants': {'description': 'Manage Participants', 'menu_caller': participant_management_menu},
        'logs': {'description': 'View Logs', 'menu_caller': log_menu},
        'shutdown': {'description': 'Shutdown PRISM', 'menu_caller': shutdown_menu},
        'exit': {'description': 'Exit PRISM User Interface', 'menu_caller': exit_interface},
        'help': {'description': 'Help', 'menu_caller': help_menu}
    }

    while True:
        clear()
        print("=" * 60)
        print(" " * 20 + "PRISM Interface Menu")
        print("=" * 60)
        for key, item in menu_options.items():
            print(f"{key:<20}{item['description']:<20}")
        choice = input("\nEnter your choice: ").strip()
        selected = menu_options.get(choice)
        if selected:
            handler = selected['menu_caller']
            handler(self)
        else:
            error("Invalid choice.")