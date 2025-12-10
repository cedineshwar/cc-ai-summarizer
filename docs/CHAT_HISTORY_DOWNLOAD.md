# Chat History Download Feature

## Overview
Added download functionality for chat histories across the entire application. Users can now export their conversation logs as CSV files for record-keeping and analysis.

## Changes Made

### 1. **app.py** (Main Application)
- **Added Helper Function**: `export_chat_history_to_csv(messages)`
  - Converts chat messages to pandas DataFrame
  - Includes fields: Role, Message, Timestamp, Response Time
  - Returns CSV-encoded data for download

- **Updated Chat Section**: 
  - Replaced single "Clear Chat History" button with two-column layout:
    - **Col 1**: Clear Chat History button
    - **Col 2**: Download Chat History button (visible only when messages exist)
  - Download button generates timestamped filename: `chat_history_YYYYMMDD_HHMMSS.csv`

### 2. **pages/2_view_all_call_summary.py** (View Summaries Page)

#### Standard Chat Tab:
- **Updated Buttons Layout**:
  - **Col 1**: Clear Chat History button
  - **Col 2**: Download Chat History button (visible only when messages exist)
  - Download filename: `chat_history_YYYYMMDD_HHMMSS.csv`

#### RAG Chat Tab:
- **Updated Buttons Layout** (now 4 columns):
  - **Col 1**: Clear RAG Chat History button
  - **Col 2**: Download Chat History button (visible only when messages exist)
  - **Col 3**: Reload Vector Store button
  - **Col 4**: (Reserved for future use)
  - Download filename: `rag_chat_history_YYYYMMDD_HHMMSS.csv`

## CSV Export Format

| Column | Description |
|--------|-------------|
| Role | User or Assistant (capitalized) |
| Message | Full chat message content |
| Timestamp | ISO format date/time (YYYY-MM-DD HH:MM:SS) |
| Response Time (s) | LLM response duration in seconds (N/A for user messages) |

## Features

✅ **Conditional Display**: Download button only shows when chat history exists
✅ **Timestamped Filenames**: Each download has unique timestamp to prevent overwrites
✅ **Clean CSV Format**: All chat metadata preserved in downloadable format
✅ **User & Assistant Messages**: Both message types included with proper roles
✅ **Performance Tracking**: Response times captured for analysis
✅ **Consistent UI**: Same export format across all chat interfaces

## Usage

1. **Main App Chat**:
   - Have a chat conversation with the summaries
   - Click "📥 Download Chat History" to export as CSV
   - File saves as: `chat_history_20250209_143052.csv`

2. **View Summaries - Standard Chat**:
   - Ask questions in the chart-enabled chat
   - Click "📥 Download Chat History" to export
   - Includes all LLM responses and timestamps

3. **View Summaries - RAG Chat**:
   - Use vector search to query summaries
   - Click "📥 Download Chat History" to export RAG responses
   - File saves as: `rag_chat_history_20250209_143052.csv`

## Benefits

- **Audit Trail**: Keep complete records of all conversations
- **Analysis**: Export data for further analysis or reporting
- **Compliance**: Maintain chat history logs for compliance requirements
- **Backup**: Create local backups of conversations
- **Performance Metrics**: Track LLM response times across sessions

## Files Modified
- `/app.py` - Added helper function and updated chat buttons
- `/pages/2_view_all_call_summary.py` - Added helper function and updated chat buttons for both tabs

## No Breaking Changes
- All existing functionality preserved
- Backward compatible with existing code
- Download buttons only appear when there's chat history to export
