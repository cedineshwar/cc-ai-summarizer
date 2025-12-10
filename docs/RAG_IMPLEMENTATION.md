# RAG-Based Chat Implementation Guide

## Overview

This document details the RAG (Retrieval-Augmented Generation) chatbot implementation for the Call Center AI Summarizer. The system now features two distinct chat modes on the "View Summaries" page: the existing **Standard Chat with Charts** and a new **RAG-Based Chat** powered by vector search.

---

## Architecture Overview

### System Components

```
┌─────────────────────────────────────────────────────────────────┐
│                    Streamlit UI (View Summaries Page)           │
│                                                                  │
│  ┌──────────────────────┐          ┌──────────────────────┐    │
│  │  Tab 1: Standard     │          │  Tab 2: RAG-Based    │    │
│  │  Chat with Charts    │          │  Chat (Vector)       │    │
│  │                      │          │                      │    │
│  │  • Chart generation  │          │  • Vector search     │    │
│  │  • Predefined Q's    │          │  • Context retrieval │    │
│  │  • Chat history      │          │  • Chat history      │    │
│  └──────────────────────┘          └──────────────────────┘    │
└─────────────────────────────────────────────────────────────────┘
           │                                   │
           │                                   │
           ▼                                   ▼
    ┌─────────────────────┐           ┌──────────────────────┐
    │ Existing Chat Flow  │           │  RAG Chat Flow       │
    │ (chat_with_bulk_    │           │                      │
    │  summaries)         │           │  ┌─────────────────┐ │
    └─────────────────────┘           │  │ VectorStoreManager
    │                                 │  │ ├─ Load summaries
    │                                 │  │ ├─ Create docs
    │                                 │  │ ├─ FAISS indexing
    │                                 │  │ └─ Similarity search
    │                                 │  └─────────────────┘
    │                                 │         │
    ▼                                 ▼         ▼
OpenAI API                    ┌──────────────────────┐
(GPT-4.1-mini)                │   FAISS Vector Store │
                              │                      │
                              │ • 5 summaries indexed│
                              │ • 5-dim retrieval    │
                              │ • Local persistence  │
                              └──────────────────────┘
                                      │
                                      ▼
                              ┌──────────────────────┐
                              │   RAGChatbot Class   │
                              │                      │
                              │ • LLM integration    │
                              │ • Prompt management  │
                              │ • Response generation│
                              └──────────────────────┘
```

---

## New Modules

### 1. **src/vector_store.py** (380 lines)

**Purpose:** Manages FAISS vector store creation, loading, and retrieval.

**Key Class:** `VectorStoreManager`

**Methods:**

| Method | Purpose |
|--------|---------|
| `__init__()` | Initialize manager with summaries file path and vector store path |
| `_load_summaries()` | Load summaries from JSON |
| `_prepare_documents()` | Convert summaries to Document objects with enriched content |
| `create_vector_store()` | Create FAISS vector store from summaries (with local persistence) |
| `get_retriever()` | Get retriever for semantic search |
| `similarity_search()` | Perform direct similarity search on vector store |
| `reload_vector_store()` | Reload vector store to pick up new summaries |

**Key Features:**

- Uses OpenAI's `text-embedding-3-small` model for embeddings
- Combines multiple summary fields (agent name, customer name, issues, emotions, scores) for rich context
- Stores metadata (call_id, agent_name, scores, resolution_status, etc.) for filtering/tracking
- Saves vector store locally to `/output_data/vector_store/` for reuse
- Supports force recreation to pick up new summaries

**Document Preparation:**

Each summary is converted to a Document with:
- **Content:** Combined text from multiple fields (agent, customer, tone, emotions, scores, resolution)
- **Metadata:** Structured fields for context (call_id, agent_name, agent_score, agent_rating, resolution_status, etc.)

### 2. **src/rag_chat.py** (240 lines)

**Purpose:** RAG-based chatbot integrating LangChain with FAISS vector store.

**Key Class:** `RAGChatbot`

**Methods:**

| Method | Purpose |
|--------|---------|
| `__init__()` | Initialize RAG chatbot with API key and file paths |
| `initialize()` | Set up vector store and LLM (must call before use) |
| `_format_retrieved_context()` | Format retrieved docs for LLM consumption |
| `_load_system_prompt()` | Load system prompt from `prompt_store/chat_system_prompt.txt` |
| `_get_default_system_prompt()` | Return default system prompt if file not found |
| `get_rag_response()` | Generate RAG response using vector retrieval + LLM |
| `reload_vector_store()` | Reload vector store for new summaries |

