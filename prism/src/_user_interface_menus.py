import requests
import time
from _helper import clear
import random

def error(message = "An unexpected error occurred."):
        print(f"Error: {message}")
        input("Press Enter to continue...")

def success(message = "Operation completed successfully."):
    print(f"Success: {message}")
    input("Press Enter to continue...")
    
def exit_menu():
    input("Press Enter to continue...")

def log_menu(self):
    while True:
        clear()
        print("View Logs\n1: Today's Transcript\n2: EMA log\n3: Feedback survey log\n\nENTER: Back to Main Menu")
        log_choice = input("Enter your choice: ").strip()
        if log_choice == '':
            break
        elif log_choice == '1' or log_choice == '2' or log_choice == '3':
            lines = input("Number of lines to display (default 10): ").strip() or '10'
            if not lines.isdigit():
                error("Invalid number of lines. Please enter a valid integer.")
                continue

            log_type = "get_transcript" if log_choice == '1' else "get_ema_log" if log_choice == '2' else "get_feedback_log" if log_choice == '3' else None
            self.request_transcript(lines, log_type)
            exit_menu()
        else:
            error("Invalid choice. Please try again.")

def participant_management_menu(self):
    def print_task_schedule():
        tasks = self.api("GET", "participants/get_participant_task_schedule")
        if tasks:
            print("Participant Task Schedule:")
            for task in tasks.get("tasks", []):
                print(f"{task['participant_id']}: {task['task_type']} at {task['task_time']} - On Study: {task['on_study']}")
            exit_menu()

    def refresh_participants_menu(self):
        if input("Refresh participants from CSV? (yes/no): ").strip().lower() == 'yes':
            if self.api("POST", "participants/refresh_participants"):
                success("Participants refreshed from CSV.")
            else:
                error(f"Failed to refresh participants. Error code: {self.api('POST', 'participants/refresh_participants').get('status_code', 'Unknown')}")
        else:
            success("Refresh cancelled.")

    def send_announcement_menu(self):
        message = input("Enter study announcement message: ").strip()
        if not message:
            error("Message cannot be empty. Please try again.")
            return
        require_on_study = input("Send to participants on study only? (yes/no): ").strip().lower()
        if require_on_study not in ('yes', 'y', 'no', 'n'):
            error("Invalid input. Cancelling. Press Enter to continue...")
            return
        if self.api("POST", f"participants/study_announcement/{require_on_study}", json = {"message": message}):
            success("Study announcement sent.")
        else:
            error("No participants found or failed to retrieve.")

    while True:
        clear()
        participants = self.get_participants()
        print("\na: Add a Participant\ns: Get Participant Task Schedule\nr: Full Participants Refresh from CSV\nn: study announcement\n\nENTER: Back to Main Menu")
        choice = input("Enter index, 'a', 's', 'r', 'n', or ENTER: ").strip()
        if choice.isdigit():
            idx = int(choice)-1
            if 0 <= idx < len(participants):
                individual_participant_menu(self, participants[idx]['unique_id'])
        elif choice.lower() == 'a':
            add_participant_menu(self)
        elif choice.lower() == 's':
            print_task_schedule()
        elif choice.lower() == 'r':
            refresh_participants_menu(self)
        elif choice.lower() == 'n':
            send_announcement_menu(self)
        elif choice == '':
            break
        else:
            error("Invalid choice.")

