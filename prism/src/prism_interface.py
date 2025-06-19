import requests
import os
import time
import csv

class PRISMInterface():
    def __init__(self):
        # check to see if the PRISM instance is running on port 5000
        self.base_url = "http://localhost:5000/system"

        # send a get_uptime request to the PRISM instance using the base_url to see if it is running
        self.get_uptime()
        if self.uptime == "PRISM instance not running":
            print("PRISM instance is not running. Please start the PRISM server first.")
            exit()

        self.task_types = {
            'CHECK_SYSTEM': 'Check System',
            'PULLDOWN_DATA': 'Pull Down Data',
            'RUN_SCRIPT_PIPELINE': 'Run Script Pipeline'
        }

        self.run()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_uptime(self):
        try:
            response = requests.get(f"{self.base_url}/uptime")
            if response.status_code == 200:
                self.uptime = response.json().get("uptime", "Unknown")
            else:
                self.uptime = "Failed to retrieve uptime"
        except requests.ConnectionError:
            self.uptime = "PRISM instance not running"
            exit()
        except Exception as e:
            self.uptime = f"Error: {str(e)}"
            exit()

    def print_main_menu(self):
        self.clear()
        print("PRISM Interface Menu:")
        print("1. Get PRISM Uptime")
        print("2. Manage System Tasks")
        print("3. Manage Participant Tasks")
        print("4. Exit")
        print()

    def print_system_task_schedule(self):
        self.clear()
        print("System Task Schedule:")
        try:
            response = requests.get(f"{self.base_url}/get_task_schedule")
            if response.status_code == 200:
                tasks = response.json().get("tasks", [])
                self.scheduled_tasks = tasks
                if tasks:
                    self.num_tasks = len(tasks)
                    task_idx = 1
                    for task in tasks:
                        print(f"{task_idx}: {task['task_type']} @ {task['task_time']} - Run Today: {task.get('run_today', False)}")
                        task_idx += 1
                else:
                    print("No tasks scheduled.")
            else:
                print("Failed to retrieve task schedule.")
        except requests.ConnectionError:
            print("PRISM instance not running.")
        except Exception as e:
            print(f"Error: {str(e)}")
        print()
        print("1. Add New Task")
        print("2. Remove Task")
        print("3. Execute Task Now")
        print("4. Back to Main Menu")
        print()

    def add_system_task(self, task_type, task_time):
        try:
            response = requests.post(f"{self.base_url}/add_system_task/{task_type}/{task_time}")
            if response.status_code == 200:
                print("Task added successfully.")
            else:
                print(f"Failed to add task: {response.json().get('error', 'Unknown error')}")
            input("Press Enter to continue...")
        except requests.ConnectionError:
            print("PRISM instance not running.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def remove_system_task(self, task_type, task_time):
        try:
            response = requests.delete(f"{self.base_url}/remove_system_task/{task_type}/{task_time}")
            if response.status_code == 200:
                print("Task removed successfully.")
            else:
                print(f"Failed to remove task: {response.json().get('error', 'Unknown error')}")
            input("Press Enter to continue...")
        except requests.ConnectionError:
            print("PRISM instance not running.")
        except Exception as e:
            print(f"Error: {str(e)}")

    def run(self):
        while True:
            self.print_main_menu()
            choice = input("Enter your choice: ")

            # get system uptime
            if choice == '1':
                self.clear()
                self.get_uptime()
                print(f"PRISM Uptime: {self.uptime}")   
                input("Press Enter to continue...")

            # task management menu
            elif choice == '2':
                while True:
                    self.print_system_task_schedule()
                    task_choice = input("Enter your choice: ")

                    # add task
                    if task_choice == '1':
                        print("Add New System Task")
                        task_type_index = input("Enter task type (1: CHECK_SYSTEM, 2: PULLDOWN_DATA, 3: RUN_SCRIPT_PIPELINE): ")
                        task_types = {
                            '1': 'CHECK_SYSTEM',
                            '2': 'PULLDOWN_DATA',
                            '3': 'RUN_SCRIPT_PIPELINE'
                        }
                        task_type = task_types.get(task_type_index)
                        if not task_type:
                            print("Invalid task type selected.")
                            input("Press Enter to continue...")
                            continue

                        task_time = input("Enter task time (HH:MM:SS in military time): ")
                        try:
                            time.strptime(task_time, '%H:%M:%S')
                        except ValueError:
                            print("Invalid time format. Please use HH:MM:SS in military time.")
                            input("Press Enter to continue...")
                            continue

                        self.add_system_task(task_type, task_time)

                    # remove task
                    elif task_choice == '2':
                        task_index = input("Enter the index of the task to remove: ")
                        try:
                            task_index = int(task_index) - 1
                            if 0 <= task_index < self.num_tasks:
                                task_type = self.scheduled_tasks[task_index]['task_type']
                                task_time = self.scheduled_tasks[task_index]['task_time']
                                self.remove_system_task(task_type, task_time)
                            else:
                                print("Invalid task index.")
                        except ValueError:
                            print("Please enter a valid number.")
                            input("Press Enter to continue...")

                    # execute task now
                    elif task_choice == '3':
                        task_index = input("Enter the index of the task to execute now (1: CHECK_SYSTEM, 2: PULLDOWN_DATA, 3: RUN_SCRIPT_PIPELINE): ")
                        try:
                            if task_index.isdigit() and 1 <= int(task_index) <= len(self.task_types):
                                if task_index == '1':
                                    task_type = 'CHECK_SYSTEM'
                                elif task_index == '2':
                                    task_type = 'PULLDOWN_DATA'
                                elif task_index == '3':
                                    task_type = 'RUN_SCRIPT_PIPELINE'
                                else:
                                    print("Invalid task index.")
                                    input("Press Enter to continue...")
                                    continue
                                response = requests.post(f"{self.base_url}/execute_task/{task_type}")
                                if response.status_code == 200:
                                    print(f"Task {task_type} executed successfully.")
                                else:
                                    print(f"Failed to execute task: {response.json().get('error', 'Unknown error')}")
                                input("Press Enter to continue...")
                            else:
                                print("Invalid task index.")
                                input("Press Enter to continue...")
                                continue
                        except Exception as e:
                            print(f"An error occurred: {str(e)}")
                            input("Press Enter to continue...")

                    # back to main menu
                    elif task_choice == '4':
                        break
                    else:
                        print("Invalid choice. Please try again.")
                        input("Press Enter to continue...")

            # manage participant tasks
            elif choice == '3':
                print("Participant task management is not implemented yet.")
                input("Press Enter to continue...")

            # exit the interface
            elif choice == '4':
                print("Exiting PRISM Interface.")
                break
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")

if __name__ == "__main__":
    PRISMInterface()