from _helper import clear
from user_interface_menus._menu_helper import error, success, exit_menu

def system_check_menu(self):
    def prompt_system_check_menu(self):
        choice = input("Would you like to run system checks (CHECK_SYSTEM Task)? (yes/no): ").strip().lower()
        if choice in ('yes', 'y'):
            if self.api("POST", "system/execute_task/CHECK_SYSTEM"):
                success("System checks complete. No issues found.")
            else:
                self.request_transcript(25, "get_transcript")
                error("Failure detected. Please check the transcript for details.")
        else:
            exit_menu()
    
    clear()
    print("Requesting PRISM status...")
    uptime_data = self.api("GET", "system/uptime")
    mode_data = self.api("GET", "system/get_mode")

    if uptime_data and mode_data:
        print(f"PRISM Uptime: {uptime_data.get('uptime', 'Unknown')}")
        print(f"PRISM Mode: {mode_data.get('mode', 'Unknown')}")
        prompt_system_check_menu(self)
    else:
        error("PRISM not running or inaccessible.")