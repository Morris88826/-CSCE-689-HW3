import os
import sqlite3
import base64
import datetime
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask, request, jsonify, g
from langchain.memory import ConversationBufferMemory
from langchain.prompts import PromptTemplate
from langchain_ollama.llms import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser
from libs.task_handler import classify_task, load_classification_chain, Task
from libs.email_handler import send_email, find_email, load_email_extraction_chain, extract_email_info
from libs.pdf_handler import read_documents, search_documents, reload_chromadb, load_search_pdf_chain
from libs.schedule_meeting_handler import schedule_meeting, authenticate_google_calendar
from libs.search_internet_handler import search_internet, load_search_internet_agent
from libs.private_data_handler import search_private_data, load_search_private_data_chain

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Set the upload folder path
UPLOAD_FOLDER = './private/docs'
DATABASE = './private/app_data.db'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


# Initialize the LLMs
local_llm = OllamaLLM(model="llama3.2")
global_llm = ChatOpenAI(name="gpt-4o-mini", temperature=0, max_tokens=256)

# Initialize ConversationBufferMemory with a limited context size
chat_memory = ConversationBufferMemory(k=5)

# Set up the classification chain
classification_chain = load_classification_chain(global_llm)
email_extraction_chain = load_email_extraction_chain(local_llm)
search_pdf_chain = load_search_pdf_chain(local_llm)
search_internet_agent = load_search_internet_agent(global_llm)
search_private_data_chain = load_search_private_data_chain(local_llm)


response_prompt_template = PromptTemplate(
    input_variables=["input"],
    template=(
        "You are an AI assistant.\n"
        "Given the user input: {input}, provide a response.\n"
    )
)
conversation_chain = RunnableSequence(response_prompt_template | global_llm | StrOutputParser())

# Function to get a database connection
def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
    return db
# Close the database connection after each request
@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

# Initialize the database schema
def init_db():
    with app.app_context():
        db = get_db()
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

# Run the database initialization when the script is run
init_db()

# API endpoint for interacting with the structured agent
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    user_input = data.get("input")

    if not user_input:
        return jsonify({"error": "Input is required"}), 400

    try:
        # Classify the task using the LLM
        task = classify_task(user_input, classification_chain)
        print(f"Task: {task.name}")
        response = None
        if task == Task.SEND_EMAIL:
            json_data = extract_email_info(user_input, email_extraction_chain)
            if json_data["receiver"] is not None and json_data['email'] is None:
                find_email(json_data, search_private_data_chain, get_db())
            response = json_data
        elif task == Task.READ_PDF:
            response = search_documents(user_input, search_pdf_chain)
        elif task == Task.SEARCH_INTERNET:
            response = search_internet(user_input, search_internet_agent)
        elif task == Task.SEARCH_PRIVATE_DATA:
            response = search_private_data(user_input, search_private_data_chain, get_db())
        elif task == Task.NORMAL_CHAT:
            response = conversation_chain.invoke({"input": user_input})
        
        return jsonify({
            "task": task.name,
            "response": response
        }), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/send_email', methods=['POST'])
def send_email_task():
    data = request.json
    if not data or 'to' not in data or 'subject' not in data or 'body' not in data:
        return jsonify({"error": "Invalid data provided"}), 400

    to_addr = data['to']
    subject = data['subject']
    body = data['body']

    send_email(to_addr, subject, body)
    return jsonify({"message": "Email sent successfully"}), 200

