import os
from datetime import datetime
import queue
import threading
from _routes import create_flask_app
import pandas as pd
import importlib
from waitress import serve
from _helper import send_sms

class PRISM():
    def __init__(self, mode="test", hot_reload = False, notify_coordinators = False):
        self.clear()
        self.add_to_transcript("Initializing PRISM application...", "INFO")
        self.mode = mode
        self.hot_reload = hot_reload
        self.notify_coordinators = notify_coordinators
        

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
        threading.Thread(target = self.run_system_task_processor, daemon = True).start()

        # set up participant sms thread
        self.participants = []
        self.load_participants()
        self.sms_queue = queue.Queue()
        threading.Thread(target = self.run_participant_sms_processor, daemon = True).start()

        # set up participant API call thread

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

    ############################
    #        Task Logic        #
    ############################

    # update task types
    def update_task_types(self):
        self.add_to_transcript("Loading task types...", "INFO")
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

        if self.hot_reload:
            self.update_task_types()  # Ensure task types are up to date

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

    def run_system_task_processor(self):
        # task processing loop
        self.add_to_transcript("Starting system task processor...", "INFO")
        while self.running:
            self.check_scheduled_tasks()
            try:
                result = self.process_task(self.task_queue.get(timeout = 1))
            except queue.Empty:
                pass
            except Exception as e:
                print(f"An error occurred while processing tasks: {e}")
                self.running = False

    #######################################
    #        Participant SMS Logic        #
    #######################################

    def load_participants(self):
        # ../config/study_participants.csv contains the following information:
        # "unique_id","last_name","first_name","on_study","phone_number","ema_time","ema_reminder_time","feedback_time","feedback_reminder_time"
        self.add_to_transcript("Loading study participants...", "INFO")
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

        # schedule SMS tasks for each participant
        self.scheduled_sms_tasks = []
        for participant in self.participants:
            # split up each participant into four separate tasks
            if participant['on_study']:

                participant_name = f"{participant['first_name']} {participant['last_name']}"
                participant_id = participant['unique_id']
                participant_phone_number = participant['phone_number']

                if participant['ema_time']:
                    self.scheduled_sms_tasks.append({
                        'task_type': 'ema',
                        'task_time': datetime.strptime(participant['ema_time'], '%H:%M:%S').time(),
                        'participant_name': participant_name,
                        'participant_id': participant_id,
                        'participant_phone_number': participant_phone_number,
                        'run_today': False  # Flag to indicate if the task has run today
                    })
                if participant['ema_reminder_time']:
                    self.scheduled_sms_tasks.append({
                        'task_type': 'ema_reminder',
                        'task_time': datetime.strptime(participant['ema_reminder_time'], '%H:%M:%S').time(),
                        'participant_name': participant_name,
                        'participant_id': participant_id,
                        'participant_phone_number': participant_phone_number,
                        'run_today': False  # Flag to indicate if the task has run today
                    })
                if participant['feedback_time']:
                    self.scheduled_sms_tasks.append({
                        'task_type': 'feedback',
                        'task_time': datetime.strptime(participant['feedback_time'], '%H:%M:%S').time(),
                        'participant_name': participant_name,
                        'participant_id': participant_id,
                        'participant_phone_number': participant_phone_number,
                        'run_today': False  # Flag to indicate if the task has run today
                    })
                if participant['feedback_reminder_time']:
                    self.scheduled_sms_tasks.append({
                        'task_type': 'feedback_reminder',
                        'task_time': datetime.strptime(participant['feedback_reminder_time'], '%H:%M:%S').time(),
                        'participant_name': participant_name,
                        'participant_id': participant_id,
                        'participant_phone_number': participant_phone_number,
                        'run_today': False  # Flag to indicate if the task has run today
                    })

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
        task_type = sms_task['task_type']
        participant_name = sms_task['participant_name']
        participant_id = sms_task['participant_id']
        participant_phone_number = sms_task['participant_phone_number']
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
        self.add_to_transcript("Starting participant SMS processor...", "INFO")
        while self.running:
            self.check_scheduled_sms()
            try:
                result = self.process_participant_sms(self.sms_queue.get(timeout = 1))
            except queue.Empty:
                pass
            except Exception as e:
                print(f"An error occurred while processing participant SMS: {e}")
                self.running = False

if __name__ == "__main__":
    mode = "test"
    hot_reload = True
    notify_coordinators = False
    prism = PRISM(mode = "test", hot_reload = True, notify_coordinators = False)
    if hot_reload:
        prism.add_to_transcript("Running in hot reload mode.", "INFO")
    if prism.notify_coordinators:
        prism.add_to_transcript("Coordinators will be notified of the results of system tasks.", "INFO")
    else:
        prism.add_to_transcript("Coordinators will not be notified of the results of system tasks.", "INFO")
    prism.add_to_transcript(f"PRISM started with {len(prism.scheduled_tasks)} scheduled system tasks", "INFO")
    if mode == "test":
        prism.add_to_transcript("Running in test mode. Flask app will be served on localhost:5000", "INFO")
        serve(prism.flask_app, host = '127.0.0.1', port = 5000)
    elif mode == "prod":
        prism.add_to_transcript("Running in production mode. Flask app will be served on all interfaces on port 5000", "INFO")
        serve(prism.flask_app, host = '0.0.0.0', port = 5000)