"""
Concept: Vector stores enable semantic search
- Embeddings: Convert text to numerical vectors
- Similarity search: Find relevant chunks using cosine similarity
- Persistence: Store vectors for reuse across sessions
"""

import chromadb
from sentence_transformers import SentenceTransformer
from typing import List, Dict
import logging

class VectorStore:
    def __init__(self, persist_directory="./chroma_db"):
        self.logger = logging.getLogger(__name__)
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        self.collection_name = "pdf_documents"
        self.collection = self.create_or_get_collection()
    
    def create_or_get_collection(self):
        """Create or retrieve existing collection"""
        try:
            collection = self.client.get_collection(name=self.collection_name)
            self.logger.info(f"Collection '{self.collection_name}' already exists.")
            return collection
        except Exception as e:
            self.logger.info(f"Collection '{self.collection_name}' not found. Creating new collection.")
            collection = self.client.create_collection(
                name=self.collection_name,
                metadata={"hnsw:space": "cosine"} # l2 is the default
            )
            return collection
    
    def add_documents(self, chunks: List[Dict]):
        """Add document chunks to vector store"""
        self.logger.info(f"Adding {len(chunks)} chunks to the vector store.")
        try:
            self.collection.add(
                ids=[str(i) for i in range(len(chunks))],
                documents=[chunk['page_content'] for chunk in chunks],
                metadatas=[chunk['metadata'] for chunk in chunks]
            )
            self.logger.info("Successfully added documents to the vector store.")
        except Exception as e:
            self.logger.error(f"Error adding documents to vector store: {e}")

    def similarity_search(self, query: str, k=5) -> List[Dict]:
        """Search for similar chunks"""
        self.logger.info(f"Performing similarity search for query: '{query}'")
        try:
            query_embedding = self.embedding_model.encode(query).tolist()
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k
            )
            self.logger.info(f"Found {len(results)} similar chunks.")
            return results
        except Exception as e:
            self.logger.error(f"Error during similarity search: {e}")
            return []
