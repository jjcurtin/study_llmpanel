from user_interface_menus._menu_helper import *

def developer_documentation(self):
    def getting_started(self):
        def api_key_setup(self):
            print_menu_header("API Key Setup")
            print("The following API keys are required to be in the api/ folder and have the described format for PRISM to function correctly:")
            print('1. qualtrics.api: "api_token","datacenter","ema_survey_id","feedback_survey_id"')
            print('2. followmee.api: "username","api_token"')
            print('3. twilio.api: "account_sid","auth_token","from_number"')
            print('4. research_drive.api: "destination_path","drive_letter","network_domain","network_username","wisc_netid","wisc_password"')
            print('5. ngrok.api: "auth_token","domain"')
            exit_menu()

        def config_setup(self):
            print_menu_header("Config Setup")
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
            print_menu_header("Getting Started with PRISM")
            if print_menu_options(self, menu_options, submenu = True):
                break

    def prism_backend_logic_documentation(self):
        def task_abstraction_format(self):
            print_menu_header("Task Abstraction Format")
            print("PRISM uses a task abstraction format to manage and execute tasks.")
            print("Each task is defined by its type, time, and optional R script path.")
            print("Tasks can be scheduled to run at specific times or executed immediately.")
            print("The task types are defined in the system_tasks/ folder and must follow these rules:")
            print("1. Task files must be all lowercase, named with a leading underscore, words separated by an underscore, and have a .py extension.")
            print("2. Each task must inherit from the SystemTask class and implement the run method.")
            print("3. The run method must set `self.task_type` to the task type and return 0 for success or a non-zero value for failure.")
            print()
            print("Example task file name: _example_task.py")
            print("Example task class name: ExampleTask")
            print("Example task type: EXAMPLE_TASK")
            print()
            print("Example run method:")
            print('''def run(self):\n\tself.task_type = "EXAMPLE_TASK"\n\treturn 0  # Return 0 for success, non-zero for failure''')
            print()
            print("This format allows for dynamic loading and execution of tasks, enabling PRISM to adapt to new tasks without requiring a restart.")
            print("The task manager will automatically load all tasks from the system_tasks/ folder and make them available for scheduling and execution.")
            print("This allows for easy extension of PRISM's functionality by simply adding new task files.")
            print("The task manager also provides methods to add, remove, and execute tasks, as well as to retrieve the current task schedule.")
            print()
            print("To run R Scripts as a task, PRISM uses the RunRScript class, which inherits from SystemTask.")
            print("This class handles changing directories, running the R script using subprocess, and managing the task lifecycle.")
            print("The R script path is specified when creating the RunRScript task, and the task will execute the script in the scripts/ directory.")
            print("To allow PRISM to run R scripts, ensure that the Rscript command is available in your system's PATH and that all R scripts are placed in the ../../scripts directory.")
            exit_menu()

        def task_managers(self):
            print_menu_header("Task Managers")
            print("PRISM uses task managers to handle the scheduling and execution of tasks.")
            print("The TaskManager class is the base class for all task managers in PRISM.")
            print("It provides common functionality for managing tasks, such as the task scheduling logic, task queue, and thread setup.")
            print("Subclasses of TaskManager, such as SystemTaskManager and ParticipantManager, implement specific task management logic but can provide their own methods for added flexibility.")
            print()
            print("The SystemTaskManager is responsible for managing system tasks, which include scheduled tasks and R script tasks.")
            print("It loads the task types from the system_tasks/ folder and the R script tasks from the scripts/ folder.")
            print("The SystemTaskManager provides methods to add, remove, and execute tasks, as well as to retrieve the current task schedule.")
            print("It also provides methods to clear the task schedule and to load the task schedule from the system_task_schedule.csv file.")
            print("The task schedule is stored in a CSV file, which allows for easy editing and management of scheduled tasks.")
            print()
            print("The ParticipantManager is responsible for managing participants in the study.")
            print("It provides methods to add, remove, and update participants, as well as to retrieve the current participant list.")
            print("The ParticipantManager also provides methods to load and save the participant list from the study_participants.csv file.")
            print("This allows for easy management of participants and their data, enabling PRISM to adapt to changes in the study participants without requiring a restart.")
            exit_menu()
        
        def check_system(self):
            print_menu_header("Check System")
            print("PRISM includes a system check feature that verifies the status of the application and its components.")
            print("This includes checking packages, the directory structure, required files, testing API connectivity, and some additional participant information fidelity logic.")
            exit_menu()
        
        def data_management(self):
            print_menu_header("Data Management")
            print("PRISM supports data pull down from various sources, including Qualtrics and FollowMee.")
            print("The data pull down feature allows PRISM to retrieve data from these sources and store it in the appropriate format for further processing.")
            print("Data is output to the ../data/ directory after pulldown and processing.")
            print("PRISM also supports mapping and pushing data to the Research Drive, which allows for easy access and secure management of study data.")
            exit_menu()
            
        menu_options = {
            'tasks': {'description': 'Task Abstraction Format', 'menu_caller': lambda self: task_abstraction_format(self)},
            'task_managers': {'description': 'Task Managers', 'menu_caller': lambda self: task_managers(self)},
            'check_system': {'description': 'Check System', 'menu_caller': lambda self: check_system(self)},
            'data_management': {'description': 'Data Management', 'menu_caller': lambda self: data_management(self)}
        }
        while True:
            print_menu_header("PRISM Backend Logic")
            if print_menu_options(self, menu_options, submenu = True):
                break

    def prism_server_and_api_endpoints_documentation(self):
        print_menu_header("PRISM Server and API Endpoints")
        exit_menu()

    def prism_user_interface_documentation(self):
        print_menu_header("PRISM User Interface:")
        exit_menu()

    def qualtrics_interface_documentation(self):
        print_menu_header("Qualtrics Interface")
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
        if print_menu_options(self, menu_options, submenu = True):
            break