**Key Features:**

- Lazy initialization: Vector store created on first RAG chat tab access
- Retrieves 5 most relevant documents for each query
- Passes full conversation history to LLM for context
- System prompt guides LLM to cite specific calls and provide quantitative analysis
- Falls back to default system prompt if file not found

**RAG Response Flow:**

1. User inputs a question
2. RAGChatbot retrieves 5 most relevant documents using FAISS similarity search
3. Retrieved documents are formatted with their content and metadata
4. System prompt + chat history + retrieved context + user question → LLM
5. LLM generates response based on retrieved call summaries

---

## UI Implementation

### View Summaries Page Structure

**File:** `pages/2_view_all_call_summary.py`

**Layout:**

```
┌─────────────────────────────────────────────┐
│          View Summaries (Title)             │
├─────────────────────────────────────────────┤
│        📊 Call Summaries (Table)            │
│     [Download as CSV] Button                │
├─────────────────────────────────────────────┤
│        💬 Chat with Summaries (Title)       │
│  ┌───────────────────────────────────────┐  │
│  │ Tab 1: 📊 Standard Chat (with Charts) │  │
│  │ Tab 2: 🤖 RAG-Based Chat (Vector)    │  │
│  └───────────────────────────────────────┘  │
├─────────────────────────────────────────────┤
│ TAB 1 Content:                              │
│  • 400px scrollable chat container          │
│  • Existing chat functionality              │
│  • Chart detection & generation             │
│  • 6 predefined questions                   │
│  • Clear chat history button                │
├─────────────────────────────────────────────┤
│ TAB 2 Content:                              │
│  • 400px scrollable chat container          │
│  • Vector search + LLM responses            │
│  • 6 sample questions                       │
│  • 🔄 Reload Vector Store button            │
│  • Clear RAG chat history button            │
└─────────────────────────────────────────────┘
```

### Session State Management

**Standard Chat Tab:**
- `bulk_summary_chat_history` - Message history
- `chart_images` - Base64-encoded chart images

**RAG Chat Tab:**
- `rag_chatbot` - RAGChatbot instance (lazy-initialized)
- `rag_chat_history` - Message history

### Helper Functions

**1. `_render_standard_chat(summaries)`**
- Renders existing chat interface with all features intact
- Handles chart detection and generation
- Maintains backward compatibility

**2. `_render_rag_chat()`**
- Renders RAG-based chat interface
- Initializes RAG chatbot on first access
- Handles vector store reloading
- Displays RAG-specific sample questions

---

## Dependencies

**Added to requirements.txt:**

```
langchain>=0.1.0
langchain-openai>=0.1.0
langchain-community>=0.0.10
faiss-cpu>=1.7.4
tiktoken>=0.5.0
```

| Package | Purpose |
|---------|---------|
| `langchain` | LLM orchestration framework |
| `langchain-openai` | OpenAI integration for LangChain |
| `langchain-community` | FAISS and community integrations |
| `faiss-cpu` | CPU-based vector similarity search |
| `tiktoken` | Token counting for OpenAI models |

**Note:** Python 3.14 has Pydantic v2 compatibility issues with older LangChain versions. The implementation uses `langchain_core` imports to avoid these issues.

---

## How RAG Works in This System

### Step 1: Vector Store Creation

When user first accesses RAG chat tab:

```python
rag_chatbot = RAGChatbot(api_key=api_key)
rag_chatbot.initialize(model, temperature, max_tokens)
```

This:
1. Loads 5 call summaries from `output_data/bulk_summaries.json`
2. Converts each summary to a Document with enriched content
3. Generates embeddings using OpenAI's `text-embedding-3-small`
4. Creates FAISS index for fast similarity search
5. Saves to `output_data/vector_store/` for reuse

### Step 2: User Question

User asks: *"Which agents have the highest scores?"*

### Step 3: Vector Retrieval

RAG system performs similarity search:

```python
retrieved_docs = retriever.invoke(user_message)  # Returns top 5 similar summaries
```

FAISS finds 5 most relevant call summaries based on semantic similarity to the question.

### Step 4: Context Formatting

Retrieved documents are formatted:

