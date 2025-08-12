# menu for the prism assistant

import threading
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
                result_holder = {}

                def prism_assistant_call(result_holder):
                    result_holder['response'] = make_assistant_call(choice, menu_options, api_key, endpoint, context)

                response_thread = threading.Thread(target = prism_assistant_call, args = (result_holder,))
                response_thread.start()
                assistant_header_write(self, [f"Requested '{choice}' from the assistant. Please wait..."])
                response_thread.join()

                response = result_holder['response']
                if response and 'choices' in response and len(response['choices']) > 0:
                    if 'content' in response['choices'][0]['message']:
                        content = response['choices'][0]['message']['content'].replace('**', '')
                        response = ""
                        for line in content.split('\n'):
                            if line.strip():
                                response += f"{line.strip()}\n"
                        
                        header = True
                        mode = 'normal' # or 'normal'

                        if header:
                            if mode == 'shift':
                                assistant_header_shift_write(self, [response]) # shift mode is kind of choppy at the moment
                            else:
                                assistant_header_write(self, [response])
                        else:
                            assistant_write(self, [response], self.window_0_x, self.window_0_y, self.column_width, self.window_height)
                        context.append(content)
                    else:
                        assistant_header_write(self, ["No content found in the assistant's response."])
                        ansi_show_cursor()
                else:
                    assistant_header_write(self, ["No response from the assistant."])
                    ansi_show_cursor()
                    exit_menu()
                    return
            except Exception as e:
                assistant_header_write(self, [f"{red('Error')}: {e}"])
                ansi_show_cursor()
                exit_menu()
                return
            
        if first_loop:
            first_loop = False