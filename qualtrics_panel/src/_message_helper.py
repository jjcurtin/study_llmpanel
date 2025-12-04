import os
import pandas as pd

# static method to get API credentials from a file or user input
@staticmethod
def get_credentials(model = '4'):
    try:
        file_path = '../azure4o.api' if model == '4' else '../azure5_1chat.api'
        if os.path.exists(file_path):
            api = pd.read_csv(file_path)
            api_key = api.loc[0, 'key']
            endpoint = api.loc[0, 'endpoint']
        else:
            print(f"Please set up the api credentials in {file_path} file.")
            exit(1)
        return api_key, endpoint
    except Exception as e:
        print(f"Error reading API credentials: {e}\nPlease ensure the file is formatted correctly if it exists.\nOtherwise, please delete the file and re-run the script to enter credentials manually.")
        exit(1)

# static method to load message categories and prompts from a CSV file
@staticmethod
def load_message_categories(file_path='../input/user_prompt/message_categories.csv'):
    try:
        df = pd.read_csv(file_path)
        return list(df['message_category']), list(df['prompt'])
    except Exception as e:
        print(f"Error loading message categories: {e}\nPlease ensure the file exists and is formatted correctly.")
        exit(1)

# static method to load user contexts from a CSV file
@staticmethod
def load_user_contexts(file_path='../input/user_prompt/user_contexts.csv'):
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        print(f"Error loading user contexts: {e}\nPlease ensure the file exists and is formatted correctly.")
        exit(1)

@staticmethod
def load_formality_prompts(file_path='../input/user_prompt/formality_prompts.csv'):
    try:
        df = pd.read_csv(file_path)
        return list(df['label']), list(df['prompt'])
    except Exception as e:
        print(f"Error loading formality prompts: {e}\nPlease ensure the file exists and is formatted correctly.")
        exit(1)

# static method to load user messages from a CSV file
@staticmethod
def load_existing_messages(file_path='../output/all_generated_messages.csv'):
    try:
        if os.path.exists(file_path) and os.path.getsize(file_path) > 0:
            current_messages = pd.read_csv(file_path)
        else:
            current_messages = pd.DataFrame(columns = [
                'user_index', 'lapse_risk', 'lapse_risk_change',
                'message_category', 'temperature', 'formality','generated_message'
            ])
        return current_messages
    except Exception as e:
        print(f"Error loading existing messages: {e}\nPlease ensure the file exists and is formatted correctly.")
        exit(1)