import subprocess
import os
from tasks._task import Task
import pandas as pd

class RunScriptPipeline(Task):
    def change_directory(self, new_dir):
        try:
            os.chdir(new_dir)
            print(f"Changed working directory to {os.getcwd()}")
        except Exception as e:
            print(f"ERROR: Failed to change directory to {new_dir}. Error message: {e}")
            raise Exception(f"Failed to change directory to {new_dir}. Error message: {e}")

    def run(self):
        self.task_type = "RUN_SCRIPT_PIPELINE"
        
        initial_dir = os.getcwd()
        scripts_dir = os.path.abspath(os.path.join(initial_dir, '..', 'scripts'))
        if not os.path.exists(scripts_dir):
            print(f"ERROR: Scripts directory {scripts_dir} does not exist. Please check the path.")
            return 1

        # load in script paths and arguments and enabled status from ../config/script_pipeline.csv
        # paths are relative to the ../scripts directory
        # arguments are formatted like "arg1 arg2 arg3"
        # enabled will either be "true" or "false"
        try:
            if os.path.exists('../config/script_pipeline.csv'):
                script_df = pd.read_csv('../config/script_pipeline.csv')
                self.script_paths = script_df['script_path'].tolist()
                self.args = [args.split() for args in script_df['arguments'].tolist()]
                self.enabled_scripts = []
                self.enabled_scripts = [enabled for enabled in script_df['enabled'].tolist()]
            else:
                print("ERROR: script_pipeline.csv not found in ../config. Please create this file with the required format.")
                return 1
        except Exception as e:
            print(f"ERROR: Failed to load script pipeline configuration. Error message: {e}")
            return 1
        
        print(f"paths: {self.script_paths}")
        print(f"args: {self.args}")
        print(f"enabled: {self.enabled_scripts}")

        try:
            for index, script_path in enumerate(self.script_paths):
                scripts_run = 0
                if self.enabled_scripts[index]:
                    print(f"INFO: {self.task_type} #{self.task_number} now attempting to run {script_path} with arguments {self.args[index]}...")
                    self.change_directory(scripts_dir)
                    command = ['Rscript', script_path] + self.args[index]
                    try:
                        result = subprocess.run(command, capture_output = True, text = True)
                        if result.returncode != 0:
                            print(f"ERROR: Rscript failed to run {script_path}. Error message: {result.stderr.strip()}")
                            raise Exception(result.stderr.split('\n')[0])
                    except Exception as e:
                        print(f"ERROR: {self.task_type} #{self.task_number} failed to properly run script. Error message: {e}")
                        self.change_directory(initial_dir)
                        return 1
                    print(f"SUCCESS: {self.task_type} #{self.task_number} script run complete. Output: {result.stdout.strip()}")
                    self.change_directory(initial_dir)
                    scripts_run += 1
            if scripts_run == 0:
                print(f"WARNING: No scripts were run. Please check the script_pipeline.csv file to ensure at least one script is enabled.")
                return 1
        except Exception as e:
            print(f"ERROR: An unexpected error occurred while running the script pipeline. Error message: {e}")
            self.change_directory(initial_dir)
            return 1
        return 0