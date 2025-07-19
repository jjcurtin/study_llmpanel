from user_interface_menus._menu_helper import *

def research_assistant_documentation(self):
    def getting_started(self):
        clear()
        print("Getting Started with PRISM for Research Assistants:")
        print("1. Ensure all API keys are correctly configured in the respective files.")
        print("2. Start the PRISM application using the command: python run_prism.py")
        exit_menu()

    def system_schedule_management_documentation(self):
        clear()
        print("Managing System Schedule:")
        exit_menu()

    def participant_management_documentation(self):
        clear()
        print("Managing Participants:")
        exit_menu()

    def log_viewing_documentation(self):
        clear()
        print("Viewing Logs:")
        exit_menu()

    def qualtrics_interface_documentation(self):
        clear()
        print("Qualtrics Interface:")
        exit_menu()

    menu_options = {
        '1': {'description': 'Getting Started', 'menu_caller': getting_started},
        '2': {'description': 'Managing System Schedule', 'menu_caller': system_schedule_management_documentation},
        '3': {'description': 'Managing Participants', 'menu_caller': participant_management_documentation},
        '4': {'description': 'Viewing Logs', 'menu_caller': log_viewing_documentation},
        '5': {'description': 'Qualtrics Interface', 'menu_caller': qualtrics_interface_documentation},
    }
    while True:
        print_menu_header("PRISM Research Assistant Documentation")
        for key, item in menu_options.items():
            print(f"{key:<20}{item['description']:<20}")
        print("\nENTER: Back to Help Menu")
        choice = input("Enter your choice: ").strip()
        selected = menu_options.get(choice)
        if selected:
            handler = selected['menu_caller']
            handler(self)
        elif choice == '':
            break
        else:
            error("Invalid choice.")