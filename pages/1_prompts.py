import streamlit as st
from src.utils import load_file, load_sample_call

st.header("# Prompts Library 📚") 
textarea_height =375

sp_tab, up_tab, gp_tab = st.tabs(["System Prompt", "User Prompt", "GuardRail Prompt"])

def load_sp_prompt():
    with open("prompt_store/system_prompt.txt", "r") as f:
        sysprompt = f.read()
    sysprompt = st.text_area("System Prompt", value=sysprompt, height=textarea_height)

    if st.button("Save System Prompt"):
        if sysprompt.strip() == "":
            st.warning("System Prompt cannot be empty.")
        else:
            with open("prompt_store/system_prompt.txt", "w") as f:
                f.write(sysprompt)
            st.success("System Prompt saved successfully.")

def load_up_prompt():
    with open("prompt_store/summarize_user_prompt.txt", "r") as f:
        userprompt = f.read()
    userprompt = st.text_area("User Prompt", value=userprompt, height=textarea_height)

    if st.button("Save User Prompt"):
        if userprompt.strip() == "":
            st.warning("User Prompt cannot be empty.")
        else:
            with open("prompt_store/summarize_user_prompt.txt", "w") as f:
                f.write(userprompt)
            st.success("User Prompt saved successfully.")

def load_gp_prompt():
    with open("prompt_store/summarize_guardrail_prompt.txt", "r") as f:
        guardrailprompt = f.read()
    guardrailprompt = st.text_area("GuardRail Prompt", value=guardrailprompt, height=textarea_height)

    if st.button("Save GuardRail Prompt"):
        if guardrailprompt.strip() == "":
            st.warning("GuardRail Prompt cannot be empty.")
        else:
            with open("prompt_store/summarize_guardrail_prompt.txt", "w") as f:
                f.write(guardrailprompt)
            st.success("GuardRail Prompt saved successfully.")


with sp_tab:    
    st.subheader("System Prompt")
    load_sp_prompt()

with up_tab:    
    st.subheader("User Prompt")
    load_up_prompt()

with gp_tab:    
    st.subheader("GuardRail Prompt")  
    load_gp_prompt()







# st.code("""
# Summarize the following call transcript in {max_sentences} sentences:
# {transcript}
# """)
# st.write("This prompt is used for generating a concise summary of the entire call transcript.") 