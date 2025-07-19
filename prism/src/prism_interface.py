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