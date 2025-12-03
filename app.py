import streamlit as st
from dotenv import load_dotenv
from src.utils import load_sample_call, load_file, list_files, get_next_id, save_bulk_summary
from src.summarizer import summarize_call
from src.logger import logger
import openai
import os
import pandas as pd
import json
import numpy as np


# Load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="Call Center AI Summarizer")

st.title("Call Center AI Summarizer")
st.write(":orange[AI-powered bulk call center summarization tool. Upload up to 10 call transcripts and get summaries for all.]")

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

openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")

API_KEY = openai_api_key if openai_api_key else API_KEY


model_choice = st.sidebar.selectbox("Summarization model", models_list, index=0)

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.3)
max_tokens = st.sidebar.slider("Token", 0, 1000, 600)
max_len = st.sidebar.slider("Max summary length (sentences)", 1, 10, 2)

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
    st.text_area("Transcript", value=sample_transcript, height=300, label_visibility="hidden", disabled=True)

elif cc_files:
    logger.debug(f"Loading file: {cc_files}")
    transcript = load_file(cc_files)
    transcripts[cc_files] = transcript
    st.subheader("Transcript")
    st.text_area("Transcript", value=transcript, height=300, label_visibility="hidden", disabled=True)

# Generate Summary button
if st.button("Generate Summary"):

    if API_KEY =="your_api_key_here" or API_KEY.strip() == "":
        logger.error("Please provide a valid OpenAI API Key")
        st.warning("Please enter your OpenAI API key!", icon="⚠")
        st.stop()
    else:
        openai.api_key = API_KEY

    if not transcripts:
        st.warning("Please upload transcripts or enable the sample call.")
    else:
        all_summaries = []
        start_id = get_next_id()
        
        with st.spinner(f"Summarizing {len(transcripts)} file(s)..."):
            for idx, (filename, transcript) in enumerate(transcripts.items()):
                logger.info(f"Starting summarization for file: {filename}")
                summary = summarize_call(
                    transcript,
                    model=model_choice,
                    max_sentences=max_len,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
                logger.debug(f"Summary for {filename}: {summary}")
                if summary and summary.strip():
                    try:
                        summary_json = json.loads(summary)
                        summary_json['id'] = start_id + idx
                        summary_json['filename'] = filename
                        all_summaries.append(summary_json)
                        logger.info(f"Summary generated for {filename}")
                    except json.JSONDecodeError as e:
                        logger.error(f"JSON decoding error for {filename}: {e}")
                        st.error(f"Failed to parse summary for {filename}")
                else:
                    logger.error(f"Failed to generate summary for {filename}")
                    st.error(f"Failed to generate summary for {filename}")
        
        if all_summaries:
            st.session_state.bulk_summaries = all_summaries
            st.session_state.show_bulk_table = False
            
            # Save to output_data folder
            save_bulk_summary(all_summaries)
            st.success(f"Successfully summarized {len(all_summaries)} file(s)!")
            st.rerun()

# Display summaries
if "bulk_summaries" in st.session_state and st.session_state.bulk_summaries:
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
            st.dataframe(data, hide_index=True, use_container_width=True)
            # st.subheader("Displaying  as table")
            # st.table(data)
        except Exception as e:
            logger.error(f"Error displaying table: {e}")
            st.error("Failed to display summaries as table")

    # Clear button
    if st.button("Clear All"):
        st.session_state.clear()
        st.rerun()



with st.chat_message("user"):
    st.write("Hello 👋")
    st.line_chart(np.random.randn(30, 3))
