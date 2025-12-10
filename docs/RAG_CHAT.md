# RAG-Based Chat System

## Overview

The RAG (Retrieval-Augmented Generation) Chat system enables intelligent semantic search across call summaries using vector embeddings. This feature allows users to ask natural language questions and receive context-aware answers powered by FAISS vector similarity search and LangChain.

## ✨ Features

### Core RAG Capabilities
- **Semantic Search**: FAISS-powered vector similarity search for finding relevant summaries
- **Context-Aware Responses**: LLM generates responses based on retrieved documents
- **Multi-Turn Conversation**: Full chat history maintained across multiple exchanges
- **Dynamic Vector Store**: Automatically updated with new summaries
- **Predefined Questions**: Quick-access buttons for common queries

### Architecture

**Components:**
- `src/vector_store.py` - FAISS vector store management
- `src/rag_chat.py` - RAG chatbot with LangChain integration
- `pages/2_view_all_call_summary.py` - RAG chat UI with dual tabs

**Technology Stack:**
- **FAISS (faiss-cpu)** - High-performance vector similarity search
- **LangChain** - LLM orchestration and chat management
- **OpenAI Embeddings** - text-embedding-3-small model
- **ChatOpenAI** - GPT-4.1-mini/nano for response generation

## 🎯 How It Works

### 1. Vector Store Creation
```
Summaries (JSON)
    ↓
Text Extraction
    ↓
OpenAI Embeddings
    ↓
FAISS Index
```

### 2. Query Processing
```
User Question
    ↓
Embedding Generation
    ↓
FAISS Similarity Search (k=5)
    ↓
Retrieved Documents
    ↓
LangChain Context Window
    ↓
LLM Response
```

## 📚 Vector Store Management

### VectorStoreManager Class

**Location**: `src/vector_store.py`

**Key Methods:**

#### `create_vector_store(documents: list, persist: bool = True)`
Creates a new FAISS vector store from documents.
```python
# Example
manager = VectorStoreManager()
manager.create_vector_store(summaries, persist=True)
```

#### `load_vector_store()`
Loads existing FAISS index or creates new if not found.
```python
vector_store = manager.load_vector_store()
```

#### `similarity_search(query: str, k: int = 5)`
Search for similar documents based on query.
```python
results = manager.similarity_search("agent performance issue", k=3)
```

#### `reload_vector_store()`
Refreshes vector store with latest summaries.
```python
manager.reload_vector_store()
```

## 🤖 RAG Chatbot

### RAGChatbot Class

**Location**: `src/rag_chat.py`

**Key Methods:**

#### `initialize(api_key: str, model: str, temperature: float)`
Initialize chatbot with LLM settings.
```python
chatbot = RAGChatbot()
chatbot.initialize(
    api_key="sk-...",
    model="gpt-4.1-mini-2025-04-14",
    temperature=0.0
)
```

#### `get_rag_response(user_message: str, chat_history: list) -> str`
Generate response with RAG-enhanced context.
```python
response = chatbot.get_rag_response(
    user_message="What are the top agent issues?",
    chat_history=previous_messages
)
```

#### `reload_vector_store()`
Update vector store with new summaries.
```python
chatbot.reload_vector_store()
```

## 🎨 User Interface

### RAG Chat Tab

**Location**: `pages/2_view_all_call_summary.py`

**Features:**
- **Dual Tabs**: 
  - "📊 Standard Chat (with Charts)" - Traditional chat with chart generation
  - "🤖 RAG-Based Chat (Vector Search)" - Semantic search with FAISS
  
- **Chat Interface**:
  - 400px scrollable message container
  - Auto-scroll to latest messages
  - Full message history display

- **Vector Store Controls**:
  - "🔄 Reload Vector Store" button to update with new summaries
  - Status indicator showing number of documents indexed

- **Predefined Questions** (RAG-optimized):
  - "Search for resolution issues"
  - "Find high-performing agents"
  - "What are common customer complaints?"
  - "Show me frustrated customer calls"
  - "Which calls had excellent resolution?"
  - "Identify agent collaboration patterns"

## 📊 Data Structure

