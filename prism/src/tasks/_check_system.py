import os
import sys
import subprocess
import requests
from requests.exceptions import ConnectionError, Timeout

from tasks._task import Task

class CheckSystem(Task):
    def run(self):
        self.task_type = "CHECK_SYSTEM"
        print(f"{self.task_type} #{self.task_number} initiated.")
        file_system_check = self.check_file_system()
        qualtrics_check = self.check_qualtrics()
        followmee_check = self.check_followmee()
        package_check = self.check_installed_packages()
        return file_system_check + qualtrics_check + followmee_check + package_check
    
    def check_installed_packages(self):
        print(f"INFO: Now checking installed packages...")
        try:
            with open("../requirements.txt", "r") as f:
                requirements = f.readlines()
            for req in requirements:
                req = req.strip()
                if req:
                    try:
                        __import__(req)
                    except ImportError:
                        print(f"WARNING: The package '{req}' is not installed. Attempting to install it...")
                        try:
                            subprocess.check_call([sys.executable, "-m", "pip", "install", req])
                            print(f"INFO: Successfully installed '{req}'.")
                        except subprocess.CalledProcessError as install_error:
                            print(f"ERROR: Failed to install '{req}'. {install_error}")
                            return 1
            return 0
        except Exception as e:
            print(f"ERROR: {e}")
            return 1

    def check_file_system(self):
        print(f"INFO: Now checking file system...")
        try:
            directories = [
                '../config',
                '../data',
                '../qualtrics_js',
                '../scripts',
                '../logs'
            ]
            files = [
                ['system_task_schedule.csv', 'study_coordinators.csv'], # config
                [], # data
                ['EMA_load_logic.js', 'EMA_submit_logic.js', 
                 'recommendationLoad.js', 'recommendationSubmit.js'], # qualtrics_js
                [], # scripts
                [] # logs
            ]

            for index, (directory, files_list) in enumerate(zip(directories, files)):
                if not os.path.exists(directory):
                    print(f"ERROR: The '{directory}' directory is missing.")

                for file in files_list:
                    file_path = os.path.join(directory, file)
                    if not os.path.isfile(file_path):
                        print(f"ERROR: The file '{file_path}' is missing.")

        except Exception as e:
            print(f"ERROR: {e}")
            return 1

        return 0
    
    def check_qualtrics(self):
        print(f"INFO: Now checking Qualtrics connection...")
        survey_id = self.app.ema_survey_id
        data_center = self.app.qualtrics_data_center
        api_token = self.app.qualtrics_api_token
        url = f"https://{data_center}.qualtrics.com/API/v3/survey-definitions/{survey_id}/metadata"
        headers = {"X-API-TOKEN": api_token}

        try:
            response = requests.get(url, headers = headers, timeout = 10)
            if response.status_code == 200:
                data = response.json()
                return 0
            else:
                print(f"ERROR: Status code: {response.status_code}")
                return 1
        except (ConnectionError, Timeout) as e:
            print(f"ERROR: Connection error occurred: {str(e)}")
            return 1
        
    def check_followmee(self):
        print(f"INFO: Now checking FollowMee connection...")
        username = self.app.followmee_username
        api_key = self.app.followmee_api_token

        url = f"https://www.followmee.com/api/info.aspx?key={api_key}&username={username}&function=devicelist"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                return 0
            else:
                print(f"ERROR: FollowMee connection failed. Status code: {response.status_code}")
                return 1
        except (ConnectionError, Timeout) as e:
            print(f"ERROR: FollowMee connection error occurred: {str(e)}")
            return 1