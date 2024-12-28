# Meeting Management Tool

## Overview

The Meeting Management Tool is a comprehensive solution for organizing, documenting, and analyzing meetings. It provides features for document management, agenda creation, video recording analysis, and a context-aware Q&A system.

## Features

- **Document Management**

  - Upload and process multiple document types (PDF, DOCX, TXT)
  - Automatic text extraction and vectorization
  - Discussion points management

- **Intelligent Agenda Generation**

  - AI-powered agenda creation from discussion points
  - Automatic time allocation
  - Downloadable formatted agenda

- **Meeting Recording Analysis**

  - Video file processing (MP4, AVI, MOV, MKV)
  - Automatic transcription using Whisper AI
  - Meeting summary generation
  - Analysis of covered vs. uncovered discussion points
  - Downloadable transcripts and summaries

- **Context-Aware Q&A System**
  - Search across all meeting content
  - AI-powered answers based on meeting context
  - Source context visibility

## Architecture

The tool is built using Streamlit and consists of several key components:

1. **Document Upload (upload_doc.py)**

   - Handles multiple document formats
   - Processes discussion points
   - Stores content in ChromaDB for retrieval

2. **Agenda Creation (agenda.py)**

   - Manages discussion points
   - Generates structured agendas using Gemini AI
   - Provides time allocation features

3. **Meeting Analysis (meeting.py)**

   - Processes uploaded meeting recordings
   - Performs audio transcription using Whisper
   - Generates meeting insights using Gemini AI
   - Analyzes discussion point coverage

4. **Q&A System (QnA.py)**
   - Leverages ChromaDB for efficient information retrieval
   - Provides context-aware answers using Gemini AI
   - Shows source context for transparency

## Setup Instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/your-username/Meeting_Manager.git
   cd Meeting_Manager
   ```

2. Create and activate virtual environment:

   ```bash
   python -m venv env
   source env/bin/activate  # On Windows: env\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Configure environment:

   - Create `.env` file in project root
   - Add Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

5. Launch application:
   ```bash
   streamlit run app.py
   ```

## Usage Flow

1. **Document Preparation**

   - Upload relevant documents
   - Add discussion points
   - Process materials for context

2. **Agenda Creation**

   - Set meeting duration
   - Generate AI-powered agenda
   - Download formatted agenda

3. **Meeting Analysis**

   - Upload meeting recording
   - Get transcription and summary
   - Review discussion coverage
   - Download meeting artifacts

4. **Knowledge Query**
   - Ask questions about meeting content
   - Get AI-powered answers with context
   - View source information

## Core Dependencies

- streamlit
- chromadb
- google-generativeai
- whisper
- moviepy
- langchain
- sentence-transformers
- PyPDF2
- python-docx

For complete dependencies, see `requirements.txt`.

## Note

Ensure you have:

- Sufficient disk space for document and video processing
- Valid Gemini API key
- Python 3.8+ installed
