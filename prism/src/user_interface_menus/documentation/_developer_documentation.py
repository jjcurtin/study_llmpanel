from user_interface_menus._menu_helper import *

def developer_documentation(self):
    def getting_started(self):
        def api_key_setup(self):
            clear()
            print("API Key Setup:")
            print("The following API keys are required to be in the api/ folder and have the described format for PRISM to function correctly:")
            print('1. qualtrics.api: "api_token","datacenter","ema_survey_id","feedback_survey_id"')
            print('2. followmee.api: "username","api_token"')
            print('3. twilio.api: "account_sid","auth_token","from_number"')
            print('4. research_drive.api: "destination_path","drive_letter","network_domain","network_username","wisc_netid","wisc_password"')
            print('5. ngrok.api: "auth_token","domain"')
            exit_menu()

        def config_setup(self):
            clear()
            print("Config Setup:")
            print("Ensure that the configuration files are set up correctly in the config/ folder.")
            print("This includes setting up the correct paths and environment variables for PRISM to function properly.")
            print('1. system_task_schedule.csv: "task_type","task_time","r_script_path","run_today"')
            print('2. study_participants.csv: "unique_id","last_name","first_name","on_study","phone_number","ema_time","ema_reminder_time","feedback_time","feedback_reminder_time"')
            print('3. study_coordinators.csv: "name","phone_number"')
            print('4. script_pipeline.csv: "script_path","arguments","enabled"')
            print('5. followmee_coords.csv (used for testing for now): DeviceName,DeviceID,Date,Latitude,Longitude,Type,Speed(mph),Speed(km/h),Direction,Altitude(ft),Altitude(m),Accuracy,Battery')
            exit_menu()

        menu_options = {
            'api': {'description': 'API Key Setup', 'menu_caller': api_key_setup},
            'config': {'description': 'Config Setup', 'menu_caller': config_setup}
        }
        while True:
            clear()
            print("=" * 60)
            print(" " * 15 + "Getting Started with PRISM")
            print("=" * 60)
            for key, item in menu_options.items():
                print(f"{key:<20}{item['description']:<20}")
            print("\nENTER: Back to Developer Documentation Menu")
            choice = input("Enter your choice: ").strip()
            selected = menu_options.get(choice)
            if selected:
                handler = selected['menu_caller']
                handler(self)
            elif choice == '':
                break
            else:
                error("Invalid choice.")

    def prism_backend_logic_documentation(self):
        clear()
        print("PRISM Backend Logic:")
        exit_menu()

    def prism_server_and_api_endpoints_documentation(self):
        clear()
        print("PRISM Server and API Endpoints:")
        exit_menu()

    def prism_user_interface_documentation(self):
        clear()
        print("PRISM User Interface:")
        exit_menu()

    def qualtrics_interface_documentation(self):
        clear()
        print("Qualtrics Interface:")
        exit_menu()

    menu_options = {
        'start': {'description': 'Getting Started', 'menu_caller': getting_started},
        'backend': {'description': 'PRISM Backend Logic', 'menu_caller': prism_backend_logic_documentation},
        'server': {'description': 'PRISM Server and API Endpoints', 'menu_caller': prism_server_and_api_endpoints_documentation},
        'ui': {'description': 'PRISM User Interface', 'menu_caller': prism_user_interface_documentation},
        'qualtrics': {'description': 'Qualtrics Interface', 'menu_caller': qualtrics_interface_documentation},
    }
    while True:
        print_menu_header("PRISM Developer Documentation")
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