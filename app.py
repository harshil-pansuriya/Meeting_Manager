import streamlit as st
from tasks import agenda, meeting, upload_doc,QnA
from config.path_handler import create_directories
import os
import yaml
from pathlib import Path

def load_config():
    config_path = Path("config/config.yaml")
    with open(config_path) as f:
        return yaml.safe_load(f)

def setup_page(config):
    st.set_page_config(page_title=config['app']['title'],layout=config['app']['layout'])

def display_readme():
    readme_path = Path("README.md")
    if readme_path.exists():
        st.markdown(readme_path.read_text())
    else:
        st.error("README.md not found")
        
# ---------------------- Main Function -------------------- #
def main():
    """Main application entry point."""
    create_directories()
    config = load_config()
    setup_page(config)
    
    st.title(config['app']['title'])
    
    tabs = st.tabs([
        "README",
        "Upload Documents & Points",
        "Generate Agenda",
        "Meeting Records",
        "QnA"
    ])
    
    with tabs[0]: display_readme()
    with tabs[1]: upload_doc.upload_documents()
    with tabs[2]: agenda.create_agenda()
    with tabs[3]: meeting.track_meeting()
    with tabs[4]: QnA.answer_questions()
   
if __name__ == "__main__":
    main()