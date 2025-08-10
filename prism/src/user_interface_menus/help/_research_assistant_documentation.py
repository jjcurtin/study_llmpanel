# ra docs

from user_interface_menus._menu_helper import *

def research_assistant_documentation(self):
    def getting_started(self):
        infopage(self, content = [
            f"The following API keys are required to be in the api/ folder and have the described format for PRISM to function correctly:",
            f'1. {green("qualtrics.api")}: "api_token","datacenter","ema_survey_id","feedback_survey_id"',
            f'2. {green("followmee.api")}: "username","api_token"',
            f'3. {green("twilio.api")}: "account_sid","auth_token","from_number"',
            f'4. {green("research_drive.api")}: "destination_path","drive_letter","network_domain","network_username","wisc_netid","wisc_password"',
            f'5. {green("ngrok.api")}: "auth_token","domain"'
        ], title = "help ra getting started")

    def navigation(self):
        infopage(self, content = [
            f"PRISM is designed to be navigated through commands. You can use {yellow('command <query>')} or {yellow('?<query>')} to search for commands.",
            f"You can look at all of the commands by typing {yellow('command')} or {yellow('?')} with no arguments.",
            f"\nYou can use most global commands from any menu, but keep in mind that local commands take priority.",
            f"Additionally, most local commands are only available in the menu they are defined in (e.g. most of the docs).",
            f"Local commands are the ones you see on any given screen besides the command menu, which is accessed by {yellow('command')}.",
            f"\nSome actions are mapped to multiple commands; this is to allow for flexibility.",   
            f"For example, you can use {yellow('tasks add rscript')} or {yellow('add rscript')} to schedule an R script.",
            f"The first shows the menus you need to go through, while the second is more intuitive.",
            f"\nYou can also use the {yellow('register')} command to save a command chain and then use it later.",
            f"You can also use the command of the form {yellow('$<identifier> = <command_chain>')} to register a command chain.",
            f"You can also use the command of the form {yellow('-<identifier> = <command_chain>')} to remove a saved command chain.",
            f"You can also use the command of the form {yellow('!<identifier>')} to search for saved command chains.",
            f"Command chains follow the format of {yellow('/<command1>?<input1>/<command2>?<input2>...')}.",
            f"You can put commands/inputs in any order, any saved chains will expand in place, and inputs associate with the command to their left."
        ], title = "help ra navigation")

    def terminals(self):
        infopage(self, content = [
            f"PRISM has four terminal prompts:",
            f"{cyan('prism> ')}: The main prompt for PRISM. You can use this to run commands.",
            f"{red('assistant> ')}: The prompt for the PRISM Assistant. You can use this to ask questions in natural language.",
            f"{green('twilio> ')}: The prompt for the Twilio interface. Input from this is sent as a text message.",
            f"{yellow('ENTER to Continue> ')}: This prompt is used to continue after displaying a message. No commands can be run."
        ], title = "help ra terminals")

    def task_management(self):
        infopage(self, content = [
            f"PRISM has a task management system that allows you to run R scripts and other tasks.",
            f"You can use the {yellow('tasks')} command to manage tasks.",
            f"You can add, remove, and view tasks, as well as manage their execution.",
            f"Tasks are stored in {green('config/scheduled_tasks.json')}.",
            f"You can also use the {yellow('tasks add')} command to add a task.",
            f"You can use the {yellow('tasks remove')} command to remove a task."
        ], title = "help ra tasks")

    def participants(self):
        infopage(self, content = [
            f"PRISM has a participant management system that allows you to manage participants in a study.",
            f"You can use the {yellow('participants')} command to manage participants.",
            f"You can add, remove, and view participants, as well as manage their data.",
            f"Participants are stored in {green('config/study_participants.csv')}.",
            f"You can also use the {yellow('participants add')} command to add a participant.",
            f"You can use the {yellow('participants remove')} command to remove a participant."
        ], title = "help ra participants")

    menu_options = {
        'start': {'description': 'Getting Started', 'menu_caller': getting_started},
        'navigation': {'description': 'Navigating PRISM through Commands', 'menu_caller': navigation},
        'terminals': {'description': 'Terminal Prompts', 'menu_caller': terminals},
        'task_management': {'description': 'Task Management', 'menu_caller': task_management},
        'participant_management': {'description': 'Participant Management', 'menu_caller': participants}
    }
    while True:
        if not self.commands_queue:
            print_menu_header("help ra")
        if print_menu_options(self, menu_options, submenu = True, recommended_actions = ['start', 'tasks', 'participants']):
            break