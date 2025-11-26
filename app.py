import streamlit as st 
from src.summarizer import summarize_call
from src.utils import load_sample_call, load_file, list_files


st.set_page_config(page_title="Call Center AI Summarizer")

st.title("Call Center AI Summarizer")
st.write(":orange[AI-powered call center summarization tool. Upload a call transcript and get a concise summary.]") 

cc_filelist = []

# cc_files = st.sidebar.selectbox("Select Convserations", cc_filelist , index =0)

# cc_files = st.sidebar.checkbox("Fetch Conversation Files", value=False)
cc_filelist = list_files('input_data/')
cc_files = st.sidebar.selectbox("Select Convserations", cc_filelist , index =0) 



    # if st.sidebar.button("Refresh File List"):
#     cc_filelist = list_files('input_data/')
#     cc_files = st.sidebar.selectbox("Select Convserations", cc_filelist , index =0)  

sample = st.sidebar.checkbox("Use sample data", value=False)

st.sidebar.header("Upload / Options")
uploaded_file = st.sidebar.file_uploader("Upload a call transcript (.txt)", type=["txt"])

model_choice = st.sidebar.selectbox("Summarization model", ["gpt-4.1-nano-2025-04-14","gpt-5-nano-2025-08-07","o4-mini-2025-04-16"], index=0)
#,"chatgpt-4o-latest", "gpt-4.1-2025-04-14",,"gpt-5-mini-2025-08-07"

max_len = st.sidebar.slider("Max summary length (sentences)", 1, 10, 3)

if sample and uploaded_file is None:
    transcript = load_sample_call()
elif uploaded_file is not None:
    transcript = uploaded_file.getvalue().decode('utf-8')
elif cc_files is not None:
    st.write(cc_files)
    transcript = load_file(cc_files)
else:
    transcript = ""

st.subheader("Transcript")
st.text_area("", value=transcript, height=400)


if st.button("Generate Summary"):
    if not transcript.strip():
        st.warning("Please upload a transcript or enable the sample call.")
    else:
        with st.spinner("Summarizing..."):
            summary = summarize_call(transcript, model=model_choice, max_sentences=max_len)
        st.subheader("Summary")
        st.write(summary)
