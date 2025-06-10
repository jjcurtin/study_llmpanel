# question_handler.py
# handles question creation for a Qualtrics survey.

# author: Colin Maggard

import requests

class QuestionHandler:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def add_category_question(self, message_category, message_description, message_example, block_id):
        # --- Likert Scale Question ---
        try:
            desc_resp = requests.post(
                f"{self.base_url}/questions", 
                headers=self.headers, 
                params={"blockId": block_id},
                json={
                    "QuestionText": f'<strong>{message_category}</strong><br><br>{message_description}<br><br>Example: {message_example}',
                    "QuestionType": "Matrix",
                    "Selector": "Likert",
                    "SubSelector": "SingleAnswer",
                    "Configuration": {
                        "QuestionDescriptionOption": "UseText"
                    },
                    "Choices": {
                        "1": {"Display": "I would like to receive messages from this tone category."},
                        "2": {"Display": "I would find messages from this tone category to be helpful."}
                    },
                    "Answers": {
                        "1": {"Display": "Strongly Disagree"},
                        "2": {"Display": "Disagree"},
                        "3": {"Display": "Somewhat Disagree"},
                        "4": {"Display": "Neutral"},
                        "5": {"Display": "Somewhat Agree"},
                        "6": {"Display": "Agree"},
                        "7": {"Display": "Strongly Disagree"}
                    },
                    "Validation": {
                        "Settings": {
                            "ForceResponse": "ON"
                        }
                    },
                    "DataExportTag": f" "
                }
            )
            desc_resp.raise_for_status()
            desc_id = desc_resp.json()['result']['QuestionID']
            # print(f"Created dimensional assessment for category {category}")
        except requests.RequestException as e:
            print(f"Error creating dimensional assessment for category: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for dimensional assessment question: {e}")
            print("Response:", desc_resp.json())
            exit(1)

        return desc_id
    
    def add_user_context_description_question(self, lapse_risk, lapse_risk_change, description_block_id):
        # add the description question
        try:
            desc_resp = requests.post(
                f"{self.base_url}/questions", 
                headers=self.headers, 
                params={"blockId": description_block_id},
                json={
                    "QuestionText": f'Imagine you are a recovering alcoholic with a {lapse_risk} lapse risk that has been {lapse_risk_change} over the last week.<br><br>The following page contains messages that are tailored to this user\'s context. Please read the messages and provide feedback on their helpfulness and whether you like them or not.',
                    "QuestionType": "DB",
                    "Selector": "TB",
                    "DataExportTag": f" "
                }
            )
            desc_resp.raise_for_status()
            description_id = desc_resp.json()['result']['QuestionID']
            # print(f"Created user context description question with ID: {description_id}")
        except requests.RequestException as e:
            print(f"Error creating user context description question for {lapse_risk} {lapse_risk_change}: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for user context description question: {e}")
            print("Response:", desc_resp.json())
            exit(1)

    def add_individual_message_question(self, message, category, block_id):
        # --- Likert Scale Question ---
        try:
            desc_resp = requests.post(
                f"{self.base_url}/questions", 
                headers=self.headers, 
                params={"blockId": block_id},
                json={
                    "QuestionText": f'"{message}"',
                    "QuestionType": "Matrix",
                    "Selector": "Likert",
                    "SubSelector": "SingleAnswer",
                    "Configuration": {
                        "QuestionDescriptionOption": "UseText"
                    },
                    "Choices": {
                        "1": {"Display": "I liked this message."},
                        "2": {"Display": "I found this message to be helpful."}
                    },
                    "Answers": {
                        "1": {"Display": "Strongly Disagree"},
                        "2": {"Display": "Disagree"},
                        "3": {"Display": "Somewhat Disagree"},
                        "4": {"Display": "Neutral"},
                        "5": {"Display": "Somewhat Agree"},
                        "6": {"Display": "Agree"},
                        "7": {"Display": "Strongly Disagree"}
                    },
                    "Validation": {
                        "Settings": {
                            "ForceResponse": "ON"
                        }
                    },
                    "DataExportTag": f" "
                }
            )
            desc_resp.raise_for_status()
            desc_id = desc_resp.json()['result']['QuestionID']
            # print(f"Created dimensional assessment for message: {desc_id} in category {category}")
        except requests.RequestException as e:
            print(f"Error creating dimensional assessment for message: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for dimensional assessment question: {e}")
            print("Response:", desc_resp.json())
            exit(1)
        
        return desc_id