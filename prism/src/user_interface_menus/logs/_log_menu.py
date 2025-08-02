# menu for accessing logs

from user_interface_menus._menu_helper import *

# ------------------------------------------------------------

def log_menu(self):
    menu_options = {
        'transcript': {'description': 'View Today\'s Transcript', 'menu_caller': lambda self: print_transcript(self, 'get_transcript')},
        'ema': {'description': 'View EMA Log', 'menu_caller': lambda self: print_transcript(self, 'get_ema_log')},
        'feedback': {'description': 'View Feedback Survey Log', 'menu_caller': lambda self: print_transcript(self, 'get_feedback_log')}
    }

    while True:
        print_menu_header("logs")
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

def print_transcript(self, log_type):
    num_lines = get_input(self, prompt = "Enter number of lines to view: ", default_value = "10")
    if not num_lines.isdigit():
        num_lines = '10'
    print_menu_header(f"logs {log_type.split('_')[1]}")
    self.request_transcript(num_lines, log_type)
    exit_menu()

# ------------------------------------------------------------

global PRINT_TRANSCRIPT
PRINT_TRANSCRIPT = print_transcript