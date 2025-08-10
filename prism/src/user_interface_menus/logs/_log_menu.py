# menu for accessing logs

from user_interface_menus._menu_helper import *

# ------------------------------------------------------------

def log_menu(self):
    menu_options = {
        'transcript': {'description': 'View Today\'s Transcript', 'menu_caller': lambda self: print_transcript(self, 'get_transcript')},
        'ema': {'description': 'View EMA Log', 'menu_caller': lambda self: print_transcript(self, 'get_ema_log')},
        'feedback': {'description': 'View Feedback Survey Log', 'menu_caller': lambda self: print_transcript(self, 'get_feedback_log')},
        'interface': {'description': 'View Interface Log', 'menu_caller': lambda self: print_interface_log(self)}
    }

    while True:
        clear_recommended_actions()
        if not self.commands_queue:
            print_menu_header("logs")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

def print_transcript(self, log_type):
    clear_recommended_actions()
    if not self.commands_queue:
        print_menu_header(f"logs {log_type.split('_')[1]}")
        num_lines = get_input(self, prompt = "Enter number of lines to view: ", default_value = "10")
        if not num_lines.isdigit():
            num_lines = '10'
        self.request_transcript(num_lines, log_type)
        success(f"{log_type.replace('_', ' ').title()} log retrieved.", self)

def print_interface_log(self):
    from user_interface_menus._menu_helper import read_from_interface_log
    clear_recommended_actions()
    if not self.commands_queue:
        print_menu_header("logs interface")
        try:
            content = read_from_interface_log()
            if content is None or content == "":
                error("No content found in the interface log.")
                return

            num_lines = get_input(self, prompt = "Enter number of lines to view: ", default_value = "10")
            if not num_lines.isdigit():
                num_lines = '10'
            lines = content.splitlines()
            start_index = max(0, len(lines) - int(num_lines))
            end_index = len(lines)
            for line in lines[start_index:end_index]:
                print(line)
            exit_menu()
        except FileNotFoundError:
            error(f"Interface log file not found.")
        except Exception as e:
            error(f"An unexpected error occurred while reading the interface log: {e}")

# ------------------------------------------------------------

global PRINT_TRANSCRIPT
PRINT_TRANSCRIPT = print_transcript