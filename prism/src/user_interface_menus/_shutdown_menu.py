import requests

from _helper import clear
from user_interface_menus._menu_helper import error, success, exit_menu

def shutdown_menu(self):
    if self.api("GET", "system/uptime") is not None:
        if input("Shutdown PRISM? (yes/no): ").strip().lower() == 'yes':
            try:
                self.api("POST", "system/shutdown")
                success("PRISM shut down.")
                exit(0)
            except requests.ConnectionError:
                success("PRISM is already shut down.")
                exit(0)
            except Exception as e:
                error(f"Error: {e}")
        else:
            success("Shutdown cancelled.")
    else:
        success("PRISM is already shut down.")