import subprocess
import os
import pandas as pd

from system_tasks._system_task import SystemTask

class RunRScriptPipeline(SystemTask):
    def change_directory(self, new_dir):
        try:
            os.chdir(new_dir)
            self.app.add_to_transcript(f"Changed working directory to {os.getcwd()}", "INFO")
        except Exception as e:
            self.app.add_to_transcript(f"Failed to change directory to {new_dir}. Error message: {e}", "ERROR")
            raise Exception(f"Failed to change directory to {new_dir}. Error message: {e}")

    def run(self):
        self.task_type = "RUN_RSCRIPT_PIPELINE"
        self.app.add_to_transcript(f"{self.task_type} #{self.task_number} initiated.")
        initial_dir = os.getcwd()
        scripts_dir = os.path.abspath(os.path.join(initial_dir, '..', 'scripts'))
        if not os.path.exists(scripts_dir):
            self.app.add_to_transcript(f"Scripts directory {scripts_dir} does not exist. Please check the path.", "ERROR")
            return 1
        try:
            if os.path.exists('../config/script_pipeline.csv'):
                script_df = pd.read_csv('../config/script_pipeline.csv')
                self.script_paths = script_df['script_path'].tolist()
                self.args = [args.split() for args in script_df['arguments'].tolist()]
                self.enabled_scripts = []
                self.enabled_scripts = [enabled for enabled in script_df['enabled'].tolist()]
            else:
                self.app.add_to_transcript("script_pipeline.csv not found in ../config. Please create this file with the required format.", "ERROR")
                return 1
        except Exception as e:
            self.app.add_to_transcript(f"Failed to load script pipeline configuration. Error message: {e}", "ERROR")
            return 1
        try:
            for index, script_path in enumerate(self.script_paths):
                scripts_run = 0
                if self.enabled_scripts[index]:
                    self.app.add_to_transcript(f"{self.task_type} #{self.task_number} now attempting to run {script_path} with arguments {self.args[index]}...", "INFO")
                    self.change_directory(scripts_dir)
                    command = ['Rscript', script_path] + self.args[index]
                    try:
                        result = subprocess.run(command, capture_output = True, text = True)
                        if result.returncode != 0:
                            self.app.add_to_transcript(f"Rscript failed to run {script_path}. Error message: {result.stderr.strip()}", "ERROR")
                            raise Exception(result.stderr.split('\n')[0])
                    except Exception as e:
                        self.app.add_to_transcript(f"ERROR: {self.task_type} #{self.task_number} failed to properly run script. Error message: {e}", "ERROR")
                        self.change_directory(initial_dir)
                        return 1
                    self.app.add_to_transcript(f"{self.task_type} #{self.task_number} script run complete. Output: {result.stdout.strip()}", "SUCCESS")
                    self.change_directory(initial_dir)
                    scripts_run += 1
            if scripts_run == 0:
                self.app.add_to_transcript(f"No scripts were run. Please check the script_pipeline.csv file to ensure at least one script is enabled.", "WARNING")
                return 1
        except Exception as e:
            self.app.add_to_transcript(f"An unexpected error occurred while running the script pipeline. Error message: {e}", "ERROR")
            self.change_directory(initial_dir)
            return 1
        return 0