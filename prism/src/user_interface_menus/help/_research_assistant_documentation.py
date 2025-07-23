from user_interface_menus._menu_helper import *

def research_assistant_documentation(self):
    def getting_started(self):
        print_menu_header("help ra start")
        print("The following API keys are required to be in the api/ folder and have the described format for PRISM to function correctly:")
        print(f'1. {green("qualtrics.api")}: "api_token","datacenter","ema_survey_id","feedback_survey_id"')
        print(f'2. {green("followmee.api")}: "username","api_token"')
        print(f'3. {green("twilio.api")}: "account_sid","auth_token","from_number"')
        print(f'4. {green("research_drive.api")}: "destination_path","drive_letter","network_domain","network_username","wisc_netid","wisc_password"')
        print(f'5. {green("ngrok.api")}: "auth_token","domain"')
        exit_menu()

    def navigation(self):
        print_menu_header("help ra navigation")
        print("Use the main menu to access different functionalities.")
        print("You can use the command 'command <query>' or '/<query>' to search for specific commands.")
        print("Most commands are globally accessible, but some are only available in specific menus.")
        exit_menu()

    def system_schedule_management_documentation(self):
        print_menu_header("help ra tasks")
        exit_menu()

    def participant_management_documentation(self):
        print_menu_header("help ra participants")
        exit_menu()

    def log_viewing_documentation(self):
        print_menu_header("help ra logs")
        exit_menu()

    def qualtrics_interface_documentation(self):
        print_menu_header("help ra qualtrics")
        exit_menu()

    menu_options = {
        'start': {'description': 'Getting Started', 'menu_caller': getting_started},
        'navigation': {'description': 'Navigating PRISM', 'menu_caller': navigation},
        'tasks': {'description': 'Managing System Task Schedule', 'menu_caller': system_schedule_management_documentation},
        'participants': {'description': 'Managing Participants', 'menu_caller': participant_management_documentation},
        'logs': {'description': 'Viewing Logs', 'menu_caller': log_viewing_documentation},
        'qualtrics': {'description': 'Qualtrics Interface', 'menu_caller': qualtrics_interface_documentation},
    }
    while True:
        print_menu_header("help ra")
        if print_menu_options(self, menu_options, submenu = True):
            break