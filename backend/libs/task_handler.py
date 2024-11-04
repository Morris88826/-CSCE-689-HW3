import enum
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser

# Define the task types
class Task(enum.Enum):
    SEND_EMAIL = "SEND_EMAIL"
    READ_PDF = "READ_PDF"
    SCHEDULE_MEETING = "SCHEDULE_MEETING"
    SEARCH_INTERNET = "SEARCH_INTERNET"
    SEARCH_PRIVATE_DATA = "SEARCH_PRIVATE_DATA"
    NORMAL_CHAT = "NORMAL_CHAT"

# Prompt template for task classification with examples and detailed instructions
find_task_template = PromptTemplate(
    input_variables=["user_input", "tasks"],
    template=(
        "You are an intelligent assistant tasked with classifying user input into one of the following categories: {tasks}.\n"
        "Given the user input: '{user_input}', classify the task based on the context.\n"
        "Use 'SEARCH_INTERNET' only if the input requires up-to-date or detailed information from external sources.\n"
        "Use 'SEARCH_PRIVATE_DATA' if the user asks for specific private data.\n"
        "Use 'READ_PDF' if the user asks you to read or extract information from a PDF.\n"
        "Use 'NORMAL_CHAT' for simple conversational replies or common knowledge.\n"
        "Return in the format:\n"
        "Task: <task_type>\n"
        "Reason: <reason>"
    )
)

# Function to classify the task based on the user input and chat history
def classify_task(user_input, task_chain: RunnableSequence):
    tasks_str = ", ".join([f"'{task.value}'" for task in Task])
    
    # Invoke the chain with user input and history
    response = task_chain.invoke({"user_input": user_input, "tasks": tasks_str})
    # Extract task type from response
    for task in Task:
        if task.value in response:
            return task
    return Task.NORMAL_CHAT  # Default to NORMAL_CHAT if no match is found

# Function to load the task classification chain with memory support
def load_classification_chain(llm):
    output_parser = StrOutputParser()
    return RunnableSequence(find_task_template | llm | output_parser)

if __name__ == "__main__":
    load_dotenv("../.env")
    
    # Initialize the model and memory
    llm = ChatOpenAI(name="gpt-4o-mini", temperature=0, max_tokens=256)
    
    # Load the classification chain
    find_task_chain = load_classification_chain(llm)
    
    # while True:
    #     user_input = input("You: ")
    #     task = classify_task(user_input, find_task_chain, memory)
    #     print(f"Predicted Task: {task.name}")
    #     print("=====================================")

    # Example interactions with chat history
    user_inputs = [
        "How many people are in the contact list?",
        "How many contacts are in my data?",
        "What is the email address of Austin?",
        "Can you find information on recent AI trends?",
        "Can you help me send an email to John?",
        "Can you schedule a meeting for tomorrow?",
        "What is the capital of France?",
        "According to the document, what is the deadline for the project?",
        "Can you give me a summary uploaded file?",
        "What is the stock price of Tesla?",
        "Hello, how are you?",
        "What is the weather forecast for tomorrow?",
        "Can you help me find the phone number of John?",
        "I need to schedule a meeting with the team.",
        "According to the manual, what are the safety precautions?",
    ]

    answers = [
        [Task.SEARCH_PRIVATE_DATA],
        [Task.SEARCH_PRIVATE_DATA],
        [Task.SEARCH_PRIVATE_DATA],
        [Task.SEARCH_INTERNET],
        [Task.SEND_EMAIL],
        [Task.SCHEDULE_MEETING],
        [Task.NORMAL_CHAT, Task.SEARCH_INTERNET],
        [Task.READ_PDF],
        [Task.READ_PDF],
        [Task.SEARCH_INTERNET],
        [Task.NORMAL_CHAT],
        [Task.SEARCH_INTERNET],
        [Task.SEARCH_PRIVATE_DATA],
        [Task.SCHEDULE_MEETING],
        [Task.READ_PDF],
    ]

    num_correct = 0
    # Simulate conversation with history tracking
    for user_input, answer in zip(user_inputs, answers):
        # Classify task and print the response
        task = classify_task(user_input, find_task_chain)

        print(f"User Input: {user_input}")
        print(f"Predicted Task: {task.name}")
        print(f"Expected Task: {', '.join([task.name for task in answer])}")
        print("=====================================")
        
        if task in answer:
            num_correct += 1

    print(f"Accuracy: {num_correct}/{len(user_inputs)}")