```
## Retrieved Call Summaries:

### Document 1
Call Summary:
Agent: Sarah Mitchell (ID: AG-2847)
Customer: Robert Thompson
...
Agent Performance Score: 95/100
...

### Document 2
...
```

### Step 5: LLM Processing

Full message to LLM:

```
[System Prompt - Expert call center analyst instructions]

[Retrieved Call Summaries - 5 most relevant calls with full context]

User Question: Which agents have the highest scores?

Please answer the question based on the retrieved call summaries above.
```

### Step 6: Response Generation

LLM analyzes the retrieved summaries and generates answer like:

> Based on the retrieved call summaries:
>
> **Highest Performing Agents:**
> 1. **Sarah Mitchell (AG-2847)** - Agent Score: 95/100
>    - Call: CC-2025-001847 (WiFi Connectivity Resolution)
>    - Rating: 5/5 stars
>    - Demonstrated excellent professionalism and empathy
>
> 2. **Marcus Johnson (AG-2951)** - Agent Score: 85/100
>    - Call: CC-2025-001923 (WiFi Connectivity Escalation)
>    - Rating: 4/5 stars
>    - Maintained professionalism despite unresolvable issue

---

## Key Advantages of RAG

1. **Context-Aware:** Retrieves most relevant summaries for each question
2. **Accurate Citations:** LLM references specific call IDs and agent names
3. **Scalable:** Handles large numbers of summaries efficiently
4. **Dynamic:** New summaries automatically available after reload
5. **Transparent:** Retrieved documents clearly shown in LLM context
6. **Flexible:** Supports complex analytical questions across all call data

---

## Configuration

### Model Settings

All settings inherited from main app sidebar:

| Setting | Default | Purpose |
|---------|---------|---------|
| Model | gpt-4.1-mini-2025-04-14 | OpenAI model for responses |
| Temperature | 0.0 | Consistency (0.0 = deterministic) |
| Max Tokens | 600 | Response length limit |
| API Key | Required | OpenAI authentication |

### Vector Store Settings

**File:** `src/vector_store.py`

```python
summaries_file = "output_data/bulk_summaries.json"  # Input source
vector_store_path = "output_data/vector_store"      # Storage location
embedding_model = "text-embedding-3-small"           # OpenAI embeddings
retriever_k = 5                                       # Documents to retrieve
```

### System Prompt

**File:** `prompt_store/chat_system_prompt.txt`

The RAG system uses the existing chat system prompt which guides the LLM to:
- Analyze call summaries expertly
- Cite specific calls and agent names
- Provide quantitative analysis when requested
- Highlight patterns and trends
- Offer constructive insights

If not found, uses a built-in default prompt.

---

## Usage Examples

### Example 1: Agent Performance Analysis

**User:** "Which agent got the best ratings?"

**RAG Process:**
1. Retrieves 5 summaries with rating information
2. Identifies Sarah Mitchell (5-star rating)
3. Generates response with specific citation

**Response:**
> Agent Sarah Mitchell (ID: AG-2847) achieved the highest rating with 5 stars in Call CC-2025-001847...

### Example 2: Issue Pattern Analysis

**User:** "What are the most common customer issues?"

**RAG Process:**
1. Retrieves 5 summaries with issue categories
2. Identifies patterns (WiFi connectivity, delivery issues, flight cancellation)
3. Generates summary with frequency analysis

**Response:**
> Based on the retrieved summaries, I can identify these issue categories:
> 1. Technical Support (2 calls) - WiFi connectivity issues
> 2. Order/Delivery Problems (2 calls) - Lost and wrong address deliveries
> ...

### Example 3: Sentiment Analysis

**User:** "Analyze customer sentiment patterns"

**RAG Process:**
1. Retrieves 5 summaries with sentiment data
2. Analyzes emotional states and tones
3. Generates insights about customer satisfaction

**Response:**
> Customer sentiment analysis across the retrieved calls shows:
> - Frustrated customers: 60% (flights, deliveries)
> - Neutral/Appreciative: 40% (resolved issues)
> ...

---

## Troubleshooting

### Issue 1: Vector Store Not Created

**Error:** "Failed to create vector store"

**Solution:**
- Check API key is valid
- Verify `output_data/bulk_summaries.json` exists
- Check disk space for `/output_data/vector_store/`
- Review logs for detailed error

### Issue 2: Slow Vector Store Creation

**Cause:** First-time creation with many summaries

