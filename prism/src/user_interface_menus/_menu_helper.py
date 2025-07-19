import os

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_menu_header(title):
    clear()
    padding = (60 - len(title)) // 2
    print("=" * 60)
    print(" " * padding + title)
    print("=" * 60)
    print()

def print_menu_options(self, menu_options, submenu = False, index_and_text = False):
    if index_and_text:
        for key, item in menu_options.items():
            if key.isdigit():
                print(f"{key:<20}{item['description']:<20}")
        print("-" * 60)
        print()
        for key, item in menu_options.items():
            if not key.isdigit():
                print(f"{key:<20}{item['description']:<20}")
    else:
        for key, item in menu_options.items():
            print(f"{key:<20}{item['description']:<20}")
    if submenu:
        print("\nENTER: Back to Previous Menu")
    choice = input("\nEnter your choice: ").strip()
    selected = menu_options.get(choice)
    if selected:
        handler = selected['menu_caller']
        if handler(self): # if the submenu indicates to exit
            return 1
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