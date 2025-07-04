"""
Concept: Chat engine combines retrieval with generation
- Retrieval: Find relevant chunks using similarity search
- Augmentation: Add retrieved context to user query
- Generation: Use LLM to generate response based on context
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from typing import List, Dict
from src.vector_store import VectorStore
import logging

class ChatEngine:
    def __init__(self, vector_store: VectorStore):
        self.logger = logging.getLogger(__name__)
        self.llm = ChatGoogleGenerativeAI(model="gemini-1.5-flash")
        self.vector_store = vector_store
        self.conversation_history = []
        self.prompt_template = self.create_prompt_template()

    def create_prompt_template(self):
        """Create prompt template for RAG"""
        template = """
        You are a helpful assistant. Answer the following question based on the provided context.
        If you don't know the answer, just say that you don't know, don't try to make up an answer.
        
        Context:
        {context}
        
        Question: {question}
        
        Answer:
        """
        return PromptTemplate(template=template, input_variables=["context", "question"])
    
    def generate_response(self, query: str) -> Dict:
        """Generate response with source citations"""
        self.logger.info(f"📝 Starting response generation for query: '{query}'")
        self.logger.info(f"📊 Query length: {len(query)} characters")
        
        try:
            # Step 1: Retrieve relevant chunks
            self.logger.info("🔍 Step 1: Starting similarity search...")
            search_results = self.vector_store.similarity_search(query)
            
            if not search_results or not search_results.get('documents') or not search_results['documents'][0]:
                self.logger.warning("⚠️ No search results found")
                return {"response": "Sorry, I couldn't find relevant information to answer your question.", "sources": []}
            
            # Step 2: Process search results
            documents = search_results['documents'][0]
            metadatas = search_results['metadatas'][0] if search_results.get('metadatas') else []
            distances = search_results.get('distances', [[]])[0] if search_results.get('distances') else []
            
            self.logger.info(f"📋 Step 2: Retrieved {len(documents)} relevant chunks")
            
            # Log each retrieved chunk with metadata
            for i, (doc, metadata, distance) in enumerate(zip(documents, metadatas, distances if distances else [None]*len(documents))):
                chunk_preview = doc[:100] + "..." if len(doc) > 100 else doc
                page = metadata.get('page', 'Unknown') if metadata else 'Unknown'
                dist_str = f", distance: {distance:.4f}" if distance is not None else ""
                self.logger.info(f"  📄 Chunk {i+1}: Page {page}{dist_str}")
                self.logger.debug(f"     Content preview: {chunk_preview}")
            
            # Step 3: Prepare context
            context = "\n\n".join([f"[Source: Page {metadata.get('page', 'Unknown')}]\n{doc}" for doc, metadata in zip(documents, metadatas)])
            context_length = len(context)
            self.logger.info(f"📝 Step 3: Prepared context with {context_length} characters")
            self.logger.debug(f"     Context preview: {context[:200]}...")
            
            # Step 4: Create prompt
            prompt = self.prompt_template.format(context=context, question=query)
            prompt_length = len(prompt)
            self.logger.info(f"🎯 Step 4: Created prompt with {prompt_length} characters")
            self.logger.debug(f"     Full prompt:\n{prompt}")
            
            # Step 5: Call LLM
            self.logger.info("🤖 Step 5: Calling LLM (Gemini 1.5 Flash)...")
            self.logger.info(f"🔧 LLM Model: {self.llm.model}")
            
            try:
                import time
                start_time = time.time()
                response = self.llm.invoke(prompt)
                end_time = time.time()
                
                llm_duration = end_time - start_time
                self.logger.info(f"⚡ LLM Response received in {llm_duration:.2f} seconds")
                
                # Log response details
                response_content = response.content if hasattr(response, 'content') else str(response)
                response_length = len(response_content)
                self.logger.info(f"📤 LLM Response length: {response_length} characters")
                self.logger.info(f"📄 LLM Response preview: {response_content[:200]}...")
                self.logger.debug(f"🔍 Full LLM Response:\n{response_content}")
                
                # Log any additional response metadata
                if hasattr(response, 'response_metadata'):
                    self.logger.debug(f"📊 Response metadata: {response.response_metadata}")
                    
            except Exception as llm_error:
                self.logger.error(f"❌ LLM Error: {llm_error}")
                self.logger.error(f"🔧 LLM Model used: {self.llm.model}")
                raise llm_error
            
            # Step 6: Update conversation history
            self.conversation_history.append({"user": query, "assistant": response_content})
            self.logger.info(f"💾 Step 6: Updated conversation history (total exchanges: {len(self.conversation_history)})")
            
            # Step 7: Format sources for display
            sources = []
            for i, metadata in enumerate(metadatas):
                if isinstance(metadata, dict) and 'page' in metadata:
                    source_info = {'page': metadata['page']}
                    if i < len(distances) and distances[i] is not None:
                        source_info['similarity'] = f"{(1 - distances[i]) * 100:.1f}%"
                    sources.append(source_info)
            
            self.logger.info(f"📚 Step 7: Formatted {len(sources)} sources")
            for i, source in enumerate(sources):
                similarity_info = f" (similarity: {source.get('similarity', 'N/A')})" if 'similarity' in source else ""
                self.logger.info(f"  📖 Source {i+1}: Page {source['page']}{similarity_info}")
            
            self.logger.info("✅ Successfully generated response with all steps completed")
            return {"response": response_content, "sources": sources}
            
        except Exception as e:
            self.logger.error(f"❌ Critical error in response generation: {e}")
            self.logger.error(f"🔍 Error type: {type(e).__name__}")
            import traceback
            self.logger.error(f"📋 Full traceback:\n{traceback.format_exc()}")
            return {"response": "Sorry, I encountered an error while processing your request. Please try again.", "sources": []}
