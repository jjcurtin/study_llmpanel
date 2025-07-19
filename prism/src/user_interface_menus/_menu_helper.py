import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu_header(title):
    clear()
    print("=" * 60)
    print(" " * 20 + title)
    print("=" * 60)

def error(message = "An unexpected error occurred."):
        print(f"Error: {message}")
        input("Press Enter to continue...")

def success(message = "Operation completed successfully."):
    print(f"Success: {message}")
    input("Press Enter to continue...")
    
def exit_menu():
    input("Press Enter to continue...")