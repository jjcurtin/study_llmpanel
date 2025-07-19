from user_interface_menus._menu_helper import *
from user_interface_menus.documentation._developer_documentation import developer_documentation
from user_interface_menus.documentation._research_assistant_documentation import research_assistant_documentation

def help_menu(self):
    def general_information(self):
        clear()
        print("General Information:")
        print("This application is designed to manage and monitor participants in a study.")
        print("It includes features for system checks, task management, participant management, and logging.")
        print("It is designed to incorporate data collection, data processing, and communication with participants in a single system.")
        print("\nFor more detailed information, please refer to the appropriate documentation.")
        exit_menu()

    menu_options = {
        'general': {'description': 'General Information', 'menu_caller': general_information},
        'ra': {'description': 'Research Assistant Documentation', 'menu_caller': research_assistant_documentation},
        'dev': {'description': 'Developer Documentation', 'menu_caller': developer_documentation}
    }

    while True:
        print_menu_header("PRISM Help Menu")
        for key, item in menu_options.items():
            print(f"{key:<20}{item['description']:<20}")
        print("\nENTER: Back to Main Menu")
        choice = input("Enter your choice: ").strip()
        selected = menu_options.get(choice)
        if selected:
            handler = selected['menu_caller']
            handler(self)
        elif choice == '':
            break
        else:
            error("Invalid choice.")