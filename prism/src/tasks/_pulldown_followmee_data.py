import pandas as pd
import json
from datetime import datetime
import pytz
from datetime import timedelta
import requests
from requests.exceptions import ConnectionError, Timeout
from tasks._task import Task
from collections import defaultdict
import os

class PulldownFollowmeeData(Task):
    def run(self):
        self.task_type = "PULLDOWN_FOLLOWMEE_DATA"
        self.app.add_to_transcript(f"{self.task_type} #{self.task_number} now attempting to pull down FollowMee data...", "INFO")

        if self.pull_down_followmee_data("raw_followmee_data.json", "processed_followmee_data.csv"):
            return 1
        
        return 0
    
    def get_one_week_ago_date(self):
        utc = pytz.UTC
        current_date = datetime.now(utc)
        one_week_ago = (current_date - timedelta(weeks=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return one_week_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_one_day_ago_date(self):
        utc = pytz.UTC
        current_date = datetime.now(utc)
        one_day_ago = (current_date - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        return one_day_ago.strftime("%Y-%m-%dT%H:%M:%SZ")

    def get_followmee_devices(self):
        self.app.add_to_transcript("Retrieving FollowMee devices...", "INFO")

        username = self.app.followmee_username
        api_key = self.app.followmee_api_token

        url = f"https://www.followmee.com/api/info.aspx?key={api_key}&username={username}&function=devicelist"
        
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                devices = response.json().get('Data', [])
                if len(devices) == 0:
                    self.app.add_to_transcript("ERROR: No devices found.")
                    return None
                else:
                    self.app.add_to_transcript(f"INFO: Retrieved {len(devices)} devices.")
                    file_path = f"../data/followmee/raw/followmee_device_list.json"
                    os.makedirs(os.path.dirname(file_path), exist_ok = True)
                    with open(file_path, "w") as file:
                        json.dump(devices, file, indent = 4)
                    self.app.add_to_transcript(f"INFO: Device list saved to followmee_device_list.json.")
                    return file_path
            else:
                self.app.add_to_transcript(f"ERROR: Failed to retrieve device list. Status code: {response.status_code}")
                self.app.add_to_transcript(f"ERROR: Response Text: {response.text}")
                return None
        except (ConnectionError, Timeout) as e:
            self.app.add_to_transcript(f"ERROR: Connection error occurred: {str(e)}")
            return None

    def pull_down_followmee_data(self, raw_file_name, processed_file_name):
        self.app.add_to_transcript("Now pulling down FollowMee data...", "INFO")

        username = self.app.followmee_username
        api_key = self.app.followmee_api_token

        device_list_file = self.get_followmee_devices()
        if not device_list_file:
            return 1

        with open(device_list_file, "r") as file:
            devices = json.load(file)

        device_ids = [device['DeviceID'] for device in devices]
        from_date = self.get_one_day_ago_date()
        to_date = datetime.now(pytz.UTC).strftime("%Y-%m-%dT%H:%M:%SZ")

        device_id_param = f"&deviceid={','.join(map(str, device_ids))}"
        url = f"https://www.followmee.com/api/tracks.aspx?key={api_key}&username={username}&output=json&function=daterangeforalldevices&from={from_date}&to={to_date}{device_id_param}"

        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                data = response.json()

                filepath = f"../data/followmee/raw/{raw_file_name}"
                os.makedirs(os.path.dirname(filepath), exist_ok = True)
                with open(filepath, "w") as file:
                    json.dump(data, file, indent=4)

                self.app.add_to_transcript(f"INFO: FollowMee data saved to {raw_file_name}.")
                
                if self.process_followmee_data(raw_file_name, processed_file_name) == 0:
                    return 0
                else:
                    return 1
            else:
                self.app.add_to_transcript(f"ERROR: Failed to download FollowMee data. Status code: {response.status_code}")
                self.app.add_to_transcript(f"ERROR: Response Text: {response.text}")
                return 1
        except (ConnectionError, Timeout) as e:
            self.app.add_to_transcript(f"ERROR: Connection error occurred: {str(e)}")
            return 1
        
    def process_followmee_data(self, raw_file_name, processed_file_name):
        try:
            filepath = f"../data/followmee/raw/{raw_file_name}"
            with open(filepath, "r") as file:
                new_data = json.load(file)

            new_grouped_data = defaultdict(list)
            for entry in new_data['Data']:
                device_id = entry['DeviceID']
                new_grouped_data[device_id].append(entry)

            for device_id, entries in new_grouped_data.items():
                device_processed_file = f"../data/followmee/processed/{device_id}_{processed_file_name}"

                if os.path.exists(device_processed_file):
                    existing_data = pd.read_csv(device_processed_file)
                else:
                    os.makedirs(os.path.dirname(device_processed_file), exist_ok=True)
                    existing_data = pd.DataFrame()

                new_entries_df = pd.DataFrame(entries)
                updated_data = pd.concat([existing_data, new_entries_df]).drop_duplicates()

                updated_data.to_csv(device_processed_file, index=False)

                self.app.add_to_transcript(f"INFO: Processed data for device {device_id} saved to {device_processed_file}.")

            return 0

        except Exception as e:
            self.app.add_to_transcript(f"ERROR: Failed to process FollowMee data. Exception: {str(e)}")
            return 1