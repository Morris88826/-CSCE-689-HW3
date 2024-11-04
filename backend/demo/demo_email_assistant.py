import os, re, json, time
from pydantic import BaseModel, Field
import openai
import yaml
from dotenv import load_dotenv

load_dotenv()

# check if the API key is available
if "OPENAI_API_KEY" not in os.environ:
    raise ValueError("API key for OpenAI is not available. Please set it in the environment variable.")
client = openai.Client()

private_data = None
with open("private/data.yaml", "r") as f:
    private_data = yaml.safe_load(f)

def invoke_llm(prompt:str) -> str:
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an email assistant."},
                {"role": "user", "content": prompt}
            ],
        )
        output = response.choices[0].message.content
    except Exception as e:
        output = f"Exception: {e}"
    return output

EMAIL_DB="""
NAME		EMAIL
Steve Jobs: sjobs@apple.com 
"""
def find_email(query: str) -> str:
    s = "The following lists names and email addresses of my contacts:\n"+EMAIL_DB+"\n Please return email of "+query
    response = invoke_llm(s)
    return invoke_llm(s)

def send_email_internal(to_addr: str, subject: str, body: str) -> str:
    import smtplib
    from email.mime.text import MIMEText
    from email.mime.multipart import MIMEMultipart
    

    # SMTP server configuration
    smtp_server = "smtp.gmail.com"  # This might need to be updated
    smtp_port = 587  # or 465 for SSL
    username = private_data["email"]["email"]
    password = private_data["email"]["password"]
    from_addr = username

    cc_addr = "xxx"

    # Email content

    # Setting up the MIME
    message = MIMEMultipart()
    message["From"] = from_addr
    message["To"] = to_addr
    message["Subject"] = subject
    # message["Cc"] = cc_addr  # Add CC here
    message.attach(MIMEText(body, "plain"))

    recipients = [to_addr, cc_addr]  # List of all recipients

    # Send the email
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(username, password)
            text = message.as_string()
            server.sendmail(from_addr, recipients, text)
            output = "Email successfully sent!"
    except Exception as e:
        output = f"Failed to send email: {e}"
    return output

def send_email(llm_json_str: str) -> str:
    json_regex = r"({.*})"
    match = re.search(json_regex, llm_json_str, re.DOTALL)
    if not match:
        return "Error: JSON object not found in the input string."

    try:
        patch_json_content = json.loads(match.group(1))
        to_addr = patch_json_content["to_addr"]
        subject = patch_json_content["subject"]
        body = patch_json_content["body"]
    except Exception as e:
        error_str = f"Exception: {e}"
        print("Error in parsing JSON string:", error_str)

    print(f"To: {to_addr}\n{subject}\n==============================\n{body}\n=================================\n")
    approval = input("Is the above email good to go? (yes/no): ")
    if approval.lower() == 'yes' or approval.lower() == 'y':
        # TODO: send email
        output = send_email_internal(to_addr, subject, body)
        # output = "email sent successfully"
    else:
        output = f"Email sending was not approved. Reason for disapproval: {approval}"

    return output

from string import Template
tao_template=Template("""
My name is Mu-Ruei Tseng. You are my email assistant, Monica. You have access to the following tools:
                 
    FindEmail: "Find the email addresses of my contacts. Input is the contact info such as names."
    SendEmail: "Send email tool. Input is a json object with {"to_addr: str, "subject": str, "body": str"}."

To craft an email, you should use FindEmail to find correct email addresses (to_addr) of my contacts.

Use the following format:
    
    Thought: you should always think about what to do
    Action: the action to take, should be one of [FindEmail, SendEmail]
    Action Input: the input to the action
    Observation: the result of the action
    ... (this Thought/Action/Action Input/Observation can repeat N times)
    Thought: I have now completed the task 
    Done: the final message to the task
    
Always generate Action and Action Input. Missing them will produce an error!
    
    Begin!               
    
    Question:
    $question

    Thought:
""")



MAX_ITERATION = 10
def llm_do_task(question: str):
    prompt=str(tao_template.substitute(question=question))
    iteration = 0
    while True:
        iteration =iteration+1
        if iteration>MAX_ITERATION:
            break
        llm_output = invoke_llm(prompt)
        # \s* means 0 or more spaces
        # \d* means 0 or more digits
        # .*? means non-greedy match of any character (least number of characters that satisfies the regex)
        # () is used to group the regex
        regex = (
                r"Action\s*\d*\s*:[\s]*(.*?)[\s]*Action\s*\d*\s*Input\s*\d*\s*:[\s]*(.*)"
            )
        action_match = re.search(regex, llm_output, re.DOTALL) # re.DOTALL allows . to match newline

        if action_match:
            action = action_match.group(1).strip()
            action_input = action_match.group(2)
            tool_input = action_input.strip("\n")
            if llm_output.startswith("Thought:"):
                prompt = prompt+llm_output[8:]
            else:
                prompt = prompt+llm_output
            
            print(f"------- tool: {action} input: {tool_input}\n")

            if action=="SendEmail":
                tool_output = send_email(tool_input)
                if "Email successfully sent!" in tool_output:
                    return
            elif action=="FindEmail":
                tool_output = find_email(tool_input)
            else:
                tool_output = "Error: Action "+f"'{action}' is not a valid!"

            print(f"------- tool_output ------- \n{tool_output}\n")

        elif 'Done:' in llm_output:
            print(f"\n\n{llm_output}")
            return
        else:  
            print(f"Error: wrong LLM response\n{llm_output}\n")

        prompt = prompt+"\nObservation: "+str(tool_output)+"\n"

print(f"I'm your email assistant, Monica.")
while True:
    try:
        user_input = input("Please enter a new task: ")
        tic = time.time()
        llm_do_task(user_input)
        latency = time.time() - tic
        print(f"\nLatency: {latency:.3f}s")
    except KeyboardInterrupt:
            print("\nExiting.\n")
            break