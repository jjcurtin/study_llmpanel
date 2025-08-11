# display api

import os

# ------------------------------------------------------------

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------------------------------------------

def green(message = None):
    from user_interface_menus._menu_helper import COLOR_ON
    green, color_end = ("\033[32m", "\033[0m") if COLOR_ON else ("\033[1m", "\033[0m")
    return f"{green}{message}{color_end}"

def red(message = None):
    from user_interface_menus._menu_helper import COLOR_ON
    red, color_end = ("\033[31m", "\033[0m") if COLOR_ON else ("\033[1m", "\033[0m")
    return f"{red}{message}{color_end}"

def yellow(message = None):
    from user_interface_menus._menu_helper import COLOR_ON
    yellow, color_end = ("\033[33m", "\033[0m") if COLOR_ON else ("\033[4m", "\033[0m")
    return f"{yellow}{message}{color_end}"

def cyan(message = None):
    from user_interface_menus._menu_helper import COLOR_ON
    cyan, color_end = ("\033[36m", "\033[0m") if COLOR_ON else ("", "")
    return f"{cyan}{message}{color_end}"

# ------------------------------------------------------------

def align(text, column_number, num_columns, formatless = None, window_width = None, align_right = None, locked = False, border_left = False, border_right = False):
    from user_interface_menus._menu_helper import RIGHT_ALIGN, WINDOW_WIDTH
    if window_width is None:
        window_width = int(WINDOW_WIDTH)
    if formatless is None:
        formatless = text
    if align_right is None:
        align_right = RIGHT_ALIGN

    compensation = (len(text) - len(formatless))
    format_width = int(window_width + compensation)
    middle_screen_adjustment = (WINDOW_WIDTH % num_columns)
    middle_screen_adjustment1 = middle_screen_adjustment // 2 + (middle_screen_adjustment % 2)
    middle_screen_adjustment2 = middle_screen_adjustment // 2
    format_width += middle_screen_adjustment if (
        (column_number == 0 and num_columns == 2) or
        (column_number == 1 and num_columns == 3)
    ) else middle_screen_adjustment1 if (
        column_number == 1 and num_columns == 4
    ) else middle_screen_adjustment2 if (
        column_number == 2 and num_columns == 4
    ) else 0

    if locked:
        alignment = "<" if not align_right else ">"
    else:
        if align_right and not RIGHT_ALIGN:
            alignment = "<"
        elif not align_right and RIGHT_ALIGN:
            alignment = ">"
        else:
            alignment = ">" if align_right else "<"

    left, right = "", ""
    if border_left:
        left = "| "
        # format_width -= 2
    if border_right:
        right = " |"
        # format_width -= 2
    output = f"{text:{alignment}{format_width}}"
    return output

def display_in_columns(items = None):
    from user_interface_menus._menu_helper import WINDOW_WIDTH, COLOR_ON
    import re

    if items is None:
        return "Error: No items to display."
    num_segments = len(items)

    def assemble_content():
        column_width = int(WINDOW_WIDTH / num_segments)
        output = ""
        for i, item in enumerate(items):
            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            item_formatless = ansi_escape.sub('', item['text'])
            border_settings = item.get('bordered', 'none')
            border_left = False
            border_right = False
            if border_settings == 'left' or border_settings == 'both':
                border_left = True
            if border_settings == 'right' or border_settings == 'both':
                border_right = True
            output += align(
                item['text'], i, 
                num_segments, formatless = item_formatless, 
                window_width = column_width, 
                align_right = item.get('align_right', False),
                locked = item.get('locked', False),
                border_left = border_left,
                border_right = border_right,
            )
        return output
    
    output = assemble_content()
    return output

# ------------------------------------------------------------

def error(message = "An unexpected error occurred.", self = None):
    from user_interface_menus.utils._menu_navigation import clear_commands_queue
    from user_interface_menus._menu_helper import write_to_interface_log

    print(f"{red('Error')}: {message}")
    try:
        write_to_interface_log(f"Error: {message}")
    except Exception as e:
        print(f"Error: Could not write to log file: {e}")

    # stop processing commands, error
    if self is not None:
        clear_commands_queue(self)
    exit_menu()

