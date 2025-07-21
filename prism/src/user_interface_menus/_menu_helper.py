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

# def init_global_menu_options():
#     global menu_options
#     # import all files in the user_interface_menus directory recursively
#     # go into each of their functions and build a tree of menu options

#     ui_menus = {
#        (f[:-3].upper().lstrip('_')): (f[:-3].replace('_', ' ').title().replace(' ', '')
#                                       for f in os.listdir('user_interface_menus')
#             if f.endswith('.py') and f != '_menu_helper.py'
#         )
#     }

#     module = __import__(module_name, fromlist = [task_type])
#     task_type = task_type.replace('_', ' ').title().replace(' ', '')
#     module = importlib.reload(module)
#     task_class = getattr(module, task_type)

def check_global_menu_options(query = None):
    global menu_options
    if query is None:
        return None
    result = menu_options.get(query)
    if result is None:
        return None
    return result['description'], result['menu_caller']

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
    choice = input("\nprism> ").strip()
    selected = menu_options.get(choice)
    if selected:
        handler = selected['menu_caller']
        if handler(self): # if the submenu indicates to exit
            return 1
    elif choice == '' and submenu:
        return 1
    elif choice == '' and not submenu:
        pass
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