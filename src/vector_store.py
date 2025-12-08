"""
Vector Store Management Module for RAG-based Chat

This module handles the creation, management, and retrieval of vector embeddings
from bulk summaries using FAISS for high-performance similarity search.

Functions:
- create_vector_store(): Initialize FAISS vector store from bulk summaries
- load_vector_store(): Load existing vector store from disk
- get_retriever(): Get a retriever for semantic search
"""

import json
import os
from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from src.logger import logger


class VectorStoreManager:
    """Manages FAISS vector store for RAG-based chat."""
    
    def __init__(self, summaries_file: str = "output_data/bulk_summaries.json", 
                 vector_store_path: str = "output_data/vector_store"):
        """
        Initialize the Vector Store Manager.
        
        Args:
            summaries_file: Path to bulk_summaries.json
            vector_store_path: Path to save/load FAISS vector store
        """
        self.summaries_file = summaries_file
        self.vector_store_path = vector_store_path
        self.embeddings = None
        self.vector_store = None
        self.retriever = None
        
    def _load_summaries(self) -> List[Dict]:
        """Load summaries from JSON file."""
        try:
            with open(self.summaries_file, 'r', encoding='utf-8') as f:
                summaries = json.load(f)
                logger.debug(f"Loaded {len(summaries)} summaries from {self.summaries_file}")
                return summaries
        except FileNotFoundError:
            logger.error(f"Summaries file not found: {self.summaries_file}")
            return []
        except json.JSONDecodeError:
            logger.error(f"Error decoding JSON from file: {self.summaries_file}")
            return []
    
    def _prepare_documents(self, summaries: List[Dict]) -> List[Document]:
        """
        Convert summaries to Document objects for FAISS.
        
        Combines key fields into meaningful content for better retrieval.
        """
        documents = []
        
        for summary in summaries:
            # Combine multiple fields for rich context
            content = f"""
                        Call Summary:
                        Agent: {summary.get('agentName', 'Unknown')} (ID: {summary.get('agentId', 'N/A')})
                        Customer: {summary.get('customerName', 'Unknown')}
                        Date: {summary.get('conversationDate', 'N/A')} {summary.get('conversationTime', '')}
                        Duration: {summary.get('conversationlength', 'N/A')}
                        Department: {summary.get('department', 'N/A')}

                        Issue Category: {summary.get('issueCategory', 'N/A')}
                        Summary: {summary.get('callSummary', '')}

                        Customer Tone: {summary.get('customerTone', 'N/A')}
                        Customer Emotions: {summary.get('customerEmotions', 'N/A')}
                        Agent Tone: {summary.get('agentTone', 'N/A')}
                        Agent Emotions: {summary.get('agentEmotions', 'N/A')}

                        Agent Performance Score: {summary.get('agentScore', 'N/A')}/100
                        Agent Rating: {summary.get('agentRating', 'N/A')}/5
                        Resolution Status: {summary.get('resolutionStatus', 'N/A')}
                    """
            
            # Create metadata with important fields for filtering
            metadata = {
                "call_id": summary.get('callId', ''),
                "agent_name": summary.get('agentName', ''),
                "agent_id": summary.get('agentId', ''),
                "customer_name": summary.get('customerName', ''),
                "agent_score": summary.get('agentScore', 0),
                "agent_rating": summary.get('agentRating', 0),
                "resolution_status": summary.get('resolutionStatus', ''),
                "issue_category": summary.get('issueCategory', ''),
                "department": summary.get('department', ''),
                "sentiment": summary.get('sentiment', ''),
            }
            
            doc = Document(page_content=content.strip(), metadata=metadata)
            documents.append(doc)
        
        logger.debug(f"Prepared {len(documents)} documents for vector store")
        return documents
    
    def create_vector_store(self, api_key: str, force_recreate: bool = False) -> bool:
        """
        Create or load FAISS vector store from summaries.
        
        Args:
            api_key: OpenAI API key for embeddings
            force_recreate: If True, recreate vector store even if it exists
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Initialize embeddings with OpenAI
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                model="text-embedding-3-small"
            )
            
            # Check if vector store exists and not forcing recreation
            if os.path.exists(self.vector_store_path) and not force_recreate:
                logger.info(f"Loading existing vector store from {self.vector_store_path}")
                self.vector_store = FAISS.load_local(
                    self.vector_store_path,
                    self.embeddings,
                    allow_dangerous_deserialization=True
                )
                self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
                logger.info("Vector store loaded successfully")
                return True
            
            # Load summaries and prepare documents
            summaries = self._load_summaries()
            if not summaries:
                logger.warning("No summaries available to create vector store")
                return False
            
            documents = self._prepare_documents(summaries)
            
            # Create FAISS vector store
            logger.info(f"Creating FAISS vector store with {len(documents)} documents...")
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            # Save vector store locally
            os.makedirs(self.vector_store_path, exist_ok=True)
            self.vector_store.save_local(self.vector_store_path)
            logger.info(f"Vector store saved to {self.vector_store_path}")
            
            # Create retriever
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": 5})
            logger.info("Vector store created and retriever initialized")
            
            return True
            
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            return False
    
    def get_retriever(self):
        """Get the FAISS retriever for semantic search."""
        if self.retriever is None:
            logger.warning("Retriever not initialized. Call create_vector_store() first.")
        return self.retriever
    
    def similarity_search(self, query: str, k: int = 5) -> List[Dict]:
        """
        Perform similarity search on vector store.
        
        Args:
            query: Search query
            k: Number of results to return
            
        Returns:
            List of relevant documents with metadata
        """
        if self.vector_store is None:
            logger.error("Vector store not initialized")
            return []
        
        try:
            results = self.vector_store.similarity_search(query, k=k)
            logger.debug(f"Found {len(results)} similar documents for query: {query}")
            
            return [
                {
                    "content": doc.page_content,
                    "metadata": doc.metadata
                }
                for doc in results
            ]
        except Exception as e:
            logger.error(f"Error during similarity search: {str(e)}")
            return []
    
    def reload_vector_store(self, api_key: str) -> bool:
        """
        Reload vector store to pick up new summaries.
        
        Args:
            api_key: OpenAI API key for embeddings
            
        Returns:
            bool: True if successful, False otherwise
        """
        logger.info("Reloading vector store...")
        return self.create_vector_store(api_key, force_recreate=True)
