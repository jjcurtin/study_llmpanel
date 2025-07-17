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
        return jsonify({'mode': app_instance.mode}), 200
    
    @flask_app.route('/system/uptime', methods = ['GET'])
    def get_uptime():
        return jsonify({"uptime": time.strftime('%H:%M:%S', time.gmtime((datetime.now() - app_instance.start_time).total_seconds()))})
    
    @flask_app.route('/system/get_transcript/<num_lines>', methods = ['GET'])
    def get_transcript(num_lines):
        transcript = app_instance.get_transcript(num_lines)
        if not transcript:
            return jsonify({"error": "Transcript not found"}), 404
        return jsonify({"transcript": transcript}), 200
        
    @flask_app.route('/system/shutdown', methods = ['POST'])
    def shutdown():
        app_instance.shutdown()
        return jsonify({"message": "Shutdown initiated"}), 200
    
    @flask_app.route('/system/get_task_schedule', methods = ['GET'])
    def get_task_schedule():
        tasks = app_instance.system_task_manager.get_task_schedule()
        if not tasks:
            return jsonify({"error": "No scheduled tasks found"}), 404
        return jsonify({"tasks": tasks}), 200
    
    @flask_app.route('/system/get_task_types', methods = ['GET'])
    def get_task_types():
        if not app_instance.system_task_manager.task_types:
            return jsonify({"error": "No task types available"}), 404
        return jsonify({"task_types": app_instance.system_task_manager.task_types}), 200
    
    @flask_app.route('/system/get_r_script_tasks', methods = ['GET'])
    def get_r_script_tasks():
        tasks = app_instance.system_task_manager.get_r_script_tasks()
        if not tasks:
            return jsonify({"error": "No R script tasks found"}), 404
        return jsonify({"r_script_tasks": tasks}), 200
    
    @flask_app.route('/system/add_system_task/<task_type>/<task_time>', methods = ['POST'])
    def add_system_task(task_type, task_time):
        if task_type not in app_instance.system_task_manager.task_types:
            return jsonify({"error": "Invalid task type"}), 400
        app_instance.system_task_manager.add_task(task_type, task_time)
        app_instance.system_task_manager.save_tasks()
        app_instance.add_to_transcript(f"Added system task via API: {task_type} at {task_time}", "INFO")
        return jsonify({"message": "Task added successfully"}), 200
    
    @flask_app.route('/system/remove_system_task/<task_type>/<task_time>', methods = ['DELETE'])
    def remove_system_task(task_type, task_time):
        if task_type not in app_instance.system_task_manager.task_types:
            return jsonify({"error": "Invalid task type."}), 400
        elif app_instance.system_task_manager.remove_task(task_type, task_time = task_time) != 0:
            return jsonify({"error": "Task not found."}), 404
        return jsonify({"message": "Task removed successfully."}), 200
    
    @flask_app.route('/system/execute_task/<task_type>', methods = ['POST'])
    def execute_task(task_type):
        if task_type not in app_instance.system_task_manager.task_types:
            return jsonify({"error": "Invalid task type."}), 400
        elif app_instance.system_task_manager.process_task({'task_type': task_type}) != 0:
            return jsonify({"error": f"Failed to execute {task_type}."}), 500
        return jsonify({"message": f"{task_type} executed successfully."}), 200
        
    #################
    #  Participants #
    #################

    @flask_app.route('/participants/get_participants', methods = ['GET'])
    def get_participants():
        participants = app_instance.participant_manager.get_participants()
        if not participants:
            return jsonify({"error": "No participants found"}), 404
        return jsonify({"participants": participants}), 200
    
    @flask_app.route('/participants/get_participant_task_schedule', methods = ['GET'])
    def get_participant_task_schedule():
        tasks = app_instance.participant_manager.get_task_schedule()
        if not tasks:
            return jsonify({"error": "No participant tasks found"}), 404
        return jsonify({"tasks": tasks}), 200
    
    @flask_app.route('/participants/refresh_participants', methods = ['POST'])
    def refresh_participants():
        if app_instance.participant_manager.load_participants() != 0:
            return jsonify({"error": "Failed to refresh participants"}), 500
        app_instance.add_to_transcript("Participants refreshed via API.", "WARNING")
        return jsonify({"message": "Participants refreshed successfully"}), 200
    
    @flask_app.route('/participants/get_participant/<unique_id>', methods = ['GET'])
    def get_participant(unique_id):
        participant = app_instance.participant_manager.get_participant(unique_id)
        if not participant:
            app_instance.add_to_transcript(f"Participant {unique_id} not found for retrieval", "ERROR")
            return jsonify({"error": "Participant not found"}), 404
        app_instance.add_to_transcript(f"Participant #{unique_id} information requested via API.", "INFO")
        return jsonify({"participant": participant}), 200

    @flask_app.route('/participants/add_participant', methods = ['POST'])
    def add_participant():
        data = request.get_json()
        required_fields = ['unique_id', 'last_name', 'first_name', 'on_study', 'phone_number', 'ema_time', 'ema_reminder_time', 'feedback_time', 'feedback_reminder_time']
        if not all(field in data for field in required_fields):
            return jsonify({"error": "Missing required fields"}), 400
        app_instance.participant_manager.add_participant(data)
        app_instance.add_to_transcript(f"Participant #{data['unique_id']} added via API.", "INFO")
        return jsonify({"message": "Participant added successfully"}), 200
    
    @flask_app.route('/participants/remove_participant/<unique_id>', methods = ['DELETE'])
    def remove_participant(unique_id):
        if app_instance.participant_manager.remove_participant(unique_id) != 0:
            return jsonify({"error": "Participant not found"}), 404
        app_instance.add_to_transcript(f"Participant #{unique_id} removed via API.", "INFO")
        return jsonify({"message": "Participant removed successfully"}), 200
        
    @flask_app.route('/participants/update_participant/<unique_id>/<field>/<new_value>', methods = ['PUT'])
    def update_participant(unique_id, field, new_value):
        if app_instance.participant_manager.update_participant(unique_id, field, new_value) != 0:
            return jsonify({"error": "Participant not found"}), 404
        app_instance.add_to_transcript(f"Participant #{unique_id} updated via API: {field} changed to {new_value}", "INFO")
        return jsonify({"message": "Participant updated successfully"}), 200
    
    @flask_app.route('/participants/send_survey/<unique_id>/<survey_type>', methods = ['POST'])
    def send_survey(unique_id, survey_type):
        if survey_type not in ['ema', 'feedback']:
            return jsonify({"error": "Invalid survey type"}), 400
        elif not app_instance.participant_manager.get_participant(unique_id):
            return jsonify({"error": "Participant not found"}), 404
        app_instance.participant_manager.add_task(survey_type, (datetime.now() + timedelta(seconds = 10)).strftime('%H:%M:%S'), unique_id)
        return jsonify({"message": f"{survey_type.capitalize()} survey sent to participant {unique_id}"}), 200

    return flask_app