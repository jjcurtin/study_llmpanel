# dev docs

from user_interface_menus._menu_helper import *

def developer_documentation(self):
    def getting_started(self):
        def api_key_setup(self):
            infopage(self, content = [
                f"The following API keys are required to be in the api/ folder and have the described format for PRISM to function correctly:",
                f'1. {green("qualtrics.api")}: "api_token","datacenter","ema_survey_id","feedback_survey_id"',
                f'2. {green("followmee.api")}: "username","api_token"',
                f'3. {green("twilio.api")}: "account_sid","auth_token","from_number"',
                f'4. {green("research_drive.api")}: "destination_path","drive_letter","network_domain","network_username","wisc_netid","wisc_password"',
                f'5. {green("ngrok.api")}: "auth_token","domain"'
            ], title = "help dev start api")

        def config_setup(self):
            infopage(self, content = [
                f"Ensure that the configuration files are set up correctly in the config/ folder.",
                f"This includes setting up the correct paths and environment variables for PRISM to function properly.",
                f'1. {green("system_task_schedule.csv")}: "task_type","task_time","r_script_path","run_today"',
                f'2. {green("study_participants.csv")}: "unique_id","last_name","first_name","on_study","phone_number","ema_time","ema_reminder_time","feedback_time","feedback_reminder_time"',
                f'3. {green("study_coordinators.csv")}: "name","phone_number"',
                f'4. {green("script_pipeline.csv")}: "script_path","arguments","enabled"',
                f'5. {green("followmee_coords.csv")}: (used for testing for now): DeviceName,DeviceID,Date,Latitude,Longitude,Type,Speed(mph),Speed(km/h),Direction,Altitude(ft),Altitude(m),Accuracy,Battery'
            ], title = "help dev start config")

        menu_options = {
            'api': {'description': 'API Key Setup', 'menu_caller': api_key_setup},
            'config': {'description': 'Config Setup', 'menu_caller': config_setup}
        }
        while True:
            if not self.commands_queue:
                print_menu_header("help dev start")
            if print_menu_options(self, menu_options, submenu = True):
                break

    def prism_backend_logic_documentation(self):
        def task_abstraction_format(self):
            infopage(self, content = [
                f"PRISM uses a task abstraction format to manage and execute tasks.",
                f"Each task is defined by its type, time, and optional R script path.",
                f"Tasks can be scheduled to run at specific times or executed immediately.",
                f"The task types are defined in the {green('system_tasks/')} folder and must follow these rules:",
                f"1. Task files must be all lowercase, named with a leading underscore, words separated by an underscore, and have a {green('.py')} extension.",
                f"2. Each task must inherit from the SystemTask class and implement the run method.",
                f"3. The run method must set `self.task_type` to the task type and return 0 for success or a non-zero value for failure.",
                f"\nExample task file name: {green('_example_task.py')}",
                f"Example task class name: ExampleTask",
                f"Example task type: EXAMPLE_TASK",
                f"\nExample run method:\ndef run(self):\n\tself.task_type = 'EXAMPLE_TASK'\n\treturn 0  # Return 0 for success, non-zero for failure",
                f"\nThis format allows for dynamic loading and execution of tasks, enabling PRISM to adapt to new tasks without requiring a restart.",
                f"The task manager will automatically load all tasks from the {green('system_tasks/')} folder and make them available for scheduling and execution.",
                f"This allows for easy extension of PRISM's functionality by simply adding new task files.",
                f"The task manager also provides methods to add, remove, and execute tasks, as well as to retrieve the current task schedule.",
            ], title = "help dev backend tasks")

        def task_managers(self):
            infopage(self, content = [
                f"PRISM uses task managers to handle the scheduling and execution of tasks.",
                f"The TaskManager class is the base class for all task managers in PRISM.",
                f"It provides common functionality for managing tasks, such as the task scheduling logic, task queue, and thread setup.",
                f"Subclasses of TaskManager, such as SystemTaskManager and ParticipantManager, implement specific task management logic but can provide their own methods for added flexibility.",
                f"\nThe SystemTaskManager is responsible for managing system tasks, which include scheduled tasks and R script tasks.",
                f"It loads the task types from the {green('system_tasks/')} folder and the R script tasks from the {green('scripts/')} folder.",
                f"The SystemTaskManager provides methods to add, remove, and execute tasks, as well as to retrieve the current task schedule.",
                f"It also provides methods to clear the task schedule and to load the task schedule from the {green('system_task_schedule.csv')} file.",
                f"The task schedule is stored in a CSV file, which allows for easy editing and management of scheduled tasks.",
                f"\nThe ParticipantManager is responsible for managing participants in the study.",
                f"It provides methods to add, remove, and update participants, as well as to retrieve the current participant list.",
                f"The ParticipantManager also provides methods to load and save the participant list from the {green('study_participants.csv')} file.",
                f"This allows for easy management of participants and their data, enabling PRISM to adapt to changes in the study participants without requiring a restart."
            ], title = "help dev backend task_managers")
        
        def check_system(self):
            infopage(self, content = [
                f"PRISM includes a system check feature that verifies the status of the application and its components.",
                f"This includes checking packages, the directory structure, required files, testing API connectivity, and some additional participant information fidelity logic.",
                f"The system check is performed by the SystemCheck class, which provides methods to check the status of various components of PRISM.",
                f"The system check can be run from the command line or from the user interface.",
                f"\nThe system check performs the following checks:",
                f"1. Checks if all required packages are installed and up to date.",
                f"2. Checks if the directory structure is correct and all required files are present.",
                f"3. Tests API connectivity to ensure that PRISM can communicate with external services.",
                f"4. Performs additional checks on participant information to ensure data integrity.",
                f"\nThe results of the system check are displayed in the user interface or printed to the console, allowing for easy identification of any issues that need to be addressed."
            ], title = "help dev backend check")
            
        def data_management(self):
            infopage(self, content = [
                f"PRISM supports data pull down from various sources, including Qualtrics and FollowMee.",
                f"The data pull down feature allows PRISM to retrieve data from these sources and store it in the appropriate format for further processing.",
                f"Data is output to the {green('../data/')} directory after pulldown and processing.",
                f"PRISM also supports mapping and pushing data to the Research Drive, which allows for easy access and secure management of study data.",
                f"\nThe data management system is designed to be flexible and extensible, allowing for easy integration of new data sources and formats.",
                f"The data management system provides methods to pull down data from external sources, process it, and store it in the appropriate format for further analysis.",
                f"This allows PRISM to adapt to changes in the study data without requiring a restart."
            ], title = "help dev backend data_management")
            
        menu_options = {
            'task_abstraction': {'description': 'Task Abstraction Format', 'menu_caller': lambda self: task_abstraction_format(self)},
            'task_managers': {'description': 'Task Managers', 'menu_caller': lambda self: task_managers(self)},
            'check_system': {'description': 'Check System', 'menu_caller': lambda self: check_system(self)},
            'data_management': {'description': 'Data Management', 'menu_caller': lambda self: data_management(self)}
        }
        while True:
            if not self.commands_queue:
                print_menu_header("help dev backend")
            if print_menu_options(self, menu_options, submenu = True, recommended_actions = ['tasks']):
                break

    def prism_server_and_api_endpoints_documentation(self):
        def system_endpoints(self):
            infopage(self, content = [
                f"PRISM runs a Flask server served with Waitress with localhost tunneling through ngrok.",
                f"The server provides endpoints for system purposes and Qualtrics integration.",
                f"The following endpoints are available for system management:",
                f"1. GET /system/get_mode - Returns the current mode of the application.",
                f"2. GET /system/uptime - Returns the uptime of the application.",
                f"3. GET /system/get_transcript/<num_lines> - Retrieves the last <num_lines> lines of the system transcript.",
                f"4. GET /system/get_ema_log/<num_lines> - Retrieves the last <num_lines> lines of the EMA log.",
                f"5. GET /system/get_feedback_log/<num_lines> - Retrieves the last <num_lines> lines of the feedback log.",
                f"6. POST /system/shutdown - Initiates a system shutdown.",
                f"7. GET /system/get_task_schedule - Retrieves the current system task schedule.",
                f"8. GET /system/get_task_types - Retrieves the available task types.",
                f"9. GET /system/get_r_script_tasks - Retrieves the R script tasks.",
                f"10. POST /system/add_system_task/<task_type>/<task_time> - Adds a system task.",
                f"11. DELETE /system/remove_system_task/<task_type>/<task_time> - Removes a system task.",
                f"12. DELETE /system/clear_task_schedule - Clears the task schedule.",
                f"13. POST /system/execute_task/<task_type> - Executes a specific task.",
                f"14. POST /system/add_r_script_task/<r_script_path>/<task_time> - Adds an R script task.",
                f"15. DELETE /system/remove_r_script_task/<r_script_path>/<task_time> - Removes an R script task.",
                f"16. POST /system/execute_r_script_task/<r_script_path> - Executes an R script task."
            ], title = "help dev server system")

        def participant_endpoints(self):
            infopage(self, content = [
                f"PRISM provides endpoints for managing participants in a study.",
                f"The following endpoints are available for participant management:",
                f"1. GET /participants/get_participants - Retrieves the list of participants.",
                f"2. GET /participants/get_participant_task_schedule - Retrieves the participant task schedule.",
                f"3. POST /participants/refresh_participants - Refreshes the participant list.",
                f"4. GET /participants/get_participant/<unique_id> - Retrieves information about a specific participant.",
                f"5. POST /participants/add_participant - Adds a new participant.",
                f"6. DELETE /participants/remove_participant/<unique_id> - Removes a participant.",
                f"7. PUT /participants/update_participant/<unique_id>/<field>/<new_value> - Updates a participant's information.",
                f"8. POST /participants/send_survey/<unique_id>/<survey_type> - Sends a survey to a participant.",
                f"9. POST /participants/send_custom_sms/<unique_id> - Sends a custom SMS to a participant.",
                f"10. POST /participants/study_announcement/<require_on_study> - Sends a study announcement to participants."
            ], title = "help dev server participants")

        def qualtrics_endpoints(self):
            infopage(self, content = [
                f"PRISM integrates with Qualtrics for survey management.",
                f"The following endpoints are available for Qualtrics integration:",
                f"1. GET /qualtrics/access_ema/<unique_id> - Provides access to the EMA survey for a participant.",
                f"2. GET /qualtrics/request_coords/<unique_id> - Requests the coordinates of a participant.",
                f"3. POST /qualtrics/submit_ema - Submits the EMA survey.",
                f"4. GET /qualtrics/access_feedback/<unique_id> - Provides access to the feedback survey for a participant.",
                f"5. POST /qualtrics/submit_feedback - Submits the feedback survey."
            ], title = "help dev server qualtrics")

        menu_options = {
            'system_endpoints': {'description': 'System Endpoints', 'menu_caller': system_endpoints},
            'participant_endpoints': {'description': 'Participant Endpoints', 'menu_caller': participant_endpoints},
            'qualtrics_endpoints': {'description': 'Qualtrics Endpoints', 'menu_caller': qualtrics_endpoints}
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
        infopage(self, content = [
            f"PRISM's user interface is designed to provide easy access to the application's features.",
            f"When PRISM is running, the user interface can also be run from the command line by executing the {green('prism_interface.py')} file.",
            f"The user interface communicates over localhost with the PRISM server (see server documentation).",
            f"\nThe {green('prism_interface.py')} is the main entry point for the user interface.",
            f"The code for this lies in the {green('user_interface_menus/')} folder.",
            f"\nThe {green('user_interface_menus/documentation/')} folder contains the documentation for the application (which is where the content you are viewing is loaded from)."
        ], title = "help dev ui")

    def qualtrics_interface_documentation(self):
        infopage(self, content = [
            f"The Qualtrics interface is used to manage and interact with Qualtrics surveys.",
            f"The code that I have written for Qualtrics is in the {green('../qualtrics_js/')} folder.",
            f"Each script must be added to the appropriate survey question in the desired Qualtrics survey.",
            f"Note: there are additional survey requirements for the Qualtrics interface to work correctly (e.g. layout and question types).",
            f"Additionally, the interface requires PRISM to be running."
        ], title = "help dev qualtrics")

    def architecture_overview(self):
        infopage(self, content = [
            f"PRISM is designed with many components that work together.",
            f"\nThere is the backend which is initiated by the {green('run_prism.py')} file.",
            f"The backend is responsible for managing the system, tasks, participants, and data.",
            f"The backend communicates with the other components through a web server using Flask (check out {green('routes.py')}).",
            f"The code for this lies in the {green('system_tasks/')} and {green('task_managers/')} folders and {green('_helper.py')} and {green('_routes.py')}.",
            f"\nThere is also this user interface, which is initiated by the {green('prism_interface.py')} file.",
            f"The code for this lies in the {green('user_interface_menus/')} folder.",
            f"\nThere is also a Qualtrics interface, which the code for is in the {green('qualtrics_js/')} folder.",
            f"There are a few things that need to be set up in Qualtrics for this to work (namely the right question/survey setup).",
            f"\nFeel free to contact me directly for any questions.",
            f"The {yellow('assistant')} may also be able to help with some questions."
        ], title = "help dev architecture")

    menu_options = {
        'start': {'description': 'Getting Started', 'menu_caller': getting_started},
        'architecture': {'description': 'PRISM Architecture Overview', 'menu_caller': architecture_overview},
        'backend': {'description': 'PRISM Backend Logic', 'menu_caller': prism_backend_logic_documentation},
        'server': {'description': 'PRISM Server and API Endpoints', 'menu_caller': prism_server_and_api_endpoints_documentation},
        'ui': {'description': 'PRISM User Interface', 'menu_caller': prism_user_interface_documentation},
        'qualtrics': {'description': 'Qualtrics Interface', 'menu_caller': qualtrics_interface_documentation},
    }
    while True:
        if not self.commands_queue:
            print_menu_header("help dev")
        if print_menu_options(self, menu_options, submenu = True, recommended_actions = ['start']):
            break