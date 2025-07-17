from _helper import send_sms
from task_managers._task_manager import TaskManager

class ParticipantManager(TaskManager):
    def __init__(self, app, name = "ParticipantManager"):
        super().__init__(app, name)
        self.survey_types = {
            'ema': 'ema_time',
            'ema_reminder': 'ema_reminder_time',
            'feedback': 'feedback_time',
            'feedback_reminder': 'feedback_reminder_time'
        }
        self.participants = []
        self.file_path = '../config/study_participants.csv'
        self.load_participants()

    def load_participants(self):
        try:
            self.participants.clear()
            self.tasks.clear()
            with open(self.file_path, 'r') as file:
                lines = file.readlines()
                for line in lines[1:]:
                    if line.strip():
                        parts = line.strip().split(',')
                        participant = {
                            'unique_id': parts[0].strip('"'),
                            'last_name': parts[1].strip('"'),
                            'first_name': parts[2].strip('"'),
                            'on_study': parts[3].strip('"').lower() == 'true',
                            'phone_number': parts[4].strip('"'),
                            'ema_time': parts[5].strip('"'),
                            'ema_reminder_time': parts[6].strip('"'),
                            'feedback_time': parts[7].strip('"'),
                            'feedback_reminder_time': parts[8].strip('"')
                        }
                        self.participants.append(participant)
                        self.schedule_participant_tasks(participant)
            return 0
        except Exception as e:
            self.app.add_to_transcript(f"Failed to load participants from CSV: {e}", "ERROR")
            return 1
        
    def get_participant(self, unique_id):
        try:
            for participant in self.participants:
                if participant['unique_id'] == unique_id:
                    return participant
            self.app.add_to_transcript(f"Participant with ID {unique_id} not found.", "ERROR")
            return None
        except Exception as e:
            self.app.add_to_transcript(f"Failed to retrieve participant {unique_id}: {e}", "ERROR")
            return None
    
    def get_participants(self):
        try:
            return [
                {
                    'unique_id': participant['unique_id'],
                    'last_name': participant['last_name'],
                    'first_name': participant['first_name'],
                    'on_study': participant['on_study'],
                } for participant in self.participants
            ]
        except Exception as e:
            self.app.add_to_transcript(f"Failed to retrieve participants: {e}", "ERROR")
            return []
        
    def save_participants(self):
        self.save_to_csv(self.participants, self.file_path)
        
    def update_participant(self, unique_id, field, value):
        try:
            participant = self.get_participant(unique_id)
            if participant:
                if field in participant:
                    participant[field] = value
                    self.save_participants()
                    for task_type, field_name in self.survey_types.items():
                        if field_name == field:
                            self.remove_task(task_type, participant_id = unique_id)
                            self.add_task(task_type, value, participant_id = unique_id)
                    self.app.add_to_transcript(f"Updated {field} for participant {unique_id} to {value}.", "INFO")
                    return 0
                else:
                    self.app.add_to_transcript(f"Field {field} does not exist for participant {unique_id}.", "ERROR")
                    return 1
            else:
                self.app.add_to_transcript(f"Failed to update participant {unique_id}: Participant not found.", "ERROR")
                return 1
        except Exception as e:
            self.app.add_to_transcript(f"An error occurred while updating participant {unique_id}: {e}", "ERROR")
            return 1
        
    def add_participant(self, participant):
        self.participants.append(participant)
        self.save_participants()
        self.schedule_participant_tasks(participant)

    def schedule_participant_tasks(self, participant):
        for task_type, field_name in self.survey_types.items():
            task_time_str = participant.get(field_name)
            if task_time_str:
                self.add_task(task_type, task_time_str, participant_id = participant['unique_id'])

    def remove_participant(self, unique_id):
        participant = self.get_participant(unique_id)
        if participant:
            self.participants.remove(participant)
            self.save_participants()
            for task_type, field_name in self.survey_types.items():
                self.remove_task(task_type, participant_id = unique_id)
            self.app.add_to_transcript(f"Removed participant {unique_id}.", "INFO")
            return 0
        return 1
        
    def remove_task(self, task_type, task_time = None, participant_id = None):
        for task in self.tasks:
            if task['participant_id'] == participant_id and task['task_type'] == task_type:
                self.tasks.remove(task)
                self.app.add_to_transcript(f"Removed SMS task: {task_type} for participant {participant_id}", "INFO")
                return 0
        self.app.add_to_transcript(f"SMS task {task_type} for participant {participant_id} not found.", "ERROR")
        return 1
    
    def get_task_schedule(self):
        try:
            return [
                {
                    "participant_id": task.get('participant_id', 'N/A'),
                    "on_study": self.get_participant(task['participant_id'])['on_study'] if 'participant_id' in task else 'N/A',
                    "task_type": task['task_type'],
                    "task_time": task['task_time'].strftime('%H:%M:%S'),
                    "run_today": task.get('run_today', False)
                } for task in self.tasks
            ]
        except Exception as e:
            self.add_to_transcript(f"Failed to retrieve system task schedule: {e}", "ERROR")
            return []
    
    def process_task(self, task):
        participant_id = task.get('participant_id')
        if not participant_id:
            self.app.add_to_transcript("Participant ID is missing in SMS task.", "ERROR")
            return -1
        participant = self.get_participant(participant_id)
        if participant['on_study'] is False:
            return 0
        task_type = task.get('task_type')
        participant_name = f"{participant['first_name']} {participant['last_name']}"
        participant_phone_number = participant['phone_number']
        self.app.add_to_transcript(f"Processing SMS task: {task_type} for participant {participant_id}", "INFO")
        task_map = {
            'ema': (self.app.ema_survey_id, "it's time to take your ecological momentary assessment survey."),
            'ema_reminder': (self.app.ema_survey_id, "you have not yet completed your ecological momentary assessment survey for today."),
            'feedback': (self.app.feedback_survey_id, "it's time to take your feedback survey."),
            'feedback_reminder': (self.app.feedback_survey_id, "you have not yet completed your feedback survey for today.")
        }
        if task_type not in task_map:
            self.app.add_to_transcript(f"Unknown SMS task type: {task_type}", "ERROR")
            return -1
        survey_id, message = task_map[task_type]
        survey_link = f"https://uwmadison.co1.qualtrics.com/jfe/form/{survey_id}?ParticipantID={participant_id}"
        body = f"{participant_name}, {message} {survey_link}"
        try:
            if self.app.mode == "prod":
                send_sms(self.app, [participant_phone_number], [body])
            self.app.add_to_transcript(f"SMS sent to {participant_id}.", "INFO")
            return 0
        except Exception as e:
            self.app.add_to_transcript(f"Failed to send SMS to {participant_id}: {e}", "ERROR")
            return -1