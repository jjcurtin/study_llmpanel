import os
from datetime import datetime
import queue
import threading
from _routes import create_flask_app
import pandas as pd

class PRISM():
    def __init__(self, mode="test"):
        self.clear()
        self.add_to_transcript("Initializing PRISM application...", "INFO")
        self.mode = mode

        self.notify_coordinators = False # Flag to control SMS notifications off for now since I got it working

        # make sure you are running in the src directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not current_dir.endswith('src'):
            self.add_to_transcript("Please run this script from the 'src' directory.", "ERROR")
            exit(1)

        # load api keys
        qualtrics = pd.read_csv('../qualtrics.api', quotechar='"')
        self.qualtrics_api_token = qualtrics.loc[0, 'api_token']
        self.qualtrics_data_center = qualtrics.loc[0, 'datacenter']
        self.ema_survey_id = qualtrics.loc[0, 'ema_survey_id']
        self.feedback_survey_id = qualtrics.loc[0, 'feedback_survey_id']

        followmee = pd.read_csv('../followmee.api', quotechar='"')
        self.followmee_username = followmee.loc[0, 'username']  
        self.followmee_api_token = followmee.loc[0, 'api_token']

        twilio = pd.read_csv('../twilio.api', quotechar='"')
        self.twilio_account_sid = twilio.loc[0, 'account_sid']
        self.twilio_auth_token = twilio.loc[0, 'auth_token']
        self.twilio_from_number = twilio.loc[0, 'from_number']

        # create Flask app instance
        self.flask_app = create_flask_app(self)
        threading.Thread(target = self.run_flask, daemon = True).start()

        # check all files in the tasks directory and establish task types dictionary
        self.update_task_types()

        # run main event loop
        self.running = True
        self.start_time = datetime.now()
        self.task_queue = queue.Queue()
        self.scheduled_tasks = []
        
        # Load and schedule tasks
        self.load_task_schedule()

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

    def load_task_schedule(self):

        # load task schedule from CSV file
        # "task_type","task_time"
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

    # add task to the queue when it is time to run it
    def check_scheduled_tasks(self):
        current_time = datetime.now().time()
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

        self.update_task_types()  # Ensure task types are up to date

        if task_type in self.task_types:
            module_name = f'tasks._{task_type.lower()}'
            try:
                module = __import__(module_name, fromlist = [task_type])
                task_type = task_type.replace('_', ' ').title().replace(' ', '')
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

    def get_uptime(self):
        return str(datetime.now() - self.start_time)
    
    def run_flask(self):
        self.add_to_transcript("Starting Flask application on port 5000.", "INFO")
        try:
            if self.mode == "prod":
                # for production we want external access
                self.flask_app.run(host = '0.0.0.0', port = 5000)
            elif self.mode == "test":
                # For testing, we can run on localhost which means access is limited to the local machine
                self.flask_app.run(host = '127.0.0.1', port = 5000)
            else:
                raise ValueError("Unknown mode. Cannot start Flask application.")
        except Exception as e:
            self.add_to_transcript(f"Failed to start Flask application: {e}", "ERROR")

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def add_to_transcript(self, message, message_type = "INFO"):
        print(f"{message_type} - {message}")
        current_date = datetime.now().strftime('%Y-%m-%d')
        transcript_path = f'../logs/{current_date}_transcript.txt'
        with open(transcript_path, 'a') as file:
            file.write(f"{datetime.now().strftime('%H:%M:%S')} - {message_type} - {message}\n")

    def run(self):
        if self.mode == "prod":
            self.add_to_transcript("Running in production mode.", "WARNING")
        elif self.mode == "test":
            self.add_to_transcript("Running in test mode.", "INFO")
        else:
            self.add_to_transcript("Unknown mode. Exiting.", "ERROR")
            return
        
        self.add_to_transcript(f"PRISM started with {len(self.scheduled_tasks)} scheduled tasks", "INFO")
        
        # task processing loop
        while self.running:
            self.check_scheduled_tasks()
            try:
                result = self.process_task(self.task_queue.get(timeout = 1))
            except queue.Empty:
                pass
            except Exception as e:
                print(f"An error occurred while processing tasks: {e}")
                self.running = False

if __name__ == "__main__":
    prism = PRISM(mode = "test")  # Change to "prod" for production mode
    try:
        prism.run()
    except KeyboardInterrupt:
        prism.add_to_transcript("Exiting PRISM application.", "INFO")
        prism.running = False
    except Exception as e:
        prism.add_to_transcript(f"An unexpected error occurred: {e}", "ERROR")
        prism.running = False
