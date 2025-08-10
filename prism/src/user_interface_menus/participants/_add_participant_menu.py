# menu for adding a participant

import random
import time

from user_interface_menus.utils._menu_display import *
from user_interface_menus._menu_helper import *

def add_participant_menu(self):
    clear_recommended_actions()
    if not self.commands_queue:
        print_menu_header("participants add")
    first_name = get_input(self, prompt = "First name: ")
    if not first_name:
        error("First name is required.", self)
        return
    last_name = get_input(self, prompt = "Last name: ")
    if not last_name:
        error("Last name is required.", self)
        return
    unique_id = get_input(self, prompt = "Unique ID: ")
    if not unique_id:
        unique_id = str(random.randint(100000000, 999999999))
        print(f"Unique ID not provided. Generated: {unique_id}")
    existing_participants = self.api("GET", "participants/get_participants")
    if existing_participants:
        for participant in existing_participants.get("participants", []):
            if participant.get("unique_id") == unique_id:
                new_unique_id = str(random.randint(100000000, 999999999))
                print(f"Unique ID '{unique_id}' already exists. Generated a new one: {new_unique_id}")
                unique_id = new_unique_id
    on_study = prompt_confirmation(self, prompt = "On study?")
    phone_number = get_input(self, prompt = "Phone number (press enter to skip): ")
    times = {}
    default_times = {
        'ema_time': '08:00:00',
        'ema_reminder_time': '08:15:00',
        'feedback_time': '18:00:00',
        'feedback_reminder_time': '18:15:00'
    }
    for t in ['ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']:
        val = get_input(self, prompt = f"Enter {t.replace('_', ' ')} (HH:MM:SS) ", default_value = default_times[t]) or default_times[t]
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
        success("Participant added.", self)
    else:
        error("Failed to add participant.", self)