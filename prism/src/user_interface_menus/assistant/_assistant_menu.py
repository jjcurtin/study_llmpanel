from user_interface_menus._menu_helper import *
from user_interface_menus.assistant._prism_assistant import make_assistant_call, get_credentials

def assistant_menu(self):
    first_loop = True
    context = []
    while True:
        choice = ''
        if first_loop:
            api_key, endpoint = get_credentials()
            print()
            print_dashes()
            global ASSISTANT_TEMPERATURE
            print(f"Press ENTER to exit assistant. This is an experimental feature and not all information may be accurate. Temperature: {ASSISTANT_TEMPERATURE}")
            print_dashes()

            from user_interface_menus._commands import init_commands
            menu_options = init_commands()
        choice = print_assistant_terminal_prompt()
        if not choice.strip():
            return
        else:
            try:
                response = make_assistant_call(choice, 
                                               menu_options = menu_options, 
                                               api_key = api_key, 
                                               endpoint = endpoint,
                                               context = context)
                if response and 'choices' in response and len(response['choices']) > 0:
                    global WINDOW_WIDTH
                    if 'content' in response['choices'][0]['message']:
                        content = response['choices'][0]['message']['content'].replace('**', '')
                        print()
                        print_dashes()
                        for line in content.split('\n'):
                            if line.strip():
                                print(f"{line:<{WINDOW_WIDTH - 2}}")                                     
                        print_dashes()
                        context.append(content)
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