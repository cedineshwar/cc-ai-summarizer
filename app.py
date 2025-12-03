import streamlit as st
from dotenv import load_dotenv
from src.utils import load_sample_call, load_file, list_files
from src.summarizer import summarize_call
from src.logger import logger
import openai
import os
import pandas as pd
import json

# from src.summarizer import summarize_call

#load environment variables from .env file
load_dotenv()

API_KEY = os.getenv("OPENAI_API_KEY")
st.set_page_config(page_title="Call Center AI Summarizer")

st.title("Call Center AI Summarizer")
st.write(":orange[AI-powered call center summarization tool. Upload a call transcript and get a concise summary.]") 

cc_filelist = []

cc_filelist = list_files('input_data/')
cc_files = st.sidebar.selectbox("Select Convserations", cc_filelist , index =0) 

sample = st.sidebar.checkbox("Use sample data", value=False)

st.sidebar.header("Upload / Options")
uploaded_file = st.sidebar.file_uploader("Upload a call transcript (.txt)", type=["txt"])
models_list = [
                "gpt-4.1-mini-2025-04-14",
                "gpt-4.1-nano",
                
                # "gpt-5-nano",
                # "gpt-5-mini",
                # "o4-mini"
                ]

# models_list = [
#                 "gpt-4.1-nano",
#                 "gpt-4.1-mini-2025-04-14",
#                 "gpt-5-nano-2025-08-07",
#                 "gpt-5-mini-2025-08-07",
#                 "o4-mini-2025-04-16"]
openai_api_key = st.sidebar.text_input("OpenAI API Key", type="password")
API_KEY= openai_api_key if openai_api_key else API_KEY
openai.api_key = API_KEY    


model_choice = st.sidebar.selectbox("Summarization model", models_list, index=0)
#,"chatgpt-4o-latest", "gpt-4.1-2025-04-14",,"gpt-5-mini-2025-08-07"


# # Inject CSS to change the slider color
# st.markdown("""
# <style>
# .stSlider > div[data-baseweb="slider"] > div > div {
#   background: linear-gradient(to right, #82CFD0 0%, #82CFD0 50%, #fff 50%, #fff 100%);
# }
# </style>
# """, unsafe_allow_html=True)

temperature = st.sidebar.slider("Temperature", 0.0, 1.0, 0.7)
# st.write(f"Temperature set to: {temperature}")

max_tokens = st.sidebar.slider("Token", 0, 1000, 300
                               )

max_len = st.sidebar.slider("Max summary length (sentences)", 1, 10, 3)

if sample and uploaded_file is None:
    transcript = load_sample_call()
elif uploaded_file is not None:
    transcript = uploaded_file.getvalue().decode('utf-8')
elif cc_files is not None:
    logger.debug(f"Loading file: {cc_files}")
    transcript = load_file(cc_files)
else:
    transcript = ""

st.subheader("Transcript")

st.text_area("Transcript", value=transcript, height=400, label_visibility="hidden")

if st.button("Generate Summary"):
    if not transcript.strip():
        st.warning("Please upload a transcript or enable the sample call.")
    else:
        with st.spinner("Summarizing..."):
            logger.info(f"Starting summarization with model: {model_choice}")
            summary = summarize_call(transcript, model=model_choice, max_sentences=max_len, temperature=temperature, max_tokens=max_tokens)
            if summary.strip() is None:
                st.error("Failed to generate summary. Please try again.")
            else:
                st.session_state.summary = summary
                st.session_state.show_table = False
                st.rerun()

if "summary" in st.session_state:
    st.subheader("Summary")
    summary = st.session_state.summary
    logger.info("Summary generated successfully.")
    logger.debug(f"Summary content: {summary}")
    st.text_area("Summary", value=summary, height=400, label_visibility="hidden")
    
    # Convert summary to dataframe for better visualization
    try:
        summary_json = json.loads(summary)
        data = pd.json_normalize(summary_json)
        
        if st.button("Show as Table"):
            st.session_state.show_table = True
        
        if st.session_state.get("show_table", False):
            st.dataframe(data, hide_index=True)
            
    except json.JSONDecodeError as e:
        logger.error(f"JSON decoding error: {e}")
        st.error("Failed to parse summary into JSON format.")

# Clear chat history button
if st.button("Clear Chat History"):
    st.session_state.clear()
    st.rerun()


