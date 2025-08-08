# qualtrics_message_generate.py
# This script uses the Azure OpenAI API to generate messages based on user contexts, message categories, and formality levels.
# Tunable parameters include # of messages and temperature.

import os
import requests
import pandas as pd
import csv

# these functions are defined in separate files for modularity and help break up the code
from _message_helper import get_credentials, load_existing_messages
from _config_menu import select_message_categories, select_user_contexts, select_formality_levels
from _config_menu import select_num_messages, select_temperature, select_output_file
from _config_menu import set_printing_options, set_additional_info, set_recent_feedback_mode, clear

# main class that is instantiated at run time (near the end of the script)
class MessageGenerator:

    # initialization method to set up all of the script parameters and then call the message generation process
    def __init__(self):

        self.test_mode = False  # Set to True to enable test mode with mock responses to save API costs

        try:
            clear()
            print("GPT Message Generation Interface with Qualtrics Upload")

            self.em_dashes = 0

            # if end of path not in src folder, ask the user to run the script from the src folder
            if not os.getcwd().endswith('src'):
                print("Please run this script from the 'src' folder.")
                exit(1)

            # initialize all parameters and configuration variables
            self.initialize_settings()            

            # print current settings
            clear()
            print("Current settings:\n")
            print(f"Message categories: {', '.join(self.tones_to_generate)}")
            print(f"User contexts: {', '.join([str(i + 1) for i in self.users_to_generate]) if not self.example_condition else 'Example Condition; No User Context'}")
            print(f"Formality levels: {', '.join(self.formalities_to_generate)}")
            print(f"Number of messages per category per user context: {self.num_messages}")
            print(f"Temperature values: {', '.join([str(t) for t in self.temperature_values])}")
            print(f"Output file: {self.output_file}")
            print(f"Print generated messages to terminal: {self.print_to_terminal}")
            print(f"Print prompts to terminal: {self.print_prompt}")
            print(f"Additional information: {self.additional_info if self.additional_info else 'None'}")
            print(f"Recent message feedback mode: {'Enabled' if self.recent_mode else 'Disabled'}")

            # calculate total number of messages to be generated
            self.total_messages_to_generate = (
                len(self.tones_to_generate) *
                len(self.users_to_generate) *
                len(self.formalities_to_generate) *
                self.num_messages *
                len(self.temperature_values)
            )
            print(f"\nTotal number of messages to be generated: {self.total_messages_to_generate}")

            input("\nPress ENTER to start generating messages, Ctrl-C to stop: ")
            self.run()
        except KeyboardInterrupt:
            # quick stop/restart; during setup you can press Ctrl-C and exit or restart; this is in case of entry mistakes 
            try:
                choice = input("\nProcess interrupted by user. ENTER to restart, Ctrl+C again to exit.")
                if choice == '':
                    self.__init__()
                exit(0)
            except KeyboardInterrupt:
                exit(0)
        except Exception as e:
            print(f"Unexpected error during initialization: {e}\nPlease check your input and try again.")
            exit(1)

    def initialize_settings(self):
        # Load API credentials, message categories, and user contexts
        model = input("Which model would you like to use? 4 for GPT-4o or 5 for GPT-5mini? (default: 4o): ")
        if model not in ['4', '5']:
            model = '4'
        print(f"Using model: {model}")
        self.api_key, self.endpoint = get_credentials(model = model)

        # decide which tones to generate messages for
        self.tones_to_generate, self.category_to_description = select_message_categories()

        # decide which user contexts to generate messages for
        self.users_to_generate, self.user_contexts_df, self.example_condition = select_user_contexts()

        # decide which formality levels to generate messages for
        self.formalities_to_generate, self.formality_to_prompt = select_formality_levels()

        # number of messages to generate
        self.num_messages = select_num_messages()
        
        # temperature for message generation, basically a creativity parameter
        self.temperature_values = select_temperature()
        
        # output file path choice
        self.output_file, self.write_mode = select_output_file()

        # printing options
        self.print_to_terminal, self.print_prompt = set_printing_options()

        # adding in additional information to the user prompt
        self.additional_info = set_additional_info()

        # recent message feedback mode: best method of reducing repetition
        self.recent_mode = set_recent_feedback_mode()

    # load system prompt components from files and construct the system prompt
    def create_system_prompt(self):
        try:
            with open('../input/system_prompt/1_role.txt', 'r', encoding='utf-8') as f:
                system_role = f.read()
            with open('../input/system_prompt/2_purpose.txt', 'r', encoding='utf-8') as f:
                message_purpose = f.read()
            with open('../input/system_prompt/3_format.txt', 'r', encoding='utf-8') as f:
                message_format = f.read()
            with open('../input/system_prompt/4_restrictions.txt', 'r', encoding='utf-8') as f:
                message_restrictions = f.read()
            self.system_prompt = (
                f"{system_role}\n"
                f"{message_purpose}\n"
                f"{message_format}\n"
                f"{message_restrictions}\n"
            )
            if self.print_prompt:
                print("\n" + "=" * 50)
                print("SYSTEM PROMPT")
                print("=" * 50 + "\n")
                print(f"{self.system_prompt}")
        except Exception as e:
            print(f"Error loading system prompt files: {e}\nPlease ensure the files exist and are formatted correctly.")
            exit(1)

    # create the user prompt based on the message category and user context
    def create_user_prompt(self, message_category, message_description, user_context, formality_prompt = None):
        if not self.example_condition:
            user_context_str = f"This user has a lapse risk that is {user_context.get('lapse_risk', 'N/A')} and {user_context.get('lapse_risk_change', 'N/A')}."
        else:
            user_context_str = None
        
        try:
            with open('../input/user_prompt/1_request.txt', 'r', encoding='utf-8') as f:
                user_request = f.read()
            with open('../input/user_prompt/2a_lapse_instruction.txt', 'r', encoding='utf-8') as f:
                lapse_instruction = f.read()
            with open('../input/user_prompt/3_closing_remark.txt', 'r', encoding='utf-8') as f:
                closing_remark = f.read()
        except Exception as e:
            print(f"Error loading user prompt files: {e}\nPlease ensure the files exist and are formatted correctly.")
            exit(1)
        
        user_prompt = (
            f"{user_request}\n"
            f"{user_context_str + "\n" if not self.example_condition else ""}"
            f"{lapse_instruction + "\n" if not self.example_condition else ""}"
            f"Message category: {message_category}\n"
            f"Message prompt: {message_description}\n"
            f"{formality_prompt + "\n" if formality_prompt else ''}"
            f"{self.additional_info + "\n" if self.additional_info else ''}"
            f"{closing_remark}\n"
        )
        if self.print_prompt:
            print("User Prompt")
            print("-" * 50)
            print(f"{user_prompt}")
        return user_prompt
    
    # this function makes the actual API call to Azure OpenAI
    def azure_api_call(self, user_prompt):

        # return a mock response in test mode to save API costs
        if self.test_mode:
            return {
                "choices": [
                    {
                        "message": {
                            "content": f"Test message"
                        }
                    }
                ]
            }

        # otherwise make the API call
        try:
            if not hasattr(self, 'system_prompt'):
                self.create_system_prompt()

            messages = []
            messages.append({"role": "system", "content": self.system_prompt})
            messages.append({"role": "user", "content": user_prompt})

            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            payload = {
                "model": "optimize-v2",
                "messages": messages,
                "max_tokens": 600,
                "temperature": self.temperature
            }
            response = requests.post(self.endpoint, headers=headers, json=payload)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Error making API call: {e}\nPlease check your API key and endpoint.")
        except Exception as e:
            print(f"Unexpected error during API call: {e}\nPlease check your input and try again.")
    
    # generate n messages based on the prompt and system message
    def generate_messages(self, user_prompt):
        outputs = []
        if self.print_to_terminal:
            recent_message = " (recent feedback mode enabled)" if self.recent_mode else ""
            print("Generated Messages" + recent_message)
            print("-" * 50)

        # make an api call for each message to be generated
        most_recent_message = None
        recent_prompt = ""

        for i in range(self.num_messages):
            try:
                if most_recent_message is not None:
                    recent_prompt = f"\nThe most recent message generated was: {most_recent_message}\nPlease avoid being repetitive."
                response = self.azure_api_call(user_prompt + recent_prompt if self.recent_mode and most_recent_message else user_prompt)
                if response and 'choices' in response and len(response['choices']) > 0:
                    content = response['choices'][0]['message']['content']
                    content = content.replace('\n', ' ').strip()
                    if "—" in content:
                        self.em_dashes += 1
                    if self.print_to_terminal:
                        print(f"{content}\n")
                    outputs.append(content)
                    most_recent_message = content
                    self.messages_generated += 1
                else:
                    outputs.append(f"Error: No response received (request {i + 1})")
            except Exception as e:
                outputs.append(f"Error: {e}")
        return outputs
    
    # save the generated messages to a CSV file
    def save_messages(self):
        all_output_flat = pd.DataFrame(self.all_output_rows)
        current_messages = load_existing_messages(self.output_file)

        # If the output file already exists, ask if the user would like to append to it or overwrite it
        if not current_messages.empty:
            if self.write_mode == 'a':
                print("Appending to existing file.")
                all_output_flat = pd.concat([current_messages, all_output_flat], ignore_index=True)
            else:
                print("Overwriting existing file.")
        all_output_flat.to_csv(self.output_file, index = False, quoting = csv.QUOTE_ALL)
        print(f"\n{self.messages_generated} messages generated and saved to {self.output_file}.")
        print(f"Note: {self.em_dashes} messages out of {self.messages_generated} contained em dashes (—).")

    def launch_qualtrics_upload(self):
        # Ask the user if they want to run the Qualtrics upload script after generating messages
        choice = input("Messages generated.\nWould you like to run the Qualtrics upload script? (y/n): ")
        if choice.lower() == 'y':
            try:
                from update_qualtrics import SurveyHandler
                SurveyHandler()
            except Exception as e:
                print(f"Error running Qualtrics upload script: {e}\nPlease ensure the update_qualtrics.py script is available and properly configured.")
        else:
            print("Skipping Qualtrics upload.")
        
    # main method to run the message generation process
    # essentially a series of nested loops to generate messages for each combination of parameters
    def run(self):

        clear()
        print("Starting message generation process...")

        # Generate messages for each category and user context
        self.all_output_rows = []
        self.messages_generated = 0
        self.create_system_prompt()

        try:
            # for each temperature value...
            for temp in self.temperature_values:
                self.temperature = temp
                if self.print_to_terminal or self.print_prompt:
                    print("#" * 50)
                    print(f"TEMPERATURE: {self.temperature}")
                    print("#" * 50 + "\n")

                # for each formality level...
                for formality in self.formalities_to_generate:
                    if self.print_to_terminal or self.print_prompt:
                        print("=" * 50)
                        print(f"FORMALITY LEVEL: {formality.upper()}")
                        print("=" * 50 + "\n")
                    formality_prompt = self.formality_to_prompt[formality]
                    if formality == "neutral":
                        formality_prompt = None

                    # for each message category...
                    for message_category in self.tones_to_generate:
                        if self.print_to_terminal or self.print_prompt:
                            print("-" * 50)
                            print(f"MESSAGE CATEGORY: {message_category.upper()}")
                            print("-" * 50 + "\n")
                        message_description = self.category_to_description[message_category]
                        
                        # for each user...
                        if not self.example_condition:
                            for user_index, user_row in self.user_contexts_df.iterrows():
                                if user_index not in self.users_to_generate:
                                    continue

                                # create user prompt based on the user context and message category
                                user_context = {k: str(v).strip() for k, v in user_row.items()}
                                user_prompt = self.create_user_prompt(message_category, message_description, user_context, formality_prompt)

                                # Generate n messages using the Azure API
                                try:
                                    messages = self.generate_messages(user_prompt)
                                except Exception as e:
                                    print(f"Error generating messages for user {user_index + 1} in category {message_category}: {e}")
                                    continue
                                print(f"[Generated {self.num_messages} {formality} messages for user {user_index + 1} in category {message_category} at temperature {self.temperature}]\n")
                                for msg in messages:
                                    # add the generated message to the output list
                                    self.all_output_rows.append({
                                        'user_index': user_index + 1,
                                        'lapse_risk': user_context.get('lapse_risk', ''),
                                        'lapse_risk_change': user_context.get('lapse_risk_change', ''),
                                        'temperature': self.temperature,
                                        'formality': formality,
                                        'message_category': message_category,
                                        'generated_message': msg,
                                    })
                        else:
                            user_context = None
                            user_prompt = self.create_user_prompt(message_category, message_description, user_context, formality_prompt)

                            # Generate n messages using the Azure API for the example condition
                            try:
                                messages = self.generate_messages(user_prompt)
                            except Exception as e:
                                print(f"Error generating messages for example condition in category {message_category}: {e}")
                                continue
                            print(f"[Generated {self.num_messages} {formality} messages for example condition in category {message_category} at temperature {self.temperature}]\n")
                            for msg in messages:
                                # add the generated message to the output list
                                self.all_output_rows.append({
                                    'user_index': 'Example Condition',
                                    'lapse_risk': 'NONE',
                                    'lapse_risk_change': 'NONE',
                                    'temperature': self.temperature,
                                    'formality': formality,
                                    'message_category': message_category,
                                    'generated_message': msg,
                                })

            # save messages once complete
            print(f"Message generation process complete. {self.messages_generated} messages generated.")
            self.save_messages()

            # if the output file is the production messages file, launch the Qualtrics upload script
            if self.output_file == "../output/production_messages.csv":
                self.launch_qualtrics_upload()

        except KeyboardInterrupt:
            # quick stop during the message generation process with save option
            print("\nMessage generation process interrupted by user.")
            if self.all_output_rows:
                while True:
                    save_choice = input("Would you like to save the messages generated so far? (ENTER or y/n): ")
                    if save_choice.lower() == 'y' or save_choice == '':
                        print(f"Saving {self.messages_generated} messages to {self.output_file}...")
                        self.save_messages()
                        exit(0)
                    elif save_choice.lower() == 'n':
                        print(f"Generated messages will not be saved. {self.messages_generated} messages have been discarded.")
                        exit(0)
                    else:
                        print("Invalid choice. Please enter 'y' or 'n'.")
                        continue
            else:
                print("No messages were generated.")
        
# This is the entry point for the script, which initializes the MessageGenerator and runs the message generation process
if __name__ == "__main__":

    # generate messages using the MessageGenerator class
    message_gen = MessageGenerator()