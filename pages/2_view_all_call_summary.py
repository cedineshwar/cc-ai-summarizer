#Read the summary from a file and display it as table with filters and download option as needed
import streamlit as st
import pandas as pd
import os
import json
import openai
from src.utils import save_bulk_summary, get_next_id, load_bulk_summary_chat_history, save_bulk_summary_chat_history
from src.logger import logger
from src.summarizer import chat_with_bulk_summaries

def load_summaries(file_path):
    """Load summaries from a JSON file."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            summaries = json.load(f)
            logger.debug(f"Loaded {len(summaries)} summaries from {file_path}")
            return summaries
    except FileNotFoundError:
        logger.error(f"Summaries file not found: {file_path}")
        return []
    except json.JSONDecodeError:
        logger.error(f"Error decoding JSON from file: {file_path}")
        return []

def format_summaries_for_context(summaries: list) -> str:
    """Format summaries into JSON format for the LLM context."""
    return json.dumps(summaries, indent=2)
    
def main():
    st.title("View Summaries")
    
    summaries_file = os.path.join('output_data', 'bulk_summaries.json')
    summaries = load_summaries(summaries_file)
    
    if not summaries:
        st.info("No summaries available.")
        return
    
    # ==================== TOP SECTION: SUMMARIES TABLE ====================
    st.subheader("📊 Call Summaries")
    
    # Convert summaries to DataFrame for better display
    df = pd.DataFrame(summaries)
    
    # Display the DataFrame with Streamlit
    st.dataframe(df, width="stretch", hide_index=True)
    
    # Provide download option
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download summaries as CSV",
        data=csv,
        file_name='summaries.csv',
        mime='text/csv',
    )
    
    # Divider
    st.divider()
    
    # ==================== BOTTOM SECTION: CHAT INTERFACE ====================
    st.subheader("💬 Chat with Summaries")
    
    # Initialize session state for bulk summary chat
    if 'bulk_summary_chat_history' not in st.session_state:
        st.session_state.bulk_summary_chat_history = load_bulk_summary_chat_history()
    
    # Get API key and model settings from session state
    api_key = st.session_state.get('openai_api_key')
    model = st.session_state.get('model_choice', 'gpt-4.1-mini-2025-04-14')
    temperature = st.session_state.get('temperature', 0.7)
    max_tokens = st.session_state.get('max_tokens', 150)
    
    # Check if API key is available
    if not api_key or api_key.strip() == "" or api_key == "your_api_key_here":
        st.warning("Please enter your OpenAI API key in the main app page first!")
        return
    
    # Set the API key for this session
    openai.api_key = api_key
    
    # Display chat history (scrollable)
    with st.container(height=400, border=True):
        for message in st.session_state.bulk_summary_chat_history:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
    
    # Chat input at the bottom
    if prompt := st.chat_input("Ask about the summaries...", key="bulk_summary_chat_input"):
        # Add user message to history
        st.session_state.bulk_summary_chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get summaries context for LLM
        summaries_context = format_summaries_for_context(summaries)
        
        # Get response from LLM using chat prompts
        with st.spinner("Analyzing summaries..."):
            response = chat_with_bulk_summaries(
                user_message=prompt,
                chat_history=st.session_state.bulk_summary_chat_history[:-1],  # Exclude the current user message as it's already in context
                summaries_context=summaries_context,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens
            )
        
        if response:
            # Add assistant message to history
            st.session_state.bulk_summary_chat_history.append({
                "role": "assistant",
                "content": response
            })
            
            # Save updated history
            save_bulk_summary_chat_history(st.session_state.bulk_summary_chat_history)
            
            # Display assistant message
            with st.chat_message("assistant"):
                st.markdown(response)
            
            # Rerun to show the new messages
            st.rerun()
        else:
            st.error("Failed to get response from LLM. Please check logs.")

if __name__ == "__main__":
    main()

