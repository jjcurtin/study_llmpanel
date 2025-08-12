# menu for the prism assistant

from user_interface_menus._menu_helper import *
from user_interface_menus.assistant._prism_assistant import make_assistant_call, get_credentials

def assistant_menu(self):
    self.assistant_active = True
    first_loop = True
    context = []
    while True:
        choice = ''
        if first_loop:
            api_key, endpoint = get_credentials()
            from user_interface_menus.utils._commands import init_commands
            menu_options = init_commands()
        choice = print_assistant_terminal_prompt(self)
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
                        response = ""
                        for line in content.split('\n'):
                            if line.strip():
                                response += f"{line.strip()}\n"
                        header = True
                        if header:
                            assistant_header_write(self, [response])
                        else:
                            assistant_write(self, [response], self.window_0_x, self.window_0_y, self.column_width, self.window_height)
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