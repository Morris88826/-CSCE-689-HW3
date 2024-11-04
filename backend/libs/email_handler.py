import os
import re
import time
import base64
import pandas as pd
from requests import HTTPError
from dotenv import load_dotenv
from email.mime.text import MIMEText
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from langchain_openai import ChatOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
try:
    from libs.helper import extract_json_from_text
    from libs.private_data_handler import search_private_data, get_db, load_search_private_data_chain
except:
    from helper import extract_json_from_text
    from private_data_handler import search_private_data, get_db, load_search_private_data_chain

extract_email_template = PromptTemplate(
    input_variables=["user_input"],
    template=(
        "You are an AI that can extract information from text.\n"
        "Given the user input: {user_input}, extract the following information\n"
        "You MUST return in the following JSON format or else there will be an error:\n"
        "json: {{\n"
        "  \"receiver\": \"<value or NONE>\",\n"
        "  \"subject\": \"<value or NONE>\",\n"
        "  \"body\": \"<value or NONE>\"\n"
        "}}\n"
        "Ensure that your response adheres strictly to this format.\n"
    )
)

construct_email_template = PromptTemplate(
    input_variables=["receiver", "subject", "body"],
    template=(
        "You are an AI assistant tasked with constructing a formal email on my behalf.\n"
        "Using the following details: \n"
        "- Receiver: {receiver}\n"
        "- Subject: {subject}\n"
        "- Body: {body}\n"
        "Compose a FORMAL and professional email based on this information.\n"
        "Ensure the email is concise, polite, and structured appropriately.\n"
        "You MUST return in the following format or else there will be an error:\n"
        "----------------------------------------"
        "Subject: <title of the email>\n"
        "----------------------------------------"
        "Message: <the email message>\n"
        "----------------------------------------"
        "Comments: <any additional comments>\n"
    )
)

def load_email_extraction_chain(llm):
    output_parser = StrOutputParser()
    return RunnableSequence(extract_email_template | llm | output_parser)

def load_email_constructor_chain(llm):
    output_parser = StrOutputParser()
    return RunnableSequence(construct_email_template | llm | output_parser)

def extract_email_info(user_input, chain: RunnableSequence, max_iter=10, email_constructor_chain=None):
    json_data = None
    i = 0
    while json_data is None and i < max_iter:
        response = chain.invoke({"user_input": user_input})
        json_data = extract_json_from_text(response)
        i += 1

    if json_data is None:
        json_data = {
            "receiver": None,
            "subject": None,
            "body": None
        }

    # Parse the information
    email = verify_email(json_data["receiver"])
    if not email:
        # also check if the email is in the private data
        if "NONE" not in json_data["receiver"]:
            json_data["receiver"] = json_data["receiver"]
        else:
            json_data["receiver"] = None
        json_data["email"] = None
    else:
        json_data["email"] = json_data["receiver"]
    json_data["subject"] = None if "NONE" in json_data["subject"] else json_data["subject"]
    json_data["body"] = None if "NONE" in json_data["body"] else json_data["body"]

    if email_constructor_chain is not None and (json_data["subject"] is not None or json_data["body"] is not None):
        updated_response = email_constructor_chain.invoke({
            "receiver": json_data["receiver"],
            "subject": json_data["subject"],
            "body": json_data["body"]
        })

        try:
            json_data["subject"] = updated_response.split("----------------------------------------")[1].replace("Subject:", "").strip()
            json_data["body"] = updated_response.split("----------------------------------------")[2].replace("Message:", "").strip()
        except:
            print("Error parsing email constructor response")

    return json_data

def verify_email(message):
    # check if the message is an email
    email_regex = r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+"
    email_match = re.search(email_regex, message)
    if email_match:
        return True
    return False

def find_email(json_data, search_private_data_chain, db) -> str:
    response = search_private_data(f"Can you search for the email of {json_data['receiver']}? You MUST return in the following format: \nEmail: (NONE if not found)", search_private_data_chain, db)
    if "NONE" not in response:
        regex = "Email: (.*)"
        email_match = re.search(regex, response)
        if email_match:
            json_data['email'] = email_match.group(1)
        else:
            json_data['email'] = None
    else:
        json_data['email'] = None
    return json_data

def send_email(to_addr: str, subject: str, body: str):
    SCOPES = [
        "https://www.googleapis.com/auth/gmail.send"
    ]
    flow = InstalledAppFlow.from_client_secrets_file('./private/credentials.json', SCOPES)
    creds = flow.run_local_server(port=0)
    service = build('gmail', 'v1', credentials=creds)
    message = MIMEText(body)
    message['to'] = to_addr
    message['subject'] = subject
    create_message = {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}
    try:
        message = (service.users().messages().send(userId="me", body=create_message).execute())
        print(F'sent message to {message} Message Id: {message["id"]}')
    except HTTPError as error:
        print(F'An error occurred: {error}')
        message = None


if __name__ == "__main__":
    load_dotenv("../.env")
    llm = OllamaLLM(model="llama3.2")
    email_extraction_chain = load_email_extraction_chain(llm)
    search_private_data_chain = load_search_private_data_chain(llm)

    response = extract_email_info("Can you help me send an email to morris88826@gmail.com?", email_extraction_chain)

    if response["receiver"] is not None and response['email'] is None:
        db = get_db()
        response = find_email(response, search_private_data_chain, db)
    print(response)

    # send_email("morris88826@gmail.com", "Hello", "Hello, this is a test email")
    # api_key = os.getenv("OPENAI_API_KEY")
    # llm = LLM(api_key)

    # while True:
    #     try:
    #         # user_input = input("Please enter a new task: ")
    #         user_input = "can you help me send an email?"
    #         tic = time.time()
    #         print(llm.invoke_global_llm(user_input))
    #         raise NotImplementedError("Please implement the email assistant.")
    #         latency = time.time() - tic
    #         print(f"\nLatency: {latency:.3f}s")
    #     except KeyboardInterrupt:
    #             print("\nExiting.\n")
    #             break
