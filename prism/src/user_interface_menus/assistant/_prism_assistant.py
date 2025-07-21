import requests
import os
import pandas as pd

def make_assistant_call(user_prompt, menu_options = None, api_key = None, endpoint = None):
    try:
        system_prompt = ""
        with open(os.path.join(os.path.dirname(__file__), 'system_prompt.txt'), 'r') as file:
            system_prompt = file.read().strip()

        for menu_option in menu_options.values():
            system_prompt += f"\n{menu_option['description']}"
            
        messages = []
        messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": user_prompt})

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "optimize-v2",
            "messages": messages,
            "max_tokens": 600,
            "temperature": 0.7
        }
        response = requests.post(endpoint, headers = headers, json = payload)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"Error making API call: {e}\nPlease check your API key and endpoint.")
    except Exception as e:
        print(f"Unexpected error during API call: {e}\nPlease check your input and try again.")

@staticmethod
def get_credentials():
    try:
        if os.path.exists('../api/azure.api'):
            api = pd.read_csv('../api/azure.api')
            api_key = api.loc[0, 'key']
            endpoint = api.loc[0, 'endpoint']
        else:
            api_key = input('API key: ')
            endpoint = input('Endpoint: ')
            pd.DataFrame({'key': [api_key], 'endpoint': [endpoint]}).to_csv('../api/azure.api', index=False)
            print('Credentials saved to api/azure.api')
        return api_key, endpoint
    except Exception as e:
        print(f"Error reading API credentials: {e}\nPlease ensure the file is formatted correctly if it exists.\nOtherwise, please delete the file and re-run the script to enter credentials manually.")
        exit(1)