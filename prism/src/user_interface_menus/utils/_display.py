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

def left_align(text):
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    return f"{text:<{int(WINDOW_WIDTH / 2)}}"

def align(text):
    from user_interface_menus._menu_helper import RIGHT_ALIGN, WINDOW_WIDTH
    alignment = ">" if RIGHT_ALIGN else "<"
    return f"{text:{alignment}{int(WINDOW_WIDTH / 2 - 1)}}"

# ------------------------------------------------------------

def error(message = "An unexpected error occurred."):
    print(f"{red("Error")}: {message}")
    exit_menu()

def success(message = "Operation completed successfully."):
    print(f"{green("Success")}: {message}")
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

def print_dashes():
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    print("-" * WINDOW_WIDTH)

def print_equals():
    from user_interface_menus._menu_helper import WINDOW_WIDTH
    print("=" * WINDOW_WIDTH)

# ------------------------------------------------------------

def print_fixed_terminal_prompt():
    return input(f"\n{cyan("prism> ")}").strip()

def print_assistant_terminal_prompt():
    return input(f"\n{red("assistant> ")}").strip()

def print_twilio_terminal_prompt():
    print("Please enter your message below. Press ENTER to send.")
    return input(f"\n{green("twilio> ")}").strip()