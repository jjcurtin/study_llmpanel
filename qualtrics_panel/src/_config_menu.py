import os, numpy as np
from _message_helper import load_message_categories, load_user_contexts, load_formality_prompts, load_existing_messages

def clear():
    os.system('cls' if os.name == 'nt' else 'clear')

@staticmethod
def select_message_categories():
    tones_to_generate = []
    tones, descriptions = load_message_categories()
    category_to_description = dict(zip(tones, descriptions))
    clear()
    while True:
        invalid = False
        print("Available message categories:")
        for i, tone in enumerate(tones):
            print(f"{i + 1}: {tone}")
        selected_tones = input("Enter the numbers of the message categories you want to generate messages for, separated by commas (ENTER is all): ")
        if selected_tones.strip() == '':
            tones_to_generate = tones
        else:
            selected_indices = [int(x.strip()) - 1 for x in selected_tones.split(',') if x.strip().isdigit()]
            selected_indices = list(set(selected_indices))
            for index in selected_indices:
                if index < 0 or index >= len(tones):
                    clear()
                    print(f"Invalid message category number: {index + 1}. Please try again.")
                    invalid = True
                    break
            if invalid:
                continue
            tones_to_generate = [tones[i] for i in selected_indices if 0 <= i < len(tones)]
            if not tones_to_generate:
                clear()
                print("No valid message categories selected. Please try again.")
                continue
        break
    return tones_to_generate, category_to_description

@staticmethod
def select_user_contexts():
    users_to_generate = []
    user_contexts_df = load_user_contexts()
    if user_contexts_df.empty:
        print("No user contexts available. Please ensure the user_contexts.csv file is populated.")
        exit(1)
    clear()
    while True:
        invalid = False
        print("Available user contexts:")
        for user_index, user_row in user_contexts_df.iterrows():
            user_context = {k: str(v).strip() for k, v in user_row.items()}
            print(f"{user_index + 1}: {user_context.get('lapse_risk', 'N/A')} - {user_context.get('lapse_risk_change', 'N/A')}")
        selected_users = input("Enter the numbers of the user contexts you want to generate messages for, separated by commas (ENTER is all): ")
        if selected_users.strip() == '':
            users_to_generate = list(user_contexts_df.index)
        else:
            selected_indices = [int(x.strip()) - 1 for x in selected_users.split(',') if x.strip().isdigit()]
            selected_indices = list(set(selected_indices))
            for index in selected_indices:
                if index < 0 or index >= len(user_contexts_df):
                    clear()
                    print(f"Invalid user context number: {index + 1}. Please try again.")
                    invalid = True
                    break
            if invalid:
                continue
            users_to_generate = [i for i in selected_indices if 0 <= i < len(user_contexts_df)]
            if not users_to_generate:
                clear()
                print("No valid user contexts selected. Please try again.")
                continue
        break
    return users_to_generate, user_contexts_df

@staticmethod
def select_formality_levels():
    formality_labels, formality_prompts = load_formality_prompts()
    clear()
    while True:
        invalid = False
        print("Available formality levels:")
        for i, label in enumerate(formality_labels):
            print(f"{i + 1}: {label}")
        formalities_to_generate = []
        selected_formalities = input("Enter the numbers of the formality levels you want to generate messages for, separated by commas (ENTER is all): ")
        if selected_formalities.strip() == '':
            formalities_to_generate = formality_labels
        else:
            selected_indices = [int(x.strip()) - 1 for x in selected_formalities.split(',') if x.strip().isdigit()]
            selected_indices = list(set(selected_indices))
            for index in selected_indices:
                if index < 0 or index >= len(formality_labels):
                    clear()
                    print(f"Invalid formality level number: {index + 1}. Please try again.")
                    invalid = True
                    break
            if invalid:
                continue
            formalities_to_generate = [formality_labels[i] for i in selected_indices if 0 <= i < len(formality_labels)]
            if not formalities_to_generate:
                clear()
                print("No valid formality levels selected. Please try again.")
                continue
        formality_to_prompt = dict(zip(formality_labels, formality_prompts))
        break
    return formalities_to_generate, formality_to_prompt

@staticmethod
def select_num_messages():
    clear()
    while True:
        num_messages = input("Enter the number of messages to generate for each category per user context (ENTER is 1): ")
        if num_messages.strip() == '':
            num_messages = 1
        elif not num_messages.isdigit():
            clear()
            print("Invalid input. Please enter a positive integer.")
            continue
        num_messages = int(num_messages)
        if num_messages < 1:
            clear()
            print("Number of messages must be at least 1. Please try again.")
            continue
        elif num_messages > 10:
            print("WARNING: Generating more than 10 messages per user.")
        break
    return num_messages

