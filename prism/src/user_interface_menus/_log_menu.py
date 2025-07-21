from user_interface_menus._menu_helper import *

def log_menu(self):

    def print_transcript(self, log_type):
        num_lines = input("Enter number of lines to view (default 10): ").strip()
        if not num_lines.isdigit():
            num_lines = '10'
        print_menu_header(f"{log_type}")
        self.request_transcript(num_lines, log_type)

    menu_options = {
        'transcript': {'description': 'View Today\'s Transcript', 'menu_caller': lambda self: print_transcript(self, 'get_transcript')},
        'ema': {'description': 'View EMA Log', 'menu_caller': lambda self: print_transcript(self, 'get_ema_log')},
        'feedback': {'description': 'View Feedback Survey Log', 'menu_caller': lambda self: print_transcript(self, 'get_feedback_log')}
    }

    while True:
        print_menu_header("PRISM Log Menu")
        if print_menu_options(self, menu_options, submenu = True):
            break