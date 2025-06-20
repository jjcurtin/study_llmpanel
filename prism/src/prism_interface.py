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

        self.run()

    def clear(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def get_uptime(self):
        try:
            response = requests.get(f"{self.base_url}/uptime")
            if response.status_code == 200:
                self.uptime = response.json().get("uptime", "Unknown")
            else:
                print("Failed to retrieve uptime")
                exit()
        except requests.ConnectionError:
            print("PRISM instance not running")
            exit()
        except Exception as e:
            print(f"Error: {str(e)}")
            exit()

    def print_main_menu(self):
        self.clear()
        print("PRISM Interface Menu:")
        print("1. Get PRISM Uptime")
        print("2. Manage System Tasks")
        print("3. Manage Participants")
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

    def print_participant_list(self):
        while True:
            self.clear()
            print("Participant List:")
            try:
                response = requests.get(f"{self.base_url}/get_participants")
                if response.status_code == 200:
                    participants = response.json().get("participants", [])
                    if participants:
                        for idx, participant in enumerate(participants, start=1):
                            print(f"{idx}: {participant['last_name']}, {participant['first_name']} (ID: {participant['unique_id']}) - On Study: {participant['on_study']}")
                    else:
                        print("No participants found.")
                else:
                    print("Failed to retrieve participant list.")
            except requests.ConnectionError:
                print("PRISM instance not running.")
            except Exception as e:
                print(f"Error: {str(e)}")
            print()
            participant_choice = input("Enter the index of the participant to view their information or hit 'a' to add a participant or hit ENTER to return: ")
            if participant_choice.isdigit():
                #  map participant choice to participant ID
                participant_choice = int(participant_choice) - 1
                self.print_participant_schedule(participants[participant_choice]['unique_id'])
            elif participant_choice == '':
                break
            elif participant_choice.lower() == 'a':
                self.add_participant()
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")


    def print_participant_schedule(self, participant_id):
        try:
            response = requests.get(f"{self.base_url}/get_participant/{participant_id}")
            if response.status_code == 200:
                participant = response.json().get("participant", [])
                if participant:
                    while True:
                        self.clear()
                        print(f"Information for Participant ID {participant_id}:")
                        print(f"1: First Name: {participant['first_name']}")
                        print(f"2: Last Name: {participant['last_name']}")
                        print(f"3: Unique ID: {participant['unique_id']}")
                        print(f"4: On Study: {participant['on_study']}")
                        print(f"5: Phone Number: {participant['phone_number']}")
                        print(f"6: EMA Time: {participant['ema_time']}")
                        print(f"7: EMA Reminder Time: {participant['ema_reminder_time']}")
                        print(f"8: Feedback Time: {participant['feedback_time']}")
                        print(f"9: Feedback Reminder Time: {participant['feedback_reminder_time']}")

                        edit_choice = input("ENTER to return to the participant list. Input 1-9 to edit a field or 'r' to remove participant. ")
                        if edit_choice == '':
                            break
                        elif edit_choice in ['1', '2', '3', '4', '5', '6', '7', '8', '9']:
                            field_map = {
                                '1': 'first_name',
                                '2': 'last_name',
                                '3': 'unique_id',
                                '4': 'on_study',
                                '5': 'phone_number',
                                '6': 'ema_time',
                                '7': 'ema_reminder_time',
                                '8': 'feedback_time',
                                '9': 'feedback_reminder_time'
                            }
                            field = field_map[edit_choice]
                            new_value = input(f"Enter new value for {field}: ")
                            response = requests.put(f"{self.base_url}/update_participant/{participant_id}/{field}/{new_value}")
                            participant[field] = new_value  # Update local participant data
                            if response.status_code == 200:
                                print("Participant updated successfully.")
                            else:
                                print(f"Failed to update participant: {response.json().get('error', 'Unknown error')}")
                        elif edit_choice.lower() == 'r':
                            confirm = input("Are you sure you want to remove this participant? (yes/no): ").strip().lower()
                            if confirm == 'yes':
                                response = requests.delete(f"{self.base_url}/remove_participant/{participant_id}")
                                if response.status_code == 200:
                                    print("Participant removed successfully.")
                                    break

            else:
                print("Failed to retrieve participant schedule.")
        except requests.ConnectionError:
            print("PRISM instance not running.")
        except Exception as e:
            print(f"Error: {str(e)}")
        print()

    def add_participant(self):
        try:
            self.clear()
            print("Add New Participant")
            first_name = input("Enter first name: ")
            last_name = input("Enter last name: ")
            unique_id = input("Enter unique ID: ")
            on_study = input("Is the participant on study? (yes/no): ").strip().lower()
            if on_study not in ['yes', 'no']:
                print("Invalid input for on study. Please enter 'yes' or 'no'.")
                input("Press Enter to continue...")
                return
            on_study = True if on_study == 'yes' else False
            phone_number = input("Enter phone number: ")
            ema_time = input("Enter EMA time (HH:MM:SS in military time): ")
            ema_reminder_time = input("Enter EMA reminder time (HH:MM:SS in military time): ")
            feedback_time = input("Enter feedback time (HH:MM:SS in military time): ")
            feedback_reminder_time = input("Enter feedback reminder time (HH:MM:SS in military time): ")

            # Validate time formats
            for time_str in [ema_time, ema_reminder_time, feedback_time, feedback_reminder_time]:
                try:
                    time.strptime(time_str, '%H:%M:%S')
                except ValueError:
                    print(f"Invalid time format for {time_str}. Please use HH:MM:SS in military time.")
                    input("Press Enter to continue...")
                    return

            response = requests.post(f"{self.base_url}/add_participant", json={
                "first_name": first_name,
                "on_study": on_study,
                "last_name": last_name,
                "unique_id": unique_id,
                "phone_number": phone_number,
                "ema_time": ema_time,
                "ema_reminder_time": ema_reminder_time,
                "feedback_time": feedback_time,
                "feedback_reminder_time": feedback_reminder_time
            })

            if response.status_code == 200:
                print("Participant added successfully.")
            else:
                print(f"Failed to add participant: {response.json().get('error', 'Unknown error')}")
        except requests.ConnectionError:
            print("PRISM instance not running.")
        except Exception as e:
            print(f"Error: {str(e)}")
        input("Press Enter to continue...")

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
    
    def get_task_types(self):
        try:
            response = requests.get(f"{self.base_url}/get_task_types")
            if response.status_code == 200:
                self.task_types = response.json().get("task_types", {})
                return self.task_types
            else:
                print("Failed to retrieve task types.")
                return {}
        except requests.ConnectionError:
            print("PRISM instance not running.")
            return {}
        except Exception as e:
            print(f"Error: {str(e)}")
            return {}

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
                        self.get_task_types()
                        print("Available Tasks:")
                        for index, (task_key, task_name) in enumerate(self.task_types.items(), start=1):
                            print(f"{index}: {task_name} ({task_key})")
                        task_index = input("Enter the index of the task to add: ")
                        task_type = None
                        try:
                            if task_index.isdigit() and 1 <= int(task_index) <= len(self.task_types):
                                task_index = int(task_index) - 1
                                task_type = list(self.task_types.keys())[task_index]
                            else:
                                print("Invalid task index.")
                                input("Press Enter to continue...")
                                continue
                        except ValueError:
                            print("Please enter a valid number.")
                            input("Press Enter to continue...")
                            continue
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
                        # get task types
                        self.get_task_types()
                        print("Execute Task Now")
                        print("Available Tasks:")
                        for index, (task_key, task_name) in enumerate(self.task_types.items(), start=1):
                            print(f"{index}: {task_name} ({task_key})")
                        task_index = input("Enter the index of the task to execute: ")
                        task_type = None
                        try:
                            if task_index.isdigit() and 1 <= int(task_index) <= len(self.task_types):
                                task_index = int(task_index) - 1
                                task_type = list(self.task_types.keys())[task_index]
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
                self.print_participant_list()

            # exit the interface
            elif choice == '4':
                print("Exiting PRISM Interface.")
                break
            else:
                print("Invalid choice. Please try again.")
                input("Press Enter to continue...")

if __name__ == "__main__":
    PRISMInterface()