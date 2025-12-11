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
import shutil
import glob
from typing import List, Dict, Optional
from langchain_openai import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from src.logger import logger
from src.config import Config


class VectorStoreManager:
    """Manages FAISS vector store for RAG-based chat."""
    
    def __init__(self, summaries_file: str = None, 
                 vector_store_path: str = None,
                 retriever_k: int = None):
        """
        Initialize the Vector Store Manager.
        
        Args:
            summaries_file: Path to bulk_summaries.json (uses config default if None)
            vector_store_path: Path to save/load FAISS vector store (uses config default if None)
            retriever_k: Number of documents to retrieve (uses config default if None)
        """
        # Use provided values or fall back to config defaults
        self.summaries_file = summaries_file or Config.SUMMARIES_FILE
        self.vector_store_path = vector_store_path or Config.VECTOR_STORE_PATH
        self.retriever_k = retriever_k or Config.RETRIEVER_K
        self.embeddings = None
        self.vector_store = None
        self.retriever = None
        
    def _load_summaries(self) -> List[Dict]:
        """Load summaries from JSON file."""
        try:
            with open(self.summaries_file, 'r', encoding='utf-8') as f:
                summaries = json.load(f)
                logger.info(f"✅ Successfully loaded {len(summaries)} summaries from {self.summaries_file}")
                # Debug: print first and last summary to verify data
                if summaries:
                    logger.debug(f"   First summary callId: {summaries[0].get('callId', 'N/A')}")
                    logger.debug(f"   Last summary callId: {summaries[-1].get('callId', 'N/A')}")
                return summaries
        except FileNotFoundError:
            logger.error(f"❌ Summaries file not found: {self.summaries_file}")
            return []
        except json.JSONDecodeError:
            logger.error(f"❌ Error decoding JSON from file: {self.summaries_file}")
            return []
    
    def _prepare_documents(self, summaries: List[Dict]) -> List[Document]:
        """
        Convert summaries to Document objects for FAISS.
        
        Combines key fields into meaningful content for better retrieval.
        """
        documents = []
        logger.info(f"📝 Starting document preparation for {len(summaries)} summaries...")
        
        for idx, summary in enumerate(summaries):
            # Combine multiple fields for rich context
            content = f"""
                        Call Summary:
                        Call ID: {summary.get('callId', '')}
                        Agent: {summary.get('agentName', 'Unknown')} (ID: {summary.get('agentId', 'N/A')}
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
                        Sentiment: {summary.get('sentiment', '')}

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
            logger.debug(f"   📄 Doc {idx+1}: {summary.get('callId', 'N/A')} - {summary.get('agentName', 'Unknown')}")
        
        logger.info(f"✅ Prepared {len(documents)} documents for vector store embedding")
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
            logger.info(f"🚀 Starting vector store creation (force_recreate={force_recreate})...")
            
            # Initialize embeddings with OpenAI
            logger.info("📌 Initializing OpenAI embeddings...")
            self.embeddings = OpenAIEmbeddings(
                openai_api_key=api_key,
                model=Config.EMBEDDING_MODEL
            )
            logger.info(f"✅ Embeddings initialized successfully with model: {Config.EMBEDDING_MODEL}")
            
            # If forcing recreation, delete existing vector store first
            if force_recreate and os.path.exists(self.vector_store_path):
                import shutil
                logger.info(f"🗑️  Deleting existing vector store at {self.vector_store_path}")
                shutil.rmtree(self.vector_store_path)
                logger.info(f"✅ Old vector store deleted successfully")
            
            # Check if vector store exists and not forcing recreation
            if os.path.exists(self.vector_store_path) and not force_recreate:
                logger.info(f"📂 Loading existing vector store from {self.vector_store_path}")
                try:
                    self.vector_store = FAISS.load_local(
                        self.vector_store_path,
                        self.embeddings,
                        allow_dangerous_deserialization=True
                    )
                    # Verify the vector store has documents
                    doc_count = self.vector_store.index.ntotal if hasattr(self.vector_store.index, 'ntotal') else 0
                    if doc_count == 0:
                        logger.warning(f"⚠️  Vector store exists but has 0 documents. Recreating...")
                        raise ValueError("Empty vector store")
                    
                    self.retriever = self.vector_store.as_retriever(search_kwargs={"k": self.retriever_k})
                    logger.info(f"✅ Vector store loaded successfully with {doc_count} documents (k={self.retriever_k} - retrieves up to {self.retriever_k} docs)")
                    return True
                except Exception as e:
                    logger.warning(f"⚠️  Failed to load existing vector store: {str(e)}. Recreating from scratch...")
                    # Fall through to recreation logic below
            
            # Load summaries and prepare documents
            logger.info("📖 Loading summaries from JSON...")
            summaries = self._load_summaries()
            if not summaries:
                logger.warning("⚠️  No summaries available to create vector store")
                return False
            
            logger.info(f"📝 Preparing {len(summaries)} documents for embedding...")
            documents = self._prepare_documents(summaries)
            
            # Create FAISS vector store
            logger.info(f"🔧 Creating FAISS vector store with {len(documents)} documents and embeddings...")
            self.vector_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            
            # Verify all documents were indexed
            indexed_count = self.vector_store.index.ntotal if hasattr(self.vector_store.index, 'ntotal') else len(documents)
            logger.info(f"✅ FAISS vector store created with {indexed_count} documents indexed (expected: {len(documents)})")
            
            if indexed_count != len(documents):
                logger.warning(f"⚠️  MISMATCH: Expected {len(documents)} documents but only {indexed_count} indexed!")
            else:
                logger.info(f"✅ All {len(documents)} documents successfully indexed in FAISS")
            
            # Save vector store locally
            logger.info(f"💾 Saving vector store to {self.vector_store_path}...")
            os.makedirs(self.vector_store_path, exist_ok=True)
            self.vector_store.save_local(self.vector_store_path)
            logger.info(f"✅ Vector store saved to {self.vector_store_path}")
            
            # Create retriever
            logger.info("🔍 Creating retriever for semantic search...")
            # Using configurable k value to retrieve documents
            self.retriever = self.vector_store.as_retriever(search_kwargs={"k": self.retriever_k})
            logger.info(f"✅ Vector store created and retriever initialized successfully (k={self.retriever_k} - retrieves up to {self.retriever_k} docs)")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Error creating vector store: {str(e)}")
            return False
    
    def get_retriever(self):
        """Get the FAISS retriever for semantic search."""
        if self.retriever is None:
            logger.warning("⚠️  Retriever not initialized. Call create_vector_store() first.")
            return None
        logger.debug(f"✅ Retriever available - ready for semantic search")
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
    
    def get_vector_store_info(self) -> Dict:
        """Get information about the current vector store."""
        if self.vector_store is None:
            return {"status": "not_initialized", "document_count": 0}
        
        try:
            # Get document count from FAISS index
            doc_count = self.vector_store.index.ntotal if hasattr(self.vector_store.index, 'ntotal') else 0
            logger.info(f"📊 Vector Store Info: {doc_count} documents indexed")
            
            return {
                "status": "initialized",
                "document_count": doc_count,
                "retriever_available": self.retriever is not None
            }
        except Exception as e:
            logger.error(f"Error getting vector store info: {str(e)}")
            return {"status": "error", "error": str(e)}
    
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
    
    def clear_vector_store(self) -> bool:
        """
        Clear all documents from the vector store by completely removing the vector store directory
        and resetting all in-memory references. This performs a hard delete of all vector data.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            logger.info("=" * 70)
            logger.info("🗑️  CLEARING VECTOR STORE - HARD DELETE OF ALL DOCUMENTS")
            logger.info("=" * 70)
            
            # PRE-CLEAR STATE: Get current vector store info
            logger.info("\n📊 PRE-CLEAR STATE:")
            pre_clear_info = self.get_vector_store_info()
            logger.info(f"   Status: {pre_clear_info.get('status')}")
            logger.info(f"   Documents before clear: {pre_clear_info.get('document_count', 0)}")
            logger.info(f"   Vector store path: {self.vector_store_path}")
            logger.info(f"   Path exists: {os.path.exists(self.vector_store_path)}")
            
            # Step 1: Clear in-memory references first
            logger.info("\n🔧 STEP 1: Clearing in-memory references...")
            self.vector_store = None
            self.retriever = None
            self.embeddings = None
            logger.info("✅ In-memory references cleared (vector_store, retriever, embeddings)")
            
            # Step 2: List and count files before deletion
            logger.info("\n📁 STEP 2: Analyzing files to be deleted...")
            file_count = 0
            dir_count = 0
            files_to_delete = []
            
            if os.path.exists(self.vector_store_path):
                for root, dirs, files in os.walk(self.vector_store_path):
                    dir_count += len(dirs)
                    file_count += len(files)
                    for file in files:
                        file_path = os.path.join(root, file)
                        files_to_delete.append(file_path)
                        logger.debug(f"   Will delete: {file_path}")
                
                logger.info(f"📊 Files to delete: {file_count}")
                logger.info(f"📁 Directories to delete: {dir_count}")
                
                # Step 3: Delete the entire vector store directory
                logger.info("\n🗑️  STEP 3: Deleting vector store directory...")
                logger.info(f"   Target path: {self.vector_store_path}")
                
                shutil.rmtree(self.vector_store_path)
                logger.info("✅ Directory deletion completed")
            else:
                logger.info(f"ℹ️  Vector store directory does not exist at: {self.vector_store_path}")
            
            # Step 4: Verify deletion - critical validation
            logger.info("\n✓️  STEP 4: VALIDATING DELETION...")
            if not os.path.exists(self.vector_store_path):
                logger.info(f"✅ CONFIRMED: Vector store directory no longer exists")
                logger.info(f"   Path checked: {self.vector_store_path}")
            else:
                logger.error(f"❌ FAILED: Vector store directory still exists!")
                logger.error(f"   Path: {self.vector_store_path}")
                # List remaining contents
                remaining_files = []
                for root, dirs, files in os.walk(self.vector_store_path):
                    remaining_files.extend(files)
                logger.error(f"   Remaining files: {len(remaining_files)}")
                for file in remaining_files:
                    logger.error(f"      - {file}")
                return False
            
            # Step 5: Check FAISS index files specifically
            logger.info("\n🔍 STEP 5: Checking for FAISS-specific files...")
            faiss_files = ['index.faiss', 'index.pkl', 'docstore.pkl', 'index_to_docstore_id.pkl']
            for fname in faiss_files:
                fpath = os.path.join(self.vector_store_path, fname)
                if os.path.exists(fpath):
                    logger.error(f"❌ FAISS file still exists: {fname}")
                    return False
                else:
                    logger.info(f"✅ FAISS file removed: {fname}")
            
            # Step 6: Verify no hidden files or cache
            logger.info("\n🔎 STEP 6: Checking for hidden/cache files...")
            if os.path.exists(self.vector_store_path):
                # Try one more aggressive deletion
                logger.warning("⚠️  Directory still has content, attempting force delete...")
                all_content = glob.glob(os.path.join(self.vector_store_path, '**'), recursive=True)
                logger.warning(f"   Found {len(all_content)} items in directory")
                for item in all_content:
                    logger.warning(f"      - {item}")
                shutil.rmtree(self.vector_store_path, ignore_errors=True)
                logger.info("✅ Force delete with ignore_errors=True completed")
            else:
                logger.info("✅ No hidden/cache files found - directory completely empty")
            
            # POST-CLEAR STATE: Final verification
            logger.info("\n📊 POST-CLEAR STATE:")
            post_clear_info = self.get_vector_store_info()
            logger.info(f"   Status: {post_clear_info.get('status')}")
            logger.info(f"   Documents after clear: {post_clear_info.get('document_count', 0)}")
            logger.info(f"   Path still exists: {os.path.exists(self.vector_store_path)}")
            
            # Final summary
            logger.info("\n" + "=" * 70)
            logger.info("✅ VECTOR STORE CLEAR COMPLETE - ALL DOCUMENTS REMOVED")
            logger.info(f"   Deleted files: {file_count}")
            logger.info(f"   Deleted directories: {dir_count}")
            logger.info(f"   Verification: {'PASSED' if not os.path.exists(self.vector_store_path) else 'FAILED'}")
            logger.info("=" * 70)
            
            return True
            
        except Exception as e:
            logger.error("=" * 70)
            logger.error(f"❌ ERROR CLEARING VECTOR STORE: {str(e)}")
            logger.error("=" * 70, exc_info=True)
            return False
