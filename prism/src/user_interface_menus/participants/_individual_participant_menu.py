# menu for managing an individual participant

import time

from user_interface_menus.utils._menu_display import *
from user_interface_menus._menu_helper import *

def individual_participant_menu(self, participant_id):
    def remove_participant_menu(self):
        if prompt_confirmation(self, prompt = "Remove participant?"):
            if self.api("DELETE", f"participants/remove_participant/{participant_id}"):
                success("Participant removed.", self)
                return 1
            else:
                error("Failed to remove participant.", self)
                return 0

    def update_field_menu(self, choice):
        field_map = {
            '1': 'first_name', '2': 'last_name', '3': 'unique_id', '4': 'on_study',
            '5': 'phone_number', '6': 'ema_time', '7': 'ema_reminder_time',
            '8': 'feedback_time', '9': 'feedback_reminder_time'
        }
        field = field_map[choice]
        new_val = get_input(self, prompt = f"Enter new value for {field}: ")

        if field == 'on_study':
            if new_val.lower() in ['true', 'True', 't', 'T']:
                new_val = "True"
            elif new_val.lower() in ['false', 'False', 'f', 'F']:
                new_val = "False"
            else:
                error("Invalid input for on_study. Please enter 'True' or 'False'.")
                return
        elif field in ['ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']:
            try:
                time.strptime(new_val, '%H:%M:%S')
            except ValueError:
                error(f"Invalid time format for {field}. Please use HH:MM:SS format.")
                return

        if self.api("PUT", f"participants/update_participant/{participant_id}/{field}/{new_val}"):
            participant[field] = new_val
            success("Participant updated.", self)
        else:
            error("Failed to update participant.", self)

    def send_survey_menu(self, participant_id):
        survey_type = get_input(self, prompt = "Enter survey type (ema/feedback): ").lower()
        if survey_type in ['ema', 'feedback']:
            if self.api("POST", f"participants/send_survey/{participant_id}/{survey_type}"):
                success(f"{survey_type.capitalize()} survey sent.", self)
            else:
                error(f"Failed to send {survey_type} survey.", self)
        else:
            error("Invalid survey type.", self)

    def send_message_menu(self, participant_id):
        message = print_twilio_terminal_prompt()
        if not message:
            error("Message cannot be empty.")
            return
        if self.api("POST", f"participants/send_custom_sms/{participant_id}", json={"message": message}):
            success("Message sent.", self)
        else:
            error("Failed to send message.", self)

    data = self.api("GET", f"participants/get_participant/{participant_id}")
    participant = data.get("participant") if data else None
    if not participant:
        error("Failed to retrieve participant schedule.")
        return
    
    while True:
        # menu options are redefined on each iteration to reflect current participant data
        menu_options = {
            '1': {'description': f'first_name: {participant.get('first_name')}', 'menu_caller': lambda self: update_field_menu(self, '1')},
            '2': {'description': f'last_name: {participant.get('last_name')}', 'menu_caller': lambda self: update_field_menu(self, '2')},
            '3': {'description': f'unique_id: {participant.get('unique_id')}', 'menu_caller': lambda self: update_field_menu(self, '3')},
            '4': {'description': f'on_study: {participant.get('on_study')}', 'menu_caller': lambda self: update_field_menu(self, '4')},
            '5': {'description': f'phone_number: {participant.get('phone_number')}', 'menu_caller': lambda self: update_field_menu(self, '5')},
            '6': {'description': f'ema_time: {participant.get('ema_time')}', 'menu_caller': lambda self: update_field_menu(self, '6')},
            '7': {'description': f'ema_reminder_time: {participant.get('ema_reminder_time')}', 'menu_caller': lambda self: update_field_menu(self, '7')},
            '8': {'description': f'feedback_time: {participant.get('feedback_time')}', 'menu_caller': lambda self: update_field_menu(self, '8')},
            '9': {'description': f'feedback_reminder_time: {participant.get('feedback_reminder_time')}', 'menu_caller': lambda self: update_field_menu(self, '9')},
            'remove': {'description': 'Remove Participant', 'menu_caller': lambda self: remove_participant_menu(self)},
            'survey': {'description': 'Send Survey', 'menu_caller': lambda self: send_survey_menu(self, participant_id)},
            'message': {'description': 'Send Message', 'menu_caller': lambda self: send_message_menu(self, participant_id)}
        }
        clear_recommended_actions()
        if not self.commands_queue:
            print_menu_header(f"Participant ID {participant_id} Info")
        print("Enter an index to update a field, or, choose another option.")
        print_dashes()
        if print_menu_options(self, menu_options, submenu = True, index_and_text = True):
            break
