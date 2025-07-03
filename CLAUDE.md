# PDF Chat Bot with LangChain

## Project Overview
A RAG (Retrieval-Augmented Generation) system that processes PDF documents and enables chat-based Q&A with source citations. Built with LangChain, Streamlit, ChromaDB, and Google Gemini.

## Architecture
```
PDF Upload → Text Extraction → Chunking → Embedding → Vector Storage
                                                            ↓
Query → Similarity Search → Relevant Chunks → Context + Query → LLM → Response
```

## Project Structure
```
pdf-chat-langchain/
├── pdf-chat-bot/
│   ├── src/
│   │   ├── pdf_processor.py    # PDF processing and text chunking
│   │   ├── vector_store.py     # ChromaDB operations
│   │   ├── chat_engine.py      # Chat logic with Gemini
│   │   └── utils.py            # Helper functions and logging
│   ├── data/uploads/           # Uploaded PDFs
│   ├── app.py                  # Main Streamlit application
│   └── requirements.txt        # Dependencies
├── chroma_db/                  # ChromaDB persistence
├── logs/                       # Application logs
└── pdf_chat_implementation_plan.md
```

## Dependencies
- streamlit
- langchain
- langchain-google-genai
- chromadb
- sentence-transformers
- pypdf
- python-dotenv
- tiktoken

## Environment Setup
1. Create virtual environment: `python -m venv pdf-chat-env`
2. Activate: `source pdf-chat-env/bin/activate` (Unix) or `pdf-chat-env\Scripts\activate` (Windows)
3. Install dependencies: `pip install -r pdf-chat-bot/requirements.txt`
4. Create `.env` file with `GOOGLE_API_KEY=your_gemini_api_key`

## Running the Application
```bash
cd pdf-chat-bot
streamlit run app.py
```

## Key Features
- Two-tab interface (Upload & Process, Chat)
- PDF text extraction with metadata
- Text chunking (1000 tokens, 200 overlap)
- Vector embeddings with ChromaDB
- Conversation history
- Source citations with page numbers

## Testing
- Upload a PDF in the first tab
- Process it to create embeddings
- Switch to chat tab to ask questions
- Responses include source page references

## Database Management
- ChromaDB stores embeddings persistently
- Reset database: `rm -rf ./chroma_db`
- Backup: `cp -r ./chroma_db ./chroma_db_backup_$(date +%Y%m%d)`

## Debugging
- Check logs: `tail -f logs/app.log`
- View ChromaDB collections: `python -c "import chromadb; client = chromadb.PersistentClient('./chroma_db'); print(client.list_collections())"`

## Common Commands
- `streamlit run app.py` - Start the application
- `pip install -r requirements.txt` - Install dependencies
- `python test_init.py` - Run basic tests