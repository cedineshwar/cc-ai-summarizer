# cc-ai-summarizer

Streamlit project skeleton for an AI-powered call center summarization tool.

## Structure

- `app.py` - Streamlit frontend
- `src/` - Python package with summarization logic and utilities
- `configs/` - configuration files
- `sample_data/` - example call transcript
- `tests/` - unit tests

## Quickstart

1. Create a virtual environment:
   ```
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```

2. Run the app:
   ```
   streamlit run app.py
   ```

This skeleton includes a simple placeholder summarizer (`src/summarizer.py`) — replace the summarization function with your preferred model or API (e.g., OpenAI or HuggingFace).
