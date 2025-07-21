from user_interface_menus._menu_helper import *
from user_interface_menus.assistant._prism_assistant import make_assistant_call, get_credentials

def assistant_menu(self):
    first_loop = True
    while True:
        choice = ''
        if first_loop:
            api_key, endpoint = get_credentials()
            print_menu_header("PRISM Assistant")
            print("Welcome to the PRISM Assistant. Type 'stop' to return to the main menu.")
            print("You can ask questions here that will be answered with GPT 4o with knowledge of PRISM.")
            print("Keep in mind that this feature is experimental and may not always provide accurate answers.")
            print("This assistant only has access to the documentation, not data or the system itself.")

            from user_interface_menus._commands import init_commands
            menu_options = init_commands()
        while not choice.strip():
            choice = print_fixed_terminal_prompt()
        if choice.lower() == 'stop':
            return
        else:
            try:
                response = make_assistant_call(choice, menu_options = menu_options, api_key = api_key, endpoint = endpoint)
                if response and 'choices' in response and len(response['choices']) > 0:
                    global WINDOW_WIDTH
                    if 'content' in response['choices'][0]['message']:
                        content = response['choices'][0]['message']['content'].replace('**', '')
                        print(f"\n{content:>{WINDOW_WIDTH - 2}}")
                    else:
                        print("No content in response.")
                else:
                    print("No valid response received from the assistant.")
                    exit_menu()
                    return
            except Exception as e:
                print(f"An error occurred: {e}")
                exit_menu()
                return
            
        if first_loop:
            first_loop = False