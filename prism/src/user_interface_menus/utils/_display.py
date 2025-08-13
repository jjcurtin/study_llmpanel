# display api

import os, sys, msvcrt, time


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

def white(message = None):
    from user_interface_menus._menu_helper import COLOR_ON
    white, color_end = ("\033[37m", "\033[0m") if COLOR_ON else ("", "")
    return f"{white}{message}{color_end}"

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
        format_width -= 2
    if border_right:
        right = " |"
        format_width -= 2
    truncated = text[:format_width]
    output = f"{left}{truncated:{alignment}{format_width}}{right}"
    return output

# ------------------------------------------------------------

def display_in_columns(items = None):
    from user_interface_menus._menu_helper import WINDOW_WIDTH, COLOR_ON
    import re

    if items is None:
        return "Error: No items to display."
    num_segments = len(items)

    window_positions = []

    def assemble_content():
        column_width = int(WINDOW_WIDTH / num_segments)
        frame_width = column_width
        output = ""
        initial_pos = get_cursor_position()
        initial_y = initial_pos[1] if initial_pos[1] is not None else 0

        line_text = ""
        for i, item in enumerate(items):

            if i % len(items) == 0:
                line_text = ""

            ansi_escape = re.compile(r'\x1B\[[0-?]*[ -/]*[@-~]')
            item_formatless = ansi_escape.sub('', item['text'])
            border_settings = item.get('bordered', 'none')
            border_left = False
            border_right = False
            if border_settings == 'left' or border_settings == 'both':
                border_left = True
            if border_settings == 'right' or border_settings == 'both':
                border_right = True
            initial_x = len(output)
            if border_left:
                initial_x += 2
                frame_width = column_width - 2
            window_positions.append((initial_x, initial_y))
            line_text += align(
                item['text'], i, 
                num_segments, formatless = item_formatless, 
                window_width = column_width, 
                align_right = item.get('align_right', False),
                locked = item.get('locked', False),
                border_left = border_left,
                border_right = border_right,
            )
            output += line_text

            if i % len(items) == 1:
                print(line_text)
        return output, frame_width
    
    output, column_width = assemble_content()
    # print(output)
    return window_positions, column_width

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
    padding = (WINDOW_WIDTH - len(title)) // 2
    print_equals()
    print(" " * padding + f"{red(title)}")
    print_equals()

    print()
    print_dashes()
    print()

def print_dashes(delay = None):
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    if delay is not None:
        for i in range(WINDOW_WIDTH):
            print("-", end="", flush = True)
            time.sleep(delay)
    else:
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

def re_print_fixed_terminal_prompt(self):
    x, y = save_current_cursor_pos(self)
    move_cursor(self, x + len('prism> '), y - 1)
    return input().strip()

def print_assistant_terminal_prompt(self):
    from user_interface_menus.utils._menu_navigation import get_input
    return get_input(self, f"\n{red('assistant> ')}", print_prompt = False).strip()

def print_twilio_terminal_prompt():
    print("Please enter your message below. Press ENTER to send.")
    return input(f"\n{green('twilio> ')}").strip()

# ------------------------------------------------------------
import sys, msvcrt, time

def get_cursor_position():
    sys.stdout.write("\033[6n")
    sys.stdout.flush()

    buf = ""
    while True:
        ch = msvcrt.getwch()
        buf += ch
        if ch == "R":
            break

    if not buf.startswith("\x1b["):
        return None, None  # not an ANSI response

    try:
        pos = buf[2:-1]  # strip "\x1b[" and trailing "R"
        row_str, col_str = pos.split(";")
        return int(col_str) - 1, int(row_str) - 1 
    except Exception:
        return None, None
        
def save_current_cursor_pos(self):
    x, y = get_cursor_position()
    save_cursor_pos(self, x, y)
    return x, y
        
def save_cursor_pos(self, x, y):
    if not hasattr(self, 'saved_positions'):
        self.saved_positions = []
    self.saved_positions.append((x, y))

def restore_cursor_pos(self, index=-1):
    if not hasattr(self, 'saved_positions') or not self.saved_positions:
        return
    x, y = self.saved_positions[index]
    move_cursor(self, x, y)

def move_cursor(self, x, y):
    sys.stdout.write(f"\033[{y+1};{x+1}H")
    sys.stdout.flush()

def clear_column(self, x, y, width, height):
    save_x, save_y = get_cursor_position()
    if save_x is not None and save_y is not None:
        save_cursor_pos(self, save_x, save_y)
    for row in range(height):
        move_cursor(self, x, y + row)
        sys.stdout.write(" " * width)
    restore_cursor_pos(self, 0)

