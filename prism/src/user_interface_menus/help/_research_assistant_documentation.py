# ra docs

from user_interface_menus._menu_helper import *

def research_assistant_documentation(self):
    def getting_started(self):
        infopage(self, content = [
            f"PRISM is a research study tool that allows you to manage study participant metadata and communication.",
            f"It also provides functionality for scheduling code scripts as needed for research studies.",
            f"It is designed to run 24/7 and execute study responsibilities in real time.",
            f"\nTo get started with PRISM, ensure the following folders and files exist.",
            f"\n{green("api")}\n{green("azure.api")}\n{green("followmee.api")}\n{green("ngrok.api")}\n{green("qualtrics.api")}\n{green("research_drive.api")}\n{green("twilio.api")}",
            f"\n{green("config")}\n{green("study_participants.csv")}\n{green("study_coordinators.csv")}\n{green("system_task_schedule.csv")}\n{green("script_pipeline.csv")} if using script pipelines (deprecated) \n",
            f"To run R scripts, place them in the {green("scripts")} directory and they will be automatically detected."
        ], title = "help ra getting started")

    def navigation(self):
        infopage(self, content = [
            f"To navigate PRISM, you can either traverse the menus using the options displayed on each screen, or you can use commands.",
            f"The commands are designed to allow you to access submenus faster, and there is a minimal scripting language to allow for more complex actions.",
            f"You can use these commands in any submenu, but the options displayed in each submenu are specific to that submenu if they are not registered as a command.",
            f"\nYou can use the {yellow('command')} or {yellow('?')} command to search for commands.",
            f"You can also append a search query using the form {yellow('command <query>')} or {yellow('?<query>')}.",
        ], title = "help ra navigation")

    def navigation_advanced():
        infopage(self, content = [
            f"\nSome actions are mapped to multiple commands; this is to allow for flexibility.",   
            f"For example, you can use {yellow('tasks add rscript')} or {yellow('add rscript')} to schedule an R script.",
            f"The first shows the menus you need to go through, while the second is more intuitive.",
            f"\nYou can also use the {yellow('register')} command to save a command chain (the saved version is called a macro) and then use it later.",
            f"You can also use the command of the form {yellow('$<identifier> = <command_chain>')} to register a macro.",
            f"You can use the command of the form {yellow('-<identifier> = <command_chain>')} to remove a saved macro.",
            f"You can use the command of the form {yellow('!<identifier>')} to search for saved macros.",
            f"Command chains follow the format of {yellow('/<command1>?<input1>/<command2>?<input2>...')}.",
            f"You can put commands/inputs in any order, any saved chains will expand in place, and inputs associate with the command to their left."
        ], title = "help ra navigation advanced")

    def terminals(self):
        infopage(self, content = [
            f"PRISM has four terminal prompts:",
            f"{cyan('prism> ')}: The main prompt for PRISM. You can use this to run commands.",
            f"{red('assistant> ')}: The prompt for the PRISM Assistant. You can use this to ask questions in natural language. The prefixes {yellow('@')} and {yellow('assistant')} will also query the assistant.",
            f"{green('twilio> ')}: The prompt for the Twilio interface. Input from this is sent as a text message to study participants.",
            f"{yellow('ENTER to Continue> ')}: This prompt is used to continue after displaying a message. No commands can be run."
        ], title = "help ra terminals")

    def task_management(self):
        infopage(self, content = [
            f"PRISM has a task management system that allows you to run R scripts and other tasks.",
            f"You can use the {yellow('tasks')} command to manage tasks.",
            f"You can add, remove, and view tasks, as well as manage their execution.",
            f"Tasks are stored in {green('config/scheduled_tasks.csv')}.",
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
        'navigation advanced': {'description': 'Advanced Navigation Documentation', 'menu_caller': navigation_advanced},
        'terminals': {'description': 'Terminal Prompts', 'menu_caller': terminals},
        'task management': {'description': 'Task Management', 'menu_caller': task_management},
        'participant management': {'description': 'Participant Management', 'menu_caller': participants}
    }
    while True:
        if not self.commands_queue:
            print_menu_header("help ra")
        if print_menu_options(self, menu_options, submenu = True, recommended_actions = ['start', 'tasks', 'participants']):
            break