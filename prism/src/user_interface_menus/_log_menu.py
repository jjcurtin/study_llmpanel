from user_interface_menus._menu_helper import *

def log_menu(self):
    while True:
        clear()
        print("View Logs\n1: Today's Transcript\n2: EMA log\n3: Feedback survey log\n\nENTER: Back to Main Menu")
        log_choice = input("Enter your choice: ").strip()
        if log_choice == '':
            break
        elif log_choice == '1' or log_choice == '2' or log_choice == '3':
            lines = input("Number of lines to display (default 10): ").strip() or '10'
            if not lines.isdigit():
                error("Invalid number of lines. Please enter a valid integer.")
                continue

            log_type = "get_transcript" if log_choice == '1' else "get_ema_log" if log_choice == '2' else "get_feedback_log" if log_choice == '3' else None
            self.request_transcript(lines, log_type)
            exit_menu()
        else:
            error("Invalid choice. Please try again.")