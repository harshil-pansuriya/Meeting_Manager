import streamlit as st
from tasks import agenda, meeting, upload_doc,live_meeting, QnA

         
# -------   ------------- Main Function -------------------- #
def main():
    
    st.title("Meeting Management Tool")
    
    # Create tabs for different stages of meeting management
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Upload Documents", "Discussion Points & Agenda", "Start Meeting", "Upload Video","QnA"])
    
    # Content for each tab
    with tab1:
        uploaded_files = upload_doc.upload_documents()
        if uploaded_files:
            if st.button("Process Uploaded Documents"):
                QnA.process_uploaded_documents(uploaded_files)
    
    with tab2:
        agenda.discussion_points_and_generate_agenda()
        
    with tab3:
        st.title('Live Meeting Tracker and Transcriber')  
        live_meeting.live_meeting_tracker()
    
    with tab4:
        st.title('Recorded Meeting Transcriber and Notes Generator')
        meeting.track_meeting()
    
    with tab5:
        st.title('Context-Aware Q&A System')
        query = st.text_input("Ask a question about the meeting or related topics:")
        if query:
            with st.spinner("Generating answer..."):
                answer = QnA.qna(query)
            st.write("Answer:", answer)
            
# Entry point of the script
if __name__ == "__main__":
    main()