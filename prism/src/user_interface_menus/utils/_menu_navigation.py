# menu navigation logic

from user_interface_menus.utils._display import *

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

def goto_menu(menu_caller, self):
    try:
        if callable(menu_caller):
            return menu_caller(self)
        elif isinstance(menu_caller, str):
            result = check_global_menu_options(menu_caller)
            if result:
                description, caller = result
                return caller(self)
            else:
                error(f"Menu '{menu_caller}' not found.")
                return False
        else:
            error("Invalid menu caller.")
            return False
    except Exception as e:
        error(f"An error occurred while navigating to the menu: {e}")
        return False
    
def get_input(self, prompt = None, default_value = None):
    inputs_queue = self.inputs_queue
    if inputs_queue is None:
        error("Inputs queue is not available.")
        return
    
    if inputs_queue and not inputs_queue.empty():
        input_override = inputs_queue.get()
        if input_override is not None:
            return input_override
    
    if prompt is None:
        prompt = "Input: "
    prompt += f"[default = {default_value}]: " if default_value else ""
    
    user_input = input(prompt).strip()
    if not user_input and default_value is not None:
        return default_value
    return user_input

# /command?input/command/command?input?input 
def execute_command_string(command_string, self):
    commands = command_string.split('/')
    inputs = self.inputs_queue
    for command in commands:
        command = command.strip()
        if not command:
            continue
        if '?' in command:
            command, input_value = command.split('?')
            input_values = input_value.split('?')
            for value in input_values:
                inputs.put(value.strip())
        if goto_menu(command, self):
            return 1