def individual_participant_menu(self, participant_id):
        def remove_participant_menu(self):
            if input("Remove participant? (yes/no): ").strip().lower() == 'yes':
                if self.api("DELETE", f"participants/remove_participant/{participant_id}"):
                    success("Participant removed.")
                    return
                else:
                    error("Failed to remove participant.")

        def update_field_menu(self, choice):
            field = field_map[choice]
            new_val = input(f"Enter new value for {field}: ")
            if self.api("PUT", f"participants/update_participant/{participant_id}/{field}/{new_val}"):
                participant[field] = new_val
                success("Participant updated.")
            else:
                error("Failed to update participant.")

        def send_survey_menu(self, participant_id):
            survey_type = input("Enter survey type (ema/feedback): ").strip().lower()
            if survey_type in ['ema', 'feedback']:
                if self.api("POST", f"participants/send_survey/{participant_id}/{survey_type}"):
                    success(f"{survey_type.capitalize()} survey sent.")
                else:
                    error(f"Failed to send {survey_type} survey.")
            else:
                error("Invalid survey type.")

        def send_message_menu(self, participant_id):
            message = input("Enter message to send: ").strip()
            if not message:
                error("Message cannot be empty.")
                return
            if self.api("POST", f"participants/send_custom_sms/{participant_id}", json={"message": message}):
                success("Message sent.")
            else:
                error("Failed to send message.")

        data = self.api("GET", f"participants/get_participant/{participant_id}")
        participant = data.get("participant") if data else None
        if not participant:
            error("Failed to retrieve participant schedule.")
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
                update_field_menu(self, choice)
            elif choice.lower() == 'r':
                remove_participant_menu(self)
            elif choice.lower() == 's':
                send_survey_menu(self, participant_id)
            elif choice.lower() == 'm':
                send_message_menu(self, participant_id)
            else:
                error("Invalid choice.")

def add_participant_menu(self):
        clear()
        print("Add New Participant")
        first_name = input("First name: ")
        if not first_name:
            error("First name is required.")
            return
        last_name = input("Last name: ")
        if not last_name:
            error("Last name is required.")
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
            success("Participant added.")
        else:
            error("Failed to add participant.")

def system_check_menu(self):
    clear()
    print("Requesting PRISM status...")
    uptime_data = self.api("GET", "system/uptime")
    mode_data = self.api("GET", "system/get_mode")

    if uptime_data and mode_data:
        print(f"PRISM Uptime: {uptime_data.get('uptime', 'Unknown')}")
        print(f"PRISM Mode: {mode_data.get('mode', 'Unknown')}")
        choice = input("Would you like to run system checks (CHECK_SYSTEM Task)? (yes/no): ").strip().lower()
        if choice in ('yes', 'y'):
            if self.api("POST", "system/execute_task/CHECK_SYSTEM"):
                success("System checks complete. No issues found.")
            else:
                self.request_transcript(25, "get_transcript")
                error("Failure detected. Please check the transcript for details.")
    else:
        error("PRISM not running or inaccessible.")

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

def main_menu(self):
    while True:
        clear()
        print("PRISM Interface Menu:")
        print("1: Get Status and Check System")
        print("2: Manage System Tasks")
        print("3: Manage Participants")
        print("4: View Logs")
        print("5: Shutdown PRISM")
        print("6: Exit")
        choice = input("Enter your choice: ").strip()
        
        # get mode and uptime
        if choice == '1':
            system_check_menu(self)

        # Manage System Tasks
        elif choice == '2':
            task_schedule_menu(self)

        # Manage Participants
        elif choice == '3':
            participant_management_menu(self)

        # View Logs
        elif choice == '4':
            log_menu(self)

        # Shutdown PRISM
        elif choice == '5':
            shutdown_menu(self)

        # Exit
        elif choice == '6':
            print("Exiting PRISM Interface.")
            break

        else:
            error("Invalid choice.")

