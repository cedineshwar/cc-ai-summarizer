import streamlit as st
from dotenv import load_dotenv
from src.utils import load_sample_call, load_file, list_files, get_next_id, save_bulk_summary, load_chat_history, save_chat_history
from src.summarizer import summarize_call, load_prompt
from src.logger import logger
from src.config import Config
import openai
import os
import pandas as pd
import json
import numpy as np
import time
from datetime import datetime


def export_chat_history_to_csv(messages):
    """Convert chat history messages to CSV format."""
    if not messages:
        return None
    
    chat_data = []
    for msg in messages:
        chat_data.append({
            'Role': msg.get('role', '').capitalize(),
            'Message': msg.get('content', ''),
            'Timestamp': msg.get('timestamp', 'N/A'),
            'Response Time (s)': msg.get('response_time', 'N/A')
        })
    
    df = pd.DataFrame(chat_data)
    return df.to_csv(index=False).encode('utf-8')



# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="Call Center AI Summarizer", layout="wide")

# Add CSS to make selectbox inputs read-only (disable text input)
st.markdown(
    """
    <style>
    /* Make selectbox inputs read-only by disabling text input */
    [data-baseweb="combobox"] input {
        pointer-events: none !important;
        background-color: #f0f0f0 !important;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# Initialize session state variables if they don't exist
if 'openai_api_key' not in st.session_state:
    st.session_state.openai_api_key = API_KEY

if 'model_choice' not in st.session_state:
    st.session_state.model_choice = Config.MODEL_NAME

if 'temperature' not in st.session_state:
    st.session_state.temperature = Config.TEMPERATURE

if 'max_tokens' not in st.session_state:
    st.session_state.max_tokens = Config.MAX_TOKENS

st.title("Call Center AI Summarizer")
st.write(":orange[AI-powered bulk call center summarization tool. Upload up to 10 call transcripts and get summaries for all.]")

# Display current configuration from .env at top of sidebar
with st.sidebar:
    with st.expander("⚙️ Configuration Info", expanded=False):
        st.markdown("**Current Settings from .env**")
        st.markdown(f"🤖 **Model:** `{Config.MODEL_NAME}`")
        st.markdown(f"🌡️ **Temperature:** `{Config.TEMPERATURE}`")
        st.markdown(f"📝 **Max Tokens:** `{Config.MAX_TOKENS}`")
        st.markdown(f"🔍 **Retriever K:** `{Config.RETRIEVER_K}`")
        st.divider()

# Sidebar configuration
cc_filelist = []
cc_filelist = list_files('input_data/')
cc_files = st.sidebar.selectbox("Select Conversations", cc_filelist, index=0)

sample = st.sidebar.checkbox("Use sample data", value=False)

st.sidebar.header("Upload / Options")
uploaded_files = st.sidebar.file_uploader("Upload call transcripts (.txt)", type=["txt"], accept_multiple_files=True)

models_list = [
    "gpt-4.1-mini-2025-04-14",
    "gpt-4.1-nano",
]
st.markdown(
    """
    <style>
    [title="Show password text"] {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True,
)
#openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key if st.session_state.openai_api_key else "", placeholder="Enter your OpenAI API key")

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password", value=st.session_state.openai_api_key if st.session_state.openai_api_key else "")

# Initialize API key in session state if user removes the key
st.session_state.openai_api_key = ""

# Only update API key if user enters a new one
if openai_api_key:
    st.session_state.openai_api_key = openai_api_key
    openai.api_key = openai_api_key
else:
    openai.api_key = st.session_state.openai_api_key

model_choice = st.sidebar.selectbox(
    "Summarization model", 
    models_list, 
    index=models_list.index(st.session_state.model_choice) if st.session_state.model_choice in models_list else 0,
    help=f"Default from config: {Config.MODEL_NAME}"
)

# Store model choice in session state for access across all pages
st.session_state.model_choice = model_choice

temperature = st.sidebar.slider(
    "Temperature", 
    0.0, 1.0, 
    st.session_state.temperature,
    help=f"Default from config: {Config.TEMPERATURE}"
)
max_tokens = st.sidebar.slider(
    "Max Tokens", 
    0, 10000, 
    st.session_state.max_tokens,
    help=f"Default from config: {Config.MAX_TOKENS}"
)
max_len = st.sidebar.slider("Max summary length (sentences)", 1, 10, 2)

# Store settings in session state for access across all pages
st.session_state.temperature = temperature
st.session_state.max_tokens = max_tokens

# Log configuration being used
logger.info(f"📊 Using Model: {model_choice} | Temp: {temperature} | Tokens: {max_tokens}")

# Process uploaded files
transcripts = {}
if uploaded_files:
    st.subheader("Uploaded Transcripts")
    tabs = st.tabs([f"File {i+1}" for i in range(len(uploaded_files))])
    
    for idx, uploaded_file in enumerate(uploaded_files):
        transcript = uploaded_file.getvalue().decode('utf-8')
        transcripts[uploaded_file.name] = transcript
        
        with tabs[idx]:
            st.text_area(f"Transcript - {uploaded_file.name}", value=transcript, height=300, label_visibility="hidden", disabled=True)

elif sample:
    sample_transcript = load_sample_call()
    transcripts["sample_call.txt"] = sample_transcript
    st.subheader("Sample Transcript")
    st.text_area("Transcript", value=sample_transcript, height=300, label_visibility="hidden", disabled=False)

elif cc_files:
    logger.debug(f"Loading file: {cc_files}")
    transcript = load_file(cc_files)
    transcripts[cc_files] = transcript
    st.subheader("Transcript")
    st.text_area("Transcript", value=transcript, height=300, label_visibility="hidden", disabled=True)

# Generate Summary button
if st.button("Generate Summary"):

    if st.session_state.openai_api_key == "your_api_key_here" or st.session_state.openai_api_key.strip() == "":
        logger.error("Please provide a valid OpenAI API Key")
        st.warning("Please enter your OpenAI API key!", icon="⚠")
        st.stop()
    else:
        openai.api_key = st.session_state.openai_api_key

    if not transcripts:
        st.warning("Please upload transcripts or enable the sample call.")
    else:
        all_summaries = []
        start_id = get_next_id()
        
        # Track timing metrics
        summarization_start = time.time()
        file_timings = {}
        
        with st.spinner(f"Summarizing {len(transcripts)} file(s)..."):
            for idx, (filename, transcript) in enumerate(transcripts.items()):
                file_start = time.time()
                logger.info(f"Starting summarization for file: {filename}")
                
                summary = summarize_call(
                    transcript,
                    model=model_choice,
                    max_sentences=max_len,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                
                file_end = time.time()
                file_time = file_end - file_start
                file_timings[filename] = file_time
                
                logger.debug(f"Summary for {filename}: {summary}")
                if summary and summary.strip():
                    try:
                        summary_json = json.loads(summary)
                        summary_json['id'] = start_id + idx
                        summary_json['filename'] = filename
                        all_summaries.append(summary_json)
                        logger.info(f"Summary generated for {filename} in {file_time:.2f}s")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decoding error for {filename}: {e}")
                        st.error(f"Failed to parse summary for {filename}")
                else:
                    logger.error(f"Failed to generate summary for {filename}")
                    st.error(f"Failed to generate summary for {filename}")
        
        summarization_end = time.time()
        total_time = summarization_end - summarization_start
        
        if all_summaries:
            st.session_state.bulk_summaries = all_summaries
            st.session_state.show_bulk_table = False
            st.session_state.summarization_time = total_time
            st.session_state.file_timings = file_timings
            st.session_state.all_summaries_count = len(all_summaries)
            
            # Save to output_data folder
            save_bulk_summary(all_summaries)
            
            logger.info(f"✅ Total summarization time: {total_time:.2f}s for {len(all_summaries)} files")

# Display summaries
if "bulk_summaries" in st.session_state and st.session_state.bulk_summaries:
    # Display persistent timing information if available
    if "summarization_time" in st.session_state:
        st.success(f"✅ Successfully summarized {st.session_state.all_summaries_count} file(s)!")
        
        # Highlight total time prominently
        st.markdown(f"""
        <div style="background-color: #000000; border-left: 4px solid #ffffff; padding: 12px; margin: 10px 0; border-radius: 4px;">
            <h3 style="margin: 0; color: #ffffff;">⏱️ Total LLM Response Time</h3>
            <p style="margin: 8px 0 0 0; font-size: 24px; font-weight: bold; color: #ffffff;">{st.session_state.summarization_time:.2f} seconds</p>
        </div>
        """, unsafe_allow_html=True)
        
        # Timing details in columns
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Total Time", f"{st.session_state.summarization_time:.2f}s", delta=None)
        with col2:
            avg_time = st.session_state.summarization_time / st.session_state.all_summaries_count if st.session_state.all_summaries_count else 0
            st.metric("Average Time/File", f"{avg_time:.2f}s")
        with col3:
            st.metric("Files Processed", st.session_state.all_summaries_count)
        
        # Detailed file timings
        with st.expander("📊 Detailed Timing Breakdown"):
            timing_data = []
            for filename, duration in st.session_state.file_timings.items():
                timing_data.append({
                    "Filename": filename,
                    "Response Time (s)": f"{duration:.2f}",
                    "Model": st.session_state.model_choice
                })
            timing_df = pd.DataFrame(timing_data)
            st.dataframe(timing_df, hide_index=True, width="stretch")
            
            # Summary statistics
            st.markdown("---")
            summary_col1, summary_col2, summary_col3 = st.columns(3)
            with summary_col1:
                min_time = min(st.session_state.file_timings.values()) if st.session_state.file_timings else 0
                st.metric("Fastest File", f"{min_time:.2f}s")
            with summary_col2:
                max_time = max(st.session_state.file_timings.values()) if st.session_state.file_timings else 0
                st.metric("Slowest File", f"{max_time:.2f}s")
            with summary_col3:
                st.metric("Total Processing", f"{st.session_state.summarization_time:.2f}s")
        
        st.markdown("---")
    
    st.subheader("Summaries")
    
    # Display JSON
    all_summaries_json = st.session_state.bulk_summaries
    summaries_json_str = json.dumps(all_summaries_json, indent=2)
    st.text_area("Summaries (JSON)", value=summaries_json_str, height=300, label_visibility="hidden")
    
    # Show as Table button
    if st.button("Show as Table"):
        st.session_state.show_bulk_table = True
    
    # Display table
    if st.session_state.get("show_bulk_table", False):
        try:
            data = pd.json_normalize(all_summaries_json)
            # Reorder columns to put id and filename first
            cols = data.columns.tolist()
            if 'id' in cols:
                cols.remove('id')
            if 'filename' in cols:
                cols.remove('filename')
            new_cols = ['id', 'filename'] + cols
            data = data[new_cols]
            st.dataframe(data, hide_index=True, width="stretch")
            # st.subheader("Displaying  as table")
            # st.table(data)
        except Exception as e:
            logger.error(f"Error displaying table: {e}")
            st.error("Failed to display summaries as table")

    # Clear button
    if st.button("Clear All"):
        st.session_state.clear()
        st.rerun()

# Chat widget popover - positioned using columns
col1, col2, col3 = st.columns([3, 1, 0.3])

with col3:
    with st.popover("💬", width="stretch"):
        st.subheader("Chat About Summaries")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = load_chat_history()
        
        # Check if summaries exist
        if "bulk_summaries" not in st.session_state or not st.session_state.bulk_summaries:
            st.info("Generate summaries first to chat about them!")
        else:
            # Display chat history
            if st.session_state.messages:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])
                        
                        # Display timestamp and response time if available
                        if "timestamp" in message:
                            if "response_time" in message:
                                st.caption(f"🕐 {message['timestamp']} | ⏱️ Response time: {message['response_time']:.2f}s")
                            else:
                                st.caption(f"🕐 {message['timestamp']}")
            else:
                st.info("Start chatting! Press Enter to send messages.")
            
            # Chat input - handles Enter key automatically
            user_input = st.chat_input("Ask a question about the summaries...")
            
            if user_input:
                # Add user message to history
                user_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.messages.append({
                    "role": "user", 
                    "content": user_input, 
                    "timestamp": user_timestamp
                })
                
                # Display user message immediately
                with st.chat_message("user"):
                    st.markdown(user_input)
                    st.caption(f"🕐 {user_timestamp}")
                
                # Prepare summaries context
                summaries_context = json.dumps(st.session_state.bulk_summaries, indent=2)
                
                # Load chat prompts
                chat_system_prompt = load_prompt('chat_system_prompt.txt')
                chat_user_prompt = load_prompt('chat_user_prompt.txt')
                chat_guardrail_prompt = load_prompt('chat_guardrail_prompt.txt')
                
                # Get LLM response
                try:
                    if not st.session_state.openai_api_key or st.session_state.openai_api_key == "your_api_key_here":
                        st.error("Please provide a valid OpenAI API Key")
                    else:
                        openai.api_key = st.session_state.openai_api_key
                        
                        response_start = time.time()
                        
                        # Format user prompt with summaries
                        formatted_user_prompt = chat_user_prompt.replace('{{PASTE ENTIRE SUMMARY HERE}}', summaries_context) if chat_user_prompt else summaries_context
                        
                        # Combine all prompts
                        full_system_prompt = f"{chat_system_prompt}\n\n{formatted_user_prompt}\n\n{chat_guardrail_prompt}" if chat_system_prompt and chat_guardrail_prompt else chat_system_prompt
                        
                        # Build complete message history with conversation context
                        messages = [{"role": "system", "content": full_system_prompt}]
                        
                        # Add ALL previous conversation messages for full context (excluding current message)
                        # This allows the LLM to understand the conversation flow and reference previous exchanges
                        for msg in st.session_state.messages[:-1]:
                            # Clean message - only include role and content
                            clean_msg = {"role": msg["role"], "content": msg["content"]}
                            messages.append(clean_msg)
                        
                        # Add the current user message at the end
                        messages.append({"role": "user", "content": user_input})
                        
                        logger.debug(f"Chat with {len(messages)-2} previous messages in conversation history")
                        
                        # Get response
                        with st.spinner("Thinking..."):
                            response = openai.chat.completions.create(
                                model=model_choice,
                                messages=messages,
                                temperature=st.session_state.temperature,
                                max_tokens=st.session_state.max_tokens
                            )
                        
                        response_time = time.time() - response_start
                        assistant_message = response.choices[0].message.content
                        
                        # Add to history and display
                        st.session_state.messages.append({
                            "role": "assistant",
                            "content": assistant_message,
                            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "response_time": response_time
                        })
                        
                        with st.chat_message("assistant"):
                            st.markdown(assistant_message)
                            st.caption(f"🕐 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | ⏱️ Response time: {response_time:.2f}s")
                        
                        # Save history
                        #save_chat_history(st.session_state.messages)
                        #logger.info(f"Chat query: {user_input[:100]} | Response time: {response_time:.2f}s")
                        
                except Exception as e:
                    st.error(f"Error: {str(e)}")
                    logger.error(f"Chat error: {str(e)}", exc_info=True)
            
            # Control buttons
            st.divider()
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("🗑️ Clear", key="clear_chat", width="stretch"):
                    st.session_state.messages = []
                    save_chat_history([])
                    st.rerun()
            
            with col2:
                if st.session_state.messages:
                    csv_data = export_chat_history_to_csv(st.session_state.messages)
                    if csv_data:
                        st.download_button(
                            label="📥 Download",
                            data=csv_data,
                            file_name=f'chat_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                            mime='text/csv',
                            key="download_chat",
                            width="stretch"
                        )
