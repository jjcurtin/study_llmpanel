from _helper import clear

from user_interface_menus._menu_helper import error, success, exit_menu
from user_interface_menus._system_check_menu import system_check_menu
from user_interface_menus._system_task_menu import system_task_menu
from user_interface_menus._participant_management_menus import participant_management_menu
from user_interface_menus._log_menu import log_menu
from user_interface_menus._shutdown_menu import shutdown_menu

def main_menu(self):
    def exit_interface(self):
        print("Exiting PRISM Interface.")
        exit(0)

    menu_options = {
        '1': {'description': 'Get Status and Check System', 'menu_caller': system_check_menu},
        '2': {'description': 'Manage System Tasks and R Scripts', 'menu_caller': system_task_menu},
        '3': {'description': 'Manage Participants', 'menu_caller': participant_management_menu},
        '4': {'description': 'View Logs', 'menu_caller': log_menu},
        '5': {'description': 'Shutdown PRISM', 'menu_caller': shutdown_menu},
        '6': {'description': 'Exit', 'menu_caller': exit_interface}
    }

    while True:
        clear()
        print("PRISM Interface Menu:")
        for key, item in menu_options.items():
            print(f"{key}: {item['description']}")
        choice = input("Enter your choice: ").strip()
        selected = menu_options.get(choice)
        if selected:
            handler = selected['menu_caller']
            handler(self)
        else:
            error("Invalid choice.")