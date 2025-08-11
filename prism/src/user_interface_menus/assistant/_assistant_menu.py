# menu for the prism assistant
import sys, time

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
            print()
            print_dashes()
            print(f"Press {yellow('ENTER')} to exit assistant. This is an experimental feature and not all information may be accurate.")
            print_dashes()

            from user_interface_menus.utils._commands import init_commands
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
                        response = ""
                        for line in content.split('\n'):
                            if line.strip():
                                response += f"{line.strip()}\n"
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

saved_positions = []

def save_cursor_pos(x, y):
    saved_positions.append((x, y))

def restore_cursor_pos(index=-1):
    x, y = saved_positions[index]
    move_cursor(x, y)

def move_cursor(x, y):
    sys.stdout.write(f"\033[{y+1};{x+1}H")
    sys.stdout.flush()

def clear_column(x, y, width, height):
    save_x, save_y = get_cursor_position()
    if save_x is not None and save_y is not None:
        save_cursor_pos(save_x, save_y)
    for row in range(height):
        move_cursor(x, y + row)
        sys.stdout.write(" " * width)
    restore_cursor_pos(0)

def assistant_write(self, lines, initial_x, initial_y, column_width, window_height):
    clear_assistant_area(self)
    sys.stdout.write("\033[s")  # Save cursor position

    # Merge into one string with explicit newlines
    full_text = "\n".join(lines)

    row = 0
    col = 0
    for ch in full_text:
        if ch == "\n" or col >= column_width:
            # move to next row
            row += 1
            if row >= window_height:
                time.sleep(0.5) # page delay
                clear_assistant_area(self)
                row = 0
            col = 0
            if ch == "\n":
                continue

        move_cursor(initial_x + col, initial_y + row)
        sys.stdout.write(ch)
        sys.stdout.flush()
        time.sleep(0.015)  # typing delay
        col += 1

    sys.stdout.write("\033[u")  # Restore cursor position
    sys.stdout.flush()

def clear_assistant_area(self):
    clear_column(self.window_0_x, self.window_0_y, self.column_width, self.window_height)