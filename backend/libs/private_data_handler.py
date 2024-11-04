
import sqlite3
from langchain_openai import ChatOpenAI
from langchain_ollama.llms import OllamaLLM
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser

search_private_data_template = PromptTemplate(
    input_variables=["user_input", "database"],
    template=(
        "You are an AI that can extract information from the dataset.\n"
        "Given the user input: {user_input}, return the information that matches the query.\n"
        "Data: {database}\n"
        "You MUST return in the tone of a helpful assistant."
    )
)

def get_db(database_path):
    db = sqlite3.connect(database_path)
    return db

def init_db(database_path):
    db = get_db(database_path)
    cursor = db.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS personal_info (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            first_name TEXT,
            last_name TEXT,
            phone TEXT,
            birthday TEXT,
            email TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            email TEXT,
            phone TEXT
        )
    ''')
    db.commit()
    return db

def get_personal_info(db): 
    cursor = db.cursor()
    cursor.execute('SELECT * FROM personal_info')
    
    # Get column names from the cursor description
    columns = [desc[0] for desc in cursor.description]
    
    # Convert each row to a dictionary using column names as keys
    results = cursor.fetchall()
    personal_info_list = [dict(zip(columns, row)) for row in results]
    
    return personal_info_list  # Already in JSON-compatible format

def get_contacts(db):
    cursor = db.cursor()
    cursor.execute('SELECT * FROM contacts')
    
    # Get column names from the cursor description
    columns = [desc[0] for desc in cursor.description]
    
    # Convert each row to a dictionary using column names as keys
    results = cursor.fetchall()
    contacts_list = [dict(zip(columns, row)) for row in results]
    
    return contacts_list

def search_private_data(query, private_data_chain, db):
    personal_info_results = get_personal_info(db)
    contacts_results = get_contacts(db)

    database_str = f"Personal Info: {personal_info_results}\nContacts: {contacts_results}"
    response = private_data_chain.invoke({
        "user_input": query,
        "database": database_str
    })

    return response

def load_search_private_data_chain(llm):
    output_parser = StrOutputParser()
    return RunnableSequence(search_private_data_template | llm | output_parser)

if __name__ == "__main__":
    database_path = "../private/app_data.db"
    db = init_db(database_path)

    personal_info = get_personal_info(db)
    contacts = get_contacts(db)
    
    llm = OllamaLLM(model="llama3.2")
    # user_input = "search for the email of Austin"
    user_input = "how many contacts do I have?"
    private_data_chain = load_search_private_data_chain(llm)
    response = search_private_data(user_input, private_data_chain, db)

    print(response)
    
