import os
import shutil
from dotenv import load_dotenv
from langchain.prompts import PromptTemplate
from langchain_community.document_loaders import DirectoryLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_chroma import Chroma
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain_core.runnables import RunnableSequence
from langchain_core.output_parsers import StrOutputParser

def load_documents(data_path):
    loader = DirectoryLoader(data_path, glob="*.md")
    return loader.load()

def split_text(documents, chunk_size=1000, chunk_overlap=500, verbose=True):
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        length_function=len,
        add_start_index=True
    )
    chunks = text_splitter.split_documents(documents)
    if verbose:
        print(f"Splitting {len(documents)} documents into {len(chunks)} chunks")
    return chunks

def save_to_chroma(chunks, chroma_path, verbose=True):
    if os.path.exists(chroma_path):
        shutil.rmtree(chroma_path)

    db = Chroma.from_documents(chunks, OpenAIEmbeddings(), persist_directory=chroma_path)
    if verbose:
        print(f"Saved {len(chunks)} chunks to {chroma_path}")

def retrieve_information(query: str, db: Chroma, llm, top_k=3):
    results = db.similarity_search_with_relevance_scores(query, k=top_k)    
    if len(results) == 0 or results[0][1] < 0.7: # if the most similar document has a similarity score less than 0.7
        return None
    
    context_text = "\n\n=====\n\n".join([doc.page_content for doc, _ in results])
    sources = [doc.metadata.get("source", None) for doc, _ in results]

    # format proper responses
    response_prompt = PromptTemplate(
        input_variables=["context", "user_input"],
        template=(
            "Answer the question based on only the following context:\n"
            "{context}\n"
            "=====\n"
            "Answer the question based on the above context: {user_input}"
        )
    )
    output_parser = StrOutputParser()
    response_chain = RunnableSequence(response_prompt | llm | output_parser)
    response = response_chain.invoke({"context": context_text, "user_input": query})

    return response, sources

if __name__ == "__main__":
    data_path = "data"
    chroma_path = "chroma"
    load_dotenv("../.env")

    documents = load_documents(data_path)
    chunks = split_text(documents)
    save_to_chroma(chunks, chroma_path)

    db = Chroma(persist_directory=chroma_path, embedding_function=OpenAIEmbeddings())
    llm = ChatOpenAI(name="gpt-4o-mini", temperature=0, max_tokens=256)

    prompt = input("What do you want to know? ")
    response, sources = retrieve_information(prompt, db, llm)

    if response is not None:
        print("Response:", response)
        print("Sources:", sources)