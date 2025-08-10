# system check menu; basically just runs _check_system.py

from user_interface_menus._menu_helper import *

# ------------------------------------------------------------

def diagnostics(self):
    if self.api("POST", "system/execute_task/CHECK_SYSTEM"):
        success("System checks complete. No issues found.")
    else:
        self.request_transcript(25, "get_transcript")
        error("Failure detected. Please check the transcript for details.")

# ------------------------------------------------------------

def system_check_menu(self):
    menu_options = {
        'diagnostics': {"description": "Run System Diagnostics", "menu_caller": diagnostics},
    }
    while True:
        if not self.commands_queue:
            print_menu_header("check")
        print("Checking PRISM status and system uptime...")
        uptime_data = self.api("GET", "system/uptime")
        mode_data = self.api("GET", "system/get_mode")

        if uptime_data and mode_data:
            start_time = uptime_data.get('uptime', 'Unknown')
            mode = mode_data.get('mode', 'Unknown')
        else:
            error("PRISM not running or inaccessible.")
            return
        if not self.commands_queue:
            print_menu_header("check")
        print_dashes()
        print("Mode:", mode)
        print(f"As of last check, PRISM has been up for {green(start_time)}.")
        print_dashes()
        print()
        if print_menu_options(self, menu_options, submenu = True):
            break

# ------------------------------------------------------------

global DIAGNOSTICS
DIAGNOSTICS = diagnostics