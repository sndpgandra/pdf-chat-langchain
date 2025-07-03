"""
Concept: PDF text extraction converts PDF pages into plain text
- Handles text-based PDFs (not image-based)
- Extracts page numbers for source attribution
- Maintains document structure where possible
"""

import logging
from typing import List, Dict
import pypdf
from pathlib import Path
from langchain.text_splitter import RecursiveCharacterTextSplitter
import tiktoken

class PDFProcessor:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def extract_text_with_metadata(self, pdf_path: str) -> List[Dict]:
        """Extract text from PDF with page numbers and metadata"""
        self.logger.info(f"Extracting text from {pdf_path}")
        documents = []
        try:
            with open(pdf_path, "rb") as f:
                reader = pypdf.PdfReader(f)
                for i, page in enumerate(reader.pages):
                    documents.append({
                        "page_content": page.extract_text(),
                        "metadata": {"page": i + 1}
                    })
            self.logger.info(f"Successfully extracted text from {len(documents)} pages.")
        except Exception as e:
            self.logger.error(f"Error extracting text from PDF: {e}")
        return documents

class TextChunker:
    def __init__(self, chunk_size=1000, chunk_overlap=200):
        self.logger = logging.getLogger(__name__)
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def create_chunks(self, documents: List[Dict]) -> List[Dict]:
        """Create overlapping chunks with metadata"""
        self.logger.info("Creating text chunks...")
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=lambda text: len(self.tokenizer.encode(text)),
        )
        
        chunks = []
        for doc in documents:
            splits = text_splitter.create_documents([doc["page_content"]], metadatas=[doc["metadata"]])
            for split in splits:
                chunks.append({
                    "page_content": split.page_content,
                    "metadata": split.metadata
                })
        self.logger.info(f"Created {len(chunks)} chunks.")
        return chunks
