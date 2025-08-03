# Main runner for the RA PRISM interface

import requests, queue

from user_interface_menus._main_menu import main_menu, read_me
from user_interface_menus._menu_helper import load_menus, exit_menu, load_params

class PRISMInterface:
    def __init__(self):
        self.base_url = "http://localhost:5000/"
        if self.api("GET", "system/uptime") is None:
            print("PRISM instance is not running or is not accessible. Please start the PRISM server first.")
            exit(0)

        self.inputs_queue = queue.Queue()
        self.commands_queue = queue.Queue()
            
        from user_interface_menus._menu_helper import SHOW_README
        if SHOW_README == True:
            read_me(self)
        main_menu(self)

    def api(self, method, endpoint, json=None):
        from user_interface_menus._menu_helper import TIMEOUT
        try:
            url = f"{self.base_url}/{endpoint}"
            if method == "GET":
                r = requests.get(url, timeout = TIMEOUT)
            elif method == "POST":
                r = requests.post(url, json = json, timeout = TIMEOUT)
            elif method == "PUT":
                r = requests.put(url, timeout = TIMEOUT)
            elif method == "DELETE":
                r = requests.delete(url, timeout = TIMEOUT)
            else:
                raise ValueError("Invalid HTTP method")

            if r.status_code == 200:
                return r.json()
        except requests.ConnectionError:
            print("Connection error occurred while trying to reach the PRISM server.")
        except requests.Timeout:
            print("Request timed out. Please check the PRISM server or increase the timeout value.")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
        return None

    def get_task_types(self):
        data = self.api("GET", "system/get_task_types")
        return data.get("task_types", {}) if data else {}      

    def request_transcript(self, lines, log_type):
        data = self.api("GET", f"system/{log_type}/{lines}")
        if data and "transcript" in data:
            for entry in data["transcript"]:
                print(f"{entry['timestamp']} - {entry['message']}")
        else:
            print("No transcript found or failed to retrieve.")  

if __name__ == "__main__":
    while True:
        try:
            load_params()
            load_menus()
            PRISMInterface()
        except KeyboardInterrupt:
            from user_interface_menus._menu_helper import COLOR_ON
            if COLOR_ON:
                print("\033[32m\nExiting PRISM Interface.\033[0m")
            else:
                print("\nExiting PRISM Interface.")
            break
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            exit_menu()