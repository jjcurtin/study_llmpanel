# prism assistant logic which calls 4o through azure api

import requests
import os
import pandas as pd

from user_interface_menus._menu_helper import error

def make_assistant_call(user_prompt, menu_options = None, api_key = None, endpoint = None, context = None):
    try:
        from user_interface_menus._menu_helper import ASSISTANT_TEMPERATURE, ASSISTANT_TOKENS, COLOR_ON
        system_prompt = ""
        with open('../config/system_prompt.txt', 'r') as file:
            system_prompt = file.read().strip()

        system_prompt += "List of available commands:\n"
        for key, menu_option in menu_options.items():
            system_prompt += f"\n{key}: {menu_option['description']}"

        from user_interface_menus.help._help_menu import read_me_lines
        if read_me_lines:
            system_prompt += "\n\nReadme lines:\n"
            for line in read_me_lines:
                system_prompt += f"- {line}\n"

        from user_interface_menus._menu_helper import RECENT_COMMANDS
        if RECENT_COMMANDS and len(RECENT_COMMANDS) > 0:
            system_prompt += "\nThe user has most recently used the following commands:\n"
            for command in RECENT_COMMANDS:
                system_prompt += f"- {command}\n"

        for prev_message in context:
            system_prompt += f"\nThe user has previously asked about {prev_message}"

        if COLOR_ON:
            y, g, r, stop = "\\033[33m", "\\033[32m", "\\033[31m", "\\033[0m"
        else:
            y, g, r, stop = "\\033[4m", "\\033[1m", "\\033[1m", "\\033[0m"

        system_prompt += f'\nWhen using colors include the "{stop}" escape character after the thing you are putting in color. \
                            Do not wrap the color codes in quotes.'
        system_prompt += f'\nWhen referencing files or folders, use the "{g}" escape character before the name of the file or folder. \
                            Do not wrap the file or folder name in quotes.'
        system_prompt += f'\nWhen referencing commands or macros, use the "{y}" escape character before the name of the command or \
                            macro or / or command search instructions. Do not wrap the command in quotes.'
        system_prompt += f'\nWhen referencing the prism assistant, use the "{r}" escape character before the word "assistant". \
                            Do not wrap the word in quotes.'
            
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
            "max_tokens": ASSISTANT_TOKENS,
            "temperature": ASSISTANT_TEMPERATURE
        }
        from user_interface_menus._menu_helper import TIMEOUT
        response = requests.post(endpoint, headers = headers, json = payload, timeout = TIMEOUT)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        #error(f"Error making assistant call: {e}", None)
        pass

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