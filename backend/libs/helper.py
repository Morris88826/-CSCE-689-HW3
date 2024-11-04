import re
import json

def extract_json_from_text(text):
    """
    Extracts JSON content from a given text and parses it into a Python dictionary.

    Parameters:
    text (str): The input text containing JSON.

    Returns:
    dict: The parsed JSON as a dictionary if found, otherwise None.
    """
    # Use regex to extract JSON-like content from the text
    json_match = re.search(r"json:\s*({.*})", text, re.DOTALL)

    if json_match:
        json_str = json_match.group(1)
        try:
            # Parse the JSON string to a Python dictionary
            extracted_info = json.loads(json_str)
            return extracted_info
        except json.JSONDecodeError as e:
            print("Error decoding JSON:", e)
            return None
    else:
        print("No JSON found in the text content.")
        return None