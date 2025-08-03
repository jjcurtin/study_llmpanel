# participant management menus

from user_interface_menus._menu_helper import *
from user_interface_menus.participants._individual_participant_menu import individual_participant_menu
from user_interface_menus.participants._add_participant_menu import add_participant_menu

# ------------------------------------------------------------

def refresh_participants_menu(self):
    if get_input(self, prompt = "Refresh participants from CSV? (yes/no): ").lower() == 'yes':
        if self.api("POST", "participants/refresh_participants"):
            success("Participants refreshed from CSV.")
        else:
            error(f"Failed to refresh participants. Error code: {self.api('POST', 'participants/refresh_participants').get('status_code', 'Unknown')}")
    else:
        success("Refresh cancelled.")

def send_announcement_menu(self):
    require_on_study = get_input(self, prompt = "Send to participants on study only? (yes/no): ").lower()
    if require_on_study not in ('yes', 'y', 'no', 'n'):
        error("Invalid input. Cancelling. Press Enter to continue...")
        return
    message = print_twilio_terminal_prompt()
    if not message:
        error("Message cannot be empty. Please try again.")
        return
    
    if self.api("POST", f"participants/study_announcement/{require_on_study}", json = {"message": message}):
        success("Study announcement sent.")
    else:
        error("No participants found or failed to retrieve.")

def remove_participant_menu(self):
    participant_id = get_input(self, prompt = "Please enter the unique ID of the participant that you would like to remove: ")
    if not participant_id or participant_id.strip() == '':
        error("Participant ID cannot be empty.")
        return 0
    if get_input(self, prompt = f"Are you sure you want to remove participant with ID '{participant_id}'? (yes/no): ").lower() == 'yes':
        if self.api("DELETE", f"participants/remove_participant/{participant_id}"):
            success("Participant removed.", self)
            return 1
        else:
            error("Failed to remove participant. Unique ID not found", self)
            return 0

# ------------------------------------------------------------

def participant_management_menu(self):
    def print_task_schedule(self):
        tasks = self.api("GET", "participants/get_participant_task_schedule")
        if tasks:
            print("Participant Task Schedule:")
            for task in tasks.get("tasks", []):
                print(f"{task['participant_id']}: {task['task_type']} at {task['task_time']} - On Study: {task['on_study']}")
            exit_menu()

    while True:
        print_menu_header("participants")
        menu_options = {}

        # Fetch participants from the API
        data = self.api("GET", "participants/get_participants")
        participants = data.get("participants", []) if data else []
        if participants:
            for i, p in enumerate(participants, 1):
                menu_options[str(i)] = {
                    'description': f"{p['last_name']}, {p['first_name']} (ID: {p['unique_id']}) - On Study: {p['on_study']}",
                    'menu_caller': lambda self, participant_id = p['unique_id']: individual_participant_menu(self, participant_id)
                }
        else:
            print("No participants found or failed to retrieve.")
        menu_options['add'] = {'description': 'Add a Participant', 'menu_caller': add_participant_menu}
        menu_options['schedule'] = {'description': 'Get Participant Task Schedule', 'menu_caller': print_task_schedule}
        menu_options['refresh'] = {'description': 'Full Participants Refresh from CSV', 'menu_caller': refresh_participants_menu}
        menu_options['announcement'] = {'description': 'Send Study Announcement', 'menu_caller': send_announcement_menu}
        menu_options['remove'] = {'description': 'Remove a Participant', 'menu_caller': remove_participant_menu}
        print("Enter an index to select a participant, or, choose another option.")
        print_dashes()
        if print_menu_options(self, menu_options, submenu = True, index_and_text = True):
            break

# ------------------------------------------------------------

global ADD_PARTICIPANT
ADD_PARTICIPANT = add_participant_menu

global PARTICIPANT_REFRESH
PARTICIPANT_REFRESH = refresh_participants_menu

global PARTICIPANT_ANNOUNCEMENT
PARTICIPANT_ANNOUNCEMENT = send_announcement_menu