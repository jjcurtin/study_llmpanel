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
        print_menu_header("help")
        if print_menu_options(self, menu_options, submenu = True):
            break

def read_me(self):
    print_menu_header("readme")
    print(f"I recommend looking through the {yellow('help')} section and then looking through the commands.")
    print(f"\nYou can search for commands by typing {yellow('command <query>')} or {yellow('?<query>')}. Leave {yellow('<query>')} empty to search for all commands.")
    print(f"Most commands are globally accessible but some are only available in specific menus.")
    print(f"Commands are specified in {yellow('yellow')}.")
    print(f"Example: To toggle color mode, use the command {yellow('display color')}.")
    print(f"\nThere is also a command chaining feature that allows you to chain commands together using the {yellow('/')} character for commands and {yellow('?')} for user inputs.")
    print(f"Example, to schedule the second available R script at midnight, you can use the command chain {yellow('/tasks/add/rscript?2?00:00:00')}")
    print(f"To avoid the somewhat cumbersome action of typing the same command multiple times, you can use the {yellow('register')} command to save a command chain and then use it later.")
    print(f"You can also use the command of the form {yellow('$<identifier> = <command_chain>')} to register a command chain.")

    print(f"\nTL;DR: You can navigate the entire user interface using what you see on the screen, but you can use commands to access features more quickly.")
    print(f"Command chaining is done with {yellow('/')}, but regular commands do not require this prefix.")
    print(f"\nTo stop this message from displaying on startup use the command {yellow('readme set')}.")
    exit_menu()

def general_information(self):
    print_menu_header("help general")
    print("This application is designed to manage and monitor participants in a study.")
    print("It includes features for system checks, task management, participant management, and logging.")
    print("It is designed to incorporate data collection, data processing, and communication with participants in a single system.")
    print(f"\nTo see a list of user interface commands, type {yellow('command')}.")
    print("\nFor more detailed information, please refer to the appropriate documentation.")
    exit_menu()

global GENERAL_INFORMATION
GENERAL_INFORMATION = general_information

global README
README = read_me