# qualtrics_message_generate.py
# This script generates messages for an arbitrary number of message categories
# and user contexts using the Azure OpenAI API. Use the update_qualtrics.py script to upload the generated messages to Qualtrics.

import os
import requests
import pandas as pd
import csv

from _message_helper import get_credentials, load_existing_messages
from _config_menu import select_message_categories, select_user_contexts, select_formality_levels
from _config_menu import select_num_messages, select_temperature, select_output_file
from _config_menu import set_printing_options, set_additional_info, clear

class MessageGenerator:

    # initialization method to set up the number of messages, temperature, and output file path and call the run method
    def __init__(self):

        self.test_mode = True  # Set to True to enable test mode with mock responses to save API costs

        try:
            clear()
            print("GPT Message Generation Interface with Qualtrics Upload")

            self.em_dashes = 0

            # if end of path not in src folder, ask the user to run the script from the src folder
            if not os.getcwd().endswith('src'):
                print("Please run this script from the 'src' folder.")
                exit(1)

            # Load API credentials, message categories, and user contexts
            self.api_key, self.endpoint = get_credentials()

            # decide which tones to generate messages for
            self.tones_to_generate, self.category_to_description = select_message_categories()

            # decide which user contexts to generate messages for
            self.users_to_generate, self.user_contexts_df = select_user_contexts()

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

            # print current settings
            clear()
            print("Current settings:\n")
            print(f"Message categories: {', '.join(self.tones_to_generate)}")
            print(f"User contexts: {', '.join([str(i + 1) for i in self.users_to_generate])}")
            print(f"Formality levels: {', '.join(self.formalities_to_generate)}")
            print(f"Number of messages per category per user context: {self.num_messages}")
            print(f"Temperature values: {', '.join([str(t) for t in self.temperature_values])}")
            print(f"Output file: {self.output_file}")
            print(f"Print generated messages to terminal: {self.print_to_terminal}")
            print(f"Print prompts to terminal: {self.print_prompt}")
            print(f"Additional information: {self.additional_info if self.additional_info else 'None'}")
        except KeyboardInterrupt:
            try:
                choice = input("\nProcess interrupted by user. ENTER to restart, Ctrl+C again to exit.")
                if choice == '':
                    self.__init__()
                exit(0)
            except KeyboardInterrupt:
                exit(0)
        try:
            input("\nPress ENTER to start generating messages, Ctrl-C to stop.")

            # run the message generation process
            self.run()
        except Exception as e:
            print(f"Unexpected error: {e}\n")
            exit(1)

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
        user_context_str = f"This user has a lapse risk that is {user_context.get('lapse_risk', 'N/A')} and {user_context.get('lapse_risk_change', 'N/A')}."
        user_prompt = (
            "Generate a message for a user based on the following context:\n"
            f"{user_context_str}\n"
            f"Message category: {message_category}\n"
            f"Message prompt: {message_description}\n"
            "Please tailor the message to the user's situation.\n"
            f"{formality_prompt if formality_prompt else ''}\n"
            f"{self.additional_info if self.additional_info else ''}"
        )
        if self.print_prompt:
            print("User Prompt")
            print("-" * 50)
            print(f"{user_prompt}")
        return user_prompt
    
    def azure_api_call(self, user_prompt):
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
    
    # generate messages based on the prompt and system message
    def generate_messages(self, user_prompt):
        outputs = []
        if self.print_to_terminal:
            print("Generated Messages")
            print("-" * 50)
        for i in range(self.num_messages):
            try:
                response = self.azure_api_call(user_prompt)
                if response and 'choices' in response and len(response['choices']) > 0:
                    content = response['choices'][0]['message']['content']
                    content = content.replace('\n', ' ').strip()
                    if "—" in content:
                        self.em_dashes += 1
                    if self.print_to_terminal:
                        print(f"{content}\n")
                    outputs.append(content)
                else:
                    outputs.append(f"Error: No response received (request {i + 1})")
            except Exception as e:
                outputs.append(f"Error: {e}")
        return outputs
    
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
        num_messages_generated = len(self.all_output_rows)
        print(f"\n{num_messages_generated} messages generated and saved to {self.output_file}.")
        if self.test_mode:
            print(f"Note: {self.em_dashes} messages out of {num_messages_generated} contained em dashes (—).")
        
    # main method to run the message generation process
    def run(self):

        clear()
        print("Starting message generation process...")

        # Generate messages for each category and user context
        self.all_output_rows = []
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
                        for user_index, user_row in self.user_contexts_df.iterrows():
                            if user_index not in self.users_to_generate:
                                continue

                            # create user prompt based on the user context and message category
                            user_context = {k: str(v).strip() for k, v in user_row.items()}
                            user_prompt = self.create_user_prompt(message_category, message_description, user_context, formality_prompt)

                            # Generate messages using the Azure API and store them in the output list
                            try:
                                messages = self.generate_messages(user_prompt)
                            except Exception as e:
                                print(f"Error generating messages for user {user_index + 1} in category {message_category}: {e}")
                                continue
                            print(f"[Generated {self.num_messages} {formality} messages for user {user_index + 1} in category {message_category} at temperature {self.temperature}]\n")
                            for msg in messages:
                                self.all_output_rows.append({
                                    'user_index': user_index + 1,
                                    'lapse_risk': user_context.get('lapse_risk', ''),
                                    'lapse_risk_change': user_context.get('lapse_risk_change', ''),
                                    'temperature': self.temperature,
                                    'formality': formality,
                                    'message_category': message_category,
                                    'generated_message': msg,
                                })

            # save messages once complete
            print("Message generation process complete.")
            self.save_messages()
        except KeyboardInterrupt:
            print("\nMessage generation process interrupted by user.")
            if self.all_output_rows:
                while True:
                    save_choice = input("Would you like to save the messages generated so far? (y/n): ")
                    if save_choice.lower() == 'y':
                        print("Saving generated messages...")
                        self.save_messages()
                        exit(0)
                    elif save_choice.lower() == 'n':
                        print("Generated messages will not be saved.")
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

    # Ask the user if they want to run the Qualtrics upload script after generating messages
    if message_gen.output_file == "../output/production_messages.csv":
        choice = input("Messages generated.\nWould you like to run the Qualtrics upload script? (y/n): ")
        if choice.lower() == 'y':
            try:
                from update_qualtrics import SurveyHandler
                SurveyHandler()
            except Exception as e:
                print(f"Error running Qualtrics upload script: {e}\nPlease ensure the update_qualtrics.py script is available and properly configured.")
        else:
            print("Skipping Qualtrics upload.")