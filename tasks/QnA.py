import streamlit as st
import chromadb
from chromadb.config import Settings
from chromadb.utils import embedding_functions
import google.generativeai as genai
import os
import uuid

# Initialize ChromaDB with persistence
PERSIST_DIRECTORY = os.path.join(os.getcwd(), "chroma_db")
chroma_client = chromadb.PersistentClient(path=PERSIST_DIRECTORY)

# Use get_or_create_collection to avoid errors if the collection already exists
collection = chroma_client.get_or_create_collection(
    name="meeting_docs",
    embedding_function=embedding_functions.SentenceTransformerEmbeddingFunction(model_name="all-MiniLM-L6-v2")
)

@st.cache_resource
def get_api_key():
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Gemini API key not found.")
        st.stop()
    return api_key

def add_meeting_transcript(meeting_id, transcript):
    try:
        collection.add(
            documents=[transcript],
            metadatas=[{"type": "transcript", "meeting_id": meeting_id}],
            ids=[f"transcript_{meeting_id}"]
        )
        return True
    except Exception as e:
        st.error(f"Error adding transcript to database: {str(e)}")
        return False

def add_document(doc_id, content):
    try:
        collection.add(
            documents=[content],
            metadatas=[{"type": "document", "doc_id": doc_id}],
            ids=[f"doc_{doc_id}"]
        )
        return True
    except Exception as e:
        st.error(f"Error adding document to database: {str(e)}")
        return False

def search_context(query, n_results=5):
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )
        return results['documents'][0]
    except Exception as e:
        st.error(f"Error searching context: {str(e)}")
        return []

@st.cache_data
def generate_answer(query, context):
    api_key = get_api_key()
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-pro')
    
    prompt = f"""
    You are an AI assistant tasked with answering questions about meetings and related documents. 
    Use the following context to answer the question. If the answer is not in the context, say "I don't have enough information to answer that question.
    Make sure you analyze the transcript and the context to answer the question"

    Context:
    {context}

    Question: {query}

    Answer:
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Error generating answer: {str(e)}")
        return "I'm sorry, but I encountered an error while trying to generate an answer."

def qna(query):
    relevant_context = search_context(query)
    if relevant_context:
        answer = generate_answer(query, "\n".join(relevant_context))
    else:
        answer = "I don't have enough information to answer that question."
    return answer

def process_uploaded_documents(uploaded_files):
    successful_uploads = 0
    for file in uploaded_files:
        content = file.getvalue().decode('utf-8')
        doc_id = str(uuid.uuid4())
        if add_document(doc_id, content):
            successful_uploads += 1
    
    if successful_uploads > 0:
        st.success(f"Successfully processed and added {successful_uploads} out of {len(uploaded_files)} documents to the knowledge base.")
    else:
        st.warning("No documents were successfully added to the knowledge base.")