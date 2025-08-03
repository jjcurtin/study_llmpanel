# menu navigation logic

from user_interface_menus.utils._display import *

# ------------------------------------------------------------

def get_menu_options():
    from user_interface_menus._menu_helper import _menu_options
    return _menu_options

def get_relevant_menu_options(query = None):
    from user_interface_menus._menu_helper import _menu_options, RELATED_OPTIONS_THRESHOLD

    def sort(iterable):
        from difflib import get_close_matches
        threshold = max(RELATED_OPTIONS_THRESHOLD, 0.1)
        return get_close_matches(query, iterable, n = 15, cutoff = threshold)

    menu_options = get_menu_options()
    potential_local_choices = ', '.join(menu_options.keys())
    potential_glocal_choices = ', '.join(_menu_options.keys())
    combined_choices = potential_local_choices + ', ' + potential_glocal_choices

    if query is not None:
        combined_choices = ', '.join(sort(set(combined_choices.split(', '))))
    
    combined_choices = {choice: menu_options[choice] for choice in combined_choices.split(', ') if choice in menu_options}
    return combined_choices

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
                print("\nAvailable local menu options at this point in execution:\n")
                print_local_menu_options()
                error(f"Menu '{menu_caller}' not found.", self)
                return False
        else:
            error("Invalid menu caller.", self)
            return False
    except Exception as e:
        error(f"An error occurred while navigating to the menu: {e}", self)
        return False
    
# ------------------------------------------------------------

def get_input(self, prompt = None, default_value = None):
    inputs_queue = self.inputs_queue
    if inputs_queue is None:
        error("Inputs queue is not available.", self)
        return
    
    if inputs_queue and not inputs_queue.empty():
        input_override = inputs_queue.get()
        if input_override is not None:
            print(f"{prompt}{input_override}")
            return input_override
    
    if prompt is None:
        prompt = "Input: "
    prompt += f"[default = {default_value}]: " if default_value else ""
    
    user_input = input(prompt).strip()
    if not user_input and default_value is not None:
        return default_value
    return user_input

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
    from queue import Empty
    commands_queue = self.commands_queue
    if commands_queue is None:
        error("Commands queue is not available.")
        return
    
    try:
        while True:
            commands_queue.get_nowait()
    except Empty:
        pass

# ------------------------------------------------------------

def parse_command_string(command_string, self, mode = "FIFO"):
    tokens = command_string.split('/')
    commands_to_chain = self.commands_queue

    # strictly FIFO /1/2/3 = /1/2/3/a/b/c
    if mode == "FIFO":
        for token in tokens:
            stripped_token = token.strip()
            if stripped_token:
                commands_to_chain.put(stripped_token)

    # in place macro expansion /1/2/3 = /1/a/2/b/3/c
    elif mode == "IN_PLACE":
        pass

    else:
        error(f"Unknown mode '{mode}' for command parsing.", self)
        return

def process_chained_command(self):
    import time
    commands = self.commands_queue
    inputs = self.inputs_queue
    try:
        command = commands.get()
        print(f"Executing command: {command}")
        from user_interface_menus._menu_helper import MENU_DELAY
        time.sleep(MENU_DELAY)
        if not command:
            raise ValueError("Command cannot be empty.")
        if '?' in command:
            parts = command.split('?', 1)
            print(f"Command parts: {parts}")
            command = parts[0]
            input_value = parts[1] if len(parts) > 1 else ""
            input_values = input_value.split('?')
            for value in input_values:
                inputs.put(value.strip())
        if goto_menu(command, self):
            return 1
    except Exception as e:
        error(f"Error processing command '{command}': {e}", self)
    finally:
        clear_inputs_queue(self)
        return 1