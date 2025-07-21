from user_interface_menus._menu_helper import *

def research_assistant_documentation(self):
    def getting_started(self):
        print_menu_header("Getting Started with PRISM for Research Assistants")
        print("1. Ensure all API keys are correctly configured in the respective files.")
        print("2. Start the PRISM application using the command: python run_prism.py")
        exit_menu()

    def system_schedule_management_documentation(self):
        print_menu_header("Managing System Schedule:")
        exit_menu()

    def participant_management_documentation(self):
        print_menu_header("Managing Participants")
        exit_menu()

    def log_viewing_documentation(self):
        print_menu_header("Viewing Logs")
        exit_menu()

    def qualtrics_interface_documentation(self):
        print_menu_header("Qualtrics Interface")
        exit_menu()

    menu_options = {
        'start': {'description': 'Getting Started', 'menu_caller': getting_started},
        'tasks': {'description': 'Managing System Task Schedule', 'menu_caller': system_schedule_management_documentation},
        'participants': {'description': 'Managing Participants', 'menu_caller': participant_management_documentation},
        'logs': {'description': 'Viewing Logs', 'menu_caller': log_viewing_documentation},
        'qualtrics': {'description': 'Qualtrics Interface', 'menu_caller': qualtrics_interface_documentation},
    }
    while True:
        print_menu_header("PRISM Research Assistant Documentation")
        if print_menu_options(self, menu_options, submenu = True):
            break