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
        self.llm = ChatGoogleGenerativeAI(model="gemini-pro")
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
        self.logger.info(f"Generating response for query: '{query}'")
        try:
            # Retrieve relevant chunks
            search_results = self.vector_store.similarity_search(query)
            
            # Prepare context
            context = "\n".join([result["page_content"] for result in search_results["documents"][0]])
            
            # Create prompt
            prompt = self.prompt_template.format(context=context, question=query)
            
            # Generate response
            response = self.llm.invoke(prompt)
            
            # Update conversation history
            self.conversation_history.append({"user": query, "assistant": response.content})
            
            self.logger.info("Successfully generated response.")
            return {"response": response.content, "sources": search_results["metadatas"][0]}
        except Exception as e:
            self.logger.error(f"Error generating response: {e}")
            import traceback
            traceback.print_exc()
            return {"response": "Sorry, I encountered an error. Please try again.", "sources": []}
