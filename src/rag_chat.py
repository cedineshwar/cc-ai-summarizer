"""
RAG-based Chat Module for Call Summary Analysis

This module integrates LangChain with FAISS vector store to provide
intelligent RAG-based responses to user questions about call summaries.

Functions:
- get_rag_response(): Generate response using RAG with vector retrieval
- format_retrieved_context(): Format retrieved documents for LLM
"""

import json
import os
from typing import List, Dict, Optional, Tuple
from langchain_openai import ChatOpenAI
from langchain_core.documents import Document
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
from src.vector_store import VectorStoreManager
from src.logger import logger
from src.config import get_retriever_k, Config


def load_chat_prompt(prompt_file: str) -> str:
    """
    Load chat prompt from prompt_store folder.
    
    Args:
        prompt_file: Name of the prompt file (e.g., 'chat_system_prompt.txt')
        
    Returns:
        Prompt content or empty string if file not found
    """
    prompt_path = os.path.join(os.path.dirname(__file__), '..', 'prompt_store', prompt_file)
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            logger.debug(f"Loaded prompt file: {prompt_file}")
            return content
    except FileNotFoundError:
        logger.warning(f"Chat prompt file not found: {prompt_path}")
        return ""


class RAGChatbot:
    """RAG-based chatbot for analyzing call summaries."""
    
    def __init__(self, api_key: str, summaries_file: str = None,
                 vector_store_path: str = None, retriever_k: int = None):
        """
        Initialize RAG Chatbot.
        
        Args:
            api_key: OpenAI API key
            summaries_file: Path to bulk_summaries.json (uses config default if None)
            vector_store_path: Path to FAISS vector store (uses config default if None)
            retriever_k: Number of documents to retrieve (uses config default if None)
        """
        self.api_key = api_key
        
        # Use provided values or fall back to config defaults
        from src.config import Config
        summaries_file = summaries_file or Config.SUMMARIES_FILE
        vector_store_path = vector_store_path or Config.VECTOR_STORE_PATH
        retriever_k = retriever_k or Config.RETRIEVER_K
        
        self.vector_store_manager = VectorStoreManager(summaries_file, vector_store_path, retriever_k=retriever_k)
        self.llm = None
        self.is_initialized = False
        
    def initialize(self, model: str = None, 
                   temperature: float = None, 
                   max_tokens: int = None,
                   force_recreate: bool = False) -> bool:
        """
        Initialize RAG chatbot with LLM and vector store.
        
        Args:
            model: OpenAI model name (uses Config default if None)
            temperature: Temperature for LLM responses (uses Config default if None)
            max_tokens: Maximum tokens for response (uses Config default if None)
            force_recreate: If True, recreate vector store from scratch
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        # Use Config defaults if parameters not provided
        model = model or Config.MODEL_NAME
        temperature = temperature if temperature is not None else Config.TEMPERATURE
        max_tokens = max_tokens or Config.MAX_TOKENS
        
        try:
            logger.info(f"🚀 RAG Chatbot initialization starting (force_recreate={force_recreate})...")
            
            # Create vector store (will recreate if force_recreate=True)
            logger.info("📦 Creating/loading vector store...")
            if not self.vector_store_manager.create_vector_store(self.api_key, force_recreate=force_recreate):
                logger.error("❌ Failed to create vector store")
                return False
            
            logger.info("✅ Vector store ready")
            
            # Initialize LLM
            logger.info(f"🤖 Initializing LLM (model={model}, temp={temperature}, max_tokens={max_tokens})...")
            self.llm = ChatOpenAI(
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                openai_api_key=self.api_key
            )
            logger.info("✅ LLM initialized successfully")
            
            self.is_initialized = True
            logger.info("✅ RAG Chatbot initialized successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Error initializing RAG Chatbot: {str(e)}")
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
        prompt_content = load_chat_prompt('chat_system_prompt.txt')
        if prompt_content:
            return prompt_content
        # Fallback to default if file not found
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
                        chat_history: List[Dict] = None) -> Optional[str]:
        """
        Generate RAG-based response using vector retrieval and LLM.
        
        Args:
            user_message: User's question about summaries
            chat_history: Previous conversation messages for context
            
        Returns:
            LLM response or None if error occurs
        """
        if not self.is_initialized:
            logger.error("❌ RAG Chatbot not initialized")
            return None
        
        try:
            # Retrieve relevant summaries using vector similarity
            # Uses the retriever_k value configured in vector store manager
            retriever = self.vector_store_manager.get_retriever()
            
            if retriever is None:
                logger.error("❌ Retriever not available - vector store may not be initialized")
                return None
            
            # Get relevant documents using LangChain retriever.invoke() method
            logger.info(f"🔍 Retrieving documents for query: '{user_message[:100]}...'")
            retrieved_docs = retriever.invoke(user_message)
            logger.info(f"✅ Retrieved {len(retrieved_docs)} documents (k={self.vector_store_manager.retriever_k})")
            
            if len(retrieved_docs) == 0:
                logger.warning("⚠️  No documents retrieved! Vector store might be empty or query doesn't match any documents.")
                summaries = self.vector_store_manager._load_summaries()
                logger.info(f"   Total summaries in JSON: {len(summaries)}")
                # Check vector store state
                vs_info = self.vector_store_manager.get_vector_store_info()
                logger.info(f"   Vector store state: {vs_info}")
            
            # Convert Document objects to dicts for formatting
            retrieved_results = [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in retrieved_docs
            ]
            
            # Log what was retrieved
            for i, result in enumerate(retrieved_results, 1):
                agent_name = result.get('metadata', {}).get('agent_name', 'Unknown')
                call_id = result.get('metadata', {}).get('call_id', 'N/A')
                logger.info(f"   📄 Doc {i}: Call ID={call_id}, Agent={agent_name}")
            
            context = self._format_retrieved_context(retrieved_results)
            
            # Log the actual count of retrieved documents for verification
            logger.info(f"📊 Using {len(retrieved_results)} retrieved documents in context for LLM")
            logger.info(f"📊 Full context length: {len(context)} characters")
            
            # Load system prompt
            system_prompt = self._load_system_prompt()
            
            # Load guardrail prompt to append to system prompt
            guardrail_prompt = load_chat_prompt('chat_guardrail_prompt.txt')
            full_system_prompt = f"{system_prompt}\n\n{guardrail_prompt}" if guardrail_prompt else system_prompt
            
            # Build messages for LLM
            messages = [SystemMessage(content=full_system_prompt)]
            
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
