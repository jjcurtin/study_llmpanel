import os
from datetime import datetime
import queue
import threading
from _routes import create_flask_app
import pandas as pd

from _check_system import CheckSystem

class PRISM():
    def __init__(self, mode="test"):
        self.clear()
        print("Initializing PRISM application...")
        self.mode = mode

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

        self.task_types = {
            "CHECK_SYSTEM": "Check System Status",
            "PULLDOWN_DATA": "Pull Down Data",
            "RUN_SCRIPT_PIPELINE": "Run Script Pipeline"
        }

        # run main event loop
        self.running = True
        self.start_time = datetime.now()
        self.task_queue = queue.Queue()
        self.scheduled_tasks = []
        
        # Load and schedule tasks
        self.load_task_schedule()

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
            print(f"Task schedule file not found at: {config_path}")
            return []
        except Exception as e:
            print(f"An error occurred while loading the task schedule: {e}")
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
                print(f"Scheduled task: {task_type} at {task_time}")
            except ValueError:
                print(f"Invalid time format for task {task_type}: {task_time_str}")
            except Exception as e:
                print(f"An error occurred while scheduling task {task_type}: {e}")
        
        print(f"Loaded {len(self.scheduled_tasks)} scheduled tasks")
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
                print(f"Time to execute task: {task['task_type']} (scheduled for {task_time})")
                self.task_queue.put(task['task_type'])
                task['run_today'] = True

    # task run logic
    def process_task(self, task_type):
        print(f"Executing task: {task_type}")
        result = 0  # Default result for successful execution
        
        if task_type == "PULLDOWN_DATA":
            # Add your data pulling logic here
            pass
            
        elif task_type == "RUN_SCRIPT_PIPELINE":
            # Add your script pipeline logic here
            pass
            
        elif task_type == "CHECK_SYSTEM":
            result = CheckSystem(self).execute()

        else:
            print(f"Unknown task type: {task_type}")

        return result

    def get_uptime(self):
        return str(datetime.now() - self.start_time)
    
    def run_flask(self):
        print("Starting Flask application on port 5000.")
        try:
            if self.mode == "prod":
                # For production, we can bind to all interfaces
                # This allows access from any IP address, which is useful for production servers
                self.flask_app.run(host = '0.0.0.0', port = 5000)
            elif self.mode == "test":
                # For testing, we can run on localhost
                self.flask_app.run(host = '127.0.0.1', port = 5000)
            else:
                raise ValueError("Unknown mode. Cannot start Flask application.")
        except Exception as e:
            print(f"Failed to start Flask application: {e}")

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def run(self):
        if self.mode == "prod":
            print("WARNING: Running in production mode.")
        elif self.mode == "test":
            print("INFO: Running in test mode.")
        else:
            print("ERROR: Unknown mode. Exiting.")
            return
        
        print(f"PRISM started with {len(self.scheduled_tasks)} scheduled tasks")
        
        while self.running:
            # Check for scheduled tasks
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
        print("Exiting PRISM application.")
        prism.running = False
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        prism.running = False