def task_schedule_menu(self):
        while True:
            clear()
            print("System Task Schedule:")
            tasks = self.api("GET", "system/get_task_schedule")
            if tasks and "tasks" in tasks:
                self.scheduled_tasks = tasks["tasks"]
                if self.scheduled_tasks:
                    for i, t in enumerate(self.scheduled_tasks, 1):
                        print(f"{i}. {t['task_type']} @ {t['task_time']}{f" {t['r_script_path']}" if t['r_script_path'] else ""} - Run Today: {t.get('run_today', False)}")
                else:
                    print("No tasks scheduled.")
            else:
                print("Failed to retrieve task schedule or PRISM not running.")
            print("\n1: Add New Task\n2: Remove Task\n3: Execute Task Now\n\nENTER: Back to Main Menu")  
            task_choice = input("Enter choice: ").strip()
            if task_choice == '1':
                task_types = self.get_task_types()
                if not task_types:
                    input("No task types available. Press Enter to continue...")
                    return
                print("Available Tasks:")
                for i, (k,v) in enumerate(task_types.items(),1):
                    print(f"{i}: {v} ({k})")
                idx = input("Task index to add: ").strip()
                if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
                    print("Invalid index.")
                    input("Press Enter to continue...")
                    return
                task_type = list(task_types.keys())[int(idx)-1]
                r_script_path = None
                
                if task_type == 'RUN_R_SCRIPT':
                    r_scripts = self.api("GET", "system/get_r_script_tasks")
                    if not r_scripts:
                        print("No R scripts available.")
                        input("Press Enter to continue...")
                        return
                    print("Available R Scripts:")
                    for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
                        print(f"{i}: {name}")
                    script_idx = input("Select R script index: ").strip()
                    r_script_dict = r_scripts['r_script_tasks']
                    script_names = list(r_script_dict.keys())

                    if not script_idx.isdigit() or not (1 <= int(script_idx) <= len(script_names)):
                        print("Invalid index.")
                        input("Press Enter to continue...")
                        return
                    selected_script_name = script_names[int(script_idx) - 1]
                    r_script_path = f"{r_script_dict[selected_script_name]}.R"

                task_time = input("Task time (HH:MM:SS): ").strip()
                try:
                    time.strptime(task_time, '%H:%M:%S')
                except ValueError:
                    print("Invalid time format.")
                    input("Press Enter to continue...")
                    return

                self.add_system_task(task_type, task_time, r_script_path)
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
                    return
                print("Available Tasks:")
                for i, (k,v) in enumerate(task_types.items(),1):
                    print(f"{i}: {v} ({k})")
                idx = input("Task index to execute: ").strip()
                if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
                    print("Invalid index.")
                    input("Press Enter to continue...")
                    return
                task_type = list(task_types.keys())[int(idx)-1]

                if task_type == 'RUN_R_SCRIPT':
                    r_scripts = self.api("GET", "system/get_r_script_tasks")
                    if not r_scripts:
                        print("No R scripts available.")
                        input("Press Enter to continue...")
                        return
                    print("Available R Scripts:")
                    for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
                        print(f"{i}: {name}")
                    script_idx = input("Select R script index: ").strip()
                    r_script_dict = r_scripts['r_script_tasks']
                    script_names = list(r_script_dict.keys())

                    if not script_idx.isdigit() or not (1 <= int(script_idx) <= len(script_names)):
                        print("Invalid index.")
                        input("Press Enter to continue...")
                        return
                    selected_script_name = script_names[int(script_idx) - 1]
                    r_script_path = f"{r_script_dict[selected_script_name]}.R"
                    print(f"Executing R script: {selected_script_name} at {r_script_path}")
                    if self.api("POST", f"system/execute_r_script_task/{r_script_path}"):
                        print(f"R script task {selected_script_name} executed.")
                    else:
                        print(f"Failed to execute R script task {selected_script_name}.")
                elif self.api("POST", f"system/execute_task/{task_type}"):
                    print(f"Task {task_type} executed.")
                else:
                    print("Failed to execute task.")
                    data = self.api("GET", f"system/get_transcript/{15}")
                    if data and "transcript" in data:
                        for entry in data["transcript"]:
                            print(f"{entry['timestamp']} - {entry['message']}")
                    else:
                        print("No transcript found or failed to retrieve.")

                input("Press Enter to continue...")
            elif task_choice == '':
                return
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")