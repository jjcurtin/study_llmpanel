from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import time
from datetime import datetime
from datetime import timedelta

from _helper import send_sms

def create_flask_app(app_instance):
    flask_app = Flask(__name__)
    
    if app_instance.mode == "prod":
        CORS(flask_app, resources = {
            r"/system/*": {"origins": "localhost:5000"},
            r"/system/get_uptime": {"origins": "*"},
            r"/participants/*": {"origins": "localhost:5000"},
            r"/EMA/*": {"origins": "https://uwmadison.co1.qualtrics.com"},
            r"/feedback_survey/*": {"origins": "https://uwmadison.co1.qualtrics.com"}
        })
    else:
        CORS(flask_app, resources = {
            r"/system/*": {"origins": "localhost:5000"},
            r"/participants/*": {"origins": "localhost:5000"},
            r"/EMA/*": {"origins": "https://uwmadison.co1.qualtrics.com"},
            r"/feedback_survey/*": {"origins": "https://uwmadison.co1.qualtrics.com"}
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
    
    @flask_app.route('/system/get_ema_log/<num_lines>', methods = ['GET'])
    def get_ema_log(num_lines):
        transcript = app_instance.get_transcript(num_lines, "ema_log")
        if not transcript:
            return jsonify({"error": "Transcript not found"}), 404
        return jsonify({"transcript": transcript}), 200
    
    @flask_app.route('/system/get_feedback_log/<num_lines>', methods = ['GET'])
    def get_feedback_log(num_lines):
        transcript = app_instance.get_transcript(num_lines, "feedback_log")
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
        app_instance.system_task_manager.add_task(task_type, task_time, r_script_path = "")
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
    
    @flask_app.route('/system/add_r_script_task/<r_script_path>/<task_time>', methods = ['POST'])
    def add_r_script_task(r_script_path, task_time):
        if not r_script_path:
            return jsonify({"error": "R script path cannot be empty."}), 400
        try:
            datetime.strptime(task_time, '%H:%M:%S')
        except ValueError:
            return jsonify({"error": "Invalid time format."}), 400
        app_instance.system_task_manager.add_task("RUN_R_SCRIPT", task_time, r_script_path = r_script_path)
        app_instance.system_task_manager.save_tasks()
        app_instance.add_to_transcript(f"Added R script task via API: {r_script_path} at {task_time}", "INFO")
        return jsonify({"message": "R script task added successfully"}), 200
    
    @flask_app.route('/system/remove_r_script_task/<r_script_path>/<task_time>', methods = ['DELETE'])
    def remove_r_script_task(r_script_path, task_time):
        if not r_script_path:
            return jsonify({"error": "R script path cannot be empty."}), 400
        elif app_instance.system_task_manager.remove_task("RUN_R_SCRIPT", task_time = task_time, r_script_path = r_script_path) != 0:
            return jsonify({"error": "R script task not found."}), 404
        return jsonify({"message": "R script task removed successfully."}), 200
    
    @flask_app.route('/system/execute_r_script_task/<r_script_path>', methods = ['POST'])
    def execute_r_script_task(r_script_path):
        if not r_script_path:
            return jsonify({"error": "R script path cannot be empty."}), 400
        task = {'task_type': 'RUN_R_SCRIPT', 'r_script_path': r_script_path}
        if app_instance.system_task_manager.process_task(task) != 0:
            return jsonify({"error": f"Failed to execute R script task: {r_script_path}."}), 500
        return jsonify({"message": f"R script task {r_script_path} executed successfully."}), 200
        
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
        app_instance.participant_manager.add_task(survey_type, (datetime.now() + timedelta(seconds = 10)).strftime('%H:%M:%S'), participant_id = unique_id)
        return jsonify({"message": f"{survey_type.capitalize()} survey sent to participant {unique_id}"}), 200

    @flask_app.route('/participants/send_custom_sms/<unique_id>', methods = ['POST'])
    def send_custom_sms(unique_id):
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message content is required"}), 400
        participant = app_instance.participant_manager.get_participant(unique_id)
        if not participant:
            return jsonify({"error": "Participant not found"}), 404
        if app_instance.mode == "prod":
            send_sms(app_instance, [participant['phone_number']], [data['message']])
        return jsonify({"message": f"Custom SMS sent to participant {unique_id}"}), 200
    
    @flask_app.route('/participants/study_announcement/<require_on_study>', methods = ['POST'])
    def study_announcement(require_on_study):
        data = request.get_json()
        if not data or 'message' not in data:
            return jsonify({"error": "Message content is required"}), 400
        if not app_instance.participant_manager.participants:
            return jsonify({"error": "No participants found"}), 404
        
        if require_on_study.lower() == 'yes':
            phone_numbers = [p['phone_number'] for p in app_instance.participant_manager.participants if p['on_study']]
        else:
            phone_numbers = [p['phone_number'] for p in app_instance.participant_manager.participants]
        
        if not phone_numbers:
            return jsonify({"error": "No participants on study"}), 404
        
        if app_instance.mode == "prod":
            for phone_number in phone_numbers:
                if phone_number.strip():
                    send_sms(app_instance, [phone_number], [data['message']])
                    app_instance.add_to_transcript(f"Study announcement sent to {phone_number}", "INFO")
        else:
            app_instance.add_to_transcript(f"Simulated sending messages.")
        return jsonify({"message": f"Study announcement sent to all participants, require on study: {require_on_study}"}), 200

    ####################
    #    EMA Logic     #
    ####################

    @flask_app.route('/EMA/access_ema/<unique_id>', methods=['GET'])
    def access_ema(unique_id):
        participant = app_instance.participant_manager.get_participant(unique_id)
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
                
        current_date = datetime.now().date()
        status_message = "It's time to take your ecological momentary assessment."
        transcript_message = "(first time today)"
        
        if app_instance.mode == "prod":
            log_file_path = f'../logs/ema_logs/{current_date}_ema_log.txt'
        else:
            log_file_path = '../logs/ema_logs/test_ema_log.txt'
        
        opened_ema_time = None
        finished_ema_time = None

        try:
            with open(log_file_path, 'r') as file:
                for line in file:
                    if f"#{unique_id} has opened an EMA survey" in line:
                        timestamp_str = line.split('at ')[-1].strip()
                        opened_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        if opened_time.date() == current_date:
                            opened_ema_time = opened_time
                    elif f"#{unique_id} has finished their EMA survey" in line:
                        timestamp_str = line.split('at ')[-1].strip()
                        finished_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        if finished_time.date() == current_date:
                            finished_ema_time = finished_time
            
            if finished_ema_time:
                status_message = "You've already completed your ecological momentary assessment for today."
                transcript_message = "(already completed)"
            elif opened_ema_time and not finished_ema_time:
                transcript_message = "(resumed)"
                status_message = "It's time to resume your ecological momentary assessment."
        except FileNotFoundError:
            app_instance.add_to_transcript(f"Log file {log_file_path} not found. Creating a new one.", "WARNING")
            with open(log_file_path, 'w') as file:
                file.write(f"Log file created on {current_date}.\n")
        
        app_instance.add_to_transcript(f"#{unique_id} has opened an EMA survey at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} {transcript_message}")
        
        with open(log_file_path, 'a') as file:
            file.write(f"#{unique_id} has opened an EMA survey at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        
        participant_name = f"{participant['first_name']} {participant['last_name']}"

        if participant_name:
            return jsonify({'subject_name': participant_name, 'status': status_message}), 200
        else:
            return jsonify({'error': 'Subject name not found'}), 404
        
    @flask_app.route('/EMA/request_coords/<unique_id>', methods = ['GET'])
    def request_coords(unique_id):
        app_instance.add_to_transcript(f"Coordinates requested for participant {unique_id}", "INFO")
        coords = app_instance.participant_manager.get_coords(unique_id)
        if not coords:
            app_instance.add_to_transcript(f"Coordinates not found for participant {unique_id}", "ERROR")
            return jsonify({'error': 'No coordinates found for this participant'}), 404
        
        return jsonify(coords), 200

    @flask_app.route('/EMA/submit_ema', methods=['POST'])
    def submit_ema():
        data = request.get_json()

        participant_id = data.get('participantID')
        subject_name = data.get('subjectName')

        if participant_id and subject_name:
            app_instance.add_to_transcript(f"#{participant_id} has finished their EMA survey at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            if app_instance.mode == "prod":
                current_date = datetime.now().strftime('%Y-%m-%d')
                filepath = f"../logs/ema_logs/{current_date}_ema_log.txt"
            else:
                filepath = "../logs/ema_logs/test_ema_log.txt"
            with open(filepath, 'a') as file:
                file.write(f"#{participant_id} has finished their EMA survey at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            return jsonify({'message': 'EMA submission successful'}), 200
        else:
            return jsonify({'error': 'Missing participantID or subjectName'}), 400
        
    ################################
    #    Feedback Survey Logic     #
    ################################

    @flask_app.route('/feedback_survey/access_feedback/<unique_id>', methods=['GET'])
    def access_feedback(unique_id):
        participant = app_instance.participant_manager.get_participant(unique_id)
        if not participant:
            return jsonify({'error': 'Participant not found'}), 404
        
        subject_name = f"{participant['first_name']} {participant['last_name']}"
        current_date = datetime.now().date()
        lapse_data = app_instance.participant_manager.get_lapse_data_and_message(unique_id)
        
        if app_instance.mode == "prod":
            log_file_path = f'../logs/feedback_logs/{current_date}_feedback_log.txt'
        else:
            log_file_path = '../logs/feedback_logs/test_feedback_log.txt'
        
        opened_recommendations_time = None
        finished_recommendations_time = None
        
        try:
            with open(log_file_path, 'r') as file:
                for line in file:
                    if f"#{unique_id} has opened their recommendations" in line:
                        timestamp_str = line.split('at ')[-1].strip()
                        opened_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        if opened_time.date() == current_date:
                            opened_recommendations_time = opened_time
                    elif f"#{unique_id} has finished their recommendations" in line:
                        timestamp_str = line.split('at ')[-1].strip()
                        finished_time = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        if finished_time.date() == current_date:
                            finished_recommendations_time = finished_time
        except FileNotFoundError:
            app_instance.add_to_transcript(f"Log file {log_file_path} not found. Creating a new one.", "WARNING")
            with open(log_file_path, 'w') as file:
                file.write(f"Log file created on {current_date}.\n")

        if finished_recommendations_time:
            status_message = "You've already submitted the acknowledgement of your recommendations for today."
        elif opened_recommendations_time:
            status_message = "You're viewing today's recommendations again but have not acknowledged them with the button."
        else:
            status_message = "It's time to view your recommendations for today."

        app_instance.add_to_transcript(f"#{unique_id} has opened their recommendations at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        with open(log_file_path, 'a') as file:
            file.write(f"#{unique_id} has opened their recommendations at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

        if subject_name:
            return jsonify({'subject_name': subject_name, 
                            'status': status_message,
                            'lapse_level': lapse_data['lapse_level'],
                            'lapse_change': lapse_data['lapse_change'],
                            'most_important_feature': lapse_data['most_important_feature'],
                            'message': lapse_data['message']
                            }), 200
        else:
            return jsonify({'error': 'Subject name not found'}), 404
        
    @flask_app.route('/feedback_survey/submit_feedback', methods=['POST'])
    def submit_recommendations():
        data = request.get_json()

        participant_id = data.get('participantID')
        subject_name = data.get('subjectName')

        current_date = datetime.now().strftime('%Y-%m-%d')

        if participant_id and subject_name:
            app_instance.add_to_transcript(f"#{participant_id} has finished their recommendations at {time.strftime('%Y-%m-%d %H:%M:%S')}")
            if app_instance.mode == "prod":
                filepath = f"../logs/feedback_logs/{current_date}_feedback_log.txt"
            else:
                filepath = "../logs/feedback_logs/test_feedback_log.txt"
            with open(filepath, 'a') as file:
                file.write(f"#{participant_id} has finished their recommendations at {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
            return jsonify({'message': 'Recommendations submission successful'}), 200
        else:
            return jsonify({'error': 'Missing participantID or subjectName'}), 400

    return flask_app