**Solution:**
- This is normal for initial creation
- Subsequent uses load cached vector store instantly
- Click "Reload Vector Store" only when new summaries added

### Issue 3: Pydantic Deprecation Warnings

**Warning:** "Core Pydantic V1 functionality isn't compatible with Python 3.14"

**Status:** Known issue with LangChain on Python 3.14
- Does not affect functionality
- LangChain is working on Python 3.14 support
- Can suppress by updating to langchain>=0.2.0 when available

### Issue 4: Empty Chat Despite Questions

**Cause:** API key not set in main app

**Solution:**
- Go to main app page (app.py)
- Enter valid OpenAI API key in sidebar
- Return to View Summaries page
- RAG chat will now work

---

## Performance Notes

### FAISS Performance

- **Indexing:** ~100-500ms for 5 summaries (first time)
- **Retrieval:** ~10-50ms per query (subsequent uses)
- **Memory:** ~10MB per 100 summaries (cached)

### LLM Performance

- **Average Response Time:** 1-3 seconds
- **Token Usage:** ~400-600 tokens per RAG response
- **Cost:** ~$0.001-0.003 per RAG query

### Scaling Estimates

For 100+ summaries:
- Vector store creation: ~1-2 seconds
- Query retrieval: <50ms
- Full response: 2-4 seconds

---

## Future Enhancements

### Potential Improvements

1. **Hybrid Search:** Combine semantic search with keyword filtering
2. **Summary Metadata Filtering:** Filter retrievals by agent, department, date range
3. **Multi-turn Contextual Memory:** Maintain question context across RAG queries
4. **Document Reranking:** Use a reranker to improve top-5 quality
5. **Streaming Responses:** Stream LLM output for better UX
6. **Persistence:** Save RAG chat history between sessions
7. **Analytics:** Track which questions are asked most
8. **Custom Embeddings:** Fine-tune embeddings for call center terminology

---

## Files Modified/Created

### New Files

- ✅ `src/vector_store.py` - Vector store management (380 lines)
- ✅ `src/rag_chat.py` - RAG chatbot integration (240 lines)

### Modified Files

- ✅ `pages/2_view_all_call_summary.py` - Added RAG tab and helper functions
- ✅ `requirements.txt` - Added RAG dependencies

### Unchanged Files

- ✅ `app.py` - Main app (no changes needed)
- ✅ `src/summarizer.py` - Existing chat functions (still used in Tab 1)
- ✅ `src/plotter.py` - Chart generation (still used in Tab 1)
- ✅ `src/utils.py` - Data persistence (still used in both tabs)

---

## Technical Decisions

### Why FAISS?

- **Performance:** Fastest CPU-based similarity search (vs Chroma)
- **Maturity:** Well-tested, production-ready
- **Integration:** Seamless LangChain integration
- **Scalability:** Handles thousands of vectors efficiently
- **Cost:** Free and open-source

### Why OpenAI Embeddings?

- **Quality:** Best-in-class semantic understanding
- **Consistency:** Matches LLM (GPT-4) understanding
- **Model:** `text-embedding-3-small` is fast and cost-effective
- **Reliability:** OpenAI's proven track record

### Why Lazy Initialization?

- **Performance:** Don't create vector store unless user needs RAG chat
- **Cost:** Save API calls and embedding costs
- **UX:** Faster app startup

### Why Separate Chat Sessions?

- **Organization:** Clear separation of concerns
- **Storage:** Independent history for each chat mode
- **Testing:** Easier to test each mode separately

---

## Integration with Existing Features

### Backward Compatibility

✅ **All existing features preserved:**
- Tab 1 has exact same functionality as before
- Chat input, predefined questions, chart generation all work
- Chart images still display inline
- Clear history button still available
- No breaking changes

### Complementary Features

- **Standard Chat:** Best for chart generation and quick questions
- **RAG Chat:** Best for complex analysis and multi-faceted questions

### Data Sharing

- Both tabs use same underlying `output_data/bulk_summaries.json`
- RAG automatically picks up new summaries after reload
- Standard chat loads all summaries in-memory

---

## Summary

The RAG implementation adds powerful vector search capabilities while maintaining all existing functionality. Users can now choose between:

1. **Standard Chat** - For charts and quick summaries
2. **RAG Chat** - For intelligent semantic search and analysis

Both modes work seamlessly with the existing call summarization and analytics system.

