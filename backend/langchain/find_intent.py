"""
Use Case: Structured Chatbot Workflow
Imagine we are building a chatbot that: 
    1. Takes user input and determines whether the input is a question or a command.
    2. If it's a question, the chatbot answers it directly.
    3. If it's a command, the chatbot retrieves relevant information from a vector store.

Step-by-step Implementation:
    Step 1: Classify the user's input (question vs. command).
    Step 2: If it's a question, generate a response.
    Step 3: If it's a command, retrieve relevant information from a vector store.
"""

from langchain.prompts import PromptTemplate
from langchain_openai.llms import OpenAI
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from dotenv import load_dotenv

# Load environment variables
load_dotenv("../.env")
# Step 1: Initialize the LLM
llm = OpenAI(temperature=0.7)

# Step 2: Create prompt templates for each step
intent_classification_prompt = PromptTemplate(
    input_variables=["user_input"],
    template="Classify the following input as 'question' or 'command': {user_input}"
)

answer_question_prompt = PromptTemplate(
    input_variables=["question"],
    template="Answer this question as best as possible: {question}"
)

retrieve_info_prompt = PromptTemplate(
    input_variables=["command"],
    template="Based on this command, retrieve relevant information: {command}"
)

# output parser
output_parser = StrOutputParser()

# Step 3: Create runnable sequences for each step
intent_chain = RunnableSequence(intent_classification_prompt | llm | output_parser)
question_chain = RunnableSequence(answer_question_prompt | llm | output_parser)
command_chain = RunnableSequence(retrieve_info_prompt | llm | output_parser)

# Step 4: Function to handle user input using the structured flow
def handle_user_input(user_input):
    # Step 1: Classify the intent
    intent = intent_chain.invoke({"user_input": user_input})
    intent = intent.strip().lower()

    if intent == "question":
        # Step 2: Generate an answer
        response = question_chain.invoke({"question": user_input})
    elif intent == "command":
        # Step 3: Retrieve information (mocked response or connected to a vector store)
        response = command_chain.invoke({"command": user_input})
    else:
        response = "I couldn't determine the type of input. Please try again."

    return response, intent

# Example usage
user_input = "What is the capital of France?"
response, intent = handle_user_input(user_input)
print("Chatbot Response:", response)
print("Intent:", intent)

print("\n========================\n")
user_input = "Find information on machine learning trends."
response, intent = handle_user_input(user_input)
print("Chatbot Response:", response)
print("Intent:", intent)
