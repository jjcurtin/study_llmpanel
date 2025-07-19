import requests
import time
from _helper import clear
import random

from _user_interface_menus import main_menu

class PRISMInterface:
    def __init__(self):
        self.base_url = "http://localhost:5000/"
        if self.api("GET", "system/uptime") is None:
            print("PRISM instance is not running or is not accessible. Please start the PRISM server first.")
        main_menu(self)

    def api(self, method, endpoint, json=None):
        try:
            url = f"{self.base_url}/{endpoint}"
            if method == "GET":
                r = requests.get(url)
            elif method == "POST":
                r = requests.post(url, json=json)
            elif method == "PUT":
                r = requests.put(url)
            elif method == "DELETE":
                r = requests.delete(url)
            else:
                raise ValueError("Invalid HTTP method")

            if r.status_code == 200:
                return r.json()
        except requests.ConnectionError:
            pass
        except Exception:
            pass
        return None        

    def add_system_task(self, task_type, task_time, r_script_path = None):
        if r_script_path:
            if self.api("POST", f"system/add_r_script_task/{r_script_path}/{task_time}"):
                print(f"R script task {r_script_path} scheduled at {task_time}.")
            else:
                print(f"Failed to schedule R script task {task_type}.")
        elif self.api("POST", f"system/add_system_task/{task_type}/{task_time}"):
            print("Task added.")
        else:
            print("Failed to add task.")
        input("Press Enter to continue...")

    def remove_system_task(self, task_type, task_time, r_script_path = None):
        if r_script_path:
            if self.api("DELETE", f"system/remove_r_script_task/{r_script_path}/{task_time}"):
                print(f"R script task {task_type} at {task_time} removed.")
            else:
                print(f"Failed to remove R script task {task_type}.")
        elif self.api("DELETE", f"system/remove_system_task/{task_type}/{task_time}"):
            print("Task removed.")
        else:
            print("Failed to remove task.")
        input("Press Enter to continue...")

    def get_task_types(self):
        data = self.api("GET", "system/get_task_types")
        return data.get("task_types", {}) if data else {}      

    def request_transcript(self, lines, log_type):
        data = self.api("GET", f"system/{log_type}/{lines}")
        if data and "transcript" in data:
            print("Today's Transcript:")
            for entry in data["transcript"]:
                print(f"{entry['timestamp']} - {entry['message']}")
        else:
            print("No transcript found or failed to retrieve.")  

    def get_participants(self):
        data = self.api("GET", "participants/get_participants")
        participants = data.get("participants", []) if data else []
        print("Participant List:")
        if participants:
            for i, p in enumerate(participants, 1):
                print(f"{i}: {p['last_name']}, {p['first_name']} (ID: {p['unique_id']}) - On Study: {p['on_study']}")
        else:
            print("No participants found or failed to retrieve.")
        return participants    

if __name__ == "__main__":
    PRISMInterface()