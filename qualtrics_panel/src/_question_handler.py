# question_handler.py
# handles question creation for a Qualtrics survey.

# author: Colin Maggard

import requests

class QuestionHandler:
    def __init__(self, base_url, headers, demographic_survey_url, category_survey_url):
        self.base_url = base_url
        self.headers = headers
        self.demographic_survey_url = demographic_survey_url
        self.category_survey_url = category_survey_url

    def add_likert_scale_question(self, question_text, block_id, questions):
        # --- Likert Scale Question ---
        Choices = {str(i+1): {"Display": choice} for i, choice in enumerate(questions)}
        try:
            # https://api.qualtrics.com/5d41105e8d3b7-create-question
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
                        "7": {"Display": "Strongly Agree"}
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
                    "QuestionText": f'For the following messages, imagine that you have a {lapse_risk} risk of drinking that day and that your daily risk for drinking has been {lapse_risk_change} over the past two weeks. Please rate how helpful you would find each support message in this scenario.',
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

    def add_existing_question(self, question, block_id):
        try:
            question_resp = requests.post(
                f"{self.base_url}/questions",
                headers=self.headers,
                params={"blockId": block_id},
                json=question
            )
            question_resp.raise_for_status()
            question_id = question_resp.json()['result']['QuestionID']
            # print(f"Added existing question with ID: {question_id}")
            return question_id
        except requests.RequestException as e:
            print(f"Error adding existing question: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for existing question: {e}")
            print("Response:", question_resp.json())
            exit(1)

    def get_demographic_questions(self):
        try:
            resp = requests.get(self.demographic_survey_url, headers=self.headers)
            resp.raise_for_status()
            
            demographic_questions = resp.json()['result']['Questions']
            parsed_questions = []
            for question_id, question_data in demographic_questions.items():
                parsed_questions.append({
                    "QuestionID": question_id,
                    **question_data
                })
            print(f"Found {len(parsed_questions)} demographic questions.")
            return parsed_questions
        except requests.RequestException as e:
            print(f"Error fetching demographic questions: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for demographic questions: {e}")
            print("Response:", resp.json())
            exit(1)
        except Exception as e:
            print(f"Unexpected error fetching demographic questions: {e}")
            exit(1)

    def get_tone_category_questions(self):
        try:
            resp = requests.get(self.category_survey_url, headers=self.headers)
            resp.raise_for_status()
            
            category_questions = resp.json()['result']['Questions']
            parsed_questions = []
            for question_id, question_data in category_questions.items():
                parsed_questions.append({
                    "QuestionID": question_id,
                    **question_data
                })
            print(f"Found {len(parsed_questions)} category questions.")
            return parsed_questions
        except requests.RequestException as e:
            print(f"Error fetching category questions: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for category questions: {e}")
            print("Response:", resp.json())
            exit(1)
        except Exception as e:
            print(f"Unexpected error fetching category questions: {e}")
            exit(1)