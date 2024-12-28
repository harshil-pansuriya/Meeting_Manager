import streamlit as st
from tasks.utils import get_agenda_chain
import json
from pathlib import Path

def get_discussion_points() -> list:
    points_file = Path("./data/discussion_points.json")
    if not points_file.exists():
        return []
    
    with open(points_file, 'r') as f:
        return json.load(f)

def create_agenda(): 
    st.title("Meeting Agenda Generator")
    
    points = get_discussion_points()
    
    if not points:
        st.warning("No discussion points found. Please add some first.")
        st.info("Go to 'Upload Documents & Points' tab to add discussion points.")
        return
    
    st.write("### Current Discussion Points:")
    for point in points:
        st.write(f"- {point}")
    
    st.subheader("Time Allocation")
    total_time = st.number_input(
        "Total meeting duration (minutes)",
        min_value=15,
        max_value=240,
        value=60,
        step=15
    )
    
    if st.button("Generate Agenda"):
        with st.spinner("Generating agenda..."):
            # Calculate time per point
            avg_time = total_time // len(points)
            formatted_points = "\n".join(
                f"- ({avg_time} mins) {point}" 
                for point in points
            )
            
            # Generate agenda with all points
            agenda_chain = get_agenda_chain()
            agenda = agenda_chain.run(points=formatted_points)
            
            st.subheader("Generated Agenda")
            st.markdown(agenda)
            
            st.download_button(
                "Download Agenda",
                agenda,
                "meeting_agenda.md",
                "text/markdown"
            )