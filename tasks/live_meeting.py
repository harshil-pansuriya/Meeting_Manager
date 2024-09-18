import uuid
from pathlib import Path
import streamlit as st
from aiortc.contrib.media import MediaRecorder
from streamlit_webrtc import WebRtcMode, webrtc_streamer, VideoProcessorBase

from tasks import meeting
# Set up logging
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create a directory for storing recordings
RECORD_DIR = Path("./records")
RECORD_DIR.mkdir(exist_ok=True)

def live_meeting_tracker():
    st.subheader("Discussion Points:")
    # Get discussion points from session state (assuming they're set in agenda.py)
    discussion_points = st.session_state.get("discussion_points", [])
    
    if discussion_points:
        for point in discussion_points:
            st.write(f"• {point}")
    else:
        st.write("No discussion points added.")
        
    st.subheader("Start Meeting")
    
    if "prefix" not in st.session_state:
        st.session_state["prefix"] = str(uuid.uuid4())
    prefix = st.session_state["prefix"]
    
    record_file = RECORD_DIR / f"{prefix}_meeting.mp4"
    def recorder_factory() -> MediaRecorder:
        return MediaRecorder(str(record_file), format="mp4")
    
    webrtc_ctx = webrtc_streamer(
        key="live-meeting",
        mode=WebRtcMode.SENDRECV,
        rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]},
        media_stream_constraints={
            "video": True,
            "audio": True,
        },
       
        in_recorder_factory=recorder_factory,
        async_processing=True,
    )

    # Display status
    if webrtc_ctx.state.playing:
        st.write("Recording is in progress")
    # Add controls for camera and microphone
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Camera on/off"):
            if webrtc_ctx.video_receiver:
                webrtc_ctx.video_receiver.stop() if webrtc_ctx.video_receiver.state.playing else webrtc_ctx.video_receiver.start()
    
    with col2:
        if st.button("Microphone on/off"):
            if webrtc_ctx.audio_receiver:
                webrtc_ctx.audio_receiver.stop() if webrtc_ctx.audio_receiver.state.playing else webrtc_ctx.audio_receiver.start()

    # Display recording status and provide download button
    if record_file.exists():
        
        if st.button("Process Recording"):
            try:
                with st.spinner("Processing video..."):
                    meeting.process_video(str(record_file), discussion_points)
            except Exception as e:
                st.error(f"Error processing video: {str(e)}")
            finally:
                # Optionally, clean up the recording file
                meeting.safe_delete(str(record_file))
                pass

