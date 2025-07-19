import os
import importlib
from datetime import datetime

from task_managers._task_manager import TaskManager

class SystemTaskManager(TaskManager):
    def __init__(self, app, name = "SystemTaskManager"):
        super().__init__(app, name)
        self.task_types = self.get_task_types()
        self.file_path = '../config/system_task_schedule.csv'
        self.load_task_schedule()

    def get_task_types(self):
        return {
            (f[:-3].upper().lstrip('_')): (f[:-3].replace('_', ' ').title().replace(' ', ''))
            for f in os.listdir('system_tasks')
            if f.endswith('.py') and f != '_system_task.py'
        }
    
    def get_r_script_tasks(self):
        data = {
            (f[:-2]): (f[:-2])
            for f in os.listdir('../scripts')
            if f.endswith('.R')
        }
        return data
    
    def load_task_schedule(self):
        self.tasks.clear()
        try:
            with open(self.file_path, 'r') as file:
                next(file)  # skip header
                for line in file:
                    if not line.strip():
                        continue
                    try:
                        task_type, task_time_str, r_script_path, run_today = [x.strip('"') for x in line.strip().split(',')]
                        task_time = datetime.strptime(task_time_str, '%H:%M:%S').time()
                        if task_type not in self.task_types:
                            self.app.app.add_to_transcript(f"Unknown task type: {task_type}", "ERROR")
                            continue
                        self.add_task(task_type, task_time, r_script_path = r_script_path)
                    except ValueError:
                        self.app.add_to_transcript(f"Invalid time format for task {task_type}: {task_time_str}", "ERROR")
                    except Exception as e:
                        self.app.add_to_transcript(f"Error scheduling task {task_type}: {e}", "ERROR")
                self.tasks.sort(key = lambda x: x['task_time'])
        except FileNotFoundError:
            self.app.add_to_transcript(f"Task schedule file not found at: {self.file_path}", "ERROR")
        except Exception as e:
            self.app.add_to_transcript(f"An error occurred while loading the task schedule: {e}", "ERROR")
    
    def clear_schedule(self):
        self.tasks.clear()
        self.save_tasks()

    def get_task_schedule(self):
        try:
            return [
                {
                    "task_type": task['task_type'],
                    "task_time": task['task_time'].strftime('%H:%M:%S'),
                    "r_script_path": task.get('r_script_path', ''),
                    "run_today": task.get('run_today', False)
                } for task in self.tasks
            ]
        except Exception as e:
            self.add_to_transcript(f"Failed to retrieve system task schedule: {e}", "ERROR")
            return []
        
    def save_tasks(self):
        self.tasks.sort(key = lambda x: x['task_time'])
        self.save_to_csv(self.tasks, self.file_path)

    def remove_task(self, task_type, task_time = None, participant_id = None, r_script_path = None):
        task_time = datetime.strptime(task_time, '%H:%M:%S').time()
        for task in self.tasks:
            if task['task_type'] == task_type and task['task_time'] == task_time:
                if r_script_path and task.get('r_script_path') != r_script_path:
                    continue
                self.tasks.remove(task)
                self.save_tasks()
                self.app.add_to_transcript(f"Removed system task: {task_type} at {task_time.strftime('%H:%M:%S')}", "INFO")
                return 0
        self.app.add_to_transcript(f"Task {task_type} at {task_time.strftime('%H:%M:%S')} not found.", "ERROR")
        return 1

    def process_task(self, task):
        task_type = task.get('task_type')
        self.app.add_to_transcript(f"Executing task: {task_type}", "INFO")
        if self.app.mode == "test":
            self.task_types = self.get_task_types()
        if task_type in self.task_types:
            module_name = f'system_tasks._{task_type.lower()}'
            try:
                module = __import__(module_name, fromlist = [task_type])
                task_type = task_type.replace('_', ' ').title().replace(' ', '')
                module = importlib.reload(module)
                task_class = getattr(module, task_type)
            except ImportError as e:
                self.app.add_to_transcript(f"Failed to import task {task_type}: {e}", "ERROR")
                return -1
            except Exception as e:
                self.app.add_to_transcript(f"An error occurred while importing task {task_type}: {e}", "ERROR")
                return -1
            r_script_path = task.get('r_script_path')
            if r_script_path:
                result = task_class(self.app, r_script_path).execute()
            else:
                result = task_class(self.app).execute()
        else:
            self.app.add_to_transcript(f"Unknown task type: {task_type}", "ERROR")
            return -1
        return result if result is not None else 0