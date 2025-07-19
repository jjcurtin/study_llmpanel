import time
from _helper import clear

def task_schedule_menu(self):
        while True:
            clear()
            print("System Task Schedule:")
            tasks = self.api("GET", "system/get_task_schedule")
            if tasks and "tasks" in tasks:
                self.scheduled_tasks = tasks["tasks"]
                if self.scheduled_tasks:
                    for i, t in enumerate(self.scheduled_tasks, 1):
                        print(f"{i}. {t['task_type']} @ {t['task_time']}{f" {t['r_script_path']}" if t['r_script_path'] else ""} - Run Today: {t.get('run_today', False)}")
                else:
                    print("No tasks scheduled.")
            else:
                print("Failed to retrieve task schedule or PRISM not running.")
            print("\n1: Add New Task\n2: Remove Task\n3: Execute Task Now\n\nENTER: Back to Main Menu")  
            task_choice = input("Enter choice: ").strip()
            if task_choice == '1':
                task_types = self.get_task_types()
                if not task_types:
                    input("No task types available. Press Enter to continue...")
                    return
                print("Available Tasks:")
                for i, (k,v) in enumerate(task_types.items(),1):
                    print(f"{i}: {v} ({k})")
                idx = input("Task index to add: ").strip()
                if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
                    print("Invalid index.")
                    input("Press Enter to continue...")
                    return
                task_type = list(task_types.keys())[int(idx)-1]
                r_script_path = None
                
                if task_type == 'RUN_R_SCRIPT':
                    r_scripts = self.api("GET", "system/get_r_script_tasks")
                    if not r_scripts:
                        print("No R scripts available.")
                        input("Press Enter to continue...")
                        return
                    print("Available R Scripts:")
                    for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
                        print(f"{i}: {name}")
                    script_idx = input("Select R script index: ").strip()
                    r_script_dict = r_scripts['r_script_tasks']
                    script_names = list(r_script_dict.keys())

                    if not script_idx.isdigit() or not (1 <= int(script_idx) <= len(script_names)):
                        print("Invalid index.")
                        input("Press Enter to continue...")
                        return
                    selected_script_name = script_names[int(script_idx) - 1]
                    r_script_path = f"{r_script_dict[selected_script_name]}.R"

                task_time = input("Task time (HH:MM:SS): ").strip()
                try:
                    time.strptime(task_time, '%H:%M:%S')
                except ValueError:
                    print("Invalid time format.")
                    input("Press Enter to continue...")
                    return

                self.add_system_task(task_type, task_time, r_script_path)
            elif task_choice == '2':
                try:
                    idx = int(input("Task index to remove: ")) - 1
                    if 0 <= idx < len(self.scheduled_tasks):
                        t = self.scheduled_tasks[idx]
                        self.remove_system_task(t['task_type'], t['task_time'])
                    else:
                        print("Invalid index.")
                        input("Press Enter to continue...")
                except Exception:
                    print("Invalid input.")
                    input("Press Enter to continue...")
            elif task_choice == '3':
                task_types = self.get_task_types()
                if not task_types:
                    input("No task types available. Press Enter to continue...")
                    return
                print("Available Tasks:")
                for i, (k,v) in enumerate(task_types.items(),1):
                    print(f"{i}: {v} ({k})")
                idx = input("Task index to execute: ").strip()
                if not idx.isdigit() or not (1 <= int(idx) <= len(task_types)):
                    print("Invalid index.")
                    input("Press Enter to continue...")
                    return
                task_type = list(task_types.keys())[int(idx)-1]

                if task_type == 'RUN_R_SCRIPT':
                    r_scripts = self.api("GET", "system/get_r_script_tasks")
                    if not r_scripts:
                        print("No R scripts available.")
                        input("Press Enter to continue...")
                        return
                    print("Available R Scripts:")
                    for i, (name, script) in enumerate(r_scripts['r_script_tasks'].items(), 1):
                        print(f"{i}: {name}")
                    script_idx = input("Select R script index: ").strip()
                    r_script_dict = r_scripts['r_script_tasks']
                    script_names = list(r_script_dict.keys())

                    if not script_idx.isdigit() or not (1 <= int(script_idx) <= len(script_names)):
                        print("Invalid index.")
                        input("Press Enter to continue...")
                        return
                    selected_script_name = script_names[int(script_idx) - 1]
                    r_script_path = f"{r_script_dict[selected_script_name]}.R"
                    print(f"Executing R script: {selected_script_name} at {r_script_path}")
                    if self.api("POST", f"system/execute_r_script_task/{r_script_path}"):
                        print(f"R script task {selected_script_name} executed.")
                    else:
                        print(f"Failed to execute R script task {selected_script_name}.")
                elif self.api("POST", f"system/execute_task/{task_type}"):
                    print(f"Task {task_type} executed.")
                else:
                    print("Failed to execute task.")
                    data = self.api("GET", f"system/get_transcript/{15}")
                    if data and "transcript" in data:
                        for entry in data["transcript"]:
                            print(f"{entry['timestamp']} - {entry['message']}")
                    else:
                        print("No transcript found or failed to retrieve.")

                input("Press Enter to continue...")
            elif task_choice == '':
                return
            else:
                print("Invalid choice.")
                input("Press Enter to continue...")