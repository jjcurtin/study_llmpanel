import queue
import threading
from datetime import datetime

class TaskManager():
    def __init__(self, app, name):
        self.app = app
        self.name = name
        self.running = True
        self.tasks = []
        self.task_queue = queue.Queue()
        self.thread = threading.Thread(target = self.run)
        self.thread.start()

    def add_task(self, task_type, task_time, participant_id = None):
        task_dict = {
            'task_type': task_type,
            'task_time': datetime.strptime(task_time, '%H:%M:%S').time() if isinstance(task_time, str) else task_time,
            'run_today': False
        }
        if participant_id is not None:
            task_dict['participant_id'] = participant_id
        self.tasks.append(task_dict)  

    def remove_task(self, task_type, task_time = None, participant_id = None):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def save_to_csv(self, data, file_path):
        try:
            headers = data[0].keys() if data else []
            with open(file_path, 'w') as f:
                f.write(','.join(f'"{header}"' for header in headers) + '\n')
                for row in data:
                    f.write(','.join(f'"{str(row[header])}"' for header in headers) + '\n')
        except Exception as e:
            self.app.add_to_transcript(f"Failed to save data to CSV at {file_path}: {e}", "ERROR")

    def check_tasks(self):
        current_time = datetime.now().time()
        if current_time.hour == 0 and current_time.minute == 0:
            for task in self.tasks:
                task['run_today'] = False
        for task in self.tasks:
            task_time = task['task_time']
            diff = abs((datetime.combine(datetime.today(), current_time) - datetime.combine(datetime.today(), task_time)).total_seconds())
            if diff <= 1 and not task['run_today']:
                self.task_queue.put(task)
                task['run_today'] = True

    def process_task(self, task):
        raise NotImplementedError("Subclasses must implement this method.")
    
    def run(self):
        while self.running:
            self.check_tasks()
            try:
                task = self.task_queue.get(timeout = 1)
                result = self.process_task(task)
                if result != 0:
                    self.app.add_to_transcript(f"Task {task['task_type']} failed with error code {result}.", "ERROR")
            except queue.Empty:
                pass
            except Exception as e:
                print(f"An error occurred while processing tasks: {e}")
                self.running = False
        self.app.add_to_transcript(f"{self.name} processor stopped.", "INFO")

    def stop(self):
        self.running = False
        self.thread.join()