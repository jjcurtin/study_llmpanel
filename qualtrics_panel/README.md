# README for Qualtrics Panel Study Python Code

### Note about survey import logic for demographic and tone category surveys
Survey copying logic copies over regex but requires validation to be manually set up (takes ~20 seconds total)
Do not have any questions in the trash when running the survey import logic or they will be added as well

## root/
- Requires azure.api and qualtrics.api which contain the API keys for Azure OpenAI and Qualtrics, respectively.

## root/input/
### root/input/system_prompt/
- !prompt_architecture.png displays an abstract layout of the various prompt components.
- 1_role.txt describes the LLM's role within the context of the study.
- 2_purpose.txt describes the purpose of the messages.
- 3_format.txt describes the desired format of the messages.
- 4_restrictions.txt includes examples of things we do not want in the messages.

All four prompt.txt files are concatenated together to create the system prompt which is passed directly to the system prompt of the LLM as so:

`self.system_prompt = (`
    `f"{system_role}\n"`
    `f"{message_purpose}\n"`
    `f"{message_format}\n"`
    `f"{message_restrictions}\n"`
`)`

`messages.append({"role": "system", "content": self.system_prompt})`

### root/input/user_prompt/
- formality_prompts.csv contains various "formality" levels, with "neutral" being an empty string, "informal" indicating that the messages be written as if they are coming from a peer, and with "formal" indicating that the messages be written as if they are coming from a healthcare professional.
- message_categories.csv contains various message categories, with descriptions and examples that are displayed in the associated Qualtrics survey, and prompts that are used in the user prompts when generating the messages with the LLM.
- user_contexts.csv contains the lapse risk and lapse risk change data for a set of users.

All of the information in these files is crossed, such that messages are generated for each formality level for each message tone category for each user.

The iterations are nested as follows:
1. Temperature (if multiple temperature levels selected)
2. Formality
3. Message tone category
4. User context

## root/output/
- all_generated_messages.csv is the default output file for generated messages, and is not uploaded to the repository.
- production_messages.csv contains the messages that are used by the Qualtrics upload script. These are pushed to the repo.
- question_ids.json links each question in the Qualtrics survey to its formality level, tone category, and user context.

## root/src/
### generate_messages.py
Run with `python generate_messages.py` in the src folder. The interactive app will prompt you for several pieces of information before generating messages, including desired categories and contexts to generate messages for and various output options.

Once the messages have been generated, if the messages were written to production_messages.csv, there is an option to directly run the Qualtrics upload script without running it separately.

#### code overview
- the `__init__()` method is run when the class MessageGenerator is initialized at the bottom of the script in the `if __name__ == "__main__"` section. This calls the `initialize_settings()` and `run()` methods.
- the `initialize_settings()` method contains the logic for prompting various script configuration variables.
- the `create_system_prompt()` and `create_user_prompt()` methods create the system and user prompts using the files in their respective folders in the root/input directory. If you'd like to change the prompt, edit these files instead of the python script.
- the `azure_api_call()` method makes the actual call to Azure OpenAI
- the `generate_messages()` method contains the loop that generates a specified number of messages for a given configuration (formality level, tone category, and user context). For example, 1 message for each user, 2 messages for each user, etc.
- the `save_messages()` method writes the messages to the desired output file.
- the `run()` method contains most of the logic for crossing each of the dimensions; there are 3 nested `for` loops that iterate over each of the user contexts within each of the message categories within each of the formality levels. 

### update_qualtrics.py
Run with `python update_qualtrics.py` in the src folder. You will be prompted to update the category questions (which ask questions about each tone category) and the message questions (questions about each individual message that has been generated). The survey is updated in real time, so please wait for the script to complete running before using the survey.

### other python files (do not need to be run)
- _message_helper.py is a helper file for generate_messages.py that contains various static methods that load information from various input and output files; generally does not need to be touched unless the format of the files changes.
- _config_menu.py contains all of the logic for the configuration menu; how all of the configuration parameters are prompted and set.
- _block_handler.py is a helper file for update_qualtrics.py that handles the block management logic within the Qualtrics survey. If you want to change how the survey is laid out at the block/page level, this is the script to change.
- _question_handler.py is a helper file for update_qualtrics.py that handles the question management logic within the Qualtrics survey. If you want to change the logic for individual questions (what questions are asked, what type of question it is, etc.), this is the script to change.