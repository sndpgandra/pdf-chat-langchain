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
import glob
import logging
import traceback
import psutil
import gc
from dotenv import load_dotenv

load_dotenv()

# Setup detailed logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
    handlers=[
        logging.FileHandler('logs/debug.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

def log_memory_usage(step):
    """Log current memory usage"""
    try:
        process = psutil.Process()
        memory_info = process.memory_info()
        logger.info(f"Memory usage at {step}: RSS={memory_info.rss / 1024 / 1024:.2f}MB, VMS={memory_info.vms / 1024 / 1024:.2f}MB")
    except Exception as e:
        logger.error(f"Failed to get memory info: {e}")

def check_existing_data():
    """Check if vector store already has data"""
    try:
        vector_store = VectorStore()
        has_data = vector_store.has_documents()
        count = vector_store.get_document_count()
        logger.info(f"Vector store check: has_data={has_data}, count={count}")
        return has_data, count
    except Exception as e:
        logger.error(f"Error checking existing data: {e}")
        return False, 0

def process_pdf_with_progress(pdf_file, pdf_processor, text_chunker, vector_store):
    """Process PDF with progress updates to prevent timeout"""
    # Create progress containers
    progress_container = st.container()
    status_container = st.container()
    
    with progress_container:
        progress_bar = st.progress(0)
        status_text = st.empty()
    
    try:
        # Step 1: Extract text (30% of progress)
        status_text.text("Extracting text from PDF...")
        progress_bar.progress(10)
        
        documents = pdf_processor.extract_text_with_metadata(pdf_file)
        logger.info(f"Extracted {len(documents)} documents")
        progress_bar.progress(30)
        
        # Step 2: Create chunks (50% of progress)
        status_text.text("Creating text chunks...")
        chunks = text_chunker.create_chunks(documents)
        logger.info(f"Created {len(chunks)} chunks")
        progress_bar.progress(50)
        
        # Step 3: Add to vector store in batches (100% of progress)
        status_text.text("Adding documents to vector store...")
        
        # Process in smaller batches with progress updates
        batch_size = 25  # Smaller batches for better progress tracking
        total_batches = (len(chunks) - 1) // batch_size + 1
        
        for i in range(0, len(chunks), batch_size):
            batch = chunks[i:i + batch_size]
            batch_num = i // batch_size + 1
            
            status_text.text(f"Processing batch {batch_num}/{total_batches}...")
            
            # Add batch to vector store
            if i == 0:  # First batch - use full add_documents method
                vector_store.add_documents(batch, batch_size=batch_size)
            else:  # Subsequent batches - append
                existing_count = vector_store.get_document_count()
                batch_ids = [str(existing_count + j) for j in range(len(batch))]
                vector_store.collection.add(
                    ids=batch_ids,
                    documents=[chunk['page_content'] for chunk in batch],
                    metadatas=[chunk['metadata'] for chunk in batch]
                )
            
            # Update progress
            progress = 50 + (batch_num / total_batches) * 50
            progress_bar.progress(int(progress))
            
            # Small delay to prevent timeout and allow UI updates
            import time
            time.sleep(0.1)
        
        progress_bar.progress(100)
        status_text.text("Processing complete!")
        
        # Clear progress after a short delay
        time.sleep(1)
        progress_container.empty()
        status_container.empty()
        
        return True
        
    except Exception as e:
        logger.error(f"Error in process_pdf_with_progress: {e}")
        status_text.text(f"Error: {e}")
        return False

def auto_process_existing_pdf():
    """Automatically process any existing PDF in data/uploads directory"""
    logger.info("Starting auto_process_existing_pdf function")
    
    try:
        log_memory_usage("auto_process_start")
        
        # First check if we already have data
        has_data, doc_count = check_existing_data()
        if has_data and doc_count > 0:
            logger.info(f"Vector store already has {doc_count} documents, skipping processing")
            st.session_state.processed = True
            st.session_state.processed_file = "2025_Benefits_Book_en.pdf"  # Assume this file
            st.info(f"✅ Found existing data: {doc_count} documents already processed")
            return True
        
        data_path = "./data/uploads"
        logger.info(f"Checking data path: {data_path}")
        
        if not os.path.exists(data_path):
            logger.warning(f"Data path does not exist: {data_path}")
            return False
            
        pdf_files = glob.glob(os.path.join(data_path, "*.pdf"))
        logger.info(f"Found PDF files: {pdf_files}")
        
        if not pdf_files:
            logger.info("No PDF files found")
            return False
            
        if st.session_state.processed:
            logger.info("PDF already processed in session, skipping auto-process")
            return True
            
        pdf_file = pdf_files[0]
        file_size = os.path.getsize(pdf_file) / 1024 / 1024  # MB
        logger.info(f"Processing PDF: {pdf_file}, Size: {file_size:.2f}MB")
        
        st.info(f"🔄 Processing PDF: {os.path.basename(pdf_file)} ({file_size:.1f}MB)")
        
        try:
            logger.info("Initializing components")
            pdf_processor = PDFProcessor()
            text_chunker = TextChunker()
            vector_store = VectorStore()
            
            # Process with progress updates
            success = process_pdf_with_progress(pdf_file, pdf_processor, text_chunker, vector_store)
            
            if success:
                st.session_state.processed = True
                st.session_state.processed_file = os.path.basename(pdf_file)
                logger.info(f"Successfully auto-processed: {os.path.basename(pdf_file)}")
                st.success(f"✅ Successfully processed: {os.path.basename(pdf_file)}")
                
                # Final cleanup
                gc.collect()
                log_memory_usage("final")
                return True
            else:
                st.error("❌ Failed to process PDF")
                return False
                
        except MemoryError as e:
            logger.error(f"Memory error during PDF processing: {e}")
            logger.error(traceback.format_exc())
            st.error("❌ Memory error: PDF too large to process. Try a smaller file.")
            return False
            
        except Exception as e:
            logger.error(f"Error during PDF processing: {e}")
            logger.error(traceback.format_exc())
            st.error(f"❌ Error processing PDF: {e}")
            return False
            
    except Exception as e:
        logger.error(f"Critical error in auto_process_existing_pdf: {e}")
        logger.error(traceback.format_exc())
        st.error(f"❌ Critical error: {e}")
        return False

def main():
    logger.info("Starting main function")
    
    try:
        logger.info("Setting up logging")
        setup_logging()
        
        logger.info("Setting page config")
        st.set_page_config(page_title="PDF Chat Bot", layout="wide")
        log_memory_usage("after_page_config")

        # Initialize session state
        logger.info("Initializing session state")
        if 'processed' not in st.session_state:
            st.session_state.processed = False
            logger.info("Initialized processed state to False")
        if 'chat_history' not in st.session_state:
            st.session_state.chat_history = []
            logger.info("Initialized chat_history")
        if 'processed_file' not in st.session_state:
            st.session_state.processed_file = None
            logger.info("Initialized processed_file")
        if 'initialization_complete' not in st.session_state:
            st.session_state.initialization_complete = False
            logger.info("Initialized initialization_complete")

        # Initialize components with error handling
        logger.info("Initializing components")
        log_memory_usage("before_components")
        
        try:
            logger.info("Creating PDF processor")
            pdf_processor = PDFProcessor()
            
            logger.info("Creating text chunker")
            text_chunker = TextChunker()
            
            logger.info("Creating vector store")
            vector_store = VectorStore()
            
            logger.info("Creating chat engine")
            chat_engine = ChatEngine(vector_store)
            
            log_memory_usage("after_components")
            
        except Exception as e:
            logger.error(f"Error initializing components: {e}")
            logger.error(traceback.format_exc())
            st.error(f"Error initializing application components: {e}")
            return
        
        # Auto-process existing PDF on first load
        if not st.session_state.initialization_complete:
            logger.info("Checking for existing data and auto-processing if needed")
            try:
                # Quick check first - don't process if data exists
                has_data, doc_count = check_existing_data()
                if has_data and doc_count > 0:
                    logger.info(f"Found existing {doc_count} documents, skipping processing")
                    st.session_state.processed = True
                    st.session_state.processed_file = "2025_Benefits_Book_en.pdf"
                    auto_process_success = True
                elif not st.session_state.processed:
                    logger.info("No existing data found, starting auto-processing")
                    auto_process_success = auto_process_existing_pdf()
                else:
                    auto_process_success = True
                
                logger.info(f"Auto-process result: {auto_process_success}")
                st.session_state.initialization_complete = True
            except Exception as e:
                logger.error(f"Error during auto-processing: {e}")
                logger.error(traceback.format_exc())
                st.error(f"Error during initialization: {e}")
                st.session_state.initialization_complete = True
        
        logger.info("Components initialized successfully")
        
    except Exception as e:
        logger.error(f"Critical error in main function setup: {e}")
        logger.error(traceback.format_exc())
        st.error(f"Critical application error: {e}")
        return

    st.title("PDF Chat Bot")

    tab1, tab2 = st.tabs(["📄 Upload & Process", "💬 Chat"])

    with tab1:
        st.header("Upload a PDF")
        
        # Show currently processed file if any
        if st.session_state.processed and st.session_state.processed_file:
            st.info(f"✅ Currently loaded: {st.session_state.processed_file}")
            if st.button("Clear Current PDF"):
                st.session_state.processed = False
                st.session_state.processed_file = None
                st.session_state.chat_history = []
                st.rerun()
        
        uploaded_file = st.file_uploader("Choose a PDF file", type="pdf")

        if uploaded_file is not None:
            if st.button("Process PDF"):
                logger.info(f"Manual processing initiated for file: {uploaded_file.name}")
                file_size = len(uploaded_file.getbuffer()) / 1024 / 1024  # MB
                logger.info(f"File size: {file_size:.2f}MB")
                
                with st.spinner("Processing PDF..."):
                    try:
                        log_memory_usage("before_manual_processing")
                        
                        # Save uploaded file
                        logger.info("Saving uploaded file")
                        data_path = "./data/uploads"
                        os.makedirs(data_path, exist_ok=True)
                        file_path = os.path.join(data_path, uploaded_file.name)
                        
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        logger.info(f"File saved to: {file_path}")
                        log_memory_usage("after_file_save")
                        
                        # 1. Extract text
                        logger.info("Starting text extraction")
                        documents = pdf_processor.extract_text_with_metadata(file_path)
                        logger.info(f"Extracted {len(documents)} documents")
                        log_memory_usage("after_extraction")
                        
                        # 2. Create chunks
                        logger.info("Creating text chunks")
                        chunks = text_chunker.create_chunks(documents)
                        logger.info(f"Created {len(chunks)} chunks")
                        log_memory_usage("after_chunking")
                        
                        # Force garbage collection
                        gc.collect()
                        log_memory_usage("after_gc")
                        
                        # 3. Add to vector store
                        logger.info("Adding to vector store")
                        vector_store.add_documents(chunks)
                        logger.info("Successfully added to vector store")
                        log_memory_usage("after_vector_store")
                        
                        st.session_state.processed = True
                        st.session_state.processed_file = uploaded_file.name
                        st.session_state.chat_history = []  # Clear chat history for new document
                        logger.info("PDF processed successfully")
                        st.success("PDF processed successfully!")
                        
                        # Final cleanup
                        gc.collect()
                        log_memory_usage("final_manual")
                        
                    except MemoryError as e:
                        logger.error(f"Memory error during manual processing: {e}")
                        logger.error(traceback.format_exc())
                        st.error("Memory error: PDF too large to process. Try a smaller file.")
                    except Exception as e:
                        logger.error(f"Error processing PDF: {e}")
                        logger.error(traceback.format_exc())
                        st.error(f"Error processing PDF: {e}")

    with tab2:
        st.header("Chat with your PDF")
        
        if st.session_state.processed and st.session_state.processed_file:
            st.info(f"💬 Chatting with: {st.session_state.processed_file}")

        if not st.session_state.processed:
            st.warning("Please upload and process a PDF first, or check if auto-processing failed.")
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
                    try:
                        logger.info(f"Processing user query: {prompt[:100]}...")
                        log_memory_usage("before_chat_response")
                        
                        response = chat_engine.generate_response(prompt)
                        logger.info("Generated response successfully")
                        log_memory_usage("after_chat_response")
                        
                        with st.chat_message("assistant"):
                            st.markdown(response["response"])
                            st.session_state.chat_history.append({"role": "assistant", "content": response["response"]})
                            
                            # Display sources
                            with st.expander("Sources"):
                                for source in response["sources"]:
                                    st.write(f"Page: {source['page']}")
                        
                        logger.info("Chat response displayed successfully")
                        
                    except Exception as e:
                        logger.error(f"Error generating chat response: {e}")
                        logger.error(traceback.format_exc())
                        st.error(f"Error generating response: {e}")

if __name__ == "__main__":
    try:
        logger.info("Application starting")
        main()
        logger.info("Application main completed")
    except Exception as e:
        logger.error(f"Critical application error: {e}")
        logger.error(traceback.format_exc())
        st.error(f"Critical application error: {e}")
        st.stop()
