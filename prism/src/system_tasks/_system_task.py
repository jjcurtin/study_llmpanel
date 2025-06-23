import random
from datetime import datetime
from _helper import send_sms

class SystemTask:
    def __init__(self, app):
        self.app = app
        self.task_number = str(random.randint(100000, 999999))
        self.task_start = datetime.now()

    def execute(self):
        result = self.run()
        self.outcome = "SUCCESS" if result == 0 else "FAILURE"
        self.app.add_to_transcript(f"{self.task_type} #{self.task_number} completed with status: {self.outcome}.", "INFO")
        if self.outcome == "FAILURE":
            if self.app.mode == "prod":
                sms_result = self.notify_via_sms()
                if sms_result != 0:
                    self.app.add_to_transcript(f"Failed to send {sms_result} SMS notifications.", "ERROR")
            return 1
        return 0

    def notify_via_sms(self):
        try:
            with open('../config/study_coordinators.csv', 'r') as f:
                lines = f.readlines()
                lines = lines[1:]
                for line in lines:
                    line = line.strip()
                    if line:
                        name, phone_number = line.split(',')
                        name = name.strip('"')
                        phone_number = phone_number.strip('"')
                        if phone_number and phone_number != "":
                            body = f"{name}: {self.task_type} #{self.task_number} {self.outcome}. Script was executed at {self.task_start.strftime('%m/%d/%Y at %I:%M:%S %p')}."
                            return send_sms(self.app, [phone_number], [body])
        except FileNotFoundError:
            self.app.add_to_transcript("No study coordinators found. SMS notifications will not be sent.", "WARNING")
            return 1
        except Exception as e:
            self.app.add_to_transcript(f"Failed to send SMS notifications. Error message: {e}", "ERROR")
            return 1