from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from datetime import datetime
from datetime import timedelta

def create_flask_app(app_instance):
    flask_app = Flask(__name__)
    
    if app_instance.mode == "prod":
        CORS(flask_app, resources = {
            r"/system/*": {"origins": "localhost:5000"},
            r"/system/get_uptime": {"origins": "*"}
        })
    else:
        CORS(flask_app, resources = {
            r"/system/*": {"origins": "localhost:5000"},
        })

    limiter = Limiter(
        get_remote_address,
        app = flask_app,
        default_limits = [],
        storage_uri = "memory://"
    )

    @flask_app.route('/system/get_mode', methods = ['GET'])
    def get_mode():
        app_instance.add_to_transcript("Mode requested via API", "INFO")
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
        if app_instance.mode == "test":
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
        
        task_time = task_time.time()
        app_instance.scheduled_tasks.append({
            'task_type': task_type,
            'task_time': task_time,
            'run_today': False
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
        participant = app_instance.get_participant(unique_id)
        if participant:
            app_instance.add_to_transcript(f"Participant {unique_id} requested via API", "INFO")
            return jsonify({"participant": participant}), 200
        else:
            app_instance.add_to_transcript(f"Participant {unique_id} not found for retrieval", "ERROR")
            return jsonify({"error": "Participant not found"}), 404
    
    @flask_app.route('/system/update_participant/<unique_id>/<field>/<new_value>', methods = ['PUT'])
    def update_participant(unique_id, field, new_value):
        result = app_instance.update_participant(unique_id, field, new_value)
        if result == 0:
            return jsonify({"message": "Participant updated successfully"}), 200
        else:
            app_instance.add_to_transcript(f"Participant {unique_id} not found for update", "ERROR")
            return jsonify({"error": "Participant not found"}), 404
    
    @flask_app.route('/system/add_participant', methods = ['POST'])
    def add_participant():
        data = request.get_json()
        required_fields = ['unique_id', 'last_name', 'first_name', 'on_study', 'phone_number', 'ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']
        
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        
        new_participant = {
            'unique_id': data['unique_id'],
            'last_name': data['last_name'],
            'first_name': data['first_name'],
            'on_study': data['on_study'],
            'phone_number': data['phone_number'],
            'ema_time': data['ema_time'],
            'ema_reminder_time': data['ema_reminder_time'],
            'feedback_time': data['feedback_time'],
            'feedback_reminder_time': data['feedback_reminder_time']
        }
        
        app_instance.add_participant(new_participant)
        return jsonify({"message": "Participant added successfully"}), 200
    
    @flask_app.route('/system/remove_participant/<unique_id>', methods = ['DELETE'])
    def remove_participant(unique_id):
        if app_instance.remove_participant(unique_id) == 0:
            return jsonify({"message": "Participant removed successfully"}), 200
        else:
            app_instance.add_to_transcript(f"Participant {unique_id} not found for removal", "ERROR")
            return jsonify({"error": "Participant not found"}), 404
        
    @flask_app.route('/system/get_transcript/<num_lines>', methods = ['GET'])
    def get_transcript(num_lines):
        today_date = datetime.now().strftime('%Y-%m-%d')
        transcript_path = f'../logs/transcripts/{today_date}_transcript.txt'
        try:
            with open(transcript_path, 'r') as f:
                num_lines = int(num_lines)
                content = f.read().splitlines()[-num_lines:]
                if not content:
                    return jsonify({"error": "Transcript is empty"}), 404
                transcript = [{"timestamp": line.split(' - ')[0], "message": ' - '.join(line.split(' - ')[1:])} for line in content]
                
            app_instance.add_to_transcript("Transcript requested via API", "INFO")
            return jsonify({"transcript": transcript}), 200
        except FileNotFoundError:
            return jsonify({"error": "Transcript not found"}), 404
        
    @flask_app.route('/system/shutdown', methods = ['POST'])
    def shutdown():
        app_instance.add_to_transcript("Shutdown requested via API", "INFO")
        app_instance.shutdown()
        return jsonify({"message": "Shutdown initiated"}), 200
    
    @flask_app.route('/system/send_survey/<unique_id>/<survey_type>', methods = ['POST'])
    def send_survey(unique_id, survey_type):
        if survey_type not in ['ema', 'feedback']:
            return jsonify({"error": "Invalid survey type"}), 400
        
        participant = app_instance.get_participant(unique_id)
        if not participant:
            return jsonify({"error": "Participant not found"}), 404
        
        app_instance.add_sms_task(survey_type, (datetime.now() + timedelta(seconds=10)).strftime('%H:%M:%S'), unique_id)
        app_instance.add_to_transcript(f"Survey {survey_type} sent to participant {unique_id} via API", "INFO")
        return jsonify({"message": f"{survey_type.capitalize()} survey sent to participant {unique_id}"}), 200

    return flask_app