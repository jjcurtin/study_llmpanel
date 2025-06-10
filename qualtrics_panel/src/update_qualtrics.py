# update_qualtrics.py
# This script updates a Qualtrics survey by clearing existing blocks and adding new questions based on provided CSV files.
# It allows the user to choose whether to update category ratings and message ratings.

# _block_handler.py handles block management, while _question_handler.py manages question creation.

# author: Colin Maggard

import pandas as pd
import json
import requests

from _block_handler import BlockHandler
from _question_handler import QuestionHandler

class SurveyHandler:
    def __init__(self):
        choice = input(f"Update category ratings? (y/n): ")
        if choice.lower() == 'y':
            self.update_category = True
        else:
            self.update_category = False
        choice = input(f"Update message ratings? (y/n): ")
        if choice.lower() == 'y':
            self.update_message = True
        else:
            self.update_message = False

        print(f"Update category: {self.update_category}")
        print(f"Update message: {self.update_message}")

        if not self.update_category and not self.update_message:
            print("No updates selected. Exiting.")
            exit(0)
        else:
            self.run()

    def run(self):
        # Load API configuration from file
        try:
            config_df = pd.read_csv('../qualtrics.api', quotechar='"')
            api_token = config_df.loc[0, 'api_token']
            survey_id = config_df.loc[0, 'survey_id']
            datacenter = config_df.loc[0, 'datacenter']
        except Exception as e:
            print(f"Error loading config file: {e}")
            exit(1)

        self.base_url = f'https://{datacenter}.qualtrics.com/API/v3/survey-definitions/{survey_id}'

        self.headers = {
            'X-API-Token': api_token,
            'Content-Type': 'application/json'
        }

        self.question_handler = QuestionHandler(self.base_url, self.headers)
        self.block_handler = BlockHandler(self.base_url, self.headers, self.question_handler)

        print("Starting Qualtrics survey update...")

        # Load categories and messages from CSV files
        try:
            categories_df = pd.read_csv('../input/message_categories.csv', quotechar='"')
            categories_df.columns = categories_df.columns.str.strip()
        except Exception as e:
            print(f"Error loading categories file: {e}")
            exit(1)
        try:
            messages_df = pd.read_csv('../output/production_messages.csv', quotechar='"')
            messages_df.columns = messages_df.columns.str.strip()
        except Exception as e:
            print(f"Error loading messages file: {e}")
            exit(1)

        # read existing blocks from the survey
        demographic_block_id, category_block_id, context_block_ids = self.block_handler.get_block_ids()
        if not demographic_block_id:
            print("Error: Could not find demographic block ID.")
        if not category_block_id:
            print("Error: Could not find category block ID.")
        if not demographic_block_id or not category_block_id:
            exit(1)

        # update category questions
        if self.update_category:
            self.update_categories(categories_df, category_block_id)

        # update individual message questions
        if self.update_message:
            self.update_messages(messages_df, self.block_handler, context_block_ids)

        self.publish_survey()
    
    def update_categories(self, categories_df, category_block_id):
        self.block_handler.clear_block(category_block_id, "category")
        question_category_ids = []
        for _, row in categories_df.iterrows():
            category = row['message_category']
            description = row['description']
            example = row['example']
            desc_id = self.question_handler.add_category_question(category, description, example, category_block_id)
            question_category_ids.append(desc_id)
        print(f"Added {len(question_category_ids)} category questions.")

    def update_messages(self, messages_df, block_handler, context_block_ids):
        block_handler.delete_prior_message_blocks(context_block_ids)
        context_block_ids = []

        # add the description of the user context
        messages_df = messages_df.sort_values(by='user_index')
        unique_user_indices = messages_df['user_index'].unique()
        print(f"Found {len(unique_user_indices)} unique user indices.")
        for user_index in unique_user_indices:
            user_messages = messages_df[messages_df['user_index'] == user_index]
            lapse_risk = user_messages['lapse_risk'].iloc[0]
            lapse_risk_change = user_messages['lapse_risk_change'].iloc[0]
            context_description_id, message_block_id = block_handler.create_user_context_block(lapse_risk, lapse_risk_change)
            print(f"Created context block for user index {user_index} with description ID {context_description_id} and message block ID {message_block_id}")
            context_block_ids.append({"user_index": user_index, "block_id": message_block_id})

        # add individual message questions
        question_message_ids = []
        for _, row in messages_df.iterrows():
            message = row['generated_message']
            category = row['message_category']
            message_block_id = next((b['block_id'] for b in context_block_ids if b['user_index'] == row['user_index']), None)
            if not message_block_id:
                print(f"Error: No message block ID found for user index {row['user_index']}.")
                continue
            desc_id = self.question_handler.add_individual_message_question(message, category, message_block_id)
            question_message_ids.append({"user_index": row['user_index'], "category": category, "question_id": desc_id})
            print(f"Added message question for user index {row['user_index']} in category {category} with question ID {desc_id}")
        print(f"Added {len(question_message_ids)} message questions.")
        
        # Save question IDs to a JSON file for later reference 
        with open('../output/question_ids.json', 'w') as f:
            json.dump(question_message_ids, f, indent=4)
        print("Saved question IDs to question_ids.json")
    
    def publish_survey(self):
        publish_url = f"{self.base_url}/versions"
        try:
            publish_resp = requests.post(publish_url, headers=self.headers, json={
                "Description": "Auto-generated block and questions",
                "Published": True
            })
            publish_resp.raise_for_status()
            print("Survey published successfully.")
        except requests.RequestException as e:
            print(f"Error publishing survey: {e}")
            exit(1)

if __name__ == "__main__":
    SurveyHandler()