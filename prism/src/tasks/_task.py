import random
from datetime import datetime
from _helper import send_sms

class Task:
    def __init__(self, app):
        self.app = app
        self.task_number = str(random.randint(100000, 999999))
        self.task_start = datetime.now()

    def execute(self):
        result = self.run()
        status = "SUCCESS" if result == 0 else "FAILURE"
        self.outcome = status
        print(f"{self.task_type} #{self.task_number} completed with status: {status}.")

        if self.app.notify_coordinators:
            sms_result = self.notify_via_sms()
            if sms_result != 0:
                print(f"ERROR: Failed to send {sms_result} SMS notifications.")

        if status == "FAILURE":
            return 1
        else:
            return 0

    def notify_via_sms(self):
        result = 0
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
                            result = send_sms(self.app, [phone_number], [body])
        except FileNotFoundError:
            print("WARNING: No study coordinators found. SMS notifications will not be sent.")
            return 1
        except Exception as e:
            print(f"ERROR: Failed to send SMS notifications. Error message: {e}")
            return 1

        return result