import os
from langchain_community.embeddings import HuggingFaceEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_core.prompts import ChatPromptTemplate
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.chains import LLMChain
import chromadb
from dotenv import load_dotenv

chunk_size = 200
chunk_overlap = 50
embedding_model = "sentence-transformers/all-MiniLM-L6-v2"

def initialize_llm():
    load_dotenv()
    api_key = os.getenv("GEMINI_API_KEY")
    return ChatGoogleGenerativeAI(
        model="gemini-pro",
        google_api_key=api_key,
        temperature=0.7,
        convert_system_message_to_human=True
    )

def initialize_chroma():
    persist_dir = "./data/chroma"
    os.makedirs(persist_dir, exist_ok=True)
    
    client = chromadb.PersistentClient(
        path=persist_dir,
        settings=chromadb.Settings(
            anonymized_telemetry=False,
            allow_reset=True
        )
    )
    client.reset()
    collection = client.get_or_create_collection( name="meeting_content",metadata={"hnsw:space": "cosine"})
    
    return collection

def initialize_text_processing():
    embeddings = HuggingFaceEmbeddings(model_name=embedding_model,model_kwargs={'device': 'cpu'})
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=chunk_size,chunk_overlap=chunk_overlap)
    return embeddings, text_splitter

# Initialize components
llm = initialize_llm()
embeddings, text_splitter = initialize_text_processing()
vector_store = initialize_chroma()

# Prompts
meeting_summary_prompt = """Analyze the following meeting transcript and provide:
1. Brief summary (max 150 words)
2. Key decisions made
3. Action items and next steps
4. Main topics discussed

Transcript: {transcript}
"""

agenda_prompt = """You are good AI to generate meeting agenda. Create a professional meeting agenda with details:
1. Agenda Items (with time allocations):
{points}
2. Notes Section

Format it professionally with clear time estimates.
"""

qna_prompt = """Based on the provided context, answer the following question:

Context: {context}
Question: {question}

Answer: """

def create_llm_chain(template: str):
    prompt = ChatPromptTemplate.from_template(template)
    return LLMChain(llm=llm, prompt=prompt)

def process_text(text):
    chunks = text_splitter.split_text(text)
    chunk_embeddings = embeddings.embed_documents(chunks)
    return chunks, chunk_embeddings

def get_meeting_summary_chain():
    return create_llm_chain(meeting_summary_prompt)

def get_agenda_chain():
    return create_llm_chain(agenda_prompt)

def get_qa_chain():
    return create_llm_chain(qna_prompt)