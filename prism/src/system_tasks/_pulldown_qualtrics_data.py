# script to pull down Qualtrics data and process it

import pandas as pd
import time
import requests
from requests.exceptions import ConnectionError, Timeout
import os
import warnings

from system_tasks._system_task import SystemTask

class PulldownQualtricsData(SystemTask):
    def run(self):
        self.task_type = "PULLDOWN_QUALTRICS_DATA"
        self.app.add_to_transcript(f"{self.task_type} #{self.task_number} now attempting to pull down Qualtrics data...", "INFO")

        if self.pull_down_qualtrics_data("EMA", "raw_qualtrics_ema_data.csv", "filtered_qualtrics_ema_data.csv"):
            return 1
        
        if self.pull_down_qualtrics_data("feedback", "raw_qualtrics_feedback_data.csv", "filtered_qualtrics_feedback_data.csv"):
            return 1
        
        return 0

    def pull_down_qualtrics_data(self, data_type, raw_file_name, processed_file_name):
        if data_type == "EMA":
            self.app.add_to_transcript("Now pulling down EMA data from Qualtrics...", "INFO")
            survey_id = self.app.ema_survey_id
        elif data_type == "feedback":
            self.app.add_to_transcript("Now pulling down feedback data from Qualtrics...", "INFO")
            survey_id = self.app.feedback_survey_id
        
        export_progress_id = self.initiate_qualtrics_report_generation(survey_id)
        if not export_progress_id:
            return 1

        file_id = self.poll_qualtrics_export_status(survey_id, export_progress_id)
        if not file_id:
            return 1

        data = self.download_qualtrics_report(survey_id, file_id, raw_file_name)
        if not data:
            return 1

        if self.process_qualtrics_responses(raw_file_name, processed_file_name, data_type):
            return 1

        return 0
    
    def initiate_qualtrics_report_generation(self, survey_id):
        url = f"https://{self.app.qualtrics_data_center}.qualtrics.com/API/v3/surveys/{survey_id}/export-responses"
        headers = {
            "X-API-TOKEN": self.app.qualtrics_api_token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }
        body = {
            "format": "csv",
            "compress": False,
        }

        try:
            response = requests.post(url, headers = headers, json = body)
        except (ConnectionError, Timeout) as e:
            self.app.add_to_transcript(f"Connection error occurred: {str(e)}", "ERROR")
            return None

        if response.status_code == 200:
            data = response.json()
            export_progress_id = data["result"]["progressId"]
            self.app.add_to_transcript(f"Report generation request received by Qualtrics.", "INFO")
            return export_progress_id
        else:
            self.app.add_to_transcript(f"Failed to initiate report generation. Status Code: {response.status_code}.", "ERROR")
            self.app.add_to_transcript(f"Response Text: {response.text}", "ERROR")
            return None

    def poll_qualtrics_export_status(self, survey_id, export_progress_id):
        elapsed_time = 0
        while elapsed_time <= 10:
            time.sleep(1)
            elapsed_time += 1
            url = f"https://{self.app.qualtrics_data_center}.qualtrics.com/API/v3/surveys/{survey_id}/export-responses/{export_progress_id}"
            headers = {"X-API-TOKEN": self.app.qualtrics_api_token}

            try:
                response = requests.get(url, headers = headers)
            except (ConnectionError, Timeout) as e:
                self.app.add_to_transcript(f"Connection error occurred: {str(e)}", "ERROR")
                return None

            if response.status_code == 200:
                data = response.json()
                status = data["result"]["status"]
                self.app.add_to_transcript(f"Report Status: {status}. Time Elapsed: {elapsed_time} seconds", "INFO")
                if status == "complete":
                    return data["result"]["fileId"]
            else:
                self.app.add_to_transcript(f"Failed to get export status for report. Status code: {response.status_code}", "ERROR")
                return None

        self.app.add_to_transcript(f"ERROR: Timeout. Elapsed Time: {elapsed_time} seconds")
        return None

    def download_qualtrics_report(self, survey_id, file_id, raw_file_name):
        url = f"https://{self.app.qualtrics_data_center}.qualtrics.com/API/v3/surveys/{survey_id}/export-responses/{file_id}/file"
        headers = {"X-API-TOKEN": self.app.qualtrics_api_token}

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.text
                filepath = f"../data/qualtrics/raw/{raw_file_name}"
                try:
                    os.makedirs(os.path.dirname(filepath), exist_ok=True)
                    with open(filepath, "w") as file:
                        file.write(data)
                except Exception as e:
                    self.app.add_to_transcript(f"Failed to save report to {filepath}. Error Message: {str(e)}", "ERROR")
                    return None
                self.app.add_to_transcript("Report downloaded successfully from Qualtrics.", "INFO")
                return data
            else:
                self.app.add_to_transcript(f"Failed to download report {file_id}", "ERROR")
                self.app.add_to_transcript(f"Status code: {response.status_code}", "ERROR")
                return None
        except (ConnectionError, Timeout) as e:
            self.app.add_to_transcript(f"Connection error occurred: {str(e)}", "ERROR")
            return None

    def process_qualtrics_responses(self, raw_file_name, processed_file_name, data_type):
        try:
            filepath = f"../data/qualtrics/raw/{raw_file_name}"
            df = pd.read_csv(filepath, encoding = 'ISO-8859-1', skip_blank_lines = True)
            start_row = df[df['StartDate'].notnull()].index[0]
            df = df.iloc[start_row:]
            df = df[df['StartDate'].str.match(r'\d{4}-\d{2}-\d{2}', na=False)]
            df.columns = df.columns.str.strip()
            df.columns = df.columns.str.replace(r"[^a-zA-Z0-9_\s]", "")
            with warnings.catch_warnings():
                warnings.simplefilter("ignore")
                df = df.applymap(lambda x: x.strip() if isinstance(x, str) else x)
            df = df.dropna(how='all', axis = 1)
            unwanted_string = "(already submitted feedback)"
            df = df[~df.apply(lambda row: row.astype(str).str.contains(unwanted_string, regex = False).any(), axis = 1)]
            processed_filepath = f"../data/qualtrics/processed/{processed_file_name}"
            os.makedirs(os.path.dirname(processed_filepath), exist_ok = True)
            df.to_csv(processed_filepath, index = False)
            if data_type == "ema":
                data_type_formatted = "EMA"
            elif data_type == "feedback":
                data_type_formatted = "Feedback"
            else:
                data_type_formatted = data_type
            self.app.add_to_transcript(f"{data_type_formatted} filtered and saved to {processed_file_name}.", "SUCCESS")
            return 0
        except Exception as e:
            self.app.add_to_transcript(f"Failed to filter responses. Error Message: {str(e)}", "ERROR")
            return 1