def success(message = "Operation completed successfully.", self = None):
    print(f"{green('Success')}: {message}")
    from user_interface_menus._menu_helper import write_to_interface_log
    try:
        write_to_interface_log(f"Success: {message}")
    except Exception as e:
        error(f"Could not write to log file: {e}")

    # skip exit menu
    if self is None or not self.commands_queue:
        exit_menu()
    
def exit_menu():
    input(f"\n{yellow("ENTER to Continue>")} ")

def exit_interface(self):
    print(green("Exiting PRISM Interface."))
    exit(0)

# ------------------------------------------------------------

def print_menu_header(title):
    clear()
    from user_interface_menus._menu_helper import WINDOW_WIDTH

    # title
    padding = (WINDOW_WIDTH - len(title)) // 2
    print_equals()
    print(" " * padding + f"{red(title)}")
    print_equals()

    # # recommended actions
    # from user_interface_menus._menu_helper import RECOMMENDED_ACTIONS
    # from user_interface_menus._menu_helper import WINDOW_WIDTH
    # if RECOMMENDED_ACTIONS:
    #     length = 0
    #     action_string = ""
    #     for action in RECOMMENDED_ACTIONS:
    #         action_string += f" {cyan(action)}"
    #         length += 1
    #         if action is not RECOMMENDED_ACTIONS[-1]:
    #             action_string += " |"
    #             length += 2
    #         length += len(action.strip())
    #     action_string = action_string.strip()
    #     padding = (WINDOW_WIDTH - length) // 2
    #     print(" " * padding + action_string)
    #     print_equals()
    print()

def print_dashes():
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    print("-" * WINDOW_WIDTH)

def print_guide_lines(divisions, line_type, num_segments):
    from user_interface_menus._menu_helper import WINDOW_WIDTH, COLOR_ON
    max_divisions = 3
    if divisions > max_divisions:
        error(f"Maximum divisions is {max_divisions}. You requested {divisions}.")
    
    elif line_type == "dashes":
        chars = ['-', '-', '-', '-']
        if COLOR_ON:
            chars = [f"\033[1;3{(i % 6) + 1}m{'-'}\033[0m" for i, char in enumerate(chars)]
        segment_length = WINDOW_WIDTH // num_segments
        middle_screen_adjustment = (WINDOW_WIDTH % num_segments)
        middle_screen_adjustment1 = middle_screen_adjustment // 2 + (middle_screen_adjustment % 2)
        middle_screen_adjustment2 = middle_screen_adjustment // 2
        s = "".join(
            "|" + (chars[i % len(chars)] * (
            segment_length - 2 + (
                middle_screen_adjustment if (
                (i == 0 and num_segments == 2) or
                (i == 1 and num_segments == 3)
                ) else middle_screen_adjustment1 if (
                    i == 1 and num_segments == 4
                ) else middle_screen_adjustment2 if (
                    i == 2 and num_segments == 4
                ) else 0
            )
            )) + "|"
            for i in range(num_segments)
        )
        print(s.strip())
    
    elif line_type == "dots":
        chars = ['|', '|', '|', '|']
        if COLOR_ON:
            chars = [f"\033[1;3{(i % 6) + 1}m{'|'}\033[0m" for i, char in enumerate(chars)]
        segment_length = WINDOW_WIDTH // num_segments
        middle_screen_adjustment = (WINDOW_WIDTH % num_segments)
        middle_screen_adjustment1 = middle_screen_adjustment // 2 + (middle_screen_adjustment % 2)
        middle_screen_adjustment2 = middle_screen_adjustment // 2
        s = "".join(
            chars[i % len(chars)] + (" " * (
            segment_length - 2 + (
                middle_screen_adjustment if (
                (i == 0 and num_segments == 2) or
                (i == 1 and num_segments == 3)
                ) else middle_screen_adjustment1 if (
                    i == 1 and num_segments == 4
                ) else middle_screen_adjustment2 if (
                    i == 2 and num_segments == 4
                ) else 0
            ))) + chars[i % len(chars)]
            for i in range(num_segments)
        )
        print(s.strip())

def print_equals():
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    print("=" * WINDOW_WIDTH)

# ------------------------------------------------------------

def print_fixed_terminal_prompt():
    return input(f"\n{cyan('prism> ')}").strip()

def print_assistant_terminal_prompt():
    return input(f"\n{red('assistant> ')}").strip()

def print_twilio_terminal_prompt():
    print("Please enter your message below. Press ENTER to send.")
    return input(f"\n{green('twilio> ')}").strip()