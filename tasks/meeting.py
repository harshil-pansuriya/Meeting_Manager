import streamlit as st
from streamlit_webrtc import webrtc_streamer, WebRtcMode, VideoProcessorBase
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
from sentence_transformers import SentenceTransformer,util
import os
import tempfile
import whisper
from moviepy.editor import VideoFileClip
import logging
import google.generativeai as genai
import contextlib
from tasks import QnA
st.set_page_config(layout="wide")
import uuid
# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize Whisper and Transformers models once (to avoid repeated loading)
whisper_model = whisper.load_model("base")
tokenizer = AutoTokenizer.from_pretrained("facebook/bart-base")
model=genai.GenerativeModel("gemini-pro")

def get_api_key():
    """
    Attempt to get the OpenAI API key from various sources.
    """
    # Try to get the API key from an environment variable
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        api_key = st.secrets.get("GEMINI_API_KEY")
    
    if not api_key:
        st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable or add it to your Streamlit secrets.")
        st.stop()
    
    return api_key


@contextlib.contextmanager
def temporary_file(suffix=None):
    """Context manager for creating and cleaning up a temporary file."""
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
    try:
        yield temp_file.name
    finally:
        try:
            os.unlink(temp_file.name)
        except OSError:
            pass

def safe_delete(filepath):
    """Safely delete a file if it exists."""
    try:
        if os.path.exists(filepath):
            os.remove(filepath)
            logger.info(f"Successfully deleted: {filepath}")
    except Exception as e:
        logger.error(f"Error deleting file {filepath}: {str(e)}")

        
        
def convert_video_to_audio(video_path, audio_path):
    try:
        video = VideoFileClip(video_path)
        if video.audio is None:
            logger.warning("The video does not contain an audio track.")
            return None
        video.audio.write_audiofile(audio_path, codec='mp3')
        return audio_path
    except Exception as e:
        logger.error(f"Error converting video to audio: {str(e)}")
        return None

def transcribe_audio(audio_path):
    try:
        result = whisper_model.transcribe(audio_path)
        transcribed_text= result.get("text", "")
        return transcribed_text
    
    except Exception as e:
        logger.error(f"Error transcribing audio: {str(e)}")
        return None

# Add this function to compare discussion points with transcription
def compare_discussion_points(discussion_points, transcription):
    # Initialize the sentence transformer model
    model = SentenceTransformer('all-MiniLM-L6-v2')
    
    # Encode the transcription and discussion points
    transcription_embedding = model.encode(transcription, convert_to_tensor=True)
    points_embeddings = model.encode(discussion_points, convert_to_tensor=True)
    
    # Calculate cosine similarity
    similarities = util.pytorch_cos_sim(transcription_embedding, points_embeddings)[0]
    
    # Classify points as covered or not covered
    threshold = 0.6  # Adjust this threshold as needed
    covered = []
    not_covered = []
    
    for i, point in enumerate(discussion_points):
        if similarities[i] > threshold:
            covered.append(point)
        else:
            not_covered.append(point)
    
    return covered, not_covered


def process_video(video_path, discussion_points=None):
    if not os.path.exists(video_path):
        st.error(f"Video file not found: {video_path}")
        return

    temp_files = []
    try:
        with st.spinner("Converting video to audio..."):
            audio_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3").name
            temp_files.append(audio_file)
            audio_file = convert_video_to_audio(video_path, audio_file)
        
        if audio_file is None:
            st.error("Failed to extract audio. The video might not contain an audio track.")
            return

        st.success("Video converted to audio.")
        
        with st.spinner("Transcribing audio..."):
            transcription = transcribe_audio(audio_file)
        
        if transcription is None:
            st.error("Failed to transcribe the audio.")
            return
        
        st.write("Transcription:", transcription)
        
        # Add the transcript to ChromaDB
        meeting_id = str(uuid.uuid4())  # Generate a unique ID for the meeting
        QnA.add_meeting_transcript(meeting_id, transcription)
        st.success("Meeting transcript added to the knowledge base.") 
                
        with st.spinner("Generating insights from the meeting..."):
            insights = generate_meeting_insights(transcription,discussion_points)

        if insights:
            st.subheader("Meeting Insights")
            st.markdown(insights)
        else:
            st.error("Failed to generate meeting insights.")
    
    finally:
        for file in temp_files:
            safe_delete(file)

# Generate meeting insights using OpenAI GPT
def generate_meeting_insights(transcription_text,discussion_points):
    prompts = {
        "Summary:": 
            "Please provide a concise summary of the following transcript. The summary should capture the main points and key takeaways from the meeting in no more than 150 words. Focus on summarizing the overall discussion, decisions made, and any significant insights or conclusions.",
        "Key Decisions:": 
            "Extract and list all key decisions made during the meeting from the following transcript. A key decision is one that impacts the direction of the project or organization, involves agreement or disagreement among participants, or sets a course of action. List each decision clearly with a brief explanation if necessary.",
        "Topics Discussed:": 
            "Outline the main topics discussed during the meeting from the following transcript. Provide a structured overview of the conversation by identifying the major subjects covered. List these topics in a clear and organized manner, highlighting any important subtopics or points related to each main topic.",
        "Action Items:": 
            "Extract all action items, tasks, or next steps mentioned in the meeting transcript. An action item is a specific task assigned to an individual or group, with a clear goal and deadline. List each action item, including who is responsible for it and any deadlines mentioned."
    }
        
    insights = []
    
    try:
        api_key = get_api_key()
        genai.configure(api_key=api_key)
        
        # Use a more capable model like gemini-pro
        model = genai.GenerativeModel('gemini-pro')
        
        for analysis_type, prompt in prompts.items():
            try:
                # Generate the content using your model
                response = model.generate_content(f"{prompt}\n\nTranscript:\n{transcription_text}")
                # Append formatted insights with bold and large text for headers
                insights.append(f"### **{analysis_type.replace('_', ' ')}**\n\n{response.text}\n")
            except Exception as e:
                # Handle errors and append them
                insights.append(f"### **{analysis_type.replace('_', ' ')}**\n\nError: {str(e)}\n")
        

         # Add discussion points analysis
        if discussion_points:
            covered, not_covered = compare_discussion_points(discussion_points, transcription_text)
            insights.append("**## Discussion Points Coverage**\n")
            insights.append("### Covered Topics:\n")
            for point in covered:
                insights.append(f"✅ {point}\n")
            insights.append("\n### Not Covered Topics:\n")
            for point in not_covered:
                insights.append(f"❌ {point}\n")
    
    except Exception as e:
        logger.error(f"An error occurred while generating meeting insights: {str(e)}")
        return None
    
    return "\n".join(insights)
    

def track_meeting():
    st.header("Upload Video")
    uploaded_file = st.file_uploader("Choose a video file", type=['mp4', 'avi', 'mov', 'mkv'])
    
    # Add input for discussion points
    discussion_points = st.session_state.get("discussion_points", [])
    if discussion_points:
        st.subheader("Discussion Points")
        for point in discussion_points:
            st.write(f"• {point}")
            
    if uploaded_file is not None:
        temp_video = tempfile.NamedTemporaryFile(delete=False, suffix='.mp4').name
        try:
            with open(temp_video, 'wb') as f:
                f.write(uploaded_file.read())
            st.video(temp_video)
                
            if st.button("Process Uploaded Video"):
                process_video(temp_video,discussion_points)
        finally:
            safe_delete(temp_video)


                
            


        
