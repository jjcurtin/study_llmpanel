from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from datetime import datetime
import threading

def create_flask_app(app_instance):
    flask_app = Flask(__name__)
    
    CORS(flask_app, resources={
        r"/system/*": {"origins": "localhost:5000"}
    })

    limiter = Limiter(
        get_remote_address,
        app = flask_app,
        default_limits = [],
        storage_uri = "memory://"
    )

    @flask_app.route('/system/get_mode', methods=['GET'])
    def get_mode():
        return jsonify({'mode': app_instance.mode}), 200
    
    @flask_app.route('/system/uptime', methods=['GET'])
    def get_uptime():
        uptime_seconds = datetime.now() - app_instance.start_time
        uptime_seconds = uptime_seconds.total_seconds()
        uptime_string = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
        return jsonify({"uptime": uptime_string})
    
    @flask_app.route('/system/get_task_schedule', methods=['GET'])
    def get_task_schedule():
        tasks = app_instance.scheduled_tasks
        formatted_tasks = [
            {
                "task_type": task['task_type'],
                "task_time": task['task_time'].strftime('%H:%M:%S'),
                "run_today": task.get('run_today', False)
            } for task in tasks
        ]
        return jsonify({"tasks": formatted_tasks}), 200
    
    @flask_app.route('/system/add_system_task/<task_type>/<task_time>', methods=['POST'])
    def add_system_task(task_type, task_time):
        if task_type not in ['CHECK_SYSTEM', 'PULLDOWN_DATA', 'RUN_PIPELINE']:
            return jsonify({"error": "Invalid task type"}), 400
        try:
            task_time = datetime.strptime(task_time, '%H:%M:%S')
        except ValueError:
            return jsonify({"error": "Invalid time format"}), 400
        
        # format to military time and time object
        task_time = task_time.time()
        
        app_instance.scheduled_tasks.append({
            'task_type': task_type,
            'task_time': task_time,
            'run_today': False  # Flag to indicate if the task has run today
        })

        # write to the csv file
        with open('../config/system_task_schedule.csv', 'a') as f:
            f.write(f'\n"{task_type}","{task_time.strftime('%H:%M:%S')}"')
        
        return jsonify({"message": "Task added successfully"}), 200
    
    @flask_app.route('/system/remove_system_task/<task_type>/<task_time>', methods=['DELETE'])
    def remove_system_task(task_type, task_time):
        if task_type not in ['CHECK_SYSTEM', 'PULLDOWN_DATA', 'RUN_PIPELINE']:
            return jsonify({"error": "Invalid task type"}), 400
        try:
            task_time = datetime.strptime(task_time, '%H:%M:%S').time()
        except ValueError:
            return jsonify({"error": "Invalid time format"}), 400
        
        # Find and remove the task
        for task in app_instance.scheduled_tasks:
            if task['task_type'] == task_type and task['task_time'] == task_time:
                app_instance.scheduled_tasks.remove(task)
                # write to the csv file
                with open('../config/system_task_schedule.csv', 'w') as f:
                    f.write('"task_type","task_time"')
                    for t in app_instance.scheduled_tasks:
                        f.write(f'\n"{t["task_type"]}","{t["task_time"].strftime('%H:%M:%S')}"')
                return jsonify({"message": "Task removed successfully"}), 200
        
        return jsonify({"error": "Task not found"}), 404
    
    @flask_app.route('/system/execute_task/<task_type>', methods=['POST'])
    def execute_task(task_type):
        if task_type not in app_instance.task_types:
            return jsonify({"error": "Invalid task type"}), 400
        else:
            result = app_instance.process_task(task_type)
        
        if result != 0:
            return jsonify({"error": f"Failed to execute {task_type}"}), 500
        else:
            return jsonify({"message": f"{task_type} executed successfully"}), 200

    return flask_app