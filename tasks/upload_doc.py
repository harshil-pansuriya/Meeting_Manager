import streamlit as st
from tasks import QnA
import uuid

# -------------------- Pre-Meeting Document Upload -------------------- #
def upload_documents():
    """
    Allows users to upload relevant documents for the meeting.
    Displays the names of uploaded files.
    """
    st.header("Pre-Meeting Document Upload")
    global uploaded_files
    uploaded_files = []
    uploaded_files = st.file_uploader("Upload relevant documents", accept_multiple_files=True, type=["pdf", "docx", "txt"])
    
    if uploaded_files:
        st.write("Documents uploaded:")
        for idx, file in enumerate(uploaded_files, start=1):
            st.write(f"{idx}. {file.name}")
            