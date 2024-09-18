  # Meeting Management Tool

## Overview

The Meeting Management Tool is a comprehensive solution for organizing, conducting, and analyzing meetings. It provides features for document upload, agenda creation, live meeting tracking, video processing, and a context-aware Q&A system.

## Features

- Document upload and processing
- Discussion points and agenda generation
- Live meeting tracking and recording
- Video processing and transcription
- Context-aware Q&A system

## Architecture and System Flow

The tool is built using Streamlit and consists of several interconnected components:

1. **Document Upload (upload_doc.py)**: 
   - Allows users to upload relevant documents before the meeting.
   - Processes and stores document content in a ChromaDB database for later retrieval.

2. **Agenda Creation (agenda.py)**:
   - Enables users to input discussion points.
   - Generates a structured agenda using the Gemini AI model.

3. **Live Meeting Tracker (live_meeting.py)**:
   - Provides a web interface for conducting live meetings.
   - Records audio and video of the meeting.
   - Provide Covered and not Covered topics in meeting.

4. **Meeting Recording Processing (meeting.py)**:
   - Handles uploaded or recorded meeting videos.
   - Converts video to audio, transcribes the audio, and generates meeting insights using Generativ AI.
   - Stores the transcript in the ChromaDB vector database.
   - Provide Covered and not Covered topics in meeting.

5. **Q&A System (QnA.py)**:
   - Utilizes ChromaDB for efficient storage and retrieval of meeting-related information.
   - User can ask questions related to the meeting.
   - Employs the Gemini AI model to generate context-aware answers to user queries.

6. **Main Application (app.py)**:
   - Integrates all components into a unified Streamlit interface.
   - Manages the flow between different stages of the meeting process.

## Setup Instructions

1. Clone the repository:
   ```
   git clone https://github.com/your-username/Meeting_Manager.git
   cd Meeting_Manager
   ```

2. Create a virtual environment and activate it:
   ```
   python -m venv env
   source venv/bin/activate  # On Windows, use `env\Scripts\activate`
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Set up environment variables:
   - Create a `.env` file in the project root.
   - Add your Gemini API key:
     ```
     GEMINI_API_KEY=your_api_key_here
     ```

5. Run the Streamlit app:
   ```
   streamlit run app.py
   ```

## Usage Guidelines

1. **Document Upload**: Start by uploading relevant documents for the meeting.
2. **Agenda Creation**: Input discussion points and generate a structured agenda.
3. **Live Meeting**: Use the live meeting tracker to conduct and record your meeting.
4. **Video Processing**: Upload a recorded video or process the live recording for insights.
5. **Q&A**: Use the context-aware Q&A system to ask questions about the meeting or related documents.

## Dependencies

- streamlit
- chromadb
- google-generativeai
- whisper
- moviepy
- sentence-transformers
- aiortc
- streamlit-webrtc

For a complete list of dependencies, refer to the `requirements.txt` file.

## Note

Ensure you have the necessary API keys and permissions set up for the Gemini AI model and any other external services used in the project.
