import streamlit as st
import whisper
from moviepy.editor import VideoFileClip
import uuid
import os
from tasks.utils import get_meeting_summary_chain, process_text, vector_store, embeddings
from pathlib import Path
import json
import numpy as np
from typing import Dict, List, Tuple

def initialize_whisper():
    return whisper.load_model("base")

whisper_model = initialize_whisper()

def get_discussion_points() -> list:
    points_file = Path("./data/discussion_points.json")
    if not points_file.exists():
        return []
    with open(points_file, 'r') as f:
        return json.load(f)

def analyze_discussion_coverage(transcript: str) -> Dict[str, bool]:
    discussion_points = get_discussion_points()
    if not discussion_points:
        return {}
    
    # Get embeddings for transcript chunks
    transcript_chunks, _ = process_text(transcript)
    transcript_embeddings = embeddings.embed_documents(transcript_chunks)
    
    point_embeddings = embeddings.embed_documents(discussion_points)
    
    coverage = {}
    similarity_threshold = 0.6  # Adjust this threshold as needed
    
    # Compare each discussion point with transcript chunks
    for point, point_embedding in zip(discussion_points, point_embeddings):
        # Calculate similarities with all transcript chunks
        similarities = [
            np.dot(point_embedding, chunk_embedding)
            for chunk_embedding in transcript_embeddings
        ]
        coverage[point] = max(similarities) > similarity_threshold
    
    return coverage

def process_video_file(video_file):
    temp_video_dir = Path("./data/temp/video")
    temp_audio_dir = Path("./data/temp/audio")
    temp_video_dir.mkdir(parents=True, exist_ok=True)
    temp_audio_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate file paths
    temp_video_path = str(temp_video_dir / f"{uuid.uuid4()}.mp4")
    temp_audio_path = str(temp_audio_dir / f"{uuid.uuid4()}.mp3")
    
    # Save uploaded video
    with open(temp_video_path, 'wb') as f:
        f.write(video_file.getvalue())
    
    # Process video
    video = VideoFileClip(temp_video_path)
    video.audio.write_audiofile(temp_audio_path)
    video.close()
    
    return temp_video_path, temp_audio_path

def transcribe_and_process(audio_path):
    result = whisper_model.transcribe(audio_path)
    transcript = result["text"]
    chunks, embeddings = process_text(transcript)
    
    vector_store.add(
        embeddings=embeddings,
        documents=chunks,
        ids=[f"transcript_{uuid.uuid4()}_{i}" for i in range(len(chunks))]
    )
    return transcript

def track_meeting():
    st.header("Meeting Recording Processor")
    
    uploaded_file = st.file_uploader(
        "Upload meeting recording",
        type=["mp4", "avi", "mov", "mkv"]
    )
    if uploaded_file and st.button("Process Recording"):
        with st.spinner("Processing meeting recording..."):
            video_path, audio_path = process_video_file(uploaded_file)
            
            transcript = transcribe_and_process(audio_path)
            
            st.subheader("Meeting Transcript")
            st.write(transcript)
            
            st.subheader("Meeting Summary")
            summary_chain = get_meeting_summary_chain()
            summary = summary_chain.run(transcript=transcript)
            st.markdown(summary)
            
            st.subheader("Discussion Points Coverage")
            coverage = analyze_discussion_coverage(transcript)
            
            if coverage:
                st.write("Analysis of planned discussion points:")
                
                st.write("✅ **Discussed Points:**")
                discussed = [point for point, covered in coverage.items() if covered]
                if discussed:
                    for point in discussed:
                        st.write(f"- {point}")
                else:
                    st.write("- None of the planned points were discussed.")
                    
                st.write("❌ **Points Not Discussed:**")
                not_discussed = [point for point, covered in coverage.items() if not covered]
                if not_discussed:
                    for point in not_discussed:
                        st.write(f"- {point}")
                else:
                    st.write("- All planned points were discussed!")
            else:
                st.info("No discussion points were set for this meeting.")
            
            st.download_button(
                "Download Transcript",
                transcript,
                "meeting_transcript.txt",
                "text/plain"
            )
            st.download_button(
                "Download Summary",
                summary,
                "meeting_summary.md",
                "text/markdown"
            )
            
            try:
                os.remove(video_path)
                os.remove(audio_path)
            except:
                pass