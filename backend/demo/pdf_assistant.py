import os
import fitz  # PyMuPDF
import requests
from dotenv import load_dotenv
from libs.llm import LLM


# Function to read text from a PDF file
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf:
        for page_num in range(len(pdf)):
            page = pdf[page_num]
            text += page.get_text("text")  # Extract text from each page
    return text

# Function to send text to Ollama API
def send_text_to_ollama(text, api_url="http://localhost:11434/api/generate", model="llama3.2"):
    headers = {
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "prompt": "Help me read this document and summarize it. Here is the text:\n" + text,
        "stream": False,
    }
    response = requests.post(api_url, json=data, headers=headers)
    if response.status_code == 200:
        return response.json()['response']
    else:
        raise Exception(f"Error: {response.status_code}, {response.text}")


if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    llm = LLM(api_key)

    pdf_path = "./private/docs/resume.pdf"
    pdf_text = extract_text_from_pdf(pdf_path)  # Extract text from PDF

    response = llm.invoke_local_llm("Help me read this document and summarize it. Here is the text:\n" + pdf_text)
    print(response)
