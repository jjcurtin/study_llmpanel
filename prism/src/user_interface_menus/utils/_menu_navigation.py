# menu navigation logic

from user_interface_menus.utils._display import *

# ------------------------------------------------------------

def menu_loop(self, menu_options, header = "main", name = "Main Menu", submenu = True, recommended_actions = [], additional_content = None):
    if 'print_menu_options' not in globals():
        from user_interface_menus.utils._menu_display import print_menu_options
    if (name == "Main Menu" or header == "main") and submenu:
        error("Please call menu loop with the appropriate parameters.", self)

    while True:
        if not self.commands_queue:
            print_menu_header(header)
            if additional_content:
                for line in additional_content:
                    if line == "-":
                        print_dashes()
                    elif line == "":
                        print()
                    else:
                        print(line)
            assistant_header_write(self, [name])
        if print_menu_options(self, menu_options, submenu = submenu, recommended_actions = recommended_actions) and submenu:
            break

# ------------------------------------------------------------

def get_menu_options():
    from user_interface_menus._menu_helper import _menu_options
    return _menu_options

def get_relevant_menu_options(query = None, exact_match = False):
    from user_interface_menus._menu_helper import RELATED_OPTIONS_THRESHOLD
    from difflib import get_close_matches

    def sort(iterable):
        threshold = max(RELATED_OPTIONS_THRESHOLD, 0.1)
        return get_close_matches(query, iterable, n = 15, cutoff = threshold)
    
    def find_subset_matches(iterable):
        matches = []
        for item in iterable:
            if query in item:
                matches.append(item)
        return matches

    menu_options = get_menu_options()
    potential_global_choices = ', '.join(menu_options.keys())
    if query is None:
        choices = potential_global_choices

    if query is not None:
        if exact_match:
            if perfect_match := menu_options.get(query):
                return {query: perfect_match}

        choices = ', '.join(
            sorted(
            set(sort(set(potential_global_choices.split(', ')))) | 
            set(find_subset_matches(potential_global_choices.split(', ')))
            )
        )
    
    choices = {choice: menu_options[choice] for choice in choices.split(', ') if choice in menu_options}
    return choices

def check_global_menu_options(query = None):
    if query is None:
        return None
    
    menu_options = get_menu_options()
    result = menu_options.get(query)
    if result is None:
        return None
    return result['description'], result['menu_caller']

# ------------------------------------------------------------

def goto_menu(menu_caller, self):
    import time
    from user_interface_menus._menu_helper import MENU_DELAY
    from user_interface_menus._menu_helper import get_local_menu_options, print_local_menu_options
    time.sleep(MENU_DELAY)
    try:
        if callable(menu_caller):
            return menu_caller(self)
        elif isinstance(menu_caller, str):
            result = check_global_menu_options(menu_caller)
            if result:
                description, caller = result
                return caller(self)
            
            local_results = get_local_menu_options()
            result = local_results.get(menu_caller)
            if result:
                menu_caller = result['menu_caller']
                if callable(menu_caller):
                    return menu_caller(self)
                elif isinstance(menu_caller, str):
                    return goto_menu(menu_caller, self)
            else:
                print_local_menu_options()
                error_string = f"likely a syntax error. {(yellow('?<query>'))} to search for commands, or {yellow('!<query>')} to search macros specifically."
                error(f"Command '{menu_caller}' failed; {error_string}", self)
                return False
        else:
            error("Invalid menu caller.", self)
            return False
    except Exception as e:
        error(f"An error occurred while navigating to the menu: {e}", self)
        return False
    
# ------------------------------------------------------------

def get_input(self, prompt = None, default_value = None, print_prompt = True):
    try:
        inputs_queue = self.inputs_queue
        if inputs_queue is None:
            import queue
            self.inputs_queue = queue.Queue()
        
        if inputs_queue and not inputs_queue.empty():
            input_override = inputs_queue.get()
            if input_override is not None:
                if print_prompt:
                    print(f"{prompt}{input_override}")
                return input_override
        
        if prompt is None:
            prompt = "Input: "
        prompt += f"[default = {default_value}]: " if default_value else ""
        
        user_input = input(prompt).strip()
        if not user_input and default_value is not None:
            return default_value
        return user_input
    except Exception as e:
        error(f"An error occurred while getting input: {e}", self)
        return None

def prompt_confirmation(self, prompt = "Are you sure?", default_value = "n"):
    confirmation = get_input(self, prompt + ' (y/n): ', default_value)
    if confirmation.lower() in ['y', 'yes']:
        return True
    elif confirmation.lower() in ['n', 'no']:
        return False
    else:
        print(f"Invalid confirmation input. Defaulting to {default_value}.")
        return default_value.lower() in ['y', 'yes']

# ------------------------------------------------------------

def clear_inputs_queue(self):
    from queue import Empty
    inputs_queue = self.inputs_queue
    if inputs_queue is None:
        error("Inputs queue is not available.", self)
        return
    
    try:
        while True:
            inputs_queue.get_nowait()
    except Empty:
        pass
    
def clear_commands_queue(self):
    commands_queue = self.commands_queue
    if commands_queue is None:
        error("Commands queue is not available.")
        return
    
    try:
        while True:
            commands_queue.popleft()
    except IndexError:
        pass  # empty

# ------------------------------------------------------------

class CommandInjector:
    def __init__(self, command_string):
        self.command_string = command_string

    def __call__(self, self_ref):
        try:
            tokens = self.command_string.split('/')
            for token in reversed(tokens):
                stripped = token.strip()
                if stripped:
                    self_ref.commands_queue.appendleft(stripped)
        except Exception as e:
            error(f"Error processing command string: {e}", self)
        finally:
            return True

    def __repr__(self):
        return f"<CommandInjector: {self.command_string}>"

def process_chained_command(self):
    import time
    commands = self.commands_queue
    inputs = self.inputs_queue
    try:
        command = commands.popleft()
        from user_interface_menus._menu_helper import MENU_DELAY
        time.sleep(MENU_DELAY)
        if not command:
            raise ValueError("Command cannot be empty.")
        if '?' in command:
            parts = command.split('?', 1)
            print(f"Executing command: {parts[0]}")
            command = parts[0]
            input_value = parts[1] if len(parts) > 1 else ""
            input_values = input_value.split('?')
            print(f"Input values: {input_values}")
            for value in input_values:
                inputs.put(value.strip())
        else:
            print(f"Executing command: {command}")
        if goto_menu(command, self):
            return 1
    except Exception as e:
        error(f"Error processing command '{command}': {e}", self)
    finally:
        clear_inputs_queue(self)
        return 1