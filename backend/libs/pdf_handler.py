import ollama
import chromadb
from chromadb.config import Settings
from chromadb.config import DEFAULT_TENANT, DEFAULT_DATABASE, Settings
from langchain_community.document_loaders import PyPDFDirectoryLoader  # Importing PDF loader from Langchain
from langchain.text_splitter import RecursiveCharacterTextSplitter  # Importing text splitter from Langchain
from langchain.schema import Document  # Importing Document schema from Langchain
from langchain.prompts import PromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser

client = chromadb.PersistentClient(
    path="./private/chromadb",
    settings=Settings(),
    tenant=DEFAULT_TENANT,
    database=DEFAULT_DATABASE,
)

def reload_chromadb(name="docs"):
    try:
        client.delete_collection(name)
    except Exception as e:
        pass

def load_documents(DATA_PATH="./private/docs"):
    """
    Load PDF documents from the specified directory using PyPDFDirectoryLoader.

    Returns:
        List of Document objects: Loaded PDF documents represented as Langchain Document objects.
    """
    document_loader = PyPDFDirectoryLoader(DATA_PATH)  # Initialize PDF loader with specified directory
    return document_loader.load()  # Load PDF documents and return them as a list of Document objects

def split_text(documents: list[Document]):
    """
    Split the text content of the given list of Document objects into smaller chunks.

    Args:
        documents (list[Document]): List of Document objects containing text content to split.

    Returns:
        list[Document]: List of Document objects representing the split text chunks.
    """
    # Initialize text splitter with specified parameters
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,  # Size of each chunk in characters
        chunk_overlap=100,  # Overlap between consecutive chunks
        length_function=len,  # Function to compute the length of the text
        add_start_index=True,  # Flag to add start index to each chunk
    )
    # Split documents into smaller chunks using text splitter
    chunks = text_splitter.split_documents(documents)
    print(f"Split {len(documents)} documents into {len(chunks)} chunks.")

    # Print example of page content and metadata for a chunk
    document = chunks[10]
    print(document.page_content)
    print(document.metadata)

    return chunks  # Return the list of split text chunks

def read_documents(reload=True, collection_name="docs"):
    # clear the collection
    try:
        collection = client.get_collection(name=collection_name)
        if not reload:
            return collection
        client.delete_collection(collection_name)
    except Exception as e:
        if not reload:
            return None
    
    # create a new collection
    collection = client.create_collection(name=collection_name)

    documents = load_documents()  # Load documents from a source
    chunks = split_text(documents)  # Split documents into manageable chunks

    # store each document in a vector embedding database
    for i, chunk in enumerate(chunks):
        d = chunk.page_content
        response = ollama.embeddings(model="llama3.2", prompt=d)
        embedding = response["embedding"]
        # print(f"embedding: {embedding}")
        collection.add(
            ids=[str(i)],
            embeddings=[embedding],
            documents=[d]
        )
    return collection


search_pdf_template = PromptTemplate(
    input_variables=["user_input", "information"],
    template=(
        "You are an AI assistant.\n"
        "Given the user input: {user_input}, provide a response that includes relevant information according to the information {information}.\n"
    )
)

def load_search_pdf_chain(llm):
    output_parser = StrOutputParser()
    return RunnableSequence(search_pdf_template | llm | output_parser)

def search_documents(user_input, chain: RunnableSequence, n_results=5):
    collection = read_documents(reload=False)
    # check if the collection is empty
    if collection is None:
        return "The document collection is empty."
    
    embedding = ollama.embeddings(prompt=user_input, model="llama3.2")["embedding"]
    # Query the document collection for relevant documents
    results = collection.query(query_embeddings=[embedding], n_results=n_results)

    # Extract and combine the top 5 documents
    documents = results['documents'][0]
    combined_data = "\n\n".join(documents[:n_results])  # Join top 5 results into one string

    # Generate response based on combined data and original prompt
    response = chain.invoke({"user_input": user_input, "information": combined_data})

    return response