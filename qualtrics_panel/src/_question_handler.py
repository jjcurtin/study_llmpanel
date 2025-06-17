# question_handler.py
# handles question creation for a Qualtrics survey.

# author: Colin Maggard

import requests

class QuestionHandler:
    def __init__(self, base_url, headers):
        self.base_url = base_url
        self.headers = headers

    def add_likert_scale_question(self, question_text, block_id, questions):
        # --- Likert Scale Question ---
        Choices = {str(i+1): {"Display": choice} for i, choice in enumerate(questions)}
        try:
            desc_resp = requests.post(
                f"{self.base_url}/questions", 
                headers=self.headers, 
                params={"blockId": block_id},
                json={
                    "QuestionText": question_text,
                    "QuestionType": "Matrix",
                    "Selector": "Likert",
                    "SubSelector": "SingleAnswer",
                    "Configuration": {
                        "QuestionDescriptionOption": "UseText"
                    },
                    "Choices": Choices,
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
            # print(f"Created Likert scale question with ID: {desc_id}")
        except requests.RequestException as e:
            print(f"Error creating Likert scale question: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for Likert scale question: {e}")
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