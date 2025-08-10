# ra docs

from user_interface_menus._menu_helper import *

def research_assistant_documentation(self):
    def getting_started(self):
        if not self.commands_queue:
            print_menu_header("help ra start")
            print("The following API keys are required to be in the api/ folder and have the described format for PRISM to function correctly:")
            print(f'1. {green("qualtrics.api")}: "api_token","datacenter","ema_survey_id","feedback_survey_id"')
            print(f'2. {green("followmee.api")}: "username","api_token"')
            print(f'3. {green("twilio.api")}: "account_sid","auth_token","from_number"')
            print(f'4. {green("research_drive.api")}: "destination_path","drive_letter","network_domain","network_username","wisc_netid","wisc_password"')
            print(f'5. {green("ngrok.api")}: "auth_token","domain"')
            exit_menu()

    def navigation(self):
        if not self.commands_queue:
            print_menu_header("help ra commands")
            print(f"PRISM is designed to be navigated through commands. You can use {yellow('command <query>')} or {yellow('?<query>')} to search for commands.")
            print(f"You can look at all of the commands by typing {yellow('command')} or {yellow('?')} with no arguments.")
            print(f"This menu is accessed {yellow("commands")} instead of {yellow("command")} since {yellow("command")} has the highest priority.")
            print(f"\nYou can use most global commands from any menu, but keep in mind that local commands take priority.")
            print(f"Additionally, most local commands are only available in the menu they are defined in (e.g. most of the docs).")
            print(f"Local commands are the ones you see on any given screen besides the command menu, which is accessed by {yellow("command")}.")
            print(f"\nSome actions are mapped to multiple commands; this is to allow for flexibility.")
            print(f"For example, you can use {yellow('tasks add rscript')} or {yellow('add rscript')} to schedule an R script.")
            print(f"The first shows the menus you need to go through, while the second is more intuitive.")
            print(f"\nYou can also use the {yellow('register')} command to save a command chain and then use it later.")
            print(f"You can also use the command of the form {yellow('$<identifier> = <command_chain>')} to register a command chain.")
            print(f"Command chains follow the format of {yellow('/<command1>?<input1>/<command2>?<input2>...')}.")
            print(f"You can put commands/inputs in any order, any saved chains will expand in place, and inputs associate with the command to their left.")
            exit_menu()

    def terminals(self):
        if not self.commands_queue:
            print_menu_header("help ra terminals")
            print(f"PRISM currently has four terminal prompts:")
            print(f"{cyan('prism> ')}: The main prompt for PRISM. You can use this to run commands.")
            print(f"{red('assistant> ')}: The prompt for the PRISM Assistant. You can use this to ask questions in natural language.")
            print(f"{green('twilio> ')}: The prompt for the Twilio interface. Input from this is sent as a text message.")
            print(f"{yellow('ENTER to Continue> ')}: This prompt is used to continue after displaying a message. No commands can be run.")
            exit_menu()

    def task_management(self):
        if not self.commands_queue:
            print_menu_header("help ra tasks")
            print(f"PRISM has a task management system that allows you to run R scripts and other tasks.")
            print(f"I set up the Python tasks in a specific way to allow for easy management and execution.")
            print(f"For information on how to set up one of these, refer to {yellow('help dev')}.")
            print(f"R scripts are much easier; put it in the {green('scripts/')} folder and it will be automatically detected by the system.")
            print(f"You can use the {yellow('tasks')} command to manage tasks.")
            exit_menu()

    def participants(self):
        if not self.commands_queue:
            print_menu_header("help ra participants")
            print(f"PRISM has a participant management system that allows you to manage participants in a study.")
            print(f"You can use the {yellow('participants')} command to manage participants.")
            print(f"You can add, remove, and view participants, as well as manage their data.")
            print(f"Participants are stored in {green('config/study_participants.csv')}.")
            exit_menu()

    menu_options = {
        'start': {'description': 'Getting Started', 'menu_caller': getting_started},
        'commands': {'description': 'Navigating PRISM through Commands', 'menu_caller': navigation},
        'terminals': {'description': 'Terminal Prompts', 'menu_caller': terminals},
        'tasks': {'description': 'Task Management', 'menu_caller': task_management},
        'participants': {'description': 'Participant Management', 'menu_caller': participants}
    }
    while True:
        if not self.commands_queue:
            print_menu_header("help ra")
        if print_menu_options(self, menu_options, submenu = True, recommended_actions = ['start', 'tasks', 'participants']):
            break