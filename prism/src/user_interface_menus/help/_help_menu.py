# documentation entry point

from user_interface_menus._menu_helper import *
from user_interface_menus.help._developer_documentation import developer_documentation
from user_interface_menus.help._research_assistant_documentation import research_assistant_documentation

def help_menu(self):
    menu_options = {
        'readme': {'description': 'Readme Documentation', 'menu_caller': read_me},
        'general': {'description': 'General Information', 'menu_caller': general_information},
        'ra': {'description': 'Research Assistant Documentation', 'menu_caller': research_assistant_documentation},
        'dev': {'description': 'Developer Documentation', 'menu_caller': developer_documentation}
    }

    while True:
        set_recommended_actions([
            'readme',
            'ra'
        ])
        print_menu_header("help")
        if print_menu_options(self, menu_options, submenu = True):
            break

def read_me(self):
    clear_recommended_actions()
    print_menu_header("readme")
    global read_me_lines
    for line in read_me_lines:
        print(line)
    exit_menu()

def general_information(self):
    clear_recommended_actions()
    print_menu_header("help general")
    print("This application is designed to manage and monitor participants in a study.")
    print("It includes features for system checks, task management, participant management, and logging.")
    print("It is designed to incorporate data collection, data processing, and communication with participants in a single system.")
    print(f"\nTo see a list of user interface commands, type {yellow('command')}.")
    print(f"To chain commands together, use the {yellow('/')} character for commands and {yellow('?')} for user inputs.")
    print("\nFor more detailed information, please refer to the appropriate documentation.")
    exit_menu()

global GENERAL_INFORMATION
GENERAL_INFORMATION = general_information

global README
README = read_me

global read_me_lines
read_me_lines = [
    f"I recommend looking through the {yellow('help')} section and then looking through the commands.",
    f"\nYou can search for commands by typing {yellow('command <query>')} or {yellow('?<query>')}. Leave {yellow('<query>')} empty to search for all commands.",
    f"Most commands are globally accessible but some are only available in specific menus.",
    f"Commands are specified in {yellow('yellow')}.",
    f"Example: To toggle color mode, use the command {yellow('display color')}.",
    f"\nThere is also a command chaining feature that allows you to chain commands together using the {yellow('/')} character for commands and {yellow('?')} for user inputs.",
    f"Example, to schedule the second available R script at midnight, you can use the command chain {yellow('/tasks/add/rscript?2?00:00:00')}",
    f"To avoid the somewhat cumbersome action of typing the same command multiple times, you can use the {yellow('register')} command to save a command chain and then use it later.",
    f"You can also use the command of the form {yellow('$<identifier> = <command_chain>')} to register a command chain.",
    f"\nTL;DR: You can navigate the entire user interface using what you see on the screen, but you can use commands to access features more quickly.",
    f"Command chaining is done with {yellow('/')}, but regular commands do not require this prefix.",
    f"\nTo stop this message from displaying on startup use the command {yellow('readme set')}."
]