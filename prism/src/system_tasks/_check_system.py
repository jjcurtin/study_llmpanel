import os
import sys
import subprocess
import requests
from requests.exceptions import ConnectionError, Timeout

from system_tasks._system_task import SystemTask
from system_tasks._push_data_to_research_drive import PushDataToResearchDrive

class CheckSystem(SystemTask):
    def run(self):
        self.task_type = "CHECK_SYSTEM"
        self.app.add_to_transcript(f"{self.task_type} #{self.task_number} initiated.")
        file_system_check = self.check_file_system()
        qualtrics_check = self.check_qualtrics()
        followmee_check = self.check_followmee()
        package_check = self.check_installed_packages()
        research_drive_check = self.check_research_drive()
        participant_check = self.check_participants()
        return file_system_check + qualtrics_check + followmee_check + package_check + research_drive_check + participant_check
    
    def check_installed_packages(self):
        self.app.add_to_transcript(f"INFO: Now checking installed packages...")
        try:
            with open("../requirements.txt", "r") as f:
                requirements = f.readlines()
            for req in requirements:
                req = req.strip()
                if req:
                    try:
                        __import__(req)
                    except ImportError:
                        self.app.add_to_transcript(f"WARNING: The package '{req}' is not installed. Attempting to install it...")
                        try:
                            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
                            self.app.add_to_transcript(f"INFO: Successfully installed '{req}'.")
                        except subprocess.CalledProcessError as install_error:
                            self.app.add_to_transcript(f"ERROR: Failed to install '{req}'. {install_error}")
                            return 1
            return 0
        except Exception as e:
            self.app.add_to_transcript(f"ERROR: {e}")
            return 1

    def check_file_system(self):
        self.app.add_to_transcript(f"INFO: Now checking file system...")
        try:
            directories = [
                '../config',
                '../data',
                '../qualtrics_js',
                '../scripts',
                '../logs',
                'system_tasks'
            ]
            files = [
                ['system_task_schedule.csv', 'study_coordinators.csv', 
                 'script_pipeline.csv', 'study_participants.csv'], # config
                [], # data
                ['EMA_load_logic.js', 'EMA_submit_logic.js', 
                 'recommendationLoad.js', 'recommendationSubmit.js'], # qualtrics_js
                [], # scripts
                [], # logs
                ['_check_system.py', # obviously
                 '_pulldown_qualtrics_data.py', '_pulldown_followmee_data.py',
                 '_push_data_to_research_drive.py', '_run_r_script_pipeline.py',
                 '_system_task.py' # obviously
                ] # tasks
            ]

            for index, (directory, files_list) in enumerate(zip(directories, files)):
                if not os.path.exists(directory):
                    self.app.add_to_transcript(f"ERROR: The '{directory}' directory is missing.")
                for file in files_list:
                    file_path = os.path.join(directory, file)
                    if not os.path.isfile(file_path):
                        self.app.add_to_transcript(f"ERROR: The file '{file_path}' is missing.")

        except Exception as e:
            self.app.add_to_transcript(f"ERROR: {e}")
            return 1

        return 0
    
    def check_qualtrics(self):
        self.app.add_to_transcript(f"INFO: Now checking Qualtrics connection...")
        survey_id = self.app.ema_survey_id
        data_center = self.app.qualtrics_data_center
        api_token = self.app.qualtrics_api_token
        url = f"https://{data_center}.qualtrics.com/API/v3/survey-definitions/{survey_id}/metadata"
        headers = {"X-API-TOKEN": api_token}
        try:
            response = requests.get(url, headers = headers, timeout = 10)
            if response.status_code == 200:
                return 0
            self.app.add_to_transcript(f"ERROR: Status code: {response.status_code}")
            return 1
        except (ConnectionError, Timeout) as e:
            self.app.add_to_transcript(f"ERROR: Connection error occurred: {str(e)}")
            return 1
        
    def check_followmee(self):
        self.app.add_to_transcript(f"INFO: Now checking FollowMee connection...")
        username = self.app.followmee_username
        api_key = self.app.followmee_api_token
        url = f"https://www.followmee.com/api/info.aspx?key={api_key}&username={username}&function=devicelist"
        try:
            response = requests.get(url, timeout = 10)
            if response.status_code == 200:
                return 0
            self.app.add_to_transcript(f"ERROR: FollowMee connection failed. Status code: {response.status_code}")
            return 1
        except (ConnectionError, Timeout) as e:
            self.app.add_to_transcript(f"ERROR: FollowMee connection error occurred: {str(e)}")
            return 1
        
    def check_research_drive(self):
        if self.app.mode == "prod":
            self.app.add_to_transcript(f"INFO: Now checking Research Drive connection...")
            researchdrivetest = PushDataToResearchDrive(self.app)
            researchdrivetest.task_type = "PUSH_DATA_TO_RESEARCH_DRIVE"
            result = researchdrivetest.map_network_drive()
            if result != 0:
                self.app.add_to_transcript("ERROR: Failed to connect to Research Drive.")
                return 1
            self.app.add_to_transcript("INFO: Successfully connected to Research Drive.")
        return 0
    
    def check_participants(self):
        self.app.add_to_transcript("INFO: Now checking participants...")
        
        # unique id check
        participants = self.app.participant_manager.get_participants()
        unique_ids = {}
        for p in participants:
            unique_id = p.get('unique_id')
            if unique_id:
                if unique_id in unique_ids:
                    unique_ids[unique_id].append(p['first_name'] + " " + p['last_name'])
                else:
                    unique_ids[unique_id] = [p['first_name'] + " " + p['last_name']]
        duplicates = {uid: names for uid, names in unique_ids.items() if len(names) > 1}
        if duplicates:
            self.app.add_to_transcript("ERROR: Duplicate unique IDs found among participants:")
            for uid, names in duplicates.items():
                self.app.add_to_transcript(f"Unique ID: {uid}, Participants: {', '.join(names)}")
            self.app.add_to_transcript("Please remedy these issues either through this interface or in the CSV file and refresh from CSV when you are ready.")
            return 1
        return 0