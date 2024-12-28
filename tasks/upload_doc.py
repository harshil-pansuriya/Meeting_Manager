import streamlit as st
from io import StringIO
import PyPDF2
from docx import Document
from tasks.utils import process_text, vector_store, embeddings
import json
from pathlib import Path

@st.cache_data
def extract_text(file):
    file_type = file.name.split('.')[-1].lower()
    
    if file_type == 'pdf':
        pdf_reader = PyPDF2.PdfReader(file)
        return "\n".join(page.extract_text() for page in pdf_reader.pages)
    elif file_type == 'docx':
        doc = Document(file)
        return "\n".join(paragraph.text for paragraph in doc.paragraphs)
    elif file_type == 'txt':
        return StringIO(file.getvalue().decode("utf-8")).read()
        
    raise ValueError(f"Unsupported file type: {file_type}")

def save_discussion_points(points):
    points_file = Path("./data/discussion_points.json")
    points_file.parent.mkdir(parents=True, exist_ok=True)
    
    existing_points = []
    if points_file.exists():
        with open(points_file, 'r') as f:
            existing_points = json.load(f)
    
    all_points = list(set(existing_points + points))
    
    with open(points_file, 'w') as f:
        json.dump(all_points, f, indent=2)

def upload_documents():
    st.header("Document Upload")
    
    if st.button("Clear Database"):
        vector_store.delete(where={})
        st.success("✅ Database cleared")
        st.rerun()
    
    uploaded_files = st.file_uploader(
        "Upload Documents (PDF, DOCX, TXT)",
        accept_multiple_files=True,
        type=["pdf", "docx", "txt"]
    )
    discussion_points = st.text_area(
        "Enter discussion points (one per line)",
        height=150,
        placeholder="1. \n2.\n..."
    )
    
    if st.button("Process Documents and Points"):
        if not uploaded_files and not discussion_points.strip():
            st.warning("Please upload documents or add discussion points.")
            return
        
        with st.spinner("Processing..."):
            # Process documents
            processed_files = []
            for file in uploaded_files:
                text = extract_text(file)
                chunks, chunk_embeddings = process_text(text)
                vector_store.add(
                    embeddings=chunk_embeddings,
                    documents=chunks,
                    ids=[f"doc_{file.name}_{i}" for i in range(len(chunks))]
                )
                processed_files.append(file.name)
            if processed_files:
                st.success(f"✅ Processed: {', '.join(processed_files)}")
                st.write("**Uploaded Files:** ")
                for file in uploaded_files:
                    st.write(f"- {file.name}")
        
            if discussion_points.strip():
                points = [p.strip() for p in discussion_points.splitlines() if p.strip()]
                
                save_discussion_points(points)

                for i, point in enumerate(points):
                    point_embedding = embeddings.embed_documents([point])
                    vector_store.add(
                        embeddings=[point_embedding[0]],
                        documents=[point],
                        ids=[f"point_{i}"]
                    )
                st.success("✅ Discussion points processed")
                st.write("**Discussion Points:**")
                for point in points:
                    st.write(f"- {point}")