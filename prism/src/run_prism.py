import os
from datetime import datetime
import queue
import threading
from _routes import create_flask_app
import pandas as pd
import importlib
from waitress import serve
from _helper import send_sms
import signal
from pyngrok import ngrok
import subprocess
import argparse

class PRISM():
    def __init__(self, mode = "test"):
        self.clear()
        self.add_to_transcript("Initializing PRISM application...", "INFO")
        self.mode = mode

        # make sure you are running in the src directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not current_dir.endswith('src'):
            self.add_to_transcript("Please run this script from the 'src' directory.", "ERROR")
            exit(1)

        # start tracking the uptime of the application
        self.running = True
        self.start_time = datetime.now()

        # load api keys
        self.load_api_keys()

        # create Flask app instance that will be run through waitress separately
        self.flask_app = create_flask_app(self)

        # set up system task processor thread
        self.update_task_types()
        self.scheduled_tasks = []
        self.load_task_schedule()
        self.task_queue = queue.Queue()
        self.system_task_thread = threading.Thread(target = self.run_system_task_processor)
        self.system_task_thread.start()

        # set up participant sms thread
        self.participants = []
        self.load_participants()
        self.schedule_sms_tasks()
        self.sms_queue = queue.Queue()
        self.sms_task_thread = threading.Thread(target = self.run_participant_sms_processor)
        self.sms_task_thread.start()

        # set up participant API call thread

        # set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)

        self.add_to_transcript(f"PRISM started in {self.mode} mode.", "INFO")

    ############################
    #       System Utils       #
    ############################

    def load_api_keys(self):
        try:
            qualtrics = pd.read_csv('../qualtrics.api', quotechar='"')
            self.qualtrics_api_token = qualtrics.loc[0, 'api_token']
            self.qualtrics_data_center = qualtrics.loc[0, 'datacenter']
            self.ema_survey_id = qualtrics.loc[0, 'ema_survey_id']
            self.feedback_survey_id = qualtrics.loc[0, 'feedback_survey_id']
        except Exception as e:
            self.add_to_transcript(f"Failed to load Qualtrics API keys: {e}", "ERROR")

        try:
            followmee = pd.read_csv('../followmee.api', quotechar='"')
            self.followmee_username = followmee.loc[0, 'username']  
            self.followmee_api_token = followmee.loc[0, 'api_token']
        except Exception as e:
            self.add_to_transcript(f"Failed to load FollowMee API keys: {e}", "ERROR")

        try:
            twilio = pd.read_csv('../twilio.api', quotechar='"')
            self.twilio_account_sid = twilio.loc[0, 'account_sid']
            self.twilio_auth_token = twilio.loc[0, 'auth_token']
            self.twilio_from_number = twilio.loc[0, 'from_number']
        except Exception as e:
            self.add_to_transcript(f"Failed to load Twilio API keys: {e}", "ERROR") 

        try:
            research_drive = pd.read_csv('../research_drive.api', quotechar='"')
            self.destination_path = research_drive.loc[0, 'destination_path']
            self.drive_letter = research_drive.loc[0, 'drive_letter']
            self.network_domain = research_drive.loc[0, 'network_domain']
            self.network_username = research_drive.loc[0, 'network_username']
            self.wisc_netid = research_drive.loc[0, 'wisc_netid']
            self.wisc_password = research_drive.loc[0, 'wisc_password']
        except Exception as e:
            self.add_to_transcript(f"Failed to load Research Drive API keys: {e}", "ERROR")

        try:
            ngrok = pd.read_csv('../ngrok.api', quotechar='"')
            self.ngrok_auth_token = ngrok.loc[0, 'auth_token']
            self.ngrok_domain = ngrok.loc[0, 'domain']
        except Exception as e:
            self.add_to_transcript(f"Failed to load Ngrok API keys: {e}", "ERROR")

    def get_uptime(self):
        return str(datetime.now() - self.start_time)
    
    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def stop(self):
        self.running = False

    def add_to_transcript(self, message, message_type = "INFO"):
        print(f"{message_type} - {message}")
        current_date = datetime.now().strftime('%Y-%m-%d')
        transcript_path = f'../logs/transcripts/{current_date}_transcript.txt'
        with open(transcript_path, 'a') as file:
            file.write(f"{datetime.now().strftime('%H:%M:%S')} - {message_type} - {message}\n")

    def clear_all_run_today_flags(self, system_tasks = False, sms_tasks = False):
        # Clear the run_today flag for all scheduled tasks
        if system_tasks:
            for task in self.scheduled_tasks:
                task['run_today'] = False

        # Clear the run_today flag for all scheduled SMS tasks
        if sms_tasks:
            for sms_task in self.scheduled_sms_tasks:
                sms_task['run_today'] = False

        self.add_to_transcript("Cleared all run_today flags for system and SMS tasks.", "INFO")

    def handle_shutdown(self, signum, frame):
        self.add_to_transcript("Received shutdown signal. Stopping PRISM application...", "INFO")
        self.stop()
        self.system_task_thread.join(timeout = 5)
        self.sms_task_thread.join(timeout = 5)
        os._exit(0)

    def shutdown(self):
        self.handle_shutdown(signal.SIGINT, None)

    ############################
    #        Task Logic        #
    ############################

    # update task types
    def update_task_types(self):
        self.task_types = {}
        task_files = [f for f in os.listdir('tasks') if f.endswith('.py') and f != '_task.py']
        for task_file in task_files:
            task_name = task_file[:-3]
            task_type = task_name.replace('_', ' ').title().replace(' ', '')
            task_name_for_dict = task_name.upper()
            if task_name_for_dict.startswith('_'):
                task_name_for_dict = task_name_for_dict[1:]
            self.task_types[task_name_for_dict] = task_type

    # schedule tasks from file
    def load_task_schedule(self):
        tasks = []
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', 'config', 'system_task_schedule.csv')
        try:
            with open(config_path, 'r') as file:
                lines = file.readlines()
                # Skip header line
                for line in lines[1:]:
                    if line.strip():  # Skip empty lines
                        task_type, task_time = line.strip().split(',')
                        tasks.append((task_type.strip('"'), task_time.strip('"')))
        except FileNotFoundError:
            self.add_to_transcript(f"Task schedule file not found at: {config_path}", "ERROR")
            return []
        except Exception as e:
            self.add_to_transcript(f"An error occurred while loading the task schedule: {e}", "ERROR")
            return []

        # Store scheduled tasks with their times
        self.scheduled_tasks = []
        for task_type, task_time_str in tasks:
            try:
                task_time = datetime.strptime(task_time_str, '%H:%M:%S').time()
                self.scheduled_tasks.append({
                    'task_type': task_type,
                    'task_time': task_time,
                    'run_today': False  # Flag to indicate if the task has run today
                })
            except ValueError:
                self.add_to_transcript(f"Invalid time format for task {task_type}: {task_time_str}", "ERROR")
            except Exception as e:
                self.add_to_transcript(f"An error occurred while scheduling task {task_type}: {e}", "ERROR")
        return tasks

    # add tasks to the queue when it is time to run it
    def check_scheduled_tasks(self):
        current_time = datetime.now().time()

        if current_time.hour == 0 and current_time.minute == 0:
            self.clear_all_run_today_flags(system_tasks = True)  # Reset run_today flags at midnight

        for task in self.scheduled_tasks:
            task_time = task['task_time']
            # Allow a small time window for matching tasks
            time_difference = abs((datetime.combine(datetime.today(), current_time) 
                                   - datetime.combine(datetime.today(), task_time)).total_seconds())
            if time_difference <= 1 and not task['run_today']:
                self.task_queue.put(task['task_type'])
                task['run_today'] = True

    # task run logic
    def process_task(self, task_type):
        self.add_to_transcript(f"Executing task: {task_type}", "INFO")
        result = 0  # Default result for successful execution

        # hot reload mode for test mode this only affects new tasks added during runtime so should not be needed in prod
        if self.mode == "test":
            self.update_task_types()

        # if the task is valid, import the task module and run it 
        # this allows for dynamic task loading and minor changes during prod if necessary
        if task_type in self.task_types:
            module_name = f'tasks._{task_type.lower()}'
            try:
                module = __import__(module_name, fromlist = [task_type])
                task_type = task_type.replace('_', ' ').title().replace(' ', '')
                module = importlib.reload(module)
                task_class = getattr(module, task_type)
            except ImportError as e:
                self.add_to_transcript(f"Failed to import task {task_type}: {e}", "ERROR")
                return -1
            except Exception as e:
                self.add_to_transcript(f"An error occurred while importing task {task_type}: {e}", "ERROR")
                return -1
            
            result = task_class(self).execute()
        else:
            self.add_to_transcript(f"Unknown task type: {task_type}", "ERROR")
            return -1

        return result

    # task processing loop
    def run_system_task_processor(self):
        while self.running:
            self.check_scheduled_tasks()
            try:
                result = self.process_task(self.task_queue.get(timeout = 1))
            except queue.Empty:
                pass
            except Exception as e:
                print(f"An error occurred while processing tasks: {e}")
                self.running = False
        self.add_to_transcript("System task processor stopped.", "INFO")

    #######################################
    #        Participant SMS Logic        #
    #######################################

    def load_participants(self):
        try:
            participants = []
            current_dir = os.path.dirname(os.path.abspath(__file__))
            with open(os.path.join(current_dir, '..', 'config', 'study_participants.csv'), 'r') as file:
                lines = file.readlines()
                for line in lines[1:]:
                    if line.strip():
                        parts = line.strip().split(',')
                        participant = {
                            'unique_id': parts[0].strip('"'),
                            'last_name': parts[1].strip('"'),
                            'first_name': parts[2].strip('"'),
                            'on_study': parts[3].strip('"').lower() == 'true',
                            'phone_number': parts[4].strip('"'),
                            'ema_time': parts[5].strip('"'),
                            'ema_reminder_time': parts[6].strip('"'),
                            'feedback_time': parts[7].strip('"'),
                            'feedback_reminder_time': parts[8].strip('"')
                        }
                        participants.append(participant)
            self.participants = participants
        except Exception as e:
            self.add_to_transcript(f"Failed to load participants from CSV: {e}", "ERROR")

    def schedule_sms_tasks(self):
        self.scheduled_sms_tasks = []
        for participant in self.participants:
            if participant['on_study']:
                participant_id = participant['unique_id']
                task_definitions = [
                    ('ema', 'ema_time'),
                    ('ema_reminder', 'ema_reminder_time'),
                    ('feedback', 'feedback_time'),
                    ('feedback_reminder', 'feedback_reminder_time')
                ]
                for task_type, time_key in task_definitions:
                    task_time_str = participant.get(time_key)
                    if task_time_str:
                        self.scheduled_sms_tasks.append({
                            'task_type': task_type,
                            'task_time': datetime.strptime(task_time_str, '%H:%M:%S').time(),
                            'participant_id': participant_id,
                            'run_today': False
                        })

    def get_participant(self, unique_id):
        for participant in self.participants:
            if participant['unique_id'] == unique_id:
                return participant
        self.add_to_transcript(f"Participant with ID {unique_id} not found.", "ERROR")
        return None
    
    def update_participant(self, unique_id, field, value):
        try:
            participant = self.get_participant(unique_id)
            if participant:
                if field in participant:
                    participant[field] = value
                    
                    # Update the participant in the CSV file
                    with open('../config/study_participants.csv', 'w') as f:
                        f.write('"unique_id","last_name","first_name","on_study","phone_number","ema_time","ema_reminder_time","feedback_time","feedback_reminder_time"')
                        for p in self.participants:
                            f.write(f'\n"{p["unique_id"]}","{p["last_name"]}","{p["first_name"]}","{p["on_study"]}","{p["phone_number"]}","{p["ema_time"]}","{p["ema_reminder_time"]}","{p["feedback_time"]}","{p["feedback_reminder_time"]}"')
                    
                    # If the field is a time field, update the participant's scheduled SMS tasks
                    if field in ['ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']:
                        task_type_map = {
                            'ema_time': 'ema',
                            'ema_reminder_time': 'ema_reminder',
                            'feedback_time': 'feedback',
                            'feedback_reminder_time': 'feedback_reminder'
                        }
                        task_type = task_type_map.get(field)
                        if task_type:
                            self.update_participant_task(participant, task_type, field)
                        else:
                            self.add_to_transcript(f"Invalid field for time update: {field}", "ERROR")
                            return 1
                    self.add_to_transcript(f"Updated {field} for participant {unique_id} to {value}.", "INFO")
                    return 0
                else:
                    self.add_to_transcript(f"Field {field} does not exist for participant {unique_id}.", "ERROR")
                    return 1
            else:
                self.add_to_transcript(f"Failed to update participant {unique_id}: Participant not found.", "ERROR")
                return 1
        except Exception as e:
            self.add_to_transcript(f"An error occurred while updating participant {unique_id}: {e}", "ERROR")
            return 1
    
    def update_participant_task(self, participant, task_type, time_field):
        if not participant['on_study']:
            return
        
        participant_id = participant['unique_id']
        
        # Remove old task of this type for this participant
        self.scheduled_sms_tasks = [
            task for task in self.scheduled_sms_tasks
            if not (task['task_type'] == task_type and task['participant_id'] == participant_id)
        ]
        
        time_str = participant.get(time_field)
        if time_str:
            self.scheduled_sms_tasks.append({
                'task_type': task_type,
                'task_time': datetime.strptime(time_str, '%H:%M:%S').time(),
                'participant_id': participant_id,
                'run_today': False
            })
        
    def add_participant(self, participant):
        try:
            self.participants.append(participant)

            # write to the csv file
            with open('../config/study_participants.csv', 'a') as f:
                f.write(f'\n"{participant["unique_id"]}","{participant["last_name"]}","{participant["first_name"]}","{participant["on_study"]}","{participant["phone_number"]}","{participant["ema_time"]}","{participant["ema_reminder_time"]}","{participant["feedback_time"]}","{participant["feedback_reminder_time"]}"')

            # Add the participant to the scheduled SMS tasks if they are on study
            if participant['on_study']:
                participant_id = participant['unique_id']
                task_definitions = [
                    ('ema', 'ema_time'),
                    ('ema_reminder', 'ema_reminder_time'),
                    ('feedback', 'feedback_time'),
                    ('feedback_reminder', 'feedback_reminder_time')
                ]
                for task_type, field_name in task_definitions:
                    self.scheduled_sms_tasks.append({
                        'task_type': task_type,
                        'task_time': datetime.strptime(participant[field_name], '%H:%M:%S').time(),
                        'participant_id': participant_id,
                        'run_today': False
                    })
            self.add_to_transcript(f"Added new participant via API: {participant['first_name']} {participant['last_name']}", "INFO")
        except Exception as e:
            self.add_to_transcript(f"Failed to add participant: {e}", "ERROR")
            return 1

    def remove_participant(self, unique_id):
        participant = self.get_participant(unique_id)
        if participant:
            self.participants.remove(participant)
            # write to the csv file
            with open('../config/study_participants.csv', 'w') as f:
                f.write('"unique_id","last_name","first_name","on_study","phone_number","ema_time","ema_reminder_time","feedback_time","feedback_reminder_time"')
                for p in self.participants:
                    f.write(f'\n"{p["unique_id"]}","{p["last_name"]}","{p["first_name"]}","{p["on_study"]}","{p["phone_number"]}","{p["ema_time"]}","{p["ema_reminder_time"]}","{p["feedback_time"]}","{p["feedback_reminder_time"]}"')
            
            # Remove the participant's tasks from the scheduled SMS tasks
            self.scheduled_sms_tasks = [
                task for task in self.scheduled_sms_tasks
                if task['participant_id'] != unique_id
            ]
            self.add_to_transcript(f"Removed participant {unique_id} via API", "INFO")
            return 0
        else:
            return 1
        
    def check_scheduled_sms(self):
        current_time = datetime.now().time()

        if current_time.hour == 0 and current_time.minute == 0:
            self.clear_all_run_today_flags(sms_tasks = True)

        for task in self.scheduled_sms_tasks:
            task_time = task['task_time']
            # Allow a small time window for matching tasks
            time_difference = abs((datetime.combine(datetime.today(), current_time) 
                                   - datetime.combine(datetime.today(), task_time)).total_seconds())
            if time_difference <= 1 and not task['run_today']:
                self.sms_queue.put(task)
                task['run_today'] = True

    def process_participant_sms(self, sms_task):
        participant_id = sms_task['participant_id']
        if not participant_id:
            self.add_to_transcript("Participant ID is missing in SMS task.", "ERROR")
            return -1
        else:
            participant = self.get_participant(participant_id)

            task_type = sms_task['task_type']
            participant_name = f"{participant['first_name']} {participant['last_name']}"
            participant_phone_number = participant['phone_number']
            self.add_to_transcript(f"Processing SMS task: {task_type} for participant {participant_id}", "INFO")

            if task_type == 'ema' or task_type == 'ema_reminder':
                survey_id = self.ema_survey_id
                if task_type == 'ema':
                    message = "it's time to take your ecological momentary assessment survey."
                else:
                    message = "you have not yet completed your ecological momentary assessment survey for today."
            elif task_type == 'feedback' or task_type == 'feedback_reminder':
                survey_id = self.feedback_survey_id
                if task_type == 'feedback':
                    message = "it's time to take your feedback survey."
                else:
                    message = "you have not yet completed your feedback survey for today."
            else:
                self.add_to_transcript(f"Unknown SMS task type: {task_type}", "ERROR")
                return -1

            survey_link = (
                f"https://uwmadison.co1.qualtrics.com/jfe/form/{survey_id}?ParticipantID={participant_id}"
            )
            body = f"{participant_name}, {message} {survey_link}"
            try:
                if self.mode == "prod":
                    send_sms(
                        self,
                        [participant_phone_number],
                        [body]
                    )
                self.add_to_transcript(f"SMS sent to {participant_id}.", "INFO")
                return 0
            except Exception as e:
                self.add_to_transcript(f"Failed to send SMS to {participant_id}: {e}", "ERROR")
                return -1

    def run_participant_sms_processor(self):
        # SMS processing loop
        while self.running:
            self.check_scheduled_sms()
            try:
                result = self.process_participant_sms(self.sms_queue.get(timeout = 1))
            except queue.Empty:
                pass
            except Exception as e:
                print(f"An error occurred while processing participant SMS: {e}")
                self.running = False
        self.add_to_transcript("Participant SMS processor stopped.", "INFO")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description = "Run the PRISM application.")
    parser.add_argument(
        '-mode', 
        choices = ['test', 'prod'], 
        default = 'test', 
        help = "Mode to run the application in. 'test' for development, 'prod' for production."
    )
    args = parser.parse_args()
    mode = args.mode
    
    prism = PRISM(mode = mode)

    if mode == "prod":
        ngrok.set_auth_token(prism.ngrok_auth_token)
        subprocess.Popen(
            ["ngrok", "http", f"--url={prism.ngrok_domain}", "5000"], 
            stdout = subprocess.DEVNULL,
            stderr = subprocess.DEVNULL
        )
    
    serve(prism.flask_app, host = '127.0.0.1', port = 5000)