@staticmethod
def select_temperature():
    clear()
    while True:
        temperature = input("Enter the temperature for message generation (ENTER is 0, maximum is 1, \"cross\" for cross over interval): ")
        if temperature.lower() == 'cross':
            while True:
                min_temp = input("Enter the minimum temperature for the cross over interval (default is 0): ")
                min_temp = float(min_temp) if min_temp else 0.0
                if min_temp < 0:
                    clear()
                    print("Minimum temperature must be at least 0. Try again.")
                    continue
                elif min_temp > 2:
                    clear()
                    print("Minimum temperature is too high. Try again.")
                    continue
                max_temp = input("Enter the maximum temperature for the cross over interval (ENTER is 1): ")
                max_temp = float(max_temp) if max_temp else 1.0
                if max_temp < 0:
                    clear()
                    print("Maximum temperature must be at least 0. Try again.")
                    continue
                elif max_temp > 2:
                    clear()
                    print("Maximum temperature is too high. Try again.")
                    continue
                elif max_temp <= min_temp:
                    clear()
                    print("Maximum temperature must be greater than minimum temperature. Try again.")
                    continue
                resolution = input("Enter the difference between temperature values in the cross over interval (ENTER is 0.25): ")
                resolution = float(resolution) if resolution else 0.25
                if resolution <= 0:
                    clear()
                    print("Resolution must be greater than 0. Try again.")
                    continue
                elif resolution > max_temp - min_temp:
                    clear()
                    print("Resolution is too high. Try again.")
                    continue
                temperature_values = [round(x, 2) for x in list(np.arange(min_temp, max_temp + resolution, resolution))]
                print(f"Temperature values for cross over interval: {temperature_values}")
                break
            break
        else:
            temperature = float(temperature) if temperature else 0.0
            if temperature < 0:
                clear()
                print("Temperature must be at least 0. Try again.")
                continue
            elif temperature > 1:
                clear()
                print("Temperature is too high. Try again.")
                continue
            temperature_values = [temperature]
            break
    return temperature_values

@staticmethod
def select_output_file():
    clear()
    while True:
        output_file_choice = input("Which output path would you like? ENTER/1 for default 2 for production (what is uploaded to qualtrics): ")
        if output_file_choice == '1' or output_file_choice == '':
            output_file = "../output/all_generated_messages.csv"
        elif output_file_choice == '2':
            output_file = "../output/production_messages.csv"
        else:
            clear()
            print("Invalid choice, please try again.")
            continue
        break

    current_messages = load_existing_messages(output_file)
    if not current_messages.empty:
        clear()
        while True:
            choice = input("Output file already exists. Do you want to append to it (ENTER or a) or overwrite it (o)?: ")
            if choice.lower() == 'o':
                print("Existing messages will be overwritten.")
                write_mode = 'w'
            elif choice.lower() == 'a' or choice == '':
                print("New messages will be appended to existing messages.")
                write_mode = 'a'
            else:
                clear()
                print("Invalid choice, please try again.")
                continue
            break
    else:
        print("No existing messages found. New messages will be written to the file.")
        write_mode = 'w'
    return output_file, write_mode

@staticmethod
def set_printing_options():
    clear()
    while True:
        print_to_terminal = input("Would you like to print the generated messages to the terminal? (ENTER for yes, n for no): ")
        if print_to_terminal.lower() == '':
            print_to_terminal = True
        elif print_to_terminal.lower() == 'n':
            print_to_terminal = False
        else:
            clear()
            print("Invalid choice, please try again.")
            continue
        break

    clear()
    while True:
        print_prompt = input("Would you like to print the system and user prompts to the terminal? (ENTER for yes, n for no): ")
        if print_prompt.lower() == '':
            print_prompt = True
        elif print_prompt.lower() == 'n':
            print_prompt = False
        else:
            clear()
            print("Invalid choice, please try again.")
            continue
        break

    return print_to_terminal, print_prompt

@staticmethod
def set_additional_info():
    clear()
    additional_info = input("Add any additional information here (hit ENTER to skip): ").strip()
    if additional_info == '':
        additional_info = None
    return additional_info

@staticmethod
def set_recent_feedback_mode():
    clear()
    while True:
        recent_mode = input("Would you like to feed the most recent message back into the prompt to reduce repetition? (ENTER or y for yes/n for no): ")
        if recent_mode.lower() == '' or recent_mode.lower() == 'y':
            return True
        elif recent_mode.lower() == 'n':
            return False
        else:
            clear()
            print("Invalid choice. Please enter 'y' or 'n'.")
            continue