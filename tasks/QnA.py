import streamlit as st
from tasks.utils import vector_store, get_qa_chain

def answer_questions():
    st.header("Meeting Knowledge Base Q&A")
    
    question = st.text_input("Ask a question about meeting:")
    if question and st.button("Get Answer"):
        st.spinner("Searching for answer...")
        
        results = vector_store.query(query_texts=[question], n_results=3)
        if not results['documents']:
            st.warning("No relevant information found.")
            return
        
        context = "\n".join(results['documents'][0])
        
        qa_chain = get_qa_chain()
        answer = qa_chain.run(context=context, question=question)
        
        st.subheader("Answer:")
        st.write(answer)
        
        with st.expander("View source context"):
            st.markdown(context)