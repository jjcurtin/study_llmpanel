import os

from system_tasks._system_task import SystemTask

class PushDataToResearchDrive(SystemTask):
    def map_network_drive(self):
        self.app.add_to_transcript(f"{self.task_type} #{self.task_number} now attempting to map to the research drive...")
        mapped_drives = os.popen("net use").read()
        if self.app.drive_letter not in mapped_drives:
            try:
                netid = self.app.wisc_netid
                password = self.app.wisc_password
                domain_netid = f"{netid}@ad.wisc.edu"
                network_domain = self.app.network_domain
                network_username = self.app.network_username
                network_path = f"\\\\{network_domain}\\{network_username}"
                command = f'net use {self.app.drive_letter} "{network_path}" /user:{domain_netid} "{password}"'
                result = os.system(command)
                if result == 0:
                    self.app.add_to_transcript("INFO: Network drive mapped successfully.")
                    return 0
                else:
                    raise ConnectionError("Failed to map network drive. Please check your credentials and ensure you are connected to WiscVPN.")
            except Exception as e:
                self.app.add_to_transcript(f"ERROR: Authentication failed: {e}")
                print("ERROR: Authentication failed. Please try again.")
                return 1
        else:
            self.app.add_to_transcript(f"INFO: Drive {self.app.drive_letter} is already mapped. Skipping authentication.")
            return 0

    def upload_files(self):
        source_paths = [
                "../data"
            ]
        for source_path in source_paths:
            source_folder = source_path.split("/")[-1]
            destination_folder = f"{self.app.drive_letter}\\{self.app.destination_path}\\{source_folder}"
            try:
                os.system(f"robocopy {source_path} {destination_folder} /MIR")
            except Exception as e:
                self.app.add_to_transcript(f"ERROR: Failed to copy {source_folder} to Research Drive. Error: {str(e)}")
                return 1
            self.app.add_to_transcript(f"INFO: {source_folder} copied to Research Drive.")
        return 0

    def run(self):
        self.task_type = "PUSH_DATA_TO_RESEARCH_DRIVE"

        if self.map_network_drive() != 0:
            return 1
        
        if self.upload_files() != 0:
            return 1

        return 0