from difflib import get_close_matches

from user_interface_menus.utils._display import *
from user_interface_menus.utils._menu_navigation import *

# ------------------------------------------------------------

def print_menu_options(self, menu_options, submenu = False, index_and_text = False, choice = None):
    from user_interface_menus._menu_helper import add_recent_command
    
    def print_key_line(key, item):
        print(f"{yellow(left_align(key))} {align(item['description'])}")

    def print_keys():
        if index_and_text:
            for key, item in menu_options.items():
                if key.isdigit():
                    print(f"{yellow(key)}: {item['description']}")
            print_dashes()
            print()
            for key, item in menu_options.items():
                if not key.isdigit():
                    print_key_line(key, item)
        else:
            for key, item in menu_options.items():
                print_key_line(key, item)
        if submenu:
            print(f"\n{yellow("ENTER")}: Back to Previous Menu")

    if choice is None:
        print_keys()
        choice = print_fixed_terminal_prompt()
    
    if choice.split(" ")[0] == "command":
        query = ' '.join(choice.split(" ")[1:]) if len(choice.split(" ")) > 1 else None
        print_global_command_menu(self, query)
        return 1
    elif choice.startswith("/"):
        query = choice[1:].strip()
        if query == '':
            query = None
        print_global_command_menu(self, query)
        return 1

    selected = menu_options.get(choice)
    if selected:
        try:
            menu_caller = selected['menu_caller']
            add_recent_command(choice)
            if goto_menu(menu_caller, self):
                return 1
        except Exception as e:  
            error(f"Local menu option error: {e}")
            return 0
    elif check_global_menu_options(choice):
        try:
            description, menu_caller = check_global_menu_options(choice)
            add_recent_command(choice)
            if goto_menu(menu_caller, self):
                return 1
        except Exception as e:
            error(f"Global menu option error: {e}")
            return 0
    elif choice == '' and submenu:
        return 1
    elif choice == '' and not submenu:
        pass
    else:
        invalid_choice_menu(self, menu_options, choice)
    return 0

# ------------------------------------------------------------

def print_global_command_menu(self, query = None):
    menu_options = get_relevant_menu_options(query)
    if query is None:
        menu_options = {k: v for k, v in sorted(menu_options.items(), key=lambda item: item[0])}
    print_menu_header("command")
    if not menu_options:
        print(f"{red("No commands found matching your query.")}")
    if print_menu_options(self, menu_options, submenu = True):
        return

def print_recent_commands(self):
    from user_interface_menus._menu_helper import RECENT_COMMANDS
    if not RECENT_COMMANDS:
        print("No recent commands found.")
        exit_menu()
        return
    menu_options = {}
    for command in RECENT_COMMANDS:
        menu_options[command] = {
            'description': f"",
            'menu_caller': lambda self, cmd = command: goto_menu(cmd, self)
        }
    print_menu_header("recent")
    if print_menu_options(self, menu_options, submenu = True):
        return

# ------------------------------------------------------------

def invalid_choice_menu(self, menu_options, choice = None):
    from user_interface_menus._menu_helper import RELATED_OPTIONS_THRESHOLD, \
                                                  BEST_OPTIONS_THRESHOLD, _menu_options, \
                                                  add_recent_command
    
    def sort(iterable):
        overall_matches = get_close_matches(choice, iterable, n = 5, cutoff = max(RELATED_OPTIONS_THRESHOLD, 0.1))
        best_matches = get_close_matches(choice, iterable, n = 5, cutoff = BEST_OPTIONS_THRESHOLD)
        if best_matches and RELATED_OPTIONS_THRESHOLD < BEST_OPTIONS_THRESHOLD:
            return best_matches
        return overall_matches

    potential_local_choices = ', '.join(menu_options.keys())
    potential_glocal_choices = ', '.join(_menu_options.keys())
    combined_choices = potential_local_choices + ', ' + potential_glocal_choices
    combined_choices = ', '.join(sort(set(combined_choices.split(', '))))

    diagnosis = f"\n{red("Invalid choice.")}"

    if combined_choices == '':
        diagnosis += f" Please use {yellow("command")} to see a list of commands or {yellow("help")} to view documentation."
        print(diagnosis)
    else:    
        diagnosis += " Did you mean one of these?"
        print(diagnosis)
        
        for potential_choice in combined_choices.split(', ')[:5]:
            print(f"- {yellow(potential_choice)}")
        print(f"\nEnter {yellow("yes")} to select the first command, or enter a {yellow("different command")}.")
    
    choice = print_fixed_terminal_prompt()
    if choice.lower() == 'yes' and combined_choices != '':
        first_choice = combined_choices.split(', ')[0]
        add_recent_command(first_choice)
        if first_choice in menu_options:
            menu_caller = menu_options[first_choice]['menu_caller']
            goto_menu(menu_caller, self)
        elif first_choice in _menu_options:
            menu_caller = _menu_options[first_choice]['menu_caller']
            goto_menu(menu_caller, self)
    else:
        print_menu_options(self, menu_options, submenu = True, index_and_text = False, choice = choice)