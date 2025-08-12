# menu display api most text based methods are in _display.py

from difflib import get_close_matches

from user_interface_menus.utils._display import *
from user_interface_menus.utils._menu_navigation import *

# ------------------------------------------------------------

def print_menu_options(self, menu_options, submenu = False, index_and_text = False, choice = None, recommended_actions = None):
    from user_interface_menus._menu_helper import add_recent_command, set_local_menu_options, add_user_defined_global_command, save_macro

    if submenu:
        set_local_menu_options("debug", menu_options)
    
    def print_key_line(key, item, index, total_items):
        recommended_text = f" (recommended)" if recommended_actions is not None and key in recommended_actions else ""
        items = [
            # can have up to four columns
            {"text": f"", "align_right" : False, "locked": True, "bordered": "left"},
            # {"text": f"", "align_right" : False, "locked": True, "bordered": "both"},
            {"text": f"{yellow(key + green(recommended_text))}", "align_right" : False, "locked": True, "bordered": "left"},
            {"text": f"{item['description']}", "align_right": False, "locked": False, "bordered": "both"},
        ]
        window_positions, column_width = display_in_columns(items)
        for i, pos in enumerate(window_positions):
            if index == 0:
                setattr(self, f"window_{i}_x", pos[0])
                setattr(self, f"window_{i}_y", pos[1])
        self.column_width = column_width
        self.window_height = total_items
        self.num_columns = len(window_positions)
        # print_guide_lines(len(items) - 1, "dashes", len(items))

    def print_keys():
        if index_and_text:
            for key, item in menu_options.items():
                if key.isdigit():
                    print(f"{yellow(key)}: {item['description']}")
            print_dashes()
            print()
            print_dashes()
            for index, (key, item) in enumerate(menu_options.items()):
                if not key.isdigit():
                    print_key_line(key, item, index, len(menu_options))
        else:
            print_dashes()
            for index, (key, item) in enumerate(menu_options.items()):
                if not key.isdigit():
                    print_key_line(key, item, index, len(menu_options))
        print_dashes()
        if submenu:
            print(f"\n{yellow("ENTER")}: Back to Previous Menu")

    def check_for_special_commands(choice, self):
        from user_interface_menus._menu_helper import remove_macro, macro_search
        def check_prefix(prefix):
            return choice.startswith(prefix)
        
        def check_prefixes(prefixes):
            return [check_prefix(prefix) for prefix in prefixes]

        command, \
        command_query, \
        execute_commands, \
        register_command, \
        remove_command, \
        search_macros, \
        query_assistant, \
        query_assistant_alias = \
        \
        check_prefixes (
            ["command ", 
             "?", 
             "/", 
             "$", 
             "-", 
             "!",
             "@",
             "assistant ",
             ]
        )

        iterations = int(choice.split(".")[1]) if "." in choice and choice.split(".")[1].isdigit() else 1
        if iterations:
            choice = choice.split(".")[0]

        if command or command_query:
            query = ' '.join(choice.split(" ")[1:]) if len(choice.split(" ")) > 1 and command else choice[1:] if len(choice) > 1 else None
            print_global_command_menu(self, query)
        elif execute_commands:
            for _ in range(iterations):
                CommandInjector(choice)(self)
        elif register_command:
            identifier = choice.split("=")[0][1:].strip()
            command_string = choice.split("=")[1].strip() if '=' in choice else None
            print(f"Registering {identifier} as {command_string}")
            if add_user_defined_global_command(identifier, command_string, self = self):
                save_macro(self, identifier, command_string)
        elif remove_command:
            remove_macro(self, choice)
        elif search_macros:
            macro_search(self, choice, all = (len(choice) == 1))
        elif query_assistant or query_assistant_alias:
            query = ' '.join(choice.split(" ")[1:]) if query_assistant_alias else choice[1:] if query_assistant else None
            self.inputs_queue.put(query)
            from user_interface_menus.assistant._assistant_menu import assistant_menu
            assistant_menu(self)
        else:
            return False
        return True

    if choice is None:
        if self.commands_queue:
            return process_chained_command(self)
        print_keys()
        choice = print_fixed_terminal_prompt()

    if not submenu:
        while choice == '':
            choice = re_print_fixed_terminal_prompt(self)

    if choice == '':
        return 1
    elif check_for_special_commands(choice, self):
        return 1
    elif menu_options.get(choice):
        try:
            selected = menu_options.get(choice)
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
    else:
        invalid_choice_menu(self, menu_options, choice)
    return 0

# ------------------------------------------------------------

def print_register_command_menu(self):
    from user_interface_menus._menu_helper import add_user_defined_global_command, save_macro
    identifier = get_input(self, prompt = "Enter the command identifier (e.g., 'my_command'): ")
    command_string = get_input(self, prompt = "Enter the command string (e.g., '/command1?input'): ")
    description = get_input(self, prompt = "Enter a description for the command (optional): ")
    if not identifier or not command_string:
        error("Identifier and command string cannot be empty.")
        return
    if description == '':
        description = None
    if add_user_defined_global_command(identifier, command_string, description, self):
        save_macro(self, identifier, command_string, description)

def print_global_command_menu(self, query = None):
    menu_options = get_relevant_menu_options(query)
    if query is None:
        menu_options = {k: v for k, v in sorted(menu_options.items(), key=lambda item: item[0])}
    if not self.commands_queue:
        print_menu_header("command")
        if not menu_options:
            print(f"{red("No commands found matching your query.")}")
    if print_menu_options(self, menu_options, submenu = True):
        return

def print_recent_commands(self):
    from user_interface_menus._menu_helper import RECENT_COMMANDS
    if not RECENT_COMMANDS:
        if not self.commands_queue:
            print("No recent commands found.")
            exit_menu()
        return
    menu_options = {}
    for command in RECENT_COMMANDS:
        menu_options[command] = {
            'description': f"",
            'menu_caller': lambda self, cmd = command: goto_menu(cmd, self)
        }
    if not self.commands_queue:
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
        print(f"\nEnter {yellow("yes")} to select the first command or enter a different command.")
    print(f"If you meant to enter a command string, please include {yellow("/")} at the start of your command.")
    print(f"To search for commands, use {yellow("?")} followed by your query.")
    
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

# ------------------------------------------------------------

def infopage(self, content = [], title = 'help infopage'):
    if not self.commands_queue:
        if content:
            print_menu_header(title)
            for line in content:
                print(line)
            exit_menu()
        else:
            print(f"{red('No content available for this infopage.')}")
            exit_menu()