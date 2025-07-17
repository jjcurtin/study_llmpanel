import subprocess, os
from system_tasks._system_task import SystemTask

class RunRScript(SystemTask):
    def __init__(self, app, r_script_path):
        super().__init__(app)
        self.r_script_path = r_script_path

    def change_directory(self, new_dir):
        try:
            os.chdir(new_dir)
            self.app.add_to_transcript(f"Changed working directory to {os.getcwd()}", "INFO")
        except Exception as e:
            self.app.add_to_transcript(f"Failed to change directory to {new_dir}. Error message: {e}", "ERROR")
            raise Exception(f"Failed to change directory to {new_dir}. Error message: {e}")

    def run(self):
        self.task_type = f"RUN_RSCRIPT ({self.r_script_path})"
        self.app.add_to_transcript(f"{self.task_type} #{self.task_number} initiated.")
        initial_dir = os.getcwd()
        scripts_dir = os.path.abspath(os.path.join(initial_dir, '..', 'scripts'))
        if not os.path.exists(scripts_dir):
            self.app.add_to_transcript(f"Scripts directory {scripts_dir} does not exist. Please check the path.", "ERROR")
            return 1
        self.change_directory(scripts_dir)
        if not os.path.exists(self.r_script_path):
            self.app.add_to_transcript(f"R script {self.r_script_path} does not exist in {scripts_dir}. Please check the path.", "ERROR")
            self.change_directory(initial_dir)
            return 1
        try:
            result = subprocess.run(['Rscript', self.r_script_path], capture_output=True, text=True)
            if result.returncode != 0:
                self.app.add_to_transcript(f"R script failed to run {self.r_script_path}. Error message: {result.stderr.strip()}", "ERROR")
                self.change_directory(initial_dir)
                return 1
            self.app.add_to_transcript(f"{self.task_type} #{self.task_number} script run complete. Output: {result.stdout.strip()}", "SUCCESS")
            self.change_directory(initial_dir)
            return 0
        except Exception as e:
            self.app.add_to_transcript(f"ERROR: {self.task_type} #{self.task_number} failed to properly run script. Error message: {e}", "ERROR")
            self.change_directory(initial_dir)
            return 1