# consolidate_prompt.py
# used to save a copy of the current system prompt to the archive folder

import os
from datetime import datetime

# Ensure the script is executed from the correct directory
expected_folder = r"qualtrics_panel\input\system_prompt"
current_folder = os.getcwd()
if not current_folder.endswith(expected_folder):
    print(f"Please run this script from the '{expected_folder}' folder. Current folder: {current_folder}")
    exit(1)

input_files = [
    "1_role.txt",
    "2_purpose.txt",
    "3_format.txt",
    "4_restrictions.txt"
]
archive_folder = "archive"

os.makedirs(archive_folder, exist_ok=True)
today_date = datetime.now().strftime("%Y-%m-%d")
output_file = os.path.join(archive_folder, f"{today_date}_system_prompt.txt")
counter = 1
base_output_file = output_file

# make sure we save a new copy for any day that has more than one prompt
while os.path.exists(output_file):
    output_file = os.path.join(archive_folder, f"{today_date}_system_prompt_{counter}.txt")
    counter += 1

# consolidate prompt
consolidated_content = ""
for file in input_files:
    if os.path.exists(file):
        with open(file, "r", encoding="utf-8") as f:
            consolidated_content += f.read() + "\n\n"
    else:
        print(f"Warning: {file} does not exist and will be skipped.")
with open(output_file, "w", encoding="utf-8") as f:
    f.write(consolidated_content.strip())
print(f"System prompt saved to {output_file}.")