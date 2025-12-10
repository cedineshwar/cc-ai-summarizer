# Call Center AI Summarizer

An AI-powered Streamlit application for bulk call center summarization with intelligent chat analysis and professional data visualization. Process up to 10 call transcripts simultaneously, generate comprehensive summaries, analyze data with interactive charts, and interact with an LLM to extract insights from your call data.

## 📋 Table of Contents

- [Quick Navigation](#-quick-navigation)
- [Features](#-features)
- [Installation & Setup](#-installation--setup)
- [Usage Guide](#-usage-guide)
- [Chart Features](#-chart-features)
- [RAG-Based Chat](#-rag-based-chat)
- [Logging System](#-logging-system)
- [Technical Specifications](#-technical-specifications)
- [Project Structure](#-project-structure)
- [Configuration](#-configuration)
- [Troubleshooting](#-troubleshooting)

---

## 🗺️ Quick Navigation

| Document | Purpose |
|----------|----------|
| **[QUICK_START.md](docs/QUICK_START.md)** | 30-second setup and first chart generation |
| **[CHART_FEATURES.md](docs/CHART_FEATURES.md)** | Complete guide to all 7 chart types with examples |
| **[RAG_CHAT.md](docs/RAG_CHAT.md)** | Vector-based semantic search and RAG chatbot |
| **[LOGGING_SYSTEM.md](docs/LOGGING_SYSTEM.md)** | Daily logging system and log viewer page |
| **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** | Quick lookup for keywords, commands, and troubleshooting |
| **[CHARTING_IMPLEMENTATION.md](docs/CHARTING_IMPLEMENTATION.md)** | Technical implementation details for charting system |
| **[IMPLEMENTATION_COMPLETE.md](docs/IMPLEMENTATION_COMPLETE.md)** | Full technical documentation and architecture |

👉 **New to the project?** Start with [QUICK_START.md](docs/QUICK_START.md)  
👉 **Want to see available charts?** Check [CHART_FEATURES.md](docs/CHART_FEATURES.md)  
👉 **Interested in semantic search?** See [RAG_CHAT.md](docs/RAG_CHAT.md)  
👉 **Need to check logs?** Visit [LOGGING_SYSTEM.md](docs/LOGGING_SYSTEM.md)  
👉 **Need quick answers?** Use [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)

---

## 🎯 Features

### Core Summarization
- **Bulk Call Summarization**: Process up to 10 call transcripts in a single batch
- **Multi-Model Support**: Choose between GPT-4.1-mini and GPT-4.1-nano models
- **Configurable Parameters**:
  - Temperature control (0.0-1.0) for response consistency
  - Token limits (0-1000) for response length
  - Summary length (1-10 sentences)
- **Flexible Input Methods**:
  - Upload call transcripts (.txt files)
  - Select from pre-loaded conversations in `input_data/` folder
  - Use sample call data for testing
- **Auto-Incrementing ID System**: Automatic ID assignment for bulk summaries with metadata tracking
- **Persistent Storage**: Save summaries to JSON with auto-appending (no data loss)
- **CSV Export**: Download summaries as CSV files

### Functional Flow Diagram

![alt text](image.png)


### Chat & Analysis
- **Interactive Chat with Summaries**: Ask questions about all summaries on the "View Summaries" page
- **Full Context Awareness**: LLM has access to complete summary data including:
  - Agent name, ID, and performance scores
  - Customer tone and emotions
  - Call duration and timing
  - Issues identified and resolutions
  - Sentiment analysis and ratings
- **Persistent Chat History**: Chat conversations saved to `output_data/bulk_summary_chat_history.json`
- **Multi-Turn Conversations**: LLM maintains context across multiple exchanges
- **Structured Prompts**: Dedicated system, user, and guardrail prompts for chat interactions
- **Predefined Questions**: 6 quick-action buttons for instant chart generation:
  - 📊 Show agent performance
  - 😊 What's the sentiment distribution?
  - ⭐ What are the agent ratings?
  - ✅ What's the resolution rate?
  - ⏱️ How long are the calls?
  - 🎯 Which agent handled the most calls?

### RAG-Based Chat (NEW)
- **Semantic Search**: FAISS-powered vector similarity search for intelligent queries
- **Vector Embeddings**: OpenAI text-embedding-3-small for high-quality embeddings
- **Context-Aware Responses**: LLM retrieves and synthesizes information from relevant summaries
- **Dual-Tab Interface**: Toggle between Standard Chat and RAG-Based Chat
- **Dynamic Vector Store**: Automatically updated with new summaries via reload button
- **Predefined RAG Questions**: 6 semantic-search optimized quick buttons:
  - 🔍 Search for resolution issues
  - 🏆 Find high-performing agents
  - 📢 What are common customer complaints?
  - 😠 Show me frustrated customer calls
  - ✨ Which calls had excellent resolution?
  - 🤝 Identify agent collaboration patterns
- **Vector Store Management**: View document count, reload with latest data
- **Technology**: FAISS for vector search, LangChain for LLM orchestration

### Logging System (NEW)
- **Daily Log Files**: One log file per day (format: `log_YYYYMMDD.txt`)
- **All Sessions Combined**: All app runs within a day append to same file
- **Log Viewer Page**: Dedicated sidebar page with search and analytics
- **3-Tab Log Interface**:
  - **Full View**: Complete log display with download option
  - **Search**: Case-insensitive search with line numbers and match highlighting
  - **Statistics**: Log level breakdown (INFO, DEBUG, WARNING, ERROR, CRITICAL)
- **Log Management Tools**:
  - Clear today's log with one click
  - View logs folder location
  - Analyze all logs (total lines and errors)
  - Delete logs older than 30 days
- **Automatic Cleanup**: Old logs deleted after 30 days
- **Session State Refresh**: Proper widget caching with refresh counters
- **Enhanced Error Handling**: Graceful fallback for empty/corrupted JSON files

### Prompt Management
- **6 Customizable Prompts** in `prompt_store/`:
  - **Summarization Prompts** (3 files):
    - `summarize_system_prompt.txt` - System instructions for summarization
    - `summarize_user_prompt.txt` - User instructions with JSON output format
    - `summarize_guardrail_prompt.txt` - Safety and quality guidelines
  - **Chat Prompts** (3 files):
    - `chat_system_prompt.txt` - System context for chat analysis
    - `chat_user_prompt.txt` - Chat instructions with structure definition
    - `chat_guardrail_prompt.txt` - Chat safety guidelines
- **Prompt Editor Page**: View and edit all prompts in organized hierarchical tabs
- **Template Substitution**: Dynamic prompt template replacement with actual data

### User Interface

#### Main App Page (`app.py`)
- Sidebar configuration for model, temperature, tokens, and API key
- Tabbed transcript viewer for multi-file uploads
- Real-time summary generation with progress indicator
- JSON and table view options for summaries
- Integrated chat widget for quick questions (popover format)

#### View Summaries Page (`pages/2_view_all_call_summary.py`)
- Full-width summaries table with download option
- Divider-separated chat interface (400px scrollable container)
- Chat history with auto-scroll functionality
- Predefined quick question buttons below chat input
- Chart generation with inline image display
- Full context awareness for intelligent responses

#### Prompts Management Page (`pages/1_prompts.py`)
- Hierarchical tab structure (Summarize Prompts | Chat Prompts)
- Sub-tabs for each prompt type (System | User | GuardRail)
- Split-column view (Current Prompt | Edit Prompt)
- Real-time prompt editing and saving

---

## 🚀 Installation & Setup

### Prerequisites
- Python 3.13+
- pip (Python package manager)

### Installation Steps

```bash
# 1. Clone/navigate to the repository
cd cc-ai-summarizer

# 2. Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create .env file with your OpenAI API key
echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
```

### Verify Installation
```bash
# Check all dependencies are installed
pip list | grep -E "streamlit|openai|pandas|matplotlib"

# Run the application
streamlit run app.py
```

The app will open at `http://localhost:8501`

**Note**: On first run, Watchdog may suggest installing additional tools. This is optional but recommended for better performance during development.

👉 **For detailed setup, see [QUICK_START.md](docs/QUICK_START.md)**

---

## 📖 Usage Guide

### Getting Started (3 Steps)
1. **Configure API Key**: Enter your OpenAI API key in the main app sidebar
2. **Upload/Select Transcripts**: Choose from uploaded files or pre-loaded conversations
3. **Generate Summaries**: Click "Generate Summary" and view results

### Using the Chart Feature

**Method 1: Click Predefined Questions**
1. Go to "View Summaries" page
2. View chat history at top
3. Click any quick question button (e.g., "📊 Show agent performance")
4. Chart auto-generates and displays in chat box

**Method 2: Type Custom Requests**
1. Go to "View Summaries" page
2. Type in the chat input box
3. System detects chart keywords and generates appropriate visualization
4. Example: "Create a bar chart showing agent performance"

**Method 3: Ask Natural Questions**
1. Ask any question about summaries
2. LLM analyzes data and responds with insights
3. Example: "Which agent has the highest score?"

### Bulk Analysis Workflow
1. Upload multiple call transcripts (up to 10)
2. Click "Generate Summary" to process all at once
3. Go to "View Summaries" page
4. Explore data with predefined charts or custom questions
5. Export data to CSV if needed

### Managing Prompts
1. Click "Prompts Library" in sidebar
2. Select "Summarize Prompts" or "Chat Prompts" tabs
3. Choose System/User/GuardRail subtabs
4. Edit prompts in the right column
5. Click "Save" to persist changes

---

## 📊 Chart Features

### Available Charts

| Chart | Triggered By | Best For |
|-------|-------------|----------|
| Agent Performance | "agent performance", "agent scores" | Comparing individual agent skills |
| Score Distribution | "score distribution", "breakdown" | Understanding team performance levels |
| Call Duration | "duration", "how long" | Identifying call patterns |
| Agent Workload | "calls per agent", "conversation count" | Load distribution analysis |
| Customer Sentiment | "sentiment", "emotion", "mood" | Customer satisfaction insights |
| Agent Ratings | "ratings", "stars" | Star rating distribution |
| Resolution Status | "resolution", "success rate" | Call resolution metrics |

### Quick Examples

**Chart Request Examples:**
```
"Show agent performance"
"What's the sentiment distribution?"
"Agent ratings breakdown"
"How many calls per agent?"
"Call duration by agent"
"What's the resolution rate?"
"Score distribution"
```

👉 **For detailed chart examples and keywords, see [CHART_FEATURES.md](docs/CHART_FEATURES.md)**

---

## 🤖 RAG-Based Chat

### Semantic Search with Vector Database

The RAG (Retrieval-Augmented Generation) chat system enables intelligent semantic search across all call summaries using FAISS vector similarity search.

### Features
- **FAISS Vector Store**: High-performance similarity search over embeddings
- **Dual-Tab Interface**: Switch between Standard Chat and RAG Chat
- **Context Retrieval**: Automatically retrieves top 5 most relevant summaries
- **Semantic Understanding**: Understands intent beyond keywords
- **Vector Store Reload**: Update index with latest summaries

### How to Use RAG Chat

**Method 1: Use Predefined RAG Questions**
1. Go to "View Summaries" page
2. Click the "🤖 RAG-Based Chat (Vector Search)" tab
3. Click any RAG-optimized quick button (e.g., "🔍 Search for resolution issues")
4. System searches vector store and returns contextual answers

**Method 2: Ask Natural Semantic Questions**
1. Type questions like:
   - "Which agents have excellent customer satisfaction?"
   - "What patterns do you see in customer complaints?"
   - "Find calls with frustrated customers and identify root causes"
2. FAISS finds semantically similar documents
3. LLM synthesizes comprehensive answer

**Method 3: Reload Vector Store**
1. Click "🔄 Reload Vector Store" button to refresh with new summaries
2. Button shows current document count in index
3. Useful after adding new summaries

### Architecture
```
Summaries (JSON) 
    ↓
OpenAI Embeddings (text-embedding-3-small)
    ↓
FAISS Vector Index (1536 dimensions)
    ↓
Semantic Search (top-k results)
    ↓
LangChain Chat (context window)
    ↓
LLM Response (GPT-4.1-mini/nano)
```

### Technology Stack
- **FAISS**: Fast similarity search with efficient indexing
- **LangChain**: LLM orchestration and chat management
- **OpenAI**: Embeddings and chat models
- **Python**: Vector operations and data handling

👉 **For detailed RAG documentation, see [RAG_CHAT.md](docs/RAG_CHAT.md)**

---

## 📊 Logging System

### Daily Log Files & Log Viewer Page

All application events are logged to daily files with a dedicated viewer page for search, analysis, and management.

### Features
- **Daily Format**: One log file per day (e.g., `log_20251208.txt`)
- **All Sessions**: All app runs within a day append to the same file
- **3-Tab Log Viewer**:
  - **Full View**: Complete log display with download option
  - **Search**: Case-insensitive search with line numbers
  - **Statistics**: Log level breakdown and file analytics
- **Log Management**:
  - Clear today's log with confirmation
  - View logs folder location
  - Analyze all logs (totals and error counts)
  - Auto-delete logs older than 30 days

### How to Use Log Viewer

**Access Logs**:
1. Click "View Logs" in sidebar
2. Select log file from dropdown
3. Choose tab (Full View, Search, or Stats)

**Search Logs**:
1. Go to "Search" tab
2. Type search term (case-insensitive)
3. Results show line numbers and match count
4. Click to view context

**Clear Today's Logs**:
1. Click "Clear Today's Log" button
2. Confirm action
3. Log file cleared with timestamp header
4. Full View tab updates immediately

**Download Logs**:
1. Select log file
2. Click "📥 Download" button
3. File downloads to your device

### Log Levels
- **DEBUG**: Detailed information (data operations, processing)
- **INFO**: General information (startup, successful operations)
- **WARNING**: Potential issues (deprecated features)
- **ERROR**: Error conditions (API failures, file errors)
- **CRITICAL**: Critical failures (system crashes)

### Typical Log Growth
- **Per Day**: ~50KB (typical usage)
- **Per Entry**: ~100-150 bytes
- **Retention**: 30+ days (auto-delete after 30 days)

👉 **For detailed logging documentation, see [LOGGING_SYSTEM.md](docs/LOGGING_SYSTEM.md)**

---

## 💻 Technical Specifications

### Technology Stack
| Component | Technology |
|-----------|-----------|
| **Framework** | Streamlit 1.50.0+ |
| **LLM** | OpenAI API (GPT-4.1-mini, GPT-4.1-nano) |
| **Language** | Python 3.13+ |
| **Vector Search** | FAISS (Retrieval-Augmented Generation) |
| **LLM Orchestration** | LangChain with ChatOpenAI |
| **Data Processing** | Pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |
| **File Monitoring** | Watchdog |
| **Logging** | Python logging module |

### Dependencies
```
streamlit>=1.20                    # Web framework
openai>=1.0                        # OpenAI API client
pandas                             # Data manipulation and tables
numpy                              # Numerical computing
python-dotenv                      # Environment variable management
PyYAML                             # Configuration file parsing
matplotlib                         # Chart generation
seaborn                            # Statistical visualization
watchdog                           # File monitoring for auto-reload
faiss-cpu>=1.7.4                   # Vector similarity search (RAG)
langchain>=0.0.200                 # LLM orchestration framework
langchain-openai>=0.0.2            # OpenAI integration for LangChain
langchain-community                # Community modules for LangChain
```

### Architecture

**Modular Design:**
- `app.py` - Main Streamlit application and single-call interface
- `src/summarizer.py` - LLM interaction and prompt management
- `src/utils.py` - File I/O, data persistence, chat history management (with graceful empty file handling)
- `src/logger.py` - Application logging with daily file format
- `src/plotter.py` - Chart generation (7 chart types)
- `src/vector_store.py` - FAISS vector store management for RAG
- `src/rag_chat.py` - RAG chatbot with LangChain integration
- `pages/1_prompts.py` - Prompt editor and manager
- `pages/2_view_all_call_summary.py` - Summary viewer with dual chat tabs (Standard + RAG)
- `pages/3_view_logs.py` - Log viewer with search and analytics
- `pages/` - Streamlit multi-page app structure

**Session State Management:** All settings, chat history, vector store, and refresh counters stored in Streamlit session state for cross-page access

**File-Based Persistence:**
- `output_data/bulk_summaries.json` - All generated summaries (appended)
- `output_data/bulk_summary_metadata.json` - Metadata with last_id and total count
- `output_data/app_chat_history.json` - Main app chat history
- `output_data/bulk_summary_chat_history.json` - View summaries page chat history (with empty file handling)
- `logs/log_YYYYMMDD.txt` - Daily application logs (one file per day)
- `vector_store/faiss_index` - FAISS vector store for RAG
- `vector_store/faiss_metadata.pkl` - Vector store metadata and document info

### Data Flow
```
Input Transcripts
    ↓
[Summarization Pipeline]
    ↓
JSON Output (with auto-incrementing ID)
    ↓
Database (bulk_summaries.json)
    ↓
[Chat Analysis Interface]
    ↓
[Chart Generation System]
    ↓
LLM with Full Context
    ↓
Interactive Responses with Visualizations
```

### JSON Summary Structure
```json
{
  "id": 1,
  "filename": "call_001.txt",
  "agentName": "string",
  "agentId": "string",
  "department": "string",
  "customerName": "string",
  "conversationDate": "2025-01-15",
  "conversationTime": "14:30 - 14:45",
  "conversationlength": "15 minutes",
  "callSummary": "string (main conversation summary)",
  "summary": "string (extracted summary)",
  "sentiment": "string (customer sentiment: happy, frustrated, neutral, etc.)",
  "issues": "string (identified issues from call)",
  "resolution": "string (how issue was resolved)",
  "customerTone": "string (tone of customer voice)",
  "customerEmotions": "string (detected customer emotions)",
  "agentTone": "string (tone of agent voice)",
  "agentEmotions": "string (detected agent emotions)",
  "agentScore": "0-100 (numerical score)",
  "agentScoreReason": "string (explanation of agent score)",
  "agentRating": "1-5 (star rating)",
  "agentRatingReason": "string (explanation of agent rating)",
  "resolutionStatus": "string (Resolved/Unresolved with context)"
}
```

### Key Functions

**Summarizer Module:**
- `load_prompt(prompt_file)` - Load prompt templates from files
- `summarize_call()` - Generate summary for single transcript
- `chat_with_bulk_summaries()` - Chat with LLM about bulk summaries

**Plotter Module:**
- `detect_chart_request(user_message)` - Intelligent chart type detection (keyword-based)
- `generate_chart(chart_type, summaries)` - Main dispatcher for chart generation
- `generate_agent_performance_bar_chart()` - Agent scores bar chart (0-100 scale)
- `generate_agent_score_distribution_pie()` - Performance tier distribution pie chart
- `generate_conversation_duration_chart()` - Call duration by agent bar chart
- `generate_agent_vs_conversation_count()` - Workload distribution bar chart
- `generate_customer_sentiment_distribution()` - Customer emotion pie chart
- `generate_agent_rating_distribution()` - 1-5 star rating bar chart
- `generate_resolution_status_chart()` - Resolution status pie chart
- `encode_plot_to_base64()` - Convert matplotlib figures to base64 for embedding

**Vector Store Module (RAG):**
- `create_vector_store(documents)` - Create FAISS index from documents
- `load_vector_store()` - Load existing or create new FAISS index
- `similarity_search(query, k=5)` - Find k most similar documents
- `reload_vector_store()` - Refresh vector store with latest summaries

**RAG Chat Module:**
- `initialize(api_key, model, temperature)` - Setup RAG chatbot
- `get_rag_response(user_message, chat_history)` - Generate RAG-enhanced response
- `reload_vector_store()` - Update vector store in chatbot

**Utils Module:**
- `load_sample_call()` - Load example call transcript
- `load_file(filename)` - Load conversation from input_data/
- `list_files(folderpath)` - List available conversations (filters to .txt files only)
- `get_next_id()` - Get next sequential ID for bulk summaries
- `save_bulk_summary(summaries)` - Append summaries persistently to JSON
- `load_bulk_summary()` - Load existing summaries from storage
- `load_chat_history()` / `save_chat_history()` - Main app chat persistence (with empty file handling)
- `load_bulk_summary_chat_history()` / `save_bulk_summary_chat_history()` - View summaries chat persistence (with empty file handling)

**Logger Module:**
- `get_logs_dir()` - Return logs directory path
- `get_today_log_file()` - Get today's log file in YYYYMMDD format
- `get_all_log_files()` - Return all log files sorted by date
- `clear_today_log()` - Clear today's log with timestamp header
- `setup_logger()` - Configure and return logger instance

---

## 📁 Project Structure

```
cc-ai-summarizer/
├── app.py                              # Main Streamlit app
├── README.md                           # Main documentation (you are here)
├── requirements.txt                    # Python dependencies
├── .env                                # Environment variables (not in repo)
│
├── 📚 Documentation Files
│   ├── QUICK_START.md                 # 30-second setup guide
│   ├── CHART_FEATURES.md              # Complete chart documentation
│   ├── RAG_CHAT.md                    # RAG-based semantic search guide (NEW)
│   ├── LOGGING_SYSTEM.md              # Logging and log viewer guide (NEW)
│   ├── QUICK_REFERENCE.md             # Quick lookup guide
│   ├── CHARTING_IMPLEMENTATION.md     # Technical implementation
│   └── IMPLEMENTATION_COMPLETE.md     # Full technical specs
│
├── src/
│   ├── __init__.py
│   ├── summarizer.py                  # LLM summarization logic
│   ├── plotter.py                     # Chart generation (7 types)
│   ├── utils.py                       # Utility functions with graceful error handling
│   ├── logger.py                      # Daily logging configuration
│   ├── vector_store.py                # FAISS vector store for RAG (NEW)
│   └── rag_chat.py                    # RAG chatbot with LangChain (NEW)
│
├── pages/
│   ├── 1_prompts.py                   # Prompt editor and manager
│   ├── 2_view_all_call_summary.py     # Summary viewer with dual chat tabs (Standard + RAG)
│   └── 3_view_logs.py                 # Log viewer with search and stats (NEW)
│
├── prompt_store/
│   ├── summarize_system_prompt.txt
│   ├── summarize_user_prompt.txt
│   ├── summarize_guardrail_prompt.txt
│   ├── chat_system_prompt.txt
│   ├── chat_user_prompt.txt
│   └── chat_guardrail_prompt.txt
│
├── input_data/                        # Call transcripts for selection
├── sample_data/                       # Example call transcript
├── output_data/                       # Generated summaries and chat history
│   ├── bulk_summaries.json
│   ├── bulk_summary_metadata.json
│   ├── app_chat_history.json
│   └── bulk_summary_chat_history.json
├── vector_store/                      # FAISS vector store files (NEW)
│   ├── faiss_index
│   └── faiss_metadata.pkl
├── logs/                              # Daily application logs (NEW)
│   ├── log_20251208.txt               # Today's log
│   ├── log_20251207.txt
│   └── ... (up to 50+ historical logs)
├── configs/                           # Configuration files
└── tests/                             # Unit tests
```

---

## ⚙️ Configuration

### LLM Models
- **gpt-4.1-mini-2025-04-14** (Recommended for most use cases)
- **gpt-4.1-nano** (Lighter weight, faster responses)

### Temperature Range
| Range | Behavior | Use Case |
|-------|----------|----------|
| 0.0-0.3 | Deterministic, consistent | Production summaries |
| 0.3-0.7 | Balanced | General analysis |
| 0.7-1.0 | Creative, varied | Brainstorming |

### Token Limits
- **Default**: 600 tokens for summaries, 500 for chat
- **Adjustable**: 0-1000 tokens depending on needs
- **Note**: Higher tokens = longer responses but higher API costs

### Environment Variables
Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

---

## 🔧 Troubleshooting

### Common Issues

**"Please enter your OpenAI API key"**
- ✅ Add OPENAI_API_KEY to .env file
- ✅ Or enter API key in main app sidebar
- ✅ Ensure the key is valid and has quota

**Charts not generating**
- ✅ Check API key is configured
- ✅ Ensure summaries have been generated first
- ✅ Try using simpler keywords (e.g., "sentiment" vs "customer mood")
- ✅ Check logs in `/logs/` folder for errors

**Chat on View Summaries page not working**
- ✅ Ensure you've entered API key in main app first
- ✅ Check that summaries have been generated
- ✅ Try refreshing the page (Ctrl+R)
- ✅ Clear browser cache if issues persist

**Prompts not loading**
- ✅ Verify prompt files exist in `prompt_store/` directory
- ✅ Check file encoding is UTF-8
- ✅ Ensure file names match exactly (case-sensitive)

**Application runs slowly**
- ✅ Install Watchdog: `pip install watchdog`
- ✅ Check API response times
- ✅ Reduce number of summaries being processed

**Star symbols not displaying in charts**
- ✅ This is normal - matplotlib has font limitations
- ✅ Stars are displayed as "1 Star", "2 Stars", etc. instead
- ✅ No impact on chart functionality

### Debug Mode
Check application logs:
```bash
tail -f logs/log_*.txt
```

Logs include:
- API calls and responses
- File I/O operations
- Chart generation events
- Error messages with stack traces

👉 **For more troubleshooting, see [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)**

---

## 📝 Notes & Best Practices

- **All summaries are automatically appended** to avoid data loss
- **Chat history persists** across sessions
- **Prompt templates support dynamic substitution** with `{{PLACEHOLDER}}`
- **IDs are auto-incremented** and persistent
- **API key is stored in session state** for cross-page access
- **Charts are generated on-demand** (not cached) for fresh data
- **Maximum 10 transcripts** per batch for optimal performance

---

## 🤝 Support & Feedback

For issues, questions, or feedback:
1. Check [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) - Known issues and solutions
2. Review application logs in `/logs/` directory
3. Check Streamlit console error messages
4. Verify API key and quota in OpenAI dashboard
5. Test with sample data first if issues persist

---

## 📄 License

This project is part of the Dineshwar - Capstone Project Program.

---

## 📞 Support

| Issue | Resource |
|-------|----------|
| Getting started | [QUICK_START.md](docs/QUICK_START.md) |
| Chart usage | [CHART_FEATURES.md](docs/CHART_FEATURES.md) |
| RAG semantic search | [RAG_CHAT.md](docs/RAG_CHAT.md) |
| Logging and log viewer | [LOGGING_SYSTEM.md](LOGGING_SYSTEM.md) |
| Quick answers | [QUICK_REFERENCE.md](QUICK_REFERENCE.md) |
| Technical details | [IMPLEMENTATION_COMPLETE.md](IMPLEMENTATION_COMPLETE.md) |
| Implementation details | [CHARTING_IMPLEMENTATION.md](CHARTING_IMPLEMENTATION.md) |

---

## ✨ Key Highlights

✅ **7 Professional Charts** - Bar, pie, and distribution charts for comprehensive analytics  
✅ **RAG-Based Semantic Search** - FAISS vector database for intelligent document retrieval  
✅ **Dual Chat Interface** - Standard chat with charts + RAG chat with vector search  
✅ **Daily Logging System** - One log file per day with dedicated viewer page  
✅ **Intelligent Detection** - Keywords automatically trigger relevant visualizations  
✅ **Persistent Data** - All summaries and chat history saved automatically with graceful error handling  
✅ **Customizable Prompts** - Edit system, user, and guardrail prompts in real-time  
✅ **Full Context Chat** - LLM has access to complete summary data for accurate analysis  
✅ **Log Search & Analytics** - Find errors, analyze patterns with case-insensitive search  
✅ **Auto-Scroll Chat** - New messages automatically visible without manual scrolling  
✅ **Vector Store Management** - Reload vector index with new summaries on demand  
✅ **CSV Export** - Download summaries for external analysis  
✅ **Production Ready** - Tested, documented, and deployed-ready  

---

**Version**: 1.0.1 | **Last Updated**: December 2025 | **Status**: Production Ready ✅

