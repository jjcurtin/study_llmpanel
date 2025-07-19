import time
from _helper import clear
import random

from user_interface_menus._menu_helper import error, success, exit_menu

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