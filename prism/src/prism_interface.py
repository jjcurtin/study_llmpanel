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

    def print_participant_schedule(self, participant_id):
        data = self.api("GET", f"participants/get_participant/{participant_id}")
        participant = data.get("participant") if data else None
        if not participant:
            print("Failed to retrieve participant schedule.")
            input("Press Enter to continue...")
            return
        field_map = {
            '1': 'first_name', '2': 'last_name', '3': 'unique_id', '4': 'on_study',
            '5': 'phone_number', '6': 'ema_time', '7': 'ema_reminder_time',
            '8': 'feedback_time', '9': 'feedback_reminder_time'
        }
        while True:
            clear()
            print(f"Participant ID {participant_id} Info:")
            for k, f in sorted(field_map.items()):
                print(f"{k}: {f.replace('_',' ').capitalize()}: {participant.get(f)}")
            print("\nindex: select field, s: send survey, r: remove participant, m: send message, ENTER: back")

            choice = input("Enter choice: ").strip()
            if choice == '':
                break
            elif choice in field_map:
                field = field_map[choice]
                new_val = input(f"Enter new value for {field}: ")
                if self.api("PUT", f"participants/update_participant/{participant_id}/{field}/{new_val}"):
                    participant[field] = new_val
                    print("Participant updated.")
                else:
                    print("Failed to update participant.")
                input("Press Enter to continue...")
            elif choice.lower() == 'r':
                if input("Remove participant? (yes/no): ").strip().lower() == 'yes':
                    if self.api("DELETE", f"participants/remove_participant/{participant_id}"):
                        print("Participant removed.")
                        input("Press Enter to continue...")
                        break
                    else:
                        print("Failed to remove participant.")
                        input("Press Enter to continue...")
            elif choice.lower() == 's':
                survey_type = input("Enter survey type (ema/feedback): ").strip().lower()
                if survey_type in ['ema', 'feedback']:
                    if self.api("POST", f"participants/send_survey/{participant_id}/{survey_type}"):
                        print(f"{survey_type.capitalize()} survey sent.")
                    else:
                        print(f"Failed to send {survey_type} survey.")
                else:
                    print("Invalid survey type.")
                input("Press Enter to continue...")
            elif choice.lower() == 'm':
                message = input("Enter message to send: ").strip()
                if self.api("POST", f"participants/send_custom_sms/{participant_id}", json={"message": message}):
                    print("Message sent.")
                else:
                    print("Failed to send message.")
                input("Press Enter to continue...")
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")

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