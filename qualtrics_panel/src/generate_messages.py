# qualtrics_message_generate.py
# This script generates messages for an arbitrary number of message categories
# and user contexts using the Azure OpenAI API. Use the update_qualtrics.py script to upload the generated messages to Qualtrics.

import os
import requests
import pandas as pd
import csv

from _message_helper import get_credentials, load_message_categories, load_user_contexts, load_existing_messages, load_formality_prompts

class MessageGenerator:

    # initialization method to set up the number of messages, temperature, and output file path and call the run method
    def __init__(self):

        os.system('cls' if os.name == 'nt' else 'clear')
        print("GPT Message Generation Interface with Qualtrics Upload")

        # if end of path not in src folder, ask the user to run the script from the src folder
        if not os.getcwd().endswith('src'):
            print("Please run this script from the 'src' folder.")
            exit(1)

        # decide which tones to generate messages for
        self.tones_to_generate = []
        tones, descriptions = load_message_categories()
        self.category_to_description = dict(zip(tones, descriptions))
        print("\nAvailable message categories:")
        for i, tone in enumerate(tones):
            print(f"{i + 1}: {tone}")
        selected_tones = input("Enter the numbers of the message categories you want to generate messages for, separated by commas (default is all): ")
        if selected_tones.strip() == '':
            self.tones_to_generate = tones
        else:
            selected_indices = [int(x.strip()) - 1 for x in selected_tones.split(',') if x.strip().isdigit()]
            self.tones_to_generate = [tones[i] for i in selected_indices if 0 <= i < len(tones)]
            if not self.tones_to_generate:
                print("No valid message categories selected. Exiting...")
                exit(1)

        # decide which user contexts to generate messages for
        self.users_to_generate = []
        user_contexts_df = load_user_contexts()
        if user_contexts_df.empty:
            print("No user contexts available. Please ensure the user_contexts.csv file is populated.")
            exit(1)
        print("\nAvailable user contexts:")
        for user_index, user_row in user_contexts_df.iterrows():
            user_context = {k: str(v).strip() for k, v in user_row.items()}
            print(f"{user_index + 1}: {user_context.get('lapse_risk', 'N/A')} - {user_context.get('lapse_risk_change', 'N/A')}")
        selected_users = input("Enter the numbers of the user contexts you want to generate messages for, separated by commas (default is all): ")
        if selected_users.strip() == '':
            self.users_to_generate = list(user_contexts_df.index)
        else:
            selected_indices = [int(x.strip()) - 1 for x in selected_users.split(',') if x.strip().isdigit()]
            self.users_to_generate = [i for i in selected_indices if 0 <= i < len(user_contexts_df)]
            if not self.users_to_generate:
                print("No valid user contexts selected. Exiting...")
                exit(1)

        # decide which formality levels to generate messages for
        self.formality_labels, self.formality_prompts = load_formality_prompts()
        print("\nAvailable formality levels:")
        for i, label in enumerate(self.formality_labels):
            print(f"{i + 1}: {label}")
        self.formalities_to_generate = []
        selected_formalities = input("Enter the numbers of the formality levels you want to generate messages for, separated by commas (default is all): ")
        if selected_formalities.strip() == '':
            self.formalities_to_generate = self.formality_labels
        else:
            selected_indices = [int(x.strip()) - 1 for x in selected_formalities.split(',') if x.strip().isdigit()]
            self.formalities_to_generate = [self.formality_labels[i] for i in selected_indices if 0 <= i < len(self.formality_labels)]
            if not self.formalities_to_generate:
                print("No valid formality levels selected. Exiting...")
                exit(1)
        self.formality_to_prompt = dict(zip(self.formality_labels, self.formality_prompts))

        # number of messages to generate
        num_messages = input("Enter the number of messages to generate for each category per user context (default is 1): ")
        num_messages = int(num_messages) if num_messages.isdigit() else 1
        if num_messages < 1:
            print("Number of messages must be at least 1. Setting to default value of 1.")
            num_messages = 1
        elif num_messages > 10:
            print("Number of messages is too high. Setting to maximum of 10.")
            num_messages = 10
        self.num_messages = num_messages
        
        # temperature for message generation, basically a creativity parameter
        temperature = input("Enter the temperature for message generation (default is 0, maximum is 1): ")
        temperature = float(temperature) if temperature else 0.0
        if temperature < 0:
            print("Temperature must be at least 0. Setting to default value of 0.")
            temperature = 0.0
        elif temperature > 1:
            print("Temperature is too high. Setting to maximum of 1.")
            temperature = 1.0
        self.temperature = temperature
        
        # output file path choice
        output_file_choice = input("Which output path would you like? 1 for default 2 for production (what is uploaded to qualtrics): ")
        if output_file_choice == '1' or output_file_choice == '':
            output_file = "../output/all_generated_messages.csv"
        elif output_file_choice == '2':
            output_file = "../output/production_messages.csv"
        else:
            print("Invalid choice, using default output path.")
            output_file = "../output/all_generated_messages.csv"
        self.output_file = output_file

        # printing options
        print_to_terminal = input("Would you like to print the generated messages to the terminal? (ENTER for yes, n for no): ")
        if print_to_terminal.lower() == '':
            self.print_to_terminal = True
        elif print_to_terminal.lower() == 'n':
            self.print_to_terminal = False
        else:
            print("Invalid choice, defaulting to printing messages to terminal.")
            self.print_to_terminal = True
        print_prompt = input("Would you like to print the system and user prompts to the terminal? (ENTER for yes, n for no): ")
        if print_prompt.lower() == '':
            self.print_prompt = True
        elif print_prompt.lower() == 'n':
            self.print_prompt = False
        else:
            print("Invalid choice, defaulting to printing prompts to terminal.")
            self.print_prompt = True

        # adding in additional information to the user prompt
        additional_info = input("Add any additional information here (hit ENTER to skip): ")
        if additional_info.strip() == '':
            self.additional_info = None
        else:
            self.additional_info = f"{additional_info.strip()}"

        # run the message generation process
        self.run()

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
            f"{self.additional_info if self.additional_info else ''}\n"
        )
        if self.print_prompt:
            print(f"User prompt:\n{user_prompt}")
        return user_prompt
    
    def azure_api_call(self, user_prompt):
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
            exit(1)
        except Exception as e:
            print(f"Unexpected error during API call: {e}\nPlease check your input and try again.")
            exit(1)
    
    # generate messages based on the prompt and system message
    def generate_messages(self, user_prompt):
        outputs = []
        for i in range(self.num_messages):
            try:
                response = self.azure_api_call(user_prompt)
                if response and 'choices' in response and len(response['choices']) > 0:
                    content = response['choices'][0]['message']['content']
                    content = content.replace('\n', ' ').strip()
                    if self.print_to_terminal:
                        print(f"{content}\n")
                    outputs.append(content)
                else:
                    outputs.append(f"Error: No response received (request {i + 1})")
            except Exception as e:
                outputs.append(f"Error: {e}")
        return outputs
    
    def save_messages(self, all_output_rows):
        all_output_flat = pd.DataFrame(all_output_rows)
        current_messages = load_existing_messages(self.output_file)

        # If the output file already exists, ask if the user would like to append to it or overwrite it
        if not current_messages.empty:
            choice = input("Output file already exists. Do you want to append to it (y) or overwrite it (n)?: ")
            if choice.lower() == 'y':
                all_output_flat = pd.concat([current_messages, all_output_flat], ignore_index=True)
            else:
                print("Not appending to existing file. Overwriting with new messages.")
        
        # Save the generated messages to the output file
        all_output_flat.to_csv(self.output_file, index = False, quoting = csv.QUOTE_ALL)
        print(f"Generated messages saved to {self.output_file}")
    
    # main method to run the message generation process
    def run(self):

        os.system('cls' if os.name == 'nt' else 'clear')
        print("Starting message generation process...")

        # Load API credentials, message categories, and user contexts
        self.api_key, self.endpoint = get_credentials()
        user_contexts_df = load_user_contexts()

        # Generate messages for each category and user context
        all_output_rows = []
        self.create_system_prompt()

        # for each formality level...
        for formality in self.formalities_to_generate:
            print("\n" + "=" * 50)
            print(f"FORMALITY LEVEL: {formality.upper()}")
            print("=" * 50 + "\n")
            print(f"Generating messages for formality level: {formality}")
            formality_prompt = self.formality_to_prompt[formality]
            if formality == "neutral":
                formality_prompt = None

            # for each message category...
            for message_category in self.tones_to_generate:
                print("\n" + "-" * 50)
                print(f"MESSAGE CATEGORY: {message_category.upper()}")
                print("-" * 50 + "\n")
                print(f"Generating messages for category: {message_category}")
                message_description = self.category_to_description[message_category]
                
                # for each user...
                for user_index, user_row in user_contexts_df.iterrows():
                    if user_index not in self.users_to_generate:
                        continue

                    # create user prompt based on the user context and message category
                    user_context = {k: str(v).strip() for k, v in user_row.items()}
                    user_prompt = self.create_user_prompt(message_category, message_description, user_context, formality_prompt)

                    # Generate messages using the Azure API and store them in the output list
                    messages = self.generate_messages(user_prompt)
                    print(f"Generated messages for user {user_index + 1} in category {message_category}")
                    for msg in messages:
                        all_output_rows.append({
                            'user_index': user_index + 1,
                            'lapse_risk': user_context.get('lapse_risk', ''),
                            'lapse_risk_change': user_context.get('lapse_risk_change', ''),
                            'temperature': self.temperature,
                            'formality': formality,
                            'message_category': message_category,
                            'generated_message': msg,
                        })

        self.save_messages(all_output_rows)

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