### Indexed Documents
Each summary is converted to a searchable document:
```
Agent: [Agent Name]
Performance Score: [0-100]
Rating: [1-5 stars]
Sentiment: [customer sentiment]
Issues: [identified issues]
Resolution: [resolution details]
Department: [department name]
Duration: [call length]
Date: [conversation date]
```

### Metadata
FAISS index includes metadata:
- Summary ID
- Filename
- Agent name
- Creation timestamp

## ⚙️ Configuration

### Embedding Model
- **Model**: text-embedding-3-small
- **Dimension**: 1536
- **Provider**: OpenAI

### Vector Store Settings
```python
# FAISS Index Configuration
FAISS_INDEX_PATH = "vector_store/faiss_index"
FAISS_METADATA_PATH = "vector_store/faiss_metadata.pkl"
```

### Search Parameters
- **k (top-k results)**: 5 documents retrieved per query
- **Similarity Metric**: L2 (Euclidean distance)
- **Score Threshold**: All results returned (no filtering)

### LLM Settings (Inherited from Main App)
- **Model**: Configurable (gpt-4.1-mini or gpt-4.1-nano)
- **Temperature**: 0.0 (deterministic)
- **Max Tokens**: 600 (configurable)

## 🔍 Usage Examples

### Example 1: Finding High-Performing Agents
**User**: "Which agents have the best performance scores?"
```
1. Embed query
2. Search FAISS for agent scores
3. Retrieve top 5 matching summaries
4. LLM synthesizes: "Based on the retrieved summaries, 
   agents John and Sarah have scores above 90..."
```

### Example 2: Issue Analysis
**User**: "What are the most common issues our customers face?"
```
1. Embed "common issues"
2. Search for issue-related documents
3. Retrieve diverse issue summaries
4. LLM summarizes patterns: "Billing disputes appear 
   in 40% of calls, with slow resolution times..."
```

### Example 3: Sentiment-Based Query
**User**: "Show me calls with frustrated customers"
```
1. Embed "frustrated customers"
2. FAISS finds summaries with matching sentiment
3. Retrieve customer tone and emotion data
4. LLM provides context: "I found 12 calls with 
   frustrated customers, primarily due to..."
```

## 📈 Performance Characteristics

### Vector Store Size
- **Documents**: Grows with each new summary
- **Index Size**: ~1MB per 100 documents (1536-dim embeddings)
- **Search Time**: <100ms per query
- **Reload Time**: <500ms (depends on summary count)

### Scaling
- **Tested**: Up to 50+ summaries without issues
- **Recommended**: Reload every 10-20 new summaries
- **Optimization**: FAISS automatically optimized for fast searches

## 🔧 Troubleshooting

### Vector Store Not Found
**Problem**: "IndexNotFoundError" on first use
**Solution**: Vector store auto-creates on first RAG query

### Stale Results
**Problem**: New summaries not appearing in RAG results
**Solution**: Click "🔄 Reload Vector Store" button in UI

### Low Relevance Results
**Problem**: Results don't match query intent
**Reason**: Semantic similarity sometimes returns unexpected matches
**Solution**: Refine query with more specific keywords

### Memory Issues
**Problem**: FAISS consuming too much memory
**Solution**: Reduce number of indexed summaries or use CPU-only version (faiss-cpu)

## 📚 Dependencies

```
faiss-cpu>=1.7.4          # Vector similarity search
langchain>=0.0.200        # LLM orchestration
langchain-openai>=0.0.2   # OpenAI integration
openai>=1.0               # OpenAI API
python-dotenv             # Environment config
```

## 🚀 Future Enhancements

- [ ] Hybrid search (keyword + semantic)
- [ ] Query expansion with multiple interpretations
- [ ] Result ranking/filtering options
- [ ] Citation tracking (source references)
- [ ] Custom embedding models
- [ ] Multi-language support
- [ ] Query history and suggestions

## 📝 Notes

- **Embeddings are cached**: No re-embedding on reload
- **FAISS is thread-safe**: Safe for concurrent queries
- **No external database required**: Self-contained vector store
- **Privacy**: All data stored locally (no external indexing service)
- **Cost**: Only OpenAI embedding calls cost (chat responses counted separately)

---

**Version**: 1.0.0 | **Last Updated**: December 2025
