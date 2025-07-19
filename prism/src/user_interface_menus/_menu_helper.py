import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu_header(title):
    clear()
    padding = (60 - len(title)) // 2
    print("=" * 60)
    print(" " * padding + title)
    print("=" * 60)

def print_menu_options(self, menu_options, submenu = False):
    for key, item in menu_options.items():
        print(f"{key:<20}{item['description']:<20}")
    if submenu:
        print("\nENTER: Back to Previous Menu")
    choice = input("\nEnter your choice: ").strip()
    selected = menu_options.get(choice)
    if selected:
        handler = selected['menu_caller']
        handler(self)
    elif choice == '' and submenu:
        return 1
    else:
        error("Invalid choice.")
    return 0

def error(message = "An unexpected error occurred."):
        print(f"Error: {message}")
        input("Press Enter to continue...")

def success(message = "Operation completed successfully."):
    print(f"Success: {message}")
    input("Press Enter to continue...")
    
def exit_menu():
    input("Press Enter to continue...")