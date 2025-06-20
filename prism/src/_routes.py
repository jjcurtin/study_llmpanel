from flask import Flask, jsonify
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from datetime import datetime

def create_flask_app(app_instance):
    flask_app = Flask(__name__)
    
    CORS(flask_app, resources = {
        r"/system/*": {"origins": "localhost:5000"}
    })

    limiter = Limiter(
        get_remote_address,
        app = flask_app,
        default_limits = [],
        storage_uri = "memory://"
    )

    @flask_app.route('/system/get_mode', methods = ['GET'])
    def get_mode():
        return jsonify({'mode': app_instance.mode}), 200
    
    @flask_app.route('/system/uptime', methods = ['GET'])
    def get_uptime():
        uptime_seconds = datetime.now() - app_instance.start_time
        uptime_seconds = uptime_seconds.total_seconds()
        uptime_string = time.strftime('%H:%M:%S', time.gmtime(uptime_seconds))
        app_instance.add_to_transcript(f"Uptime requested via API: {uptime_string}", "INFO")
        return jsonify({"uptime": uptime_string})
    
    @flask_app.route('/system/get_task_schedule', methods = ['GET'])
    def get_task_schedule():
        tasks = app_instance.scheduled_tasks
        formatted_tasks = [
            {
                "task_type": task['task_type'],
                "task_time": task['task_time'].strftime('%H:%M:%S'),
                "run_today": task.get('run_today', False)
            } for task in tasks
        ]
        app_instance.add_to_transcript("Task schedule requested via API", "INFO")
        return jsonify({"tasks": formatted_tasks}), 200
    
    @flask_app.route('/system/get_task_types', methods = ['GET'])
    def get_task_types():
        if app_instance.hot_reload:
            app_instance.update_task_types()
        task_types = app_instance.task_types
        app_instance.add_to_transcript("Task types requested via API", "INFO")
        return jsonify({"task_types": task_types}), 200
    
    @flask_app.route('/system/add_system_task/<task_type>/<task_time>', methods = ['POST'])
    def add_system_task(task_type, task_time):
        if task_type not in app_instance.task_types:
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

        app_instance.add_to_transcript(f"Added new task via API: {task_type} at {task_time.strftime('%H:%M:%S')}", "INFO")
        
        return jsonify({"message": "Task added successfully"}), 200
    
    @flask_app.route('/system/remove_system_task/<task_type>/<task_time>', methods = ['DELETE'])
    def remove_system_task(task_type, task_time):
        if task_type not in app_instance.task_types:
            return jsonify({"error": "Invalid task type"}), 400
        try:
            task_time = datetime.strptime(task_time, '%H:%M:%S').time()
        except ValueError:
            return jsonify({"error": "Invalid time format"}), 400
        
        # Find and remove the task
        try:
            for task in app_instance.scheduled_tasks:
                if task['task_type'] == task_type and task['task_time'] == task_time:
                    app_instance.scheduled_tasks.remove(task)
                    # write to the csv file
                    with open('../config/system_task_schedule.csv', 'w') as f:
                        f.write('"task_type","task_time"')
                        for t in app_instance.scheduled_tasks:
                            f.write(f'\n"{t["task_type"]}","{t["task_time"].strftime('%H:%M:%S')}"')
                    app_instance.add_to_transcript(f"Removed task: {task_type} at {task_time.strftime('%H:%M:%S')}", "INFO")
                    return jsonify({"message": "Task removed via API successfully"}), 200
        except Exception as e:
            app_instance.add_to_transcript(f"Failed to remove task: {task_type} at {task_time.strftime('%H:%M:%S')}. Error message: {e}", "ERROR")
        
        return jsonify({"error": "Task not found"}), 404
    
    @flask_app.route('/system/execute_task/<task_type>', methods = ['POST'])
    def execute_task(task_type):
        if task_type not in app_instance.task_types:
            return jsonify({"error": "Invalid task type"}), 400
        elif app_instance.process_task(task_type) != 0:
            return jsonify({"error": f"Failed to execute {task_type}"}), 500
        else:
            app_instance.add_to_transcript(f"Executed task: {task_type} via API", "INFO")
            return jsonify({"message": f"{task_type} executed successfully"}), 200
        
    @flask_app.route('/system/get_participants', methods = ['GET'])
    def get_participants():
        participants = app_instance.participants
        formatted_participants = [
            {
                'unique_id': participant['unique_id'],
                'last_name': participant['last_name'],
                'first_name': participant['first_name'],
                'on_study': participant['on_study']
            } for participant in participants
        ]
        app_instance.add_to_transcript("Participants requested via API", "INFO")
        return jsonify({"participants": formatted_participants}), 200
    
    @flask_app.route('/system/get_participant/<unique_id>', methods = ['GET'])
    def get_participant(unique_id):
        for participant in app_instance.participants:
            if participant['unique_id'] == unique_id:
                formatted_participant = {
                    'unique_id': participant['unique_id'],
                    'last_name': participant['last_name'],
                    'first_name': participant['first_name'],
                    'on_study': participant['on_study'],
                    'phone_number': participant['phone_number'],
                    'ema_time': participant['ema_time'],
                    'ema_reminder_time': participant['ema_reminder_time'],
                    'feedback_time': participant['feedback_time'],
                    'feedback_reminder_time': participant['feedback_reminder_time'],
                }
                app_instance.add_to_transcript(f"Participant {unique_id} requested via API", "INFO")
                return jsonify({"participant": formatted_participant}), 200
        app_instance.add_to_transcript(f"Participant {unique_id} not found", "ERROR")
        return jsonify({"error": "Participant not found"}), 404
    
    @flask_app.route('/system/update_participant/<unique_id>/<field>/<new_value>', methods = ['PUT'])
    def update_participant(unique_id, field, new_value):
        for participant in app_instance.participants:
            if participant['unique_id'] == unique_id:
                if field not in participant:
                    return jsonify({"error": "Invalid field"}), 400
                participant[field] = new_value

                # Update the participant in the CSV file
                with open('../config/study_participants.csv', 'w') as f:
                    f.write('"unique_id","last_name","first_name","on_study","phone_number","ema_time","ema_reminder_time","feedback_time","feedback_reminder_time"')
                    for p in app_instance.participants:
                        f.write(f'\n"{p["unique_id"]}","{p["last_name"]}","{p["first_name"]}","{p["on_study"]}","{p["phone_number"]}","{p["ema_time"]}","{p["ema_reminder_time"]}","{p["feedback_time"]}","{p["feedback_reminder_time"]}"')

                # if the field is a ema, ema_reminder, feedback, or feedback_reminder time need to add to queue and remove the old value
                if field in ['ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']:
                    if participant['on_study']:
                        participant_name = f"{participant['first_name']} {participant['last_name']}"
                        participant_id = participant['unique_id']
                        participant_phone_number = participant['phone_number']

                        if field == 'ema_time':
                            app_instance.scheduled_sms_tasks = [
                                task for task in app_instance.scheduled_sms_tasks
                                if not (task['task_type'] == 'ema' and task['participant_id'] == participant_id)
                            ]
                            app_instance.scheduled_sms_tasks.append({
                                'task_type': 'ema',
                                'task_time': datetime.strptime(participant['ema_time'], '%H:%M:%S').time(),
                                'participant_name': participant_name,
                                'participant_id': participant_id,
                                'participant_phone_number': participant_phone_number,
                                'run_today': False  # Flag to indicate if the task has run today
                            })
                        elif field == 'ema_reminder_time':
                            app_instance.scheduled_sms_tasks = [
                                task for task in app_instance.scheduled_sms_tasks
                                if not (task['task_type'] == 'ema_reminder' and task['participant_id'] == participant_id)
                            ]
                            app_instance.scheduled_sms_tasks.append({
                                'task_type': 'ema_reminder',
                                'task_time': datetime.strptime(participant['ema_reminder_time'], '%H:%M:%S').time(),
                                'participant_name': participant_name,
                                'participant_id': participant_id,
                                'participant_phone_number': participant_phone_number,
                                'run_today': False  # Flag to indicate if the task has run today
                            })
                        elif field == 'feedback_time':
                            app_instance.scheduled_sms_tasks = [
                                task for task in app_instance.scheduled_sms_tasks
                                if not (task['task_type'] == 'feedback' and task['participant_id'] == participant_id)
                            ]
                            app_instance.scheduled_sms_tasks.append({
                                'task_type': 'feedback',
                                'task_time': datetime.strptime(participant['feedback_time'], '%H:%M:%S').time(),
                                'participant_name': participant_name,
                                'participant_id': participant_id,
                                'participant_phone_number': participant_phone_number,
                                'run_today': False  # Flag to indicate if the task has run today
                            })
                        elif field == 'feedback_reminder_time':
                            app_instance.scheduled_sms_tasks = [
                                task for task in app_instance.scheduled_sms_tasks
                                if not (task['task_type'] == 'feedback_reminder' and task['participant_id'] == participant_id)
                            ]
                            app_instance.scheduled_sms_tasks.append({
                                'task_type': 'feedback_reminder',
                                'task_time': datetime.strptime(participant['feedback_reminder_time'], '%H:%M:%S').time(),
                                'participant_name': participant_name,
                                'participant_id': participant_id,
                                'participant_phone_number': participant_phone_number,
                                'run_today': False  # Flag to indicate if the task has run today
                            })
                        else:
                            app_instance.add_to_transcript(f"Invalid field for time update: {field}", "ERROR")
                            return jsonify({"error": "Invalid field for time update"}), 400

                app_instance.add_to_transcript(f"Updated participant {unique_id}: {field} set to {new_value}", "INFO")
                return jsonify({"message": "Participant updated successfully"}), 200
        app_instance.add_to_transcript(f"Participant {unique_id} not found for update", "ERROR")
        return jsonify({"error": "Participant not found"}), 404

    return flask_app