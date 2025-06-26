# _block_handler.py
# Handles block management for a Qualtrics survey

# author: Colin Maggard

import requests

class BlockHandler:
    def __init__(self, base_url, headers, question_handler):
        self.base_url = base_url
        self.headers = headers
        self.question_handler = question_handler

    def get_block_ids(self):
        demographic_block_id = None
        category_block_id = None
        context_block_ids = []
        other_block_ids = []

        try:
            survey_info_resp = requests.get(self.base_url, headers=self.headers)
            survey_info_resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching survey info: {e}")
            exit(1)
        survey_info_json = survey_info_resp.json()
        if 'result' not in survey_info_json:
            print("Error: No result found in survey info response.")
            exit(1)
        blocks = survey_info_json.get('result', {}).get('Blocks', {})
        for block_id, block_data in blocks.items():
            block_description = block_data.get('Description')
            if (block_description == None):
                print("No description found.")
            elif (block_description == "demographic"):
                demographic_block_id = block_id
                #print(f"Demographic Block ID: {block_id}")
            elif (block_description == "category"):
                category_block_id = block_id
                #print(f"Category Block ID: {block_id}")
            elif (block_description.startswith("context_description_")):
                context_block_ids.append(block_id)
                # print(f"Context Description Block ID: {block_id}")
            elif (block_description.startswith("context_messages_")):
                context_block_ids.append(block_id)
                # print(f"Context Messages Block ID: {block_id}")
            elif (block_description.startswith("Trash")):
                pass # Skip trash blocks
            else:
                other_block_ids.append(block_id)
                #print(f"Other Block ID found: {block_id}")
        if (not demographic_block_id):
            print("Error: Could not find demographic block ID.")
            exit(1)
        elif (not category_block_id):
            print("Error: Could not find category block ID.")
            exit(1)
        elif (len(other_block_ids) > 0):
            print(f"Warning: Found {len(other_block_ids)} other blocks that are not 'demographic' or 'category'. These will not be cleared.")

        print(f"Found {len(context_block_ids)} previous message blocks.")

        return demographic_block_id, category_block_id, context_block_ids

    def clear_block(self, block_id, name):
        print(f"Clearing {name} block...")
        block_url = f"{self.base_url}/blocks/{block_id}"
        try:
            block_resp = requests.get(block_url, headers=self.headers)
            block_resp.raise_for_status()
        except requests.RequestException as e:
            print(f"Error fetching block info: {e}")
            exit(1)
        except Exception as e:
            print(f"Unexpected error: {e}")
            exit(1)
        
        block_json = block_resp.json()
        if 'result' not in block_json:
            print("Error: No result found in block info response.")
            exit(1)

        elements = block_json.get('result', {}).get('BlockElements', [])
        for element in elements:
            element_id = element.get('QuestionID')
            if not element_id:
                print("No QuestionID found for element.")
                exit(1)
            delete_url = f"{self.base_url}/questions/{element_id}"
            try:
                delete_resp = requests.delete(delete_url, headers=self.headers)
                delete_resp.raise_for_status()
                # print(f"Deleted question {element_id} successfully.")
            except requests.RequestException as e:
                print(f"Error deleting question {element_id}: {e}")
                exit(1)

        print(f"Cleared {name} block successfully, deleting {len(elements)} {name} questions.")

    def delete_prior_message_blocks(self, context_block_ids):
        print("Deleting prior message blocks...")
        for block_id in context_block_ids:
            delete_url = f"{self.base_url}/blocks/{block_id}"
            try:
                delete_resp = requests.delete(delete_url, headers=self.headers)
                delete_resp.raise_for_status()
                # print(f"Deleted block {block_id} successfully.")
            except requests.RequestException as e:
                print(f"Error deleting block {block_id}: {e}")
                exit(1)
        print("Prior message blocks deleted successfully.")

    def create_user_context_block(self, lapse_risk, lapse_risk_change):
        # create the block with the description
        try:
            block_resp = requests.post(
                f"{self.base_url}/blocks", 
                headers=self.headers, 
                json={
                    "Description": f"context_description_{lapse_risk}_{lapse_risk_change}",
                    "BlockElements": []
                }
            )
            block_resp.raise_for_status()
            description_block_id = block_resp.json()['result']['BlockID']
            # print(f"Created user context block with ID: {description_block_id}")
        except requests.RequestException as e:
            print(f"Error creating user context block for {lapse_risk} {lapse_risk_change}: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for user context block: {e}")
            print("Response:", block_resp.json())
            exit(1)

        self.question_handler.add_user_context_description_question(lapse_risk, lapse_risk_change, description_block_id)
    
        # create the block with the message questions
        try:
            block_resp = requests.post(
                f"{self.base_url}/blocks", 
                headers=self.headers, 
                json={
                    "Description": f"context_messages_{lapse_risk}_{lapse_risk_change}",
                    "BlockElements": []
                    # , # add options for randomization, can also be used as a PUT request after messages are added to block
                    # "Options": {
                    #    "RandomizeQuestions": "Advanced",
                    #    "Randomization": {
                    #        "Advanced": {
                    #            "QuestionsPerPage": "5",
                    #            "RandomSubset": [],
                    #            "TotalRandSubset": "5"
                    #        },
                    #        "EvenPresentation": "true",
                    #    }
                    # }
                    # https://api.qualtrics.com/2d5286cc34ed6-create-block
                }
            )
            block_resp.raise_for_status()
            message_block_id = block_resp.json()['result']['BlockID']
            # print(f"Created user context message block with ID: {message_block_id}")
        except requests.RequestException as e:
            print(f"Error creating user context message block for {lapse_risk} {lapse_risk_change}: {e}")
            exit(1)
        except KeyError as e:
            print(f"Error parsing response for user context message block: {e}")
            print("Response:", block_resp.json())
            exit(1)
        
        return description_block_id, message_block_id