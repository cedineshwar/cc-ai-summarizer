"""
RAG-based Chat Module for Call Summary Analysis

This module integrates LangChain with FAISS vector store to provide
intelligent RAG-based responses to user questions about call summaries.

Functions:
- get_rag_response(): Generate response using RAG with vector retrieval
- format_retrieved_context(): Format retrieved documents for LLM
"""

import json
from typing import List, Dict, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.vector_store import VectorStoreManager
from src.logger import logger


class RAGChatbot:
    """RAG-based chatbot for analyzing call summaries."""
    
    def __init__(self, api_key: str, summaries_file: str = "output_data/bulk_summaries.json",
                 vector_store_path: str = "output_data/vector_store"):
        """
        Initialize RAG Chatbot.
        
        Args:
            api_key: OpenAI API key
            summaries_file: Path to bulk_summaries.json
            vector_store_path: Path to FAISS vector store
        """
        self.api_key = api_key
        self.vector_store_manager = VectorStoreManager(summaries_file, vector_store_path)
        self.llm = None
        self.is_initialized = False
        
    def initialize(self, model: str = "gpt-4.1-mini-2025-04-14", 
                   temperature: float = 0.0, 
                   max_tokens: int = 600) -> bool:
        """
        Initialize RAG chatbot with LLM and vector store.
        
        Args:
            model: OpenAI model name
            temperature: Temperature for LLM responses
            max_tokens: Maximum tokens for response
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Create vector store
            if not self.vector_store_manager.create_vector_store(self.api_key):
                logger.error("Failed to create vector store")
                return False
            
            # Initialize LLM
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=self.api_key
            )
            
            self.is_initialized = True
            logger.info("RAG Chatbot initialized successfully")
            return True
            
        except Exception as e:
            logger.error(f"Error initializing RAG Chatbot: {str(e)}")
            return False
    
    def _format_retrieved_context(self, results: List[Dict]) -> str:
        """
        Format retrieved documents for LLM context.
        
        Args:
            results: List of retrieved documents with metadata
            
        Returns:
            Formatted context string
        """
        if not results:
            return "No relevant call summaries found."
        
        context = "## Retrieved Call Summaries:\n\n"
        for i, result in enumerate(results, 1):
            context += f"### Document {i}\n"
            context += result.get('content', '')
            context += "\n\n"
        
        return context
    
    def _load_system_prompt(self, prompt_file: str = "prompt_store/chat_system_prompt.txt") -> str:
        """
        Load system prompt from file.
        
        Args:
            prompt_file: Path to system prompt file
            
        Returns:
            System prompt content or default if file not found
        """
        try:
            with open(prompt_file, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            logger.warning(f"System prompt file not found: {prompt_file}. Using default.")
            return self._get_default_system_prompt()
    
    def _get_default_system_prompt(self) -> str:
        """Return default system prompt for RAG chat."""
        return """You are an expert call center analyst with deep knowledge of customer service interactions.
                    You analyze call summaries to provide insights about customer satisfaction, agent performance, and service quality.

                    Instructions:
                    1. Answer questions based on the provided call summaries retrieved from the vector database
                    2. Always cite specific calls and agent names when referencing data
                    3. Provide quantitative analysis when asked about metrics (e.g., average scores, resolution rates)
                    4. Highlight patterns and trends across multiple calls
                    5. Offer constructive insights about service quality and agent performance
                    6. Be concise but thorough in your responses
                    7. Use the metadata (agent scores, ratings, resolution status) to support your analysis

                    When answering:
                    - Reference specific call IDs and agent names
                    - Use exact metrics from the retrieved summaries
                    - Organize information clearly with bullet points or tables when appropriate
                    - Provide actionable insights when possible"""
    
    def get_rag_response(self, user_message: str, 
                        chat_history: List[Dict] = None,
                        num_retrieved_docs: int = 5) -> Optional[str]:
        """
        Generate RAG-based response using vector retrieval and LLM.
        
        Args:
            user_message: User's question about summaries
            chat_history: Previous conversation messages for context
            num_retrieved_docs: Number of documents to retrieve (k)
            
        Returns:
            LLM response or None if error occurs
        """
        if not self.is_initialized:
            logger.error("RAG Chatbot not initialized")
            return None
        
        try:
            # Retrieve relevant summaries using vector similarity
            logger.debug(f"Retrieving {num_retrieved_docs} relevant documents...")
            retriever = self.vector_store_manager.get_retriever()
            
            if retriever is None:
                logger.error("Retriever not available")
                return None
            
            # Get relevant documents
            retrieved_docs = retriever.invoke(user_message)
            
            # Format retrieved context
            retrieved_results = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in retrieved_docs
            ]
            
            context = self._format_retrieved_context(retrieved_results)
            
            # Load system prompt
            system_prompt = self._load_system_prompt()
            
            # Build messages for LLM
            messages = [SystemMessage(content=system_prompt)]
            
            # Add chat history if available
            if chat_history:
                for msg in chat_history:
                    if msg['role'] == 'user':
                        messages.append(HumanMessage(content=msg['content']))
                    elif msg['role'] == 'assistant':
                        messages.append(AIMessage(content=msg['content']))
            
            # Add context and current user message
            full_message = f"""{context}

                            User Question: {user_message}

                            Please answer the question based on the retrieved call summaries above."""
            
            messages.append(HumanMessage(content=full_message))
            
            # Get response from LLM
            logger.debug("Generating LLM response...")
            response = self.llm.invoke(messages)
            
            logger.info("RAG response generated successfully")
            return response.content
            
        except Exception as e:
            logger.error(f"Error generating RAG response: {str(e)}")
            return None
    
    def reload_vector_store(self) -> bool:
        """
        Reload vector store to pick up new summaries.
        
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Reloading vector store...")
        return self.vector_store_manager.reload_vector_store(self.api_key)
