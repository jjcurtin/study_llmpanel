import os

# ------------------------------------------------------------

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

# ------------------------------------------------------------

def error(message = "An unexpected error occurred."):
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        print(f"\033[31mError\033[0m: {message}")
    else:
        print(f"Error: {message}")
    exit_menu()

def success(message = "Operation completed successfully."):
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        print(f"\033[32mSuccess\033[0m: {message}")
    else:
        print(f"Success: {message}")
    exit_menu()
    
def exit_menu():
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        input("\n\033[33mENTER to Continue> \033[0m")
    else:
        input("\nENTER to Continue> ")

def exit_interface(self):
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        print(f"\033[32mExiting PRISM Interface.\033[0m")
    else:
        print("Exiting PRISM Interface.")
    exit(0)

# ------------------------------------------------------------

def print_menu_header(title):
    clear()
    from user_interface_menus._menu_helper import WINDOW_WIDTH, COLOR_ON
    padding = (WINDOW_WIDTH - len(title)) // 2
    print_equals()
    if COLOR_ON:
        print(" " * padding + f"\033[31m{title}\033[0m")
    else:
        print(" " * padding + title)
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
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        choice = input("\n\033[36mprism> \033[0m").strip()
    else:
        choice = input("\nprism> ").strip()
    return choice

def print_assistant_terminal_prompt():
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        choice = input("\n\033[31massistant> \033[0m").strip()
    else:
        choice = input("\nassistant> ").strip()
    return choice

def print_twilio_terminal_prompt():
    print("Please enter your message below. Press ENTER to send.")
    from user_interface_menus._menu_helper import COLOR_ON
    if COLOR_ON:
        choice = input("\n\033[32mtwilio> \033[0m").strip()
    else:
        choice = input("\ntwilio> ").strip()
    return choice