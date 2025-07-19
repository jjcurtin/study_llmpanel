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

    def print_main_menu(self):
        clear()
        print("PRISM Interface Menu:")
        print("1: Get PRISM Uptime and Mode")
        print("2: Manage System Tasks")
        print("3: Manage Participants")
        print("4: View Logs")
        print("5: Shutdown PRISM")
        print("6: Exit")

    ####################
    #   System Tasks   #
    ####################

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

    ####################
    #   Participants    #
    ####################

    def add_participant(self):
        clear()
        print("Add New Participant")
        first_name = input("First name: ")
        if not first_name:
            print("First name is required.")
            input("Press Enter to continue...")
            return
        last_name = input("Last name: ")
        if not last_name:
            print("Last name is required.")
            input("Press Enter to continue...")
            return
        unique_id = input("Unique ID: ")
        if not unique_id:
            unique_id = str(random.randint(100000000, 999999999))
            print(f"Unique ID not provided. Generated: {unique_id}")
        on_study = input("On study? (yes/no): ").strip().lower()
        if on_study not in ('yes', 'y', 'no', 'n'):
            print("Invalid input for on study. Defaulting to 'no'.")
            on_study = 'no'
        elif on_study == 'y': 
            on_study = 'yes'
        elif on_study == 'n':
            on_study = 'no'
        on_study = on_study == 'yes'
        phone_number = input("Phone number (press enter to skip): ")
        times = {}
        default_times = {
            'ema_time': '08:00:00',
            'ema_reminder_time': '08:15:00',
            'feedback_time': '18:00:00',
            'feedback_reminder_time': '18:15:00'
        }
        for t in ['ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']:
            val = input(f"Enter {t.replace('_', ' ')} (HH:MM:SS) [default: {default_times[t]}]: ").strip() or default_times[t]
            try:
                time.strptime(val, '%H:%M:%S')
                times[t] = val
            except ValueError:
                print(f"Invalid time format for {val}. Using default: {default_times[t]}.\nYou can change this later.")
                times[t] = default_times[t]
        payload = dict(first_name = first_name, 
                       last_name = last_name, 
                       unique_id = unique_id, 
                       on_study = on_study, 
                       phone_number = phone_number, 
                       **times)
        if self.api("POST", "participants/add_participant", json = payload):
            print("Participant added.")
        else:
            print("Failed to add participant.")
        input("Press Enter to continue...")        

if __name__ == "__main__":
    PRISMInterface()