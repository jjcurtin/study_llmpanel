# dev docs

from user_interface_menus._menu_helper import *

def developer_documentation(self):
    def getting_started(self):
        def api_key_setup(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev start api")
                print("The following API keys are required to be in the api/ folder and have the described format for PRISM to function correctly:")
                print(f'1. {green("qualtrics.api")}: "api_token","datacenter","ema_survey_id","feedback_survey_id"')
                print(f'2. {green("followmee.api")}: "username","api_token"')
                print(f'3. {green("twilio.api")}: "account_sid","auth_token","from_number"')
                print(f'4. {green("research_drive.api")}: "destination_path","drive_letter","network_domain","network_username","wisc_netid","wisc_password"')
                print(f'5. {green("ngrok.api")}: "auth_token","domain"')
                exit_menu()

        def config_setup(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev start config")
                print("Ensure that the configuration files are set up correctly in the config/ folder.")
                print("This includes setting up the correct paths and environment variables for PRISM to function properly.")
                print(f'1. {green("system_task_schedule.csv")}: "task_type","task_time","r_script_path","run_today"')
                print(f'2. {green("study_participants.csv")}: "unique_id","last_name","first_name","on_study","phone_number","ema_time","ema_reminder_time","feedback_time","feedback_reminder_time"')
                print(f'3. {green("study_coordinators.csv")}: "name","phone_number"')
                print(f'4. {green("script_pipeline.csv")}: "script_path","arguments","enabled"')
                print(f'5. {green("followmee_coords.csv")}: (used for testing for now): DeviceName,DeviceID,Date,Latitude,Longitude,Type,Speed(mph),Speed(km/h),Direction,Altitude(ft),Altitude(m),Accuracy,Battery')
                exit_menu()

        menu_options = {
            'api': {'description': 'API Key Setup', 'menu_caller': api_key_setup},
            'config': {'description': 'Config Setup', 'menu_caller': config_setup}
        }
        while True:
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev start")
            if print_menu_options(self, menu_options, submenu = True):
                break

    def prism_backend_logic_documentation(self):
        def task_abstraction_format(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev backend tasks")
                print("PRISM uses a task abstraction format to manage and execute tasks.")
                print("Each task is defined by its type, time, and optional R script path.")
                print("Tasks can be scheduled to run at specific times or executed immediately.")
                print(f"The task types are defined in the {green('system_tasks/')} folder and must follow these rules:")
                print(f"1. Task files must be all lowercase, named with a leading underscore, words separated by an underscore, and have a {green('.py')} extension.")
                print("2. Each task must inherit from the SystemTask class and implement the run method.")
                print("3. The run method must set `self.task_type` to the task type and return 0 for success or a non-zero value for failure.")
                print()
                print(f"Example task file name: {green('_example_task.py')}")
                print("Example task class name: ExampleTask")
                print("Example task type: EXAMPLE_TASK")
                print()
                print("Example run method:")
                print('''def run(self):\n\tself.task_type = "EXAMPLE_TASK"\n\treturn 0  # Return 0 for success, non-zero for failure''')
                print()
                print("This format allows for dynamic loading and execution of tasks, enabling PRISM to adapt to new tasks without requiring a restart.")
                print(f"The task manager will automatically load all tasks from the {green('system_tasks/')} folder and make them available for scheduling and execution.")
                print("This allows for easy extension of PRISM's functionality by simply adding new task files.")
                print("The task manager also provides methods to add, remove, and execute tasks, as well as to retrieve the current task schedule.")
                print()
                print("To run R Scripts as a task, PRISM uses the RunRScript class, which inherits from SystemTask.")
                print("This class handles changing directories, running the R script using subprocess, and managing the task lifecycle.")
                print(f"The R script path is specified when creating the RunRScript task, and the task will execute the script in the {green('scripts/')} directory.")
                print(f"To allow PRISM to run R scripts, ensure that the Rscript command is available in your system's PATH and that all R scripts are placed in the {green('../../scripts')} directory.")
                exit_menu()

        def task_managers(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev backend task_managers")
                print("PRISM uses task managers to handle the scheduling and execution of tasks.")
                print("The TaskManager class is the base class for all task managers in PRISM.")
                print("It provides common functionality for managing tasks, such as the task scheduling logic, task queue, and thread setup.")
                print("Subclasses of TaskManager, such as SystemTaskManager and ParticipantManager, implement specific task management logic but can provide their own methods for added flexibility.")
                print()
                print("The SystemTaskManager is responsible for managing system tasks, which include scheduled tasks and R script tasks.")
                print(f"It loads the task types from the {green('system_tasks/')} folder and the R script tasks from the {green('scripts/')} folder.")
                print("The SystemTaskManager provides methods to add, remove, and execute tasks, as well as to retrieve the current task schedule.")
                print(f"It also provides methods to clear the task schedule and to load the task schedule from the {green('system_task_schedule.csv')} file.")
                print("The task schedule is stored in a CSV file, which allows for easy editing and management of scheduled tasks.")
                print()
                print("The ParticipantManager is responsible for managing participants in the study.")
                print("It provides methods to add, remove, and update participants, as well as to retrieve the current participant list.")
                print(f"The ParticipantManager also provides methods to load and save the participant list from the {green('study_participants.csv')} file.")
                print("This allows for easy management of participants and their data, enabling PRISM to adapt to changes in the study participants without requiring a restart.")
                exit_menu()
        
        def check_system(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev backend check")
                print("PRISM includes a system check feature that verifies the status of the application and its components.")
                print("This includes checking packages, the directory structure, required files, testing API connectivity, and some additional participant information fidelity logic.")
                exit_menu()
            
        def data_management(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev backend data_management")
                print("PRISM supports data pull down from various sources, including Qualtrics and FollowMee.")
                print("The data pull down feature allows PRISM to retrieve data from these sources and store it in the appropriate format for further processing.")
                print("Data is output to the ../data/ directory after pulldown and processing.")
                print("PRISM also supports mapping and pushing data to the Research Drive, which allows for easy access and secure management of study data.")
                exit_menu()
            
        menu_options = {
            'tasks': {'description': 'Task Abstraction Format', 'menu_caller': lambda self: task_abstraction_format(self)},
            'task_managers': {'description': 'Task Managers', 'menu_caller': lambda self: task_managers(self)},
            'check': {'description': 'Check System', 'menu_caller': lambda self: check_system(self)},
            'data_management': {'description': 'Data Management', 'menu_caller': lambda self: data_management(self)}
        }
        while True:
            set_recommended_actions([
                'tasks'
            ])
            if not self.commands_queue:
                print_menu_header("help dev backend")
            if print_menu_options(self, menu_options, submenu = True):
                break

    def prism_server_and_api_endpoints_documentation(self):
        def system_endpoints(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev server system")
                print("1. GET /system/get_mode - Returns the current mode of the application.")
                print("2. GET /system/uptime - Returns the uptime of the application.")
                print("3. GET /system/get_transcript/<num_lines> - Retrieves the last <num_lines> lines of the system transcript.")
                print("4. GET /system/get_ema_log/<num_lines> - Retrieves the last <num_lines> lines of the EMA log.")
                print("5. GET /system/get_feedback_log/<num_lines> - Retrieves the last <num_lines> lines of the feedback log.")
                print("6. POST /system/shutdown - Initiates a system shutdown.")
                print("7. GET /system/get_task_schedule - Retrieves the current system task schedule.")
                print("8. GET /system/get_task_types - Retrieves the available task types.")
                print("9. GET /system/get_r_script_tasks - Retrieves the R script tasks.")
                print("10. POST /system/add_system_task/<task_type>/<task_time> - Adds a system task.")
                print("11. DELETE /system/remove_system_task/<task_type>/<task_time> - Removes a system task.")
                print("12. DELETE /system/clear_task_schedule - Clears the task schedule.")
                print("13. POST /system/execute_task/<task_type> - Executes a specific task.")
                print("14. POST /system/add_r_script_task/<r_script_path>/<task_time> - Adds an R script task.")
                print("15. DELETE /system/remove_r_script_task/<r_script_path>/<task_time> - Removes an R script task.")
                print("16. POST /system/execute_r_script_task/<r_script_path> - Executes an R script task.")
                exit_menu()

        def participant_endpoints(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev server participants")
                print("1. GET /participants/get_participants - Retrieves the list of participants.")
                print("2. GET /participants/get_participant_task_schedule - Retrieves the participant task schedule.")
                print("3. POST /participants/refresh_participants - Refreshes the participant list.")
                print("4. GET /participants/get_participant/<unique_id> - Retrieves information about a specific participant.")
                print("5. POST /participants/add_participant - Adds a new participant.")
                print("6. DELETE /participants/remove_participant/<unique_id> - Removes a participant.")
                print("7. PUT /participants/update_participant/<unique_id>/<field>/<new_value> - Updates a participant's information.")
                print("8. POST /participants/send_survey/<unique_id>/<survey_type> - Sends a survey to a participant.")
                print("9. POST /participants/send_custom_sms/<unique_id> - Sends a custom SMS to a participant.")
                print("10. POST /participants/study_announcement/<require_on_study> - Sends a study announcement to participants.")
                exit_menu()

        def qualtrics_endpoints(self):
            clear_recommended_actions()
            if not self.commands_queue:
                print_menu_header("help dev server qualtrics")
                print("1. GET /qualtrics/access_ema/<unique_id> - Provides access to the EMA survey for a participant.")
                print("2. GET /qualtrics/request_coords/<unique_id> - Requests the coordinates of a participant.")
                print("3. POST /qualtrics/submit_ema - Submits the EMA survey.")
                print("4. GET /qualtrics/access_feedback/<unique_id> - Provides access to the feedback survey for a participant.")
                print("5. POST /qualtrics/submit_feedback - Submits the feedback survey.")
                exit_menu()

        clear_recommended_actions()
        menu_options = {
            'system': {'description': 'System Endpoints', 'menu_caller': system_endpoints},
            'participants': {'description': 'Participant Endpoints', 'menu_caller': participant_endpoints},
            'qualtrics': {'description': 'Qualtrics Endpoints', 'menu_caller': qualtrics_endpoints}
        }
        while True:
            if not self.commands_queue:
                print_menu_header("PRISM Server and API Endpoints")
            print("PRISM runs a Flask server served with Waitress with localhost tunneling through ngrok.")
            print("PRISM has endpoints for system purposes and Qualtrics integration.")
            print("Below is the documentation for the available endpoints:")
            print()
            if print_menu_options(self, menu_options, submenu = True):
                break

    def prism_user_interface_documentation(self):
        clear_recommended_actions()
        if not self.commands_queue:
            print_menu_header("help dev ui")
            print("The PRISM user interface is designed to provide easy access to the application's features.")
            print("When PRISM is running, the user interface can also be run from the command line by executing the prism_interface.py file.")
            print("The user interface communicates over localhost with the PRISM server (see server documentation).")
            print()
            print("prism_interface.py is the main entry point for the user interface.")
            print("user_interface_menus/ contains the various menus for the application.")
            print("user_interface_menus/documentation/ contains the documentation for the application (which is where the content you are viewing is loaded from).")
            exit_menu()

    def qualtrics_interface_documentation(self):
        clear_recommended_actions()
        if not self.commands_queue:
            print_menu_header("help dev qualtrics")
            print("The Qualtrics interface is used to manage and interact with Qualtrics surveys.")
            print("The code that I have written for Qualtrics is in the ../qualtrics_js folder.")
            print("Each script must be added to the appropriate survey question in the desired Qualtrics survey.")
            print("Note: there are additional survey requirements for the Qualtrics interface to work correctly (e.g. layout and question types).")
            print("Additionally, the interface requires PRISM to be running.")
            exit_menu()

    def architecture_overview(self):
        clear_recommended_actions()
        if not self.commands_queue:
            print_menu_header("help dev architecture")
            print(f"PRISM is designed with many components that work together.")
            print(f"\nThere is the backend which is initiated by the {green('run_prism.py')} file.")
            print(f"The backend is responsible for managing the system, tasks, participants, and data.")
            print(f"The backend communicates with the other components through a web server using Flask (check out {green('routes.py')}).")
            print(f"The code for this lies in the {green('system_tasks/')} and {green('task_managers/')} folders and {green('_helper.py')} and {green('_routes.py')}.")
            print(f"\nThere is also this user interface, which is initiated by the {green('prism_interface.py')} file.")
            print(f"The code for this lies in the {green('user_interface_menus/')} folder.")
            print(f"\nThere is also a Qualtrics interface, which the code for is in the {green('qualtrics_js/')} folder.")
            print(f"There are a few things that need to be set up in Qualtrics for this to work (namely the right question/survey setup).")
            print(f"\nFeel free to contact me directly for any questions.")
            print(f"The {yellow('assistant')} may also be able to help with some questions.")
            exit_menu()

    menu_options = {
        'start': {'description': 'Getting Started', 'menu_caller': getting_started},
        'architecture': {'description': 'PRISM Architecture Overview', 'menu_caller': architecture_overview},
        'backend': {'description': 'PRISM Backend Logic', 'menu_caller': prism_backend_logic_documentation},
        'server': {'description': 'PRISM Server and API Endpoints', 'menu_caller': prism_server_and_api_endpoints_documentation},
        'ui': {'description': 'PRISM User Interface', 'menu_caller': prism_user_interface_documentation},
        'qualtrics': {'description': 'Qualtrics Interface', 'menu_caller': qualtrics_interface_documentation},
    }
    while True:
        set_recommended_actions([
            'start'
        ])
        if not self.commands_queue:
            print_menu_header("help dev")
        if print_menu_options(self, menu_options, submenu = True):
            break