from user_interface_menus._menu_helper import *
from user_interface_menus.help_menu._developer_documentation import developer_documentation
from user_interface_menus.help_menu._research_assistant_documentation import research_assistant_documentation

def help_menu(self):
    menu_options = {
        'general': {'description': 'General Information', 'menu_caller': general_information},
        'ra': {'description': 'Research Assistant Documentation', 'menu_caller': research_assistant_documentation},
        'dev': {'description': 'Developer Documentation', 'menu_caller': developer_documentation}
    }

    while True:
        print_menu_header("help")
        if print_menu_options(self, menu_options, submenu = True):
            break

def general_information(self):
        from user_interface_menus._menu_helper import COLOR_ON
        print_menu_header("help general")
        print("This application is designed to manage and monitor participants in a study.")
        print("It includes features for system checks, task management, participant management, and logging.")
        print("It is designed to incorporate data collection, data processing, and communication with participants in a single system.")
        
        if COLOR_ON:
            print("\nTo see a list of user interface commands, type \033[33mcommand\033[0m.")
        else:
            print("\nTo see a list of user interface commands, type 'command'.")
        print("\nFor more detailed information, please refer to the appropriate documentation.")
        exit_menu()

global GENERAL_INFORMATION
GENERAL_INFORMATION = general_information