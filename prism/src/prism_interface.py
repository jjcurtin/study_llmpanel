import requests
import time
from _helper import clear
import random

from _user_interface_menus import task_schedule_menu

class PRISMInterface:
    def __init__(self):
        self.base_url = "http://localhost:5000/"
        if self.api("GET", "system/uptime") is None:
            print("PRISM instance is not running or is not accessible. Please start the PRISM server first.")
        self.run()

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

    def run(self):
        while True:
            self.print_main_menu()
            choice = input("Enter your choice: ").strip()
            
            # get mode and uptime
            if choice == '1':
                clear()
                uptime_data = self.api("GET", "system/uptime")
                if uptime_data:
                    print(f"PRISM Uptime: {uptime_data.get('uptime', 'Unknown')}")
                else:
                    print("PRISM not running or inaccessible.")
                mode_data = self.api("GET", "system/get_mode")
                if mode_data:
                    print(f"PRISM Mode: {mode_data.get('mode', 'Unknown')}")
                else:
                    print("PRISM not running or inaccessible.")
                input("Press Enter to continue...")

            # Manage System Tasks
            elif choice == '2':
                task_schedule_menu(self)

            # Manage Participants
            elif choice == '3':
                while True:
                    clear()
                    data = self.api("GET", "participants/get_participants")
                    participants = data.get("participants", []) if data else []
                    print("Participant List:")
                    if participants:
                        for i, p in enumerate(participants, 1):
                            print(f"{i}: {p['last_name']}, {p['first_name']} (ID: {p['unique_id']}) - On Study: {p['on_study']}")
                    else:
                        print("No participants found or failed to retrieve.")
                    print("\na: Add a Participant\ns: Get Participant Task Schedule\nr: Full Participants Refresh from CSV\nn: study announcement\n\nENTER: Back to Main Menu")
                    choice = input("Enter index, 'a', 's', 'r', 'n', or ENTER: ").strip()
                    if choice.isdigit():
                        idx = int(choice)-1
                        if 0 <= idx < len(participants):
                            self.print_participant_schedule(participants[idx]['unique_id'])
                    elif choice.lower() == 'a':
                        self.add_participant()
                    elif choice.lower() == 's':
                        tasks = self.api("GET", "participants/get_participant_task_schedule")
                        if tasks:
                            print("Participant Task Schedule:")
                            for task in tasks.get("tasks", []):
                                print(f"{task['participant_id']}: {task['task_type']} at {task['task_time']} - On Study: {task['on_study']}")
                            input("\nPress Enter to continue...")
                    elif choice.lower() == 'r':
                        if input("Refresh participants from CSV? (yes/no): ").strip().lower() == 'yes':
                            if self.api("POST", "participants/refresh_participants"):
                                print("Participants refreshed from CSV.")
                            else:
                                print(f"Failed to refresh participants. Error code: {self.api('POST', 'participants/refresh_participants').get('status_code', 'Unknown')}")
                        else:
                            print("Refresh cancelled.")
                        input("Press Enter to continue...")
                    elif choice.lower() == 'n':
                        message = input("Enter study announcement message: ").strip()
                        if not message:
                            print("Message cannot be empty.")
                            input("Press Enter to continue...")
                            continue
                        require_on_study = input("Send to participants on study only? (yes/no): ").strip().lower()
                        if require_on_study not in ('yes', 'y', 'no', 'n'):
                            input("Invalid input. Cancelling. Press Enter to continue...")
                            continue
                        if self.api("POST", f"participants/study_announcement/{require_on_study}", json = {"message": message}):
                            print("Study announcement sent.")
                        else:
                            print("No participants found or failed to retrieve.")
                        input("Press Enter to continue...")
                    elif choice == '':
                        break
                    else:
                        print("Invalid choice.")
                        input("Press Enter to continue...")

            # View Logs
            elif choice == '4':
                while True:
                    clear()
                    print("View Logs\n1: Today's Transcript\n2: EMA log\n3: Feedback survey log\n\nENTER: Back to Main Menu")
                    log_choice = input("Enter your choice: ").strip()
                    if log_choice == '':
                        break
                    elif log_choice == '1' or log_choice == '2' or log_choice == '3':
                        lines = input("Number of lines to display (default 10): ").strip() or '10'
                        if not lines.isdigit():
                            print("Invalid number.")
                            input("Press Enter to continue...")
                            continue

                        log_type = "get_transcript" if log_choice == '1' else "get_ema_log" if log_choice == '2' else "get_feedback_log" if log_choice == '3' else None

                        data = self.api("GET", f"system/{log_type}/{lines}")
                        if data and "transcript" in data:
                            print("Today's Transcript:")
                            for entry in data["transcript"]:
                                print(f"{entry['timestamp']} - {entry['message']}")
                        else:
                            print("No transcript found or failed to retrieve.")
                        input("Press Enter to continue...")
                    else:
                        print("Invalid choice.")
                        input("Press Enter to continue...")

            # Shutdown PRISM
            elif choice == '5':
                if self.api("GET", "system/uptime") is not None:
                    if input("Shutdown PRISM? (yes/no): ").strip().lower() == 'yes':
                        try:
                            self.api("POST", "system/shutdown")
                            print("PRISM shut down.")
                            exit(0)
                        except requests.ConnectionError:
                            print("PRISM shut down.")
                            exit(0)
                        except Exception as e:
                            print(f"Error: {e}")
                    else:
                        print("Shutdown cancelled.")
                else:
                    print("PRISM not running, cannot shutdown.")
                input("Press Enter to continue...")

            # Exit
            elif choice == '6':
                print("Exiting PRISM Interface.")
                break

            else:
                print("Invalid choice.")
                input("Press Enter to continue...")

if __name__ == "__main__":
    PRISMInterface()