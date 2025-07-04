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
    
    def has_documents(self) -> bool:
        """Check if the collection has any documents"""
        try:
            count = self.collection.count()
            self.logger.info(f"Collection has {count} documents")
            return count > 0
        except Exception as e:
            self.logger.error(f"Error checking document count: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get the number of documents in the collection"""
        try:
            return self.collection.count()
        except Exception as e:
            self.logger.error(f"Error getting document count: {e}")
            return 0
    
    def add_documents(self, chunks: List[Dict], batch_size: int = 50):
        """Add document chunks to vector store in batches"""
        self.logger.info(f"Adding {len(chunks)} chunks to the vector store in batches of {batch_size}.")
        try:
            # Clear existing documents if any
            existing_count = self.get_document_count()
            if existing_count > 0:
                self.logger.info(f"Clearing {existing_count} existing documents")
                # Get all existing IDs and delete them
                results = self.collection.get()
                if results['ids']:
                    self.collection.delete(ids=results['ids'])
            
            # Add documents in batches
            for i in range(0, len(chunks), batch_size):
                batch = chunks[i:i + batch_size]
                batch_ids = [str(i + j) for j in range(len(batch))]
                
                self.logger.info(f"Adding batch {i//batch_size + 1}/{(len(chunks)-1)//batch_size + 1} ({len(batch)} chunks)")
                
                self.collection.add(
                    ids=batch_ids,
                    documents=[chunk['page_content'] for chunk in batch],
                    metadatas=[chunk['metadata'] for chunk in batch]
                )
            
            self.logger.info("Successfully added all documents to the vector store.")
        except Exception as e:
            self.logger.error(f"Error adding documents to vector store: {e}")
            raise e

    def similarity_search(self, query: str, k=5) -> Dict:
        """Search for similar chunks"""
        self.logger.info(f"🔍 Starting similarity search for query: '{query[:50]}{'...' if len(query) > 50 else ''}'")
        self.logger.info(f"📊 Search parameters: k={k}, query_length={len(query)}")
        
        try:
            # Step 1: Encode query to embeddings
            self.logger.info("🤖 Step 1: Encoding query to embeddings...")
            import time
            start_time = time.time()
            
            query_embedding = self.embedding_model.encode(query)
            
            encoding_time = time.time() - start_time
            self.logger.info(f"⚡ Query encoding completed in {encoding_time:.3f} seconds")
            
            # Convert to list if numpy array
            if hasattr(query_embedding, 'tolist'):
                query_embedding = query_embedding.tolist()
            else:
                query_embedding = list(query_embedding)
            
            embedding_length = len(query_embedding)
            self.logger.info(f"📋 Query embedding shape: {embedding_length} dimensions")
            self.logger.debug(f"🔢 Embedding preview: {query_embedding[:5]}... (showing first 5 values)")
            
            # Step 2: Check collection status
            collection_count = self.get_document_count()
            self.logger.info(f"📋 Step 2: Searching in collection with {collection_count} documents")
            
            # Step 3: Perform similarity search
            self.logger.info(f"🔍 Step 3: Querying collection for top {k} matches...")
            search_start = time.time()
            
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=k,
                include=['documents', 'metadatas', 'distances']
            )
            
            search_time = time.time() - search_start
            self.logger.info(f"⚡ Vector search completed in {search_time:.3f} seconds")
            
            # Step 4: Analyze results
            self.logger.info("📋 Step 4: Analyzing search results...")
            self.logger.debug(f"🔍 Raw results structure: {type(results)}")
            self.logger.debug(f"🗺 Results keys: {list(results.keys()) if results else 'None'}")
            
            if results and results.get('documents') and results['documents'][0]:
                num_results = len(results['documents'][0])
                self.logger.info(f"✅ Found {num_results} similar chunks")
                
                # Log detailed results
                documents = results['documents'][0]
                metadatas = results.get('metadatas', [[]])[0]
                distances = results.get('distances', [[]])[0]
                
                self.logger.info("📋 Search Results Summary:")
                for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances)):
                    page = metadata.get('page', 'Unknown') if metadata else 'Unknown'
                    similarity_score = (1 - distance) * 100 if distance is not None else 'N/A'
                    doc_preview = doc[:80] + "..." if len(doc) > 80 else doc
                    
                    self.logger.info(f"  📄 Result {i+1}: Page {page}, Similarity: {similarity_score:.1f}%")
                    self.logger.debug(f"       Distance: {distance:.4f}" if distance is not None else "       Distance: N/A")
                    self.logger.debug(f"       Preview: {doc_preview}")
                
                # Log best match details
                if distances and distances[0] is not None:
                    best_similarity = (1 - distances[0]) * 100
                    worst_similarity = (1 - distances[-1]) * 100 if len(distances) > 1 else best_similarity
                    self.logger.info(f"🏆 Best match: {best_similarity:.1f}% similarity")
                    self.logger.info(f"📉 Similarity range: {worst_similarity:.1f}% - {best_similarity:.1f}%")
                    
            else:
                self.logger.warning("⚠️ No documents found in search results")
                self.logger.debug(f"🔍 Results content: {results}")
            
            total_time = time.time() - start_time
            self.logger.info(f"✅ Similarity search completed in {total_time:.3f} seconds total")
            
            return results
            
        except Exception as e:
            self.logger.error(f"❌ Error during similarity search: {e}")
            self.logger.error(f"🔍 Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"📋 Full traceback:\n{traceback.format_exc()}")
            return {'documents': [[]], 'metadatas': [[]], 'distances': [[]]}
