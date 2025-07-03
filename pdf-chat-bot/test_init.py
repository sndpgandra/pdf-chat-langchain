import os
from dotenv import load_dotenv
from src.pdf_processor import PDFProcessor, TextChunker
from src.vector_store import VectorStore
from src.chat_engine import ChatEngine
from src.utils import setup_logging

def run_test():
    print("--- Starting Initialization Test ---")
    
    # 1. Load environment variables
    print("Loading environment variables...")
    load_dotenv()
    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key or google_api_key == "your_gemini_api_key_here":
        print("WARNING: GOOGLE_API_KEY is not set or is still the placeholder. This will cause issues later.")
    else:
        print("GOOGLE_API_KEY loaded.")

    # 2. Setup logging
    print("Setting up logging...")
    setup_logging()
    print("Logging setup complete.")

    # 3. Initialize components
    try:
        print("Initializing PDFProcessor...")
        pdf_processor = PDFProcessor()
        print("PDFProcessor initialized successfully.")

        print("Initializing TextChunker...")
        text_chunker = TextChunker()
        print("TextChunker initialized successfully.")

        print("Initializing VectorStore (this may take a moment to load the embedding model)...")
        vector_store = VectorStore()
        print("VectorStore initialized successfully.")

        print("Initializing ChatEngine...")
        chat_engine = ChatEngine(vector_store)
        print("ChatEngine initialized successfully.")

        print("--- All components initialized successfully! ---")

    except Exception as e:
        print(f"ERROR during component initialization: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    run_test()