def ansi_save_cursor():
    sys.stdout.write("\033[s")
    sys.stdout.flush()

def ansi_restore_cursor():
    sys.stdout.write("\033[u")
    sys.stdout.flush()

def ansi_clear_line():
    sys.stdout.write("\033[2K")
    sys.stdout.flush()

def ansi_clear_screen():
    sys.stdout.write("\033[2J")
    sys.stdout.flush()

def ansi_write_char(c):
    sys.stdout.write(c)
    sys.stdout.flush()

def ansi_hide_cursor():
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()

def ansi_show_cursor():
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()

def ansi_write_str(s):
    sys.stdout.write(s)
    sys.stdout.flush()

# def screen_write(self, content, initial_x, initial_y, column_width, window_height):

def assistant_header_write(self, lines):
    from user_interface_menus._menu_helper import WINDOW_WIDTH, ASSISTANT_TYPE_SPEED
    import re

    lines = [line.encode().decode('unicode_escape') for line in lines]

    initial_x = 0
    initial_y = 3
    window_height = 1
    ansi_save_cursor()
    ansi_hide_cursor()

    clear_column(self, initial_x, initial_y, WINDOW_WIDTH, 1)

    full_text = "\n".join(lines)
    ansi_escape = re.compile(r'\033\[[0-?]*[ -/]*[@-~]')

    matches = list(ansi_escape.finditer(full_text))
    next_escape_idx = 0
    next_escape = matches[next_escape_idx] if matches else None

    row = 0
    col = 0
    
    time_to_read_char_fast = 0.02
    time_to_read_char_medium = 0.04
    time_to_read_char_slow = 0.05
    min_time_to_read = 1
    max_time_to_read = 10
    print_speed = ASSISTANT_TYPE_SPEED

    i = 0
    length = len(full_text)

    while i < length:
        if next_escape and i == next_escape.start():
            ansi_write_str(next_escape.group())
            i = next_escape.end()
            next_escape_idx += 1
            next_escape = matches[next_escape_idx] if next_escape_idx < len(matches) else None
            continue

        ch = full_text[i]

        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key == '\r':  # enter key
                ansi_restore_cursor()
                ansi_show_cursor()
                return

        if ch == "\n" or col >= WINDOW_WIDTH:
            row += 1
            if row >= window_height:
                if col < 20:
                    char_time = time_to_read_char_slow
                elif col < 50:
                    char_time = time_to_read_char_medium
                else:
                    char_time = time_to_read_char_fast
                text_reading_time = max(min_time_to_read, min(max_time_to_read, col * char_time))
                time.sleep(text_reading_time)
                if i < length - 1:
                    clear_column(self, initial_x, initial_y, WINDOW_WIDTH, 1)
                row = 0
            col = 0
            if ch == "\n":
                i += 1
                continue

        move_cursor(self, initial_x + col, initial_y + row)
        ansi_write_char(ch)
        time.sleep(print_speed)
        col += 1
        i += 1

    ansi_show_cursor()
    ansi_restore_cursor()

def assistant_header_shift_write(self, lines):
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    initial_x, initial_y = 0, 3
    window_height = 1

    full_text = " ".join(line.replace('\n', ' ') for line in lines)
    padding = " " * WINDOW_WIDTH
    scroll_text = padding + full_text + padding
    length = len(scroll_text)

    ansi_save_cursor()
    ansi_hide_cursor()

    for start in range(length - WINDOW_WIDTH + 1):
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key == '\r':
                clear_column(self, initial_x, initial_y, WINDOW_WIDTH, window_height)
                break

        sys.stdout.write(f"\033[u\033[{initial_y + 1};{initial_x + 1}H{scroll_text[start:start + WINDOW_WIDTH]}")
        sys.stdout.flush()

        time.sleep(0.05)

    ansi_show_cursor()
    ansi_restore_cursor()
    
def assistant_write(self, lines, initial_x, initial_y, column_width, window_height):
    clear_assistant_area(self)
    ansi_save_cursor()

    # Merge into one string with explicit newlines
    full_text = "\n".join(lines)

    row = 0
    col = 0
    for ch in full_text:
        if msvcrt.kbhit():
            key = msvcrt.getwch()
            if key == '\r':
                ansi_restore_cursor()
                break
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

        move_cursor(self, initial_x + col, initial_y + row)
        ansi_write_char(ch)
        time.sleep(0.015)  # typing delay
        col += 1

    ansi_restore_cursor()

def clear_assistant_area(self):
    clear_column(self, self.window_0_x, self.window_0_y, self.column_width, self.window_height)