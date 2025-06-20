import requests
import time
from _helper import clear

class PRISMInterface:
    def __init__(self):
        self.base_url = "http://localhost:5000/system"
        if self.api("GET", "uptime") is None:
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

    def print_system_task_schedule(self):
        clear()
        print("System Task Schedule:")
        tasks = self.api("GET", "get_task_schedule")
        if tasks and "tasks" in tasks:
            self.scheduled_tasks = tasks["tasks"]
            if self.scheduled_tasks:
                for i, t in enumerate(self.scheduled_tasks, 1):
                    print(f"{i}. {t['task_type']} @ {t['task_time']} - Run Today: {t.get('run_today', False)}")
            else:
                print("No tasks scheduled.")
        else:
            print("Failed to retrieve task schedule or PRISM not running.")
        print("\n1: Add New Task\n2: Remove Task\n3: Execute Task Now\n\nENTER: Back to Main Menu")  

    def add_system_task(self, task_type, task_time):
        if self.api("POST", f"add_system_task/{task_type}/{task_time}"):
            print("Task added.")
        else:
            print("Failed to add task.")
        input("Press Enter to continue...")

    def remove_system_task(self, task_type, task_time):
        if self.api("DELETE", f"remove_system_task/{task_type}/{task_time}"):
            print("Task removed.")
        else:
            print("Failed to remove task.")
        input("Press Enter to continue...")

    def get_task_types(self):
        data = self.api("GET", "get_task_types")
        return data.get("task_types", {}) if data else {}      

    ####################
    #   Participants    #
    ####################

    def print_participant_schedule(self, participant_id):
        data = self.api("GET", f"get_participant/{participant_id}")
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
            print("\nindex: select field, s: send survey, r: remove participant, ENTER: back")

            choice = input("Enter choice: ").strip()
            if choice == '':
                break
            elif choice in field_map:
                field = field_map[choice]
                new_val = input(f"Enter new value for {field}: ")
                if self.api("PUT", f"update_participant/{participant_id}/{field}/{new_val}"):
                    participant[field] = new_val
                    print("Participant updated.")
                else:
                    print("Failed to update participant.")
                input("Press Enter to continue...")
            elif choice.lower() == 'r':
                if input("Remove participant? (yes/no): ").strip().lower() == 'yes':
                    if self.api("DELETE", f"remove_participant/{participant_id}"):
                        print("Participant removed.")
                        input("Press Enter to continue...")
                        break
                    else:
                        print("Failed to remove participant.")
                        input("Press Enter to continue...")
            elif choice.lower() == 's':
                survey_type = input("Enter survey type (ema/feedback): ").strip().lower()
                if survey_type in ['ema', 'feedback']:
                    if self.api("POST", f"send_survey/{participant_id}/{survey_type}"):
                        print(f"{survey_type.capitalize()} survey sent.")
                    else:
                        print(f"Failed to send {survey_type} survey.")
                else:
                    print("Invalid survey type.")
                input("Press Enter to continue...")
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")

    def add_participant(self):
        clear()
        print("Add New Participant")
        first_name = input("First name: ")
        last_name = input("Last name: ")
        unique_id = input("Unique ID: ")
        on_study = input("On study? (yes/no): ").strip().lower()
        if on_study not in ('yes', 'no'):
            print("Invalid input for on study.")
            input("Press Enter to continue...")
            return
        on_study = on_study == 'yes'
        phone_number = input("Phone number: ")
        times = {}
        for t in ['ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']:
            val = input(f"Enter {t.replace('_', ' ')} (HH:MM:SS): ")
            try:
                time.strptime(val, '%H:%M:%S')
                times[t] = val
            except ValueError:
                print(f"Invalid time format for {val}.")
                input("Press Enter to continue...")
                return
        payload = dict(first_name=first_name, last_name=last_name, unique_id=unique_id, on_study=on_study, phone_number=phone_number, **times)
        if self.api("POST", "add_participant", json=payload):
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
                uptime_data = self.api("GET", "uptime")
                if uptime_data:
                    print(f"PRISM Uptime: {uptime_data.get('uptime', 'Unknown')}")
                else:
                    print("PRISM not running or inaccessible.")
                mode_data = self.api("GET", "get_mode")
                if mode_data:
                    print(f"PRISM Mode: {mode_data.get('mode', 'Unknown')}")
                else:
                    print("PRISM not running or inaccessible.")
                input("Press Enter to continue...")

            # Manage System Tasks
            elif choice == '2':
                while True:
                    self.print_system_task_schedule()
                    task_choice = input("Enter choice: ").strip()
                    if task_choice == '1':
                        task_types = self.get_task_types()
                        if not task_types:
                            input("No task types available. Press Enter to continue...")
                            continue
                        print("Available Tasks:")
                        for i, (k,v) in enumerate(task_types.items(),1):
                            print(f"{i}: {v} ({k})")
                        idx = input("Task index to add: ").strip()
                        if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
                            print("Invalid index.")
                            input("Press Enter to continue...")
                            continue
                        task_type = list(task_types.keys())[int(idx)-1]
                        task_time = input("Task time (HH:MM:SS): ").strip()
                        try:
                            time.strptime(task_time, '%H:%M:%S')
                        except ValueError:
                            print("Invalid time format.")
                            input("Press Enter to continue...")
                            continue
                        self.add_system_task(task_type, task_time)
                    elif task_choice == '2':
                        try:
                            idx = int(input("Task index to remove: ")) - 1
                            if 0 <= idx < len(self.scheduled_tasks):
                                t = self.scheduled_tasks[idx]
                                self.remove_system_task(t['task_type'], t['task_time'])
                            else:
                                print("Invalid index.")
                                input("Press Enter to continue...")
                        except Exception:
                            print("Invalid input.")
                            input("Press Enter to continue...")
                    elif task_choice == '3':
                        task_types = self.get_task_types()
                        if not task_types:
                            input("No task types available. Press Enter to continue...")
                            continue
                        print("Available Tasks:")
                        for i, (k,v) in enumerate(task_types.items(),1):
                            print(f"{i}: {v} ({k})")
                        idx = input("Task index to execute: ").strip()
                        if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
                            print("Invalid index.")
                            input("Press Enter to continue...")
                            continue
                        task_type = list(task_types.keys())[int(idx)-1]
                        if self.api("POST", f"execute_task/{task_type}"):
                            print(f"Task {task_type} executed.")
                        else:
                            print("Failed to execute task.")
                        input("Press Enter to continue...")
                    elif task_choice == '':
                        break
                    else:
                        print("Invalid choice.")
                        input("Press Enter to continue...")

            # Manage Participants
            elif choice == '3':
                while True:
                    clear()
                    data = self.api("GET", "get_participants")
                    participants = data.get("participants", []) if data else []
                    print("Participant List:")
                    if participants:
                        for i, p in enumerate(participants, 1):
                            print(f"{i}: {p['last_name']}, {p['first_name']} (ID: {p['unique_id']}) - On Study: {p['on_study']}")
                    else:
                        print("No participants found or failed to retrieve.")
                    print("\na: Add a Participant\nENTER: Back to Main Menu")
                    choice = input("Enter index, 'a', or ENTER: ").strip()
                    if choice.isdigit():
                        idx = int(choice)-1
                        if 0 <= idx < len(participants):
                            self.print_participant_schedule(participants[idx]['unique_id'])
                    elif choice.lower() == 'a':
                        self.add_participant()
                    elif choice == '':
                        break
                    else:
                        print("Invalid choice.")
                        input("Press Enter to continue...")

            # View Logs
            elif choice == '4':
                while True:
                    clear()
                    print("View Logs\n1: Today's Transcript\n\nENTER: Back to Main Menu")
                    log_choice = input("Enter your choice: ").strip()
                    if log_choice == '':
                        break
                    elif log_choice == '1':
                        lines = input("Number of lines to display (default 10): ").strip() or '10'
                        if not lines.isdigit():
                            print("Invalid number.")
                            input("Press Enter to continue...")
                            continue
                        data = self.api("GET", f"get_transcript/{lines}")
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
                clear()
                if self.api("GET", "uptime") is not None:
                    if input("Shutdown PRISM? (yes/no): ").strip().lower() == 'yes':
                        try:
                            self.api("POST", "shutdown")
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