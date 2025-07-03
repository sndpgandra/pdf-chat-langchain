"""
Concept: Two-tab interface for document processing and chat
- Tab 1: File upload and processing
- Tab 2: Chat interface with conversation history
"""

import streamlit as st
from src.pdf_processor import PDFProcessor, TextChunker
from src.vector_store import VectorStore
from src.chat_engine import ChatEngine
from src.utils import setup_logging
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    setup_logging()
    st.set_page_config(page_title="PDF Chat Bot", layout="wide")

    # Initialize session state
    if 'processed' not in st.session_state:
        st.session_state.processed = False
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    # Initialize components
    pdf_processor = PDFProcessor()
    text_chunker = TextChunker()
    vector_store = VectorStore()
    chat_engine = ChatEngine(vector_store)

    st.title("PDF Chat Bot")

    tab1, tab2 = st.tabs(["📄 Upload & Process", "💬 Chat"])

    with tab1:
        st.header("Upload a PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file is not None:
            if st.button("Process PDF"):
                with st.spinner("Processing PDF..."):
                    # Save uploaded file
                    data_path = "./pdf-chat-bot/data/uploads"
                    os.makedirs(data_path, exist_ok=True)
                    file_path = os.path.join(data_path, uploaded_file.name)
                    with open(file_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    # 1. Extract text
                    documents = pdf_processor.extract_text_with_metadata(file_path)
                    
                    # 2. Create chunks
                    chunks = text_chunker.create_chunks(documents)
                    
                    # 3. Add to vector store
                    vector_store.add_documents(chunks)
                    
                    st.session_state.processed = True
                    st.success("PDF processed successfully!")

    with tab2:
        st.header("Chat with your PDF")

        if not st.session_state.processed:
            st.warning("Please upload and process a PDF first.")
        else:
            # Display chat history
            for message in st.session_state.chat_history:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])

            # Chat input
            if prompt := st.chat_input("Ask a question about your PDF"):
                st.session_state.chat_history.append({"role": "user", "content": prompt})
                with st.chat_message("user"):
                    st.markdown(prompt)

                with st.spinner("Thinking..."):
                    response = chat_engine.generate_response(prompt)
                    with st.chat_message("assistant"):
                        st.markdown(response["response"])
                        st.session_state.chat_history.append({"role": "assistant", "content": response["response"]})
                        
                        # Display sources
                        with st.expander("Sources"):
                            for source in response["sources"]:
                                st.write(f"Page: {source['page']}")

if __name__ == "__main__":
    main()