@app.route('/upload_pdf', methods=['POST'])
def upload_pdf():
    data = request.json
    if not data or 'file' not in data:
        return jsonify({"error": "No file data provided"}), 400

    file_data = data['file']
    file_name = data.get('fileName', 'uploaded.pdf')

    file_path = os.path.join(app.config['UPLOAD_FOLDER'], file_name)

    try:
        with open(file_path, "wb") as file:
            file.write(base64.b64decode(file_data))
        # Read the documents and store them in the database
        collection = read_documents(reload=True, collection_name="docs")
        
        documents = collection.get()["documents"]
        # Prepare data to feed into the LLM
        combined_text = "\n\n".join(documents)
        response = conversation_chain.invoke({"input": f"Read the document and summarize the content. {combined_text}"})

        return jsonify({"message": "PDF uploaded successfully", "path": file_path, "response": response}), 200
    except Exception as e:
        print(f"Error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/schedule_meeting', methods=['POST'])
def schedule_meeting_task():
    try:
        # Extract data from the POST request
        data = request.json
        summary = data.get('summary')
        location = data.get('location', '')
        description = data.get('description', '')
        start_time = data.get('start_time')
        end_time = data.get('end_time')

        if not all([summary, start_time, end_time]):
            return jsonify({'error': 'Missing required fields: summary, start_time, and end_time'}), 400

        # Convert start_time and end_time to datetime objects
        start_time = datetime.datetime.fromisoformat(start_time)
        end_time = datetime.datetime.fromisoformat(end_time)

        # Get the Google Calendar service
        service = authenticate_google_calendar()

        # Create the event
        event = schedule_meeting(service, summary, location, description, start_time, end_time)

        return jsonify({
            'message': 'Meeting scheduled successfully',
            'event_link': event
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/clear_history', methods=['POST'])
def clear_history():
    # Clear files from the upload folder
    for file in os.listdir(app.config['UPLOAD_FOLDER']):
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], file)
        os.remove(file_path)

    # Clear the conversation memory
    chat_memory.clear()

   # Clear the ChromaDB
    try:
        reload_chromadb()
        print("ChromaDB cleared successfully.")
    except Exception as e:
        print(f"Error clearing ChromaDB: {e}")
        return jsonify({"error": f"Error clearing ChromaDB: {str(e)}"}), 500
    return jsonify({"message": "All documents and conversation history cleared"}), 200

@app.route('/get_personal_info', methods=['GET'])
def get_personal_info():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT * FROM personal_info ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    if result:
        personal_info = {
            'id': result[0],
            'firstName': result[1],
            'lastName': result[2],
            'phone': result[3],
            'birthday': result[4],
            'email': result[5]
        }
        return jsonify({'personalInfo': personal_info}), 200
    else:
        return jsonify({'personalInfo': None}), 404

@app.route('/update_personal_info', methods=['POST'])
def update_personal_info():
    data = request.json
    first_name = data.get('firstName')
    last_name = data.get('lastName')
    phone = data.get('phone')
    birthday = data.get('birthday')
    email = data.get('email')

    db = get_db()
    cursor = db.cursor()
    # check if the information already exists
    cursor.execute('SELECT * FROM personal_info ORDER BY id DESC LIMIT 1')
    result = cursor.fetchone()
    if result:
        cursor.execute('''
            UPDATE personal_info
            SET first_name = ?,
                last_name = ?,
                phone = ?,
                birthday = ?,
                email = ?
            WHERE id = ?
        ''', (first_name, last_name, phone, birthday, email, result[0]))
        db.commit()
        return jsonify({'message': 'Personal information updated successfully'}), 200
    else:
        # insert the new information
        cursor.execute('''
            INSERT INTO personal_info (first_name, last_name, phone, birthday, email)
            VALUES (?, ?, ?, ?, ?)
        ''', (first_name, last_name, phone, birthday, email))
        db.commit()
        return jsonify({'message': 'Personal information added successfully'}), 201

@app.route('/get_contacts', methods=['GET'])
def get_contacts():
    db = get_db()
    cursor = db.cursor()
    cursor.execute('SELECT id, name, email, phone FROM contacts')
    contacts = [{'id': row[0], 'name': row[1], 'email': row[2], 'phone': row[3]} for row in cursor.fetchall()]
    return jsonify({'contacts': contacts}), 200

@app.route('/add_contact', methods=['POST'])
def add_contact():
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')
    
    db = get_db()
    cursor = db.cursor()
    cursor.execute(
        'INSERT INTO contacts (name, email, phone) VALUES (?, ?, ?)',
        (name, email, phone)
    )
    db.commit()
    contact_id = cursor.lastrowid  # Get the ID of the newly added contact
    new_contact = {
        'id': contact_id,
        'name': name,
        'email': email,
        'phone': phone
    }
    return jsonify(new_contact), 201

@app.route('/delete_contact/<int:contact_id>', methods=['DELETE'])
def delete_contact(contact_id):
    db = get_db()
    cursor = db.cursor()
    cursor.execute('DELETE FROM contacts WHERE id = ?', (contact_id,))
    db.commit()
    if cursor.rowcount == 0:
        return jsonify({'message': 'No contact found with the given ID'}), 404
    return jsonify({'message': 'Contact deleted successfully'}), 200

@app.route('/update_contact/<int:contact_id>', methods=['PUT'])
def update_contact(contact_id):
    data = request.json
    name = data.get('name')
    email = data.get('email')
    phone = data.get('phone')

    db = get_db()
    cursor = db.cursor()
    cursor.execute('UPDATE contacts SET name = ?, email = ?, phone = ? WHERE id = ?', (name, email, phone, contact_id))
    db.commit()
    return jsonify({'message': 'Contact updated successfully'}), 200


if __name__ == '__main__':
    app.run(debug=True)
