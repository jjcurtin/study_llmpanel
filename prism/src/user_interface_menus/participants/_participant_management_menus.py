# participant management menus

from user_interface_menus._menu_helper import *
from user_interface_menus.participants._individual_participant_menu import individual_participant_menu
from user_interface_menus.participants._add_participant_menu import add_participant_menu

# ------------------------------------------------------------

def refresh_participants_menu(self):
    if prompt_confirmation(self, prompt = "Refresh participants from CSV?"):
        if self.api("POST", "participants/refresh_participants"):
            success("Participants refreshed from CSV.", self)
        else:
            error(f"Failed to refresh participants. Error code: {self.api('POST', 'participants/refresh_participants').get('status_code', 'Unknown')}", self)
    else:
        success("Refresh cancelled.", self)

def send_announcement_menu(self):
    require_on_study = prompt_confirmation(self, prompt = "Send to participants on study only?", default_value = "y")
    print("Sending to participants on study only." if require_on_study else "Sending to all participants.")
    message = print_twilio_terminal_prompt()
    if not message:
        error("Message cannot be empty. Please try again.", self)
        return
    
    if self.api("POST", f"participants/study_announcement/{require_on_study}", json = {"message": message}):
        success("Study announcement sent.", self)
    else:
        error("No participants found or failed to retrieve.", self)

def remove_participant_menu(self):
    participant_id = get_input(self, prompt = "Please enter the unique ID of the participant that you would like to remove: ")
    if not participant_id or participant_id.strip() == '':
        error("Participant ID cannot be empty.")
        return 0
    if prompt_confirmation(self, prompt = f"Are you sure you want to remove participant with ID '{participant_id}'?"):
        if self.api("DELETE", f"participants/remove_participant/{participant_id}"):
            success("Participant removed.", self)
            return 1
        else:
            error("Failed to remove participant. Unique ID not found", self)
            return 0
        
def access_specific_participant_menu(self):
    participant_id = get_input(self, prompt = "Please enter the unique ID of the participant that you would like to access: ")
    if not participant_id or participant_id.strip() == '':
        error("Participant ID cannot be empty.")
        return 0
    data = self.api("GET", f"participants/get_participant/{participant_id}")
    if data:
        individual_participant_menu(self, participant_id)
    else:
        error("Failed to retrieve participant data. Unique ID not found.", self)
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

    def _sort(participants):
        if self.participant_display_mode == "name":
            return sorted(participants, key = lambda x: (x['last_name'].lower(), x['first_name'].lower()))
        elif self.participant_display_mode == "unique_id":
            return sorted(participants, key = lambda x: int(x['unique_id']))
        elif self.participant_display_mode == "on_study":
            on_study_true = sorted([p for p in participants if p['on_study']], key = lambda x: int(x['unique_id']))
            on_study_false = sorted([p for p in participants if not p['on_study']], key = lambda x: int(x['unique_id']))
            return on_study_true + on_study_false
        else:
            return participants
        
    def change_display_mode(self):
        modes = ["name", "unique_id", "on_study"]
        print("Select display mode:")
        for mode in modes:
            print(f"{yellow(mode)}")
        print("Current mode:", red(self.participant_display_mode))
        choice = get_input(self, prompt = "Enter the mode you'd like to change to: ")
        if choice in modes:
            self.participant_display_mode = choice
            success(f"Display mode changed to {self.participant_display_mode}.", self)
        else:
            error("Invalid mode selected.", self)

    def _filter(participants):
        if not self.participant_filter_settings:
            return participants
        filtered = []
        for p in participants:
            if self.participant_filter_settings.get('on_study', 'All') == "All" or \
               (self.participant_filter_settings.get('on_study', 'All') == "True" and p['on_study']) or \
               (self.participant_filter_settings.get('on_study', 'All') == "False" and not p['on_study']):
                filtered.append(p)
        return filtered

    def filter_participants_menu(self):
        print("Current filter settings:")
        for key, value in self.participant_filter_settings.items():
            print(f"{key}: {value}")
        print("Available filters: on_study")
        filter_choice = get_input(self, prompt = "Enter filter to change: ")
        if filter_choice == '':
            return
        elif filter_choice not in self.participant_filter_settings:
            error(f"Invalid filter choice: {filter_choice}. Available filters: {', '.join(self.participant_filter_settings.keys())}", self)
            return
        new_value = get_input(self, prompt = f"Enter new value for {filter_choice} (True/False/All): ")
        if new_value not in ['True', 'False', 'All']:
            error("Invalid value. Please enter 'True', 'False', or 'All'.", self)
            return
        self.participant_filter_settings[filter_choice] = new_value
        success(f"Filter {filter_choice} set to {new_value}.", self)
        
    try:
        self.participant_display_mode = getattr(self, 'participant_display_mode', 'unique_id')
        if not self.participant_display_mode:
            self.participant_display_mode = 'unique_id'
        self.participant_filter_settings = getattr(self, 'participant_filter_settings', {})
        if not self.participant_filter_settings:
            self.participant_filter_settings = {
                'on_study': "All"
            }
        while True:
            index_and_text = True
            print_menu_header("participants")
            menu_options = {}

            # Fetch participants from the API
            data = self.api("GET", "participants/get_participants")
            participants = data.get("participants", []) if data else []
            if participants:
                for i, p in enumerate(_sort(_filter(participants)), 1):
                    menu_options[str(i)] = {
                        'description': f"{p['last_name']}, {p['first_name']} (ID: {p['unique_id']}) - On Study: {p['on_study']}",
                        'menu_caller': lambda self, participant_id = p['unique_id']: individual_participant_menu(self, participant_id)
                    }
                print("Enter an index to select a participant, or, choose another option.")
                print("Current Display Mode:", red(self.participant_display_mode))
                print("Current Filter Settings:", self.participant_filter_settings)
                print_dashes()
            else:
                print(f"{red('No participants found or failed to retrieve.')}")
                print()
                index_and_text = False
            menu_options['add'] = {'description': 'Add a Participant', 'menu_caller': add_participant_menu}
            menu_options['schedule'] = {'description': 'Get Participant Task Schedule', 'menu_caller': print_task_schedule}
            menu_options['refresh'] = {'description': 'Full Participants Refresh from CSV', 'menu_caller': refresh_participants_menu}
            menu_options['announcement'] = {'description': 'Send Study Announcement', 'menu_caller': send_announcement_menu}
            menu_options['remove'] = {'description': 'Remove a Participant', 'menu_caller': remove_participant_menu}
            menu_options['access'] = {'description': 'Access Participant Data', 'menu_caller': access_specific_participant_menu}
            menu_options['sort'] = {'description': f'Sort Participants (Current: {self.participant_display_mode})', 'menu_caller': change_display_mode}
            menu_options['filter'] = {'description': 'Filter Participants', 'menu_caller': filter_participants_menu}
            
            if print_menu_options(self, menu_options, submenu = True, index_and_text = index_and_text):
                break
    except Exception as e:
        error(f"An error occurred in the participant management menu: {e}", self)

# ------------------------------------------------------------

global ADD_PARTICIPANT
ADD_PARTICIPANT = add_participant_menu

global PARTICIPANT_REFRESH
PARTICIPANT_REFRESH = refresh_participants_menu

global PARTICIPANT_ANNOUNCEMENT
PARTICIPANT_ANNOUNCEMENT = send_announcement_menu