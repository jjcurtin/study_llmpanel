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
            r"/participants/*": {"origins": "localhost:5000"},
            r"/system/get_uptime": {"origins": "*"}
        })
    else:
        CORS(flask_app, resources = {
            r"/system/*": {"origins": "localhost:5000"},
            r"/participants/*": {"origins": "localhost:5000"}
        })

    limiter = Limiter(
        get_remote_address,
        app = flask_app,
        default_limits = [],
        storage_uri = "memory://"
    )

    ################
    #    System    #
    ################

    @flask_app.route('/system/get_mode', methods = ['GET'])
    def get_mode():
        app_instance.add_to_transcript("Mode requested via API", "INFO")
        return jsonify({'mode': app_instance.mode}), 200
    
    @flask_app.route('/system/uptime', methods = ['GET'])
    def get_uptime():
        uptime = time.strftime('%H:%M:%S', time.gmtime((datetime.now() - app_instance.start_time).total_seconds()))
        app_instance.add_to_transcript(f"Uptime requested via API: {uptime}", "INFO")
        return jsonify({"uptime": uptime})
    
    @flask_app.route('/system/get_transcript/<num_lines>', methods = ['GET'])
    def get_transcript(num_lines):
        app_instance.add_to_transcript("Transcript requested via API", "INFO")
        transcript = app_instance.get_transcript(num_lines)
        if transcript:
            return jsonify({"transcript": transcript}), 200
        else:
            return jsonify({"error": "Transcript not found"}), 404
        
    @flask_app.route('/system/shutdown', methods = ['POST'])
    def shutdown():
        app_instance.add_to_transcript("Shutdown requested via API", "INFO")
        app_instance.shutdown()
        return jsonify({"message": "Shutdown initiated"}), 200
    
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
        app_instance.add_to_transcript("Task types requested via API", "INFO")
        return jsonify({"task_types": app_instance.task_types}), 200
    
    @flask_app.route('/system/add_system_task/<task_type>/<task_time>', methods = ['POST'])
    def add_system_task(task_type, task_time):
        if task_type not in app_instance.task_types:
            return jsonify({"error": "Invalid task type"}), 400
        try:
            task_time = datetime.strptime(task_time, '%H:%M:%S')
        except ValueError:
            return jsonify({"error": "Invalid time format"}), 400
        task_time = task_time.time()
        app_instance.add_task(task_type, task_time, app_instance.scheduled_tasks)
        app_instance.save_tasks()
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
                    app_instance.save_tasks()
                    app_instance.add_to_transcript(f"Removed task: {task_type} at {task_time.strftime('%H:%M:%S')}", "INFO")
                    return jsonify({"message": "Task removed via API successfully"}), 200
        except Exception as e:
            app_instance.add_to_transcript(f"Failed to remove task: {task_type} at {task_time.strftime('%H:%M:%S')}. Error message: {e}", "ERROR")
        
        return jsonify({"error": "Task not found"}), 404
    
    @flask_app.route('/system/execute_task/<task_type>', methods = ['POST'])
    def execute_task(task_type):
        if task_type not in app_instance.task_types:
            return jsonify({"error": "Invalid task type"}), 400
        elif app_instance.process_system_task({'task_type': task_type}) != 0:
            return jsonify({"error": f"Failed to execute {task_type}"}), 500
        else:
            app_instance.add_to_transcript(f"Executed task: {task_type} via API", "INFO")
            return jsonify({"message": f"{task_type} executed successfully"}), 200
        
    #################
    #  Participants #
    #################

    @flask_app.route('/participants/get_participants', methods = ['GET'])
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
    
    @flask_app.route('/participants/refresh_participants', methods = ['POST'])
    def refresh_participants():
        if app_instance.refresh_participants() == 0:
            app_instance.add_to_transcript("Participants refreshed via API", "INFO")
            return jsonify({"message": "Participants refreshed successfully"}), 200
        else:
            app_instance.add_to_transcript("Failed to refresh participants", "ERROR")
            return jsonify({"error": "Failed to refresh participants"}), 500
    
    @flask_app.route('/participants/get_participant/<unique_id>', methods = ['GET'])
    def get_participant(unique_id):
        participant = app_instance.get_participant(unique_id)
        if participant:
            app_instance.add_to_transcript(f"Participant {unique_id} requested via API", "INFO")
            return jsonify({"participant": participant}), 200
        else:
            app_instance.add_to_transcript(f"Participant {unique_id} not found for retrieval", "ERROR")
            return jsonify({"error": "Participant not found"}), 404

    @flask_app.route('/participants/add_participant', methods = ['POST'])
    def add_participant():
        data = request.get_json()
        required_fields = ['unique_id', 'last_name', 'first_name', 'on_study', 'phone_number', 'ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        else:
            app_instance.add_participant(data)
            return jsonify({"message": "Participant added successfully"}), 200
    
    @flask_app.route('/participants/remove_participant/<unique_id>', methods = ['DELETE'])
    def remove_participant(unique_id):
        if app_instance.remove_participant(unique_id) == 0:
            return jsonify({"message": "Participant removed successfully"}), 200
        else:
            app_instance.add_to_transcript(f"Participant {unique_id} not found for removal", "ERROR")
            return jsonify({"error": "Participant not found"}), 404
        
    @flask_app.route('/participants/update_participant/<unique_id>/<field>/<new_value>', methods = ['PUT'])
    def update_participant(unique_id, field, new_value):
        if app_instance.update_participant(unique_id, field, new_value) == 0:
            return jsonify({"message": "Participant updated successfully"}), 200
        else:
            app_instance.add_to_transcript(f"Participant {unique_id} not found for update", "ERROR")
            return jsonify({"error": "Participant not found"}), 404
    
    @flask_app.route('/participants/send_survey/<unique_id>/<survey_type>', methods = ['POST'])
    def send_survey(unique_id, survey_type):
        if survey_type not in ['ema', 'feedback']:
            return jsonify({"error": "Invalid survey type"}), 400
        if not app_instance.get_participant(unique_id):
            return jsonify({"error": "Participant not found"}), 404
        app_instance.add_task(survey_type, (datetime.now() + timedelta(seconds=10)).strftime('%H:%M:%S'), app_instance.scheduled_sms_tasks, unique_id)
        app_instance.add_to_transcript(f"Survey {survey_type} sent to participant {unique_id} via API", "INFO")
        return jsonify({"message": f"{survey_type.capitalize()} survey sent to participant {unique_id}"}), 200

    return flask_app