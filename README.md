# Call Center AI Summarizer

An AI-powered Streamlit application for bulk call center summarization with intelligent chat analysis. Process up to 10 call transcripts simultaneously, generate comprehensive summaries, and interact with an LLM to analyze and extract insights from your call data.

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
  - Sentiment analysis
- **Persistent Chat History**: Chat conversations saved to `output_data/bulk_summary_chat_history.json`
- **Multi-Turn Conversations**: LLM maintains context across multiple exchanges
- **Structured Prompts**: Dedicated system, user, and guardrail prompts for chat interactions

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
- **Main App Page** (`app.py`):
  - Sidebar configuration for model, temperature, tokens, and API key
  - Tabbed transcript viewer for multi-file uploads
  - Real-time summary generation with progress indicator
  - JSON and table view options for summaries
  - Integrated chat widget for quick questions (popover format)
- **View Summaries Page** (`pages/2_view_all_call_summary.py`):
  - Full-width summaries table with download option
  - Divider-separated chat interface
  - Scrollable chat history (400px container)
  - Full context awareness for intelligent responses
- **Prompts Management Page** (`pages/1_prompts.py`):
  - Hierarchical tab structure (Summarize Prompts | Chat Prompts)
  - Sub-tabs for each prompt type (System | User | GuardRail)
  - Split-column view (Current Prompt | Edit Prompt)
  - Real-time prompt editing and saving

## 📊 Technical Specifications

### Technology Stack
- **Framework**: Streamlit 1.50.0+ (Web application framework)
- **LLM**: OpenAI API (GPT-4.1-mini-2025-04-14, GPT-4.1-nano)
- **Language**: Python 3.13+
- **Data Processing**: Pandas, NumPy, JSON

### Dependencies
```
streamlit>=1.20          # Web framework
openai                   # OpenAI API client
pandas                   # Data manipulation and tables
numpy                    # Numerical computing
python-dotenv           # Environment variable management
PyYAML                  # Configuration file parsing
```

### Architecture
- **Modular Design**:
  - `app.py` - Main Streamlit application and single-call interface
  - `src/summarizer.py` - LLM interaction and prompt management
  - `src/utils.py` - File I/O, data persistence, chat history management
  - `src/logger.py` - Application logging
  - `pages/` - Streamlit multi-page app structure

- **Session State Management**: All settings and chat history stored in Streamlit session state for cross-page access
- **File-Based Persistence**:
  - `output_data/bulk_summaries.json` - All generated summaries (appended)
  - `output_data/bulk_summary_metadata.json` - Metadata with last_id and total count
  - `output_data/chat_history.json` - Main app chat history
  - `output_data/bulk_summary_chat_history.json` - View summaries page chat history

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
LLM with Full Context
    ↓
Interactive Responses
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
  "conversationDate": "string",
  "conversationTime": "string",
  "conversationlength": "string",
  "summary": "string",
  "sentiment": "string",
  "issues": "string",
  "resolution": "string",
  "customerTone": "string",
  "customerEmotions": "string",
  "agentTone": "string",
  "agentEmotions": "string",
  "agentScore": 0-100,
  "agentScoreReason": "string",
  "agentRating": 1-5,
  "agentRatingReason": "string"
}
```

### Key Functions

#### Summarizer Module
- `load_prompt(prompt_file)` - Load prompt templates from files
- `summarize_call()` - Generate summary for single transcript with configurable parameters
- `chat_with_bulk_summaries()` - Chat with LLM about bulk summaries using chat prompts

#### Utils Module
- `load_sample_call()` - Load example call transcript
- `load_file(filename)` - Load conversation from input_data/
- `list_files(folderpath)` - List available conversations
- `get_next_id()` - Get next sequential ID for bulk summaries
- `save_bulk_summary(summaries)` - Append summaries to persistent storage
- `load_chat_history()` - Load main app chat history
- `save_chat_history(messages)` - Save main app chat history
- `load_bulk_summary_chat_history()` - Load view summaries page chat history
- `save_bulk_summary_chat_history(messages)` - Save view summaries page chat history

## 🚀 Quick Start

### Installation
```bash
# Clone repository
cd cc-ai-summarizer

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### Configuration
1. Create a `.env` file in the project root:
   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

2. Add call transcripts to `input_data/` folder (optional)

### Running the Application
```bash
streamlit run app.py
```

The app will be available at `http://localhost:8501`

## 📁 Project Structure

```
cc-ai-summarizer/
├── app.py                          # Main Streamlit app
├── README.md                       # This file
├── requirements.txt                # Python dependencies
├── .env                            # Environment variables (not in repo)
│
├── src/
│   ├── __init__.py
│   ├── summarizer.py              # LLM summarization logic
│   ├── utils.py                   # Utility functions
│   └── logger.py                  # Logging configuration
│
├── pages/
│   ├── 1_prompts.py               # Prompt editor and manager
│   └── 2_view_all_call_summary.py # Summary viewer with chat
│
├── prompt_store/
│   ├── summarize_system_prompt.txt
│   ├── summarize_user_prompt.txt
│   ├── summarize_guardrail_prompt.txt
│   ├── chat_system_prompt.txt
│   ├── chat_user_prompt.txt
│   └── chat_guardrail_prompt.txt
│
├── input_data/                     # Call transcripts for selection
├── sample_data/                    # Example call transcript
├── output_data/                    # Generated summaries and chat history
├── logs/                           # Application logs
├── configs/                        # Configuration files
└── tests/                          # Unit tests
```

## 🎮 Usage Guide

### Single Call Summarization (Main App)
1. Upload a transcript or select from available conversations
2. Configure LLM settings (model, temperature, tokens)
3. Click "Generate Summary"
4. View summary in JSON or table format
5. Download as CSV if needed

### Bulk Call Analysis
1. Click "View Summaries" in sidebar
2. View all summarized calls in the table
3. Use the chat interface to ask questions:
   - "What's the average agent score?"
   - "Which calls had negative sentiment?"
   - "List all unresolved issues"
4. Chat maintains context across multiple queries

### Managing Prompts
1. Click "Prompts Library" in sidebar
2. Select "Summarize Prompts" or "Chat Prompts" tabs
3. Choose System/User/GuardRail subtabs
4. Edit prompts in the right column
5. Click "Save" to persist changes

## 🔧 Configuration Options

### LLM Models
- `gpt-4.1-mini-2025-04-14` (Recommended for most use cases)
- `gpt-4.1-nano` (Lighter weight, faster responses)

### Temperature Range
- **0.0-0.3**: More deterministic, consistent outputs
- **0.3-0.7**: Balanced creativity and consistency
- **0.7-1.0**: More creative, varied responses

### Token Limits
- Affects response length and cost
- Default: 600 tokens for summaries, 500 for chat

## 📝 Notes

- All summaries are automatically appended to avoid data loss
- Chat history persists across sessions
- Prompt templates support dynamic substitution with `{{PLACEHOLDER}}`
- IDs are auto-incremented and persistent
- API key is stored in session state for cross-page access

## 🐛 Troubleshooting

**"Please enter your OpenAI API key"**
- Add OPENAI_API_KEY to .env file or enter in sidebar

**Chat on View Summaries page not working**
- Ensure you've entered API key in main app first
- Check that summaries have been generated

**Prompts not loading**
- Verify prompt files exist in `prompt_store/` directory
- Check file encoding is UTF-8

## 📄 License

This project is part of the Dineshwar - Capstone Project Program.
