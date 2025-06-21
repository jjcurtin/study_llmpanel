import os
from datetime import datetime
import queue
import threading
from _routes import create_flask_app
import pandas as pd
import importlib
from waitress import serve
from _helper import send_sms, clear, get_task_types
import signal
from pyngrok import ngrok
import subprocess
import argparse

class PRISM():
    def __init__(self, mode = "test"):
        if not os.path.dirname(os.path.abspath(__file__)).endswith('src'):
            self.add_to_transcript("Please run this script from the 'src' directory.", "ERROR")
            exit(1)
        
        clear()
        self.add_to_transcript("Initializing PRISM application...", "INFO")
        self.mode = mode
        self.running = True
        self.start_time = datetime.now()
        self.survey_types = {
            'ema': 'ema_time',
            'ema_reminder': 'ema_reminder_time',
            'feedback': 'feedback_time',
            'feedback_reminder': 'feedback_reminder_time'
        }
        self.system_task_schedule_file_path = '../config/system_task_schedule.csv'
        self.study_participants_file_path = '../config/study_participants.csv'

        self.load_api_keys()
        self.task_types = get_task_types()
        self.flask_app = create_flask_app(self)

        self.scheduled_tasks = []
        self.load_task_schedule()
        self.task_queue, self.system_task_thread = self.start_task_thread('System Task', self.scheduled_tasks, self.process_system_task)

        self.scheduled_sms_tasks, self.participants = [], []
        self.load_participants()
        self.sms_queue, self.sms_task_thread = self.start_task_thread('Participant SMS', self.scheduled_sms_tasks, self.process_participant_sms)

        signal.signal(signal.SIGINT, self.handle_shutdown)
        signal.signal(signal.SIGTERM, self.handle_shutdown)
        self.add_to_transcript(f"PRISM started in {self.mode} mode.", "INFO")

    # system methods

    def load_api_keys(self):
        def load_keys(file_path, field_map, label):
            try:
                df = pd.read_csv(file_path, quotechar='"')
                for attr, column in field_map.items():
                    setattr(self, attr, df.loc[0, column])
            except Exception as e:
                self.add_to_transcript(f"Failed to load {label} API keys: {e}", "ERROR")
        load_keys('../qualtrics.api', {
            'qualtrics_api_token': 'api_token',
            'qualtrics_data_center': 'datacenter',
            'ema_survey_id': 'ema_survey_id',
            'feedback_survey_id': 'feedback_survey_id'
        }, "Qualtrics")
        load_keys('../followmee.api', {
            'followmee_username': 'username',
            'followmee_api_token': 'api_token'
        }, "FollowMee")
        load_keys('../twilio.api', {
            'twilio_account_sid': 'account_sid',
            'twilio_auth_token': 'auth_token',
            'twilio_from_number': 'from_number'
        }, "Twilio")
        load_keys('../research_drive.api', {
            'destination_path': 'destination_path',
            'drive_letter': 'drive_letter',
            'network_domain': 'network_domain',
            'network_username': 'network_username',
            'wisc_netid': 'wisc_netid',
            'wisc_password': 'wisc_password'
        }, "Research Drive")
        load_keys('../ngrok.api', {
            'ngrok_auth_token': 'auth_token',
            'ngrok_domain': 'domain'
        }, "Ngrok")

    def add_to_transcript(self, message, message_type = "INFO"):
        transcript_message = f"{message_type} - {message}"
        print(transcript_message)
        current_date = datetime.now().strftime('%Y-%m-%d')
        with open(f'../logs/transcripts/{current_date}_transcript.txt', 'a') as file:
            file.write(f"{datetime.now().strftime('%H:%M:%S')} - {transcript_message}\n")

    def get_transcript(self, num_lines = 10):
        try:
            today_date = datetime.now().strftime('%Y-%m-%d')
            transcript_path = f'../logs/transcripts/{today_date}_transcript.txt'
            with open(transcript_path, 'r') as f:
                num_lines = int(num_lines)
                content = f.read().splitlines()[-num_lines:]
                if not content:
                    return None
                return [{"timestamp": line.split(' - ')[0], "message": ' - '.join(line.split(' - ')[1:])} for line in content]
        except Exception as e:
            self.add_to_transcript(f"Failed to read transcript: {e}", "ERROR")
            return None        

    def handle_shutdown(self, signum, frame):
        self.add_to_transcript("Received shutdown signal. Stopping PRISM application...", "INFO")
        self.running = False
        self.system_task_thread.join(timeout = 5)
        self.sms_task_thread.join(timeout = 5)
        os._exit(0)

    def shutdown(self):
        self.handle_shutdown(signal.SIGINT, None)

    # task loading methods

    def load_task_schedule(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        config_path = os.path.join(current_dir, '..', 'config', 'system_task_schedule.csv')
        self.scheduled_tasks.clear()
        try:
            with open(config_path, 'r') as file:
                next(file)  # skip header
                for line in file:
                    if not line.strip():
                        continue
                    try:
                        task_type, task_time_str, run_today = [x.strip('"') for x in line.strip().split(',')]
                        task_time = datetime.strptime(task_time_str, '%H:%M:%S').time()
                        if task_type not in self.task_types:
                            self.add_to_transcript(f"Unknown task type: {task_type}", "ERROR")
                            continue
                        self.add_task(task_type, task_time, self.scheduled_tasks)
                    except ValueError:
                        self.add_to_transcript(f"Invalid time format for task {task_type}: {task_time_str}", "ERROR")
                    except Exception as e:
                        self.add_to_transcript(f"Error scheduling task {task_type}: {e}", "ERROR")
        except FileNotFoundError:
            self.add_to_transcript(f"Task schedule file not found at: {config_path}", "ERROR")
        except Exception as e:
            self.add_to_transcript(f"An error occurred while loading the task schedule: {e}", "ERROR")

    def load_participants(self):
        try:
            self.participants.clear()
            self.scheduled_sms_tasks.clear()
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
                        self.participants.append(participant)
            for participant in self.participants:
                self.schedule_participant_tasks(participant['unique_id'])
            return 0
        except Exception as e:
            self.add_to_transcript(f"Failed to load participants from CSV: {e}", "ERROR")
            return 1
        
    def schedule_participant_tasks(self, participant_id):
        participant = self.get_participant(participant_id)
        if not participant:
            self.add_to_transcript(f"Participant {participant_id} not found for scheduling tasks.", "ERROR")
            return 1
        if not participant['on_study']:
            self.add_to_transcript(f"Participant {participant_id} is not on study, no tasks scheduled.", "INFO")
            return 0
        for task_type, field_name in self.survey_types.items():
            task_time_str = participant.get(field_name)
            if task_time_str:
                self.add_task(task_type, task_time_str, self.scheduled_sms_tasks, participant_id)
        return 0

    # task removal methods

    def remove_system_task(self, task_type, task_time):
        task_time = datetime.strptime(task_time, '%H:%M:%S').time()
        for task in self.scheduled_tasks:
            if task['task_type'] == task_type and task['task_time'] == task_time:
                self.scheduled_tasks.remove(task)
                self.save_to_csv(self.scheduled_tasks, self.system_task_schedule_file_path)
                self.add_to_transcript(f"Removed system task: {task_type} at {task_time.strftime('%H:%M:%S')}", "INFO")
                return 0
        self.add_to_transcript(f"Task {task_type} at {task_time.strftime('%H:%M:%S')} not found.", "ERROR")
        return 1
    
    def remove_participant_tasks(self, participant_id):
        self.scheduled_sms_tasks[:] = [
            task for task in self.scheduled_sms_tasks
            if task['participant_id'] != participant_id
        ]

    # task processing methods

    def process_system_task(self, task):
        task_type = task.get('task_type')
        self.add_to_transcript(f"Executing task: {task_type}", "INFO")
        if self.mode == "test":
            self.task_types = get_task_types()
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
        return result if result is not None else 0
    
    def process_participant_sms(self, sms_task):
        participant_id = sms_task.get('participant_id')
        if not participant_id:
            self.add_to_transcript("Participant ID is missing in SMS task.", "ERROR")
            return -1
        participant = self.get_participant(participant_id)
        task_type = sms_task.get('task_type')
        participant_name = f"{participant['first_name']} {participant['last_name']}"
        participant_phone_number = participant['phone_number']
        self.add_to_transcript(f"Processing SMS task: {task_type} for participant {participant_id}", "INFO")
        task_map = {
            'ema': (self.ema_survey_id, "it's time to take your ecological momentary assessment survey."),
            'ema_reminder': (self.ema_survey_id, "you have not yet completed your ecological momentary assessment survey for today."),
            'feedback': (self.feedback_survey_id, "it's time to take your feedback survey."),
            'feedback_reminder': (self.feedback_survey_id, "you have not yet completed your feedback survey for today.")
        }
        if task_type not in task_map:
            self.add_to_transcript(f"Unknown SMS task type: {task_type}", "ERROR")
            return -1
        survey_id, message = task_map[task_type]
        survey_link = f"https://uwmadison.co1.qualtrics.com/jfe/form/{survey_id}?ParticipantID={participant_id}"
        body = f"{participant_name}, {message} {survey_link}"
        try:
            if self.mode == "prod":
                send_sms(self, [participant_phone_number], [body])
            self.add_to_transcript(f"SMS sent to {participant_id}.", "INFO")
            return 0
        except Exception as e:
            self.add_to_transcript(f"Failed to send SMS to {participant_id}: {e}", "ERROR")
            return -1
        
    # abstracted task methods

    def save_to_csv(self, data, file_path):
        try:
            headers = data[0].keys() if data else []
            with open(file_path, 'w') as f:
                f.write(','.join(f'"{header}"' for header in headers) + '\n')
                for row in data:
                    f.write(','.join(f'"{str(row[header])}"' for header in headers) + '\n')
        except Exception as e:
            self.add_to_transcript(f"Failed to save data to CSV at {file_path}: {e}", "ERROR")

    def add_task(self, task_type, task_time, target_list, participant_id = None):
        task_dict = {
            'task_type': task_type,
            'task_time': datetime.strptime(task_time, '%H:%M:%S').time() if isinstance(task_time, str) else task_time,
            'run_today': False
        }
        if participant_id is not None:
            task_dict['participant_id'] = participant_id
        target_list.append(task_dict)   

    def check_scheduled_tasks(self, task_list, task_queue):
        current_time = datetime.now().time()
        if current_time.hour == 0 and current_time.minute == 0:
            for task in task_list:
                task['run_today'] = False
        for task in task_list:
            task_time = task['task_time']
            diff = abs((datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), task_time)).total_seconds())
            if diff <= 1 and not task['run_today']:
                task_queue.put(task)
                task['run_today'] = True

    def start_task_thread(self, name, task_list, process_function):
        task_queue = queue.Queue()
        task_thread = threading.Thread(
            target = self.run_task_processor,
            args = (name, task_list, task_queue, process_function)
        )
        task_thread.start()
        return task_queue, task_thread
    
    def run_task_processor(self, queue_name, task_list, task_queue, process_function):
        while self.running:
            self.check_scheduled_tasks(task_list, task_queue)
            try:
                task = task_queue.get(timeout = 1)
                result = process_function(task)
                if result != 0:
                    self.add_to_transcript(f"Task {task['task_type']} failed with error code {result}.", "ERROR")
            except queue.Empty:
                pass
            except Exception as e:
                print(f"An error occurred while processing tasks: {e}")
                self.running = False
        self.add_to_transcript(f"{queue_name} processor stopped.", "INFO")

    # get methods

    def get_system_task_schedule(self):
        tasks = [
            {
                "task_type": task['task_type'],
                "task_time": task['task_time'].strftime('%H:%M:%S'),
                "run_today": task.get('run_today', False)
            } for task in self.scheduled_tasks
        ]
        return tasks

    def get_participant(self, unique_id):
        for participant in self.participants:
            if participant['unique_id'] == unique_id:
                return participant
        self.add_to_transcript(f"Participant with ID {unique_id} not found.", "ERROR")
        return None
    
    def get_participants(self):
        try:
            return [
                {
                    'unique_id': participant['unique_id'],
                    'last_name': participant['last_name'],
                    'first_name': participant['first_name'],
                    'on_study': participant['on_study'],
                } for participant in self.participants
            ]
        except Exception as e:
            self.add_to_transcript(f"Failed to retrieve participants: {e}", "ERROR")
            return []
    
    # participant editing methods
    
    def update_participant(self, unique_id, field, value):
        try:
            participant = self.get_participant(unique_id)
            if participant:
                if field in participant:
                    participant[field] = value
                    self.save_to_csv(self.participants, self.study_participants_file_path)
                    if field in self.survey_types.values():
                        self.remove_participant_tasks(unique_id)
                        self.schedule_participant_tasks(unique_id)
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
        
    def add_participant(self, participant):
        self.participants.append(participant)
        self.save_to_csv(self.participants, self.study_participants_file_path)
        self.schedule_participant_tasks(participant['unique_id'])

    def remove_participant(self, unique_id):
        participant = self.get_participant(unique_id)
        if participant:
            self.participants.remove(participant)
            self.save_to_csv(self.participants, self.study_participants_file_path)
            self.remove_participant_tasks(unique_id)
            self.add_to_transcript(f"Removed participant {unique_id}.", "INFO")
            return 0
        return 1

# application entry point
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