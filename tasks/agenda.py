import streamlit as st

import google.generativeai as genai
import os
# -------------------- Add Discussion Points -------------------- #


def discussion_points_and_generate_agenda():
    """
    Manages the addition of discussion points and generation of the agenda.
    """
    st.header("Discussion Points and Agenda Manager")

    with st.form("agenda_form"):
        discussion_points_input = st.text_area("Enter discussion points (one per line):")
        col1, col2 = st.columns(2)
        with col1:
            add_points = st.form_submit_button("Add Points")
        with col2:
            generate_agenda = st.form_submit_button("Generate Agenda")

    discussion_points = [point.strip() for point in discussion_points_input.split("\n") if point.strip()]

    if add_points:
        if discussion_points:
            st.success(f"Added {len(discussion_points)} discussion points")
            # Store discussion points in session state
            st.session_state["discussion_points"] = discussion_points
        else:
            st.error("Please enter at least one valid discussion point")

    if "discussion_points" in st.session_state:
        st.write("Discussion Points:")
        for idx, point in enumerate(st.session_state["discussion_points"], start=1):
            st.write(f"{idx}. {point}")

    if generate_agenda:
        if not discussion_points:
            st.warning("No discussion points available. Please add some points first.")
        else:
            # Get API key from environment variable
            api_key = os.getenv('GEMINI_API_KEY')
            
            if not api_key:
                st.error("Gemini API key not found. Please set the GEMINI_API_KEY environment variable.")
                return

            try:
                # Configure the Gemini model
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-pro')

                # Prepare the prompt
                prompt = """Generate a structured meeting agenda based on the following discussion points:

                {}

                Please organize these points into a coherent agenda with the following:
                1. A brief 100-word summary of the overall meeting objectives related to the discussion points
                3. Any necessary grouping or prioritization of topics
                4. Clear, concise headers for each section

                Do not include generic placeholders for date, time, location, or attendees."""
                prompt = prompt.format("\n".join(f"{idx}. {point}" for idx, point in enumerate(discussion_points, start=1)))

                # Generate the agenda
                response = model.generate_content(prompt)
                
                # Display the generated agenda
                st.subheader("Generated Agenda")
                st.markdown(response.text)
            except Exception as e:
                st.error(f"An error occurred while generating the agenda: {str(e)}")
