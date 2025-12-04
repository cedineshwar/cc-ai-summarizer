import streamlit as st
from src.utils import load_file, load_sample_call

st.header("📚 Prompts Library")
textarea_height = 500

# Main tabs for Summarize vs Chat prompts
main_tabs = st.tabs(["Summarize Prompts", "Chat Prompts"])

# ==================== SUMMARIZE PROMPTS ====================
with main_tabs[0]:
    st.subheader("Call Summarization Prompts")
    
    # Tabs for different summarize prompt types
    sum_sp_tab, sum_up_tab, sum_gp_tab = st.tabs(["System Prompt", "User Prompt", "GuardRail Prompt"])
    
    def load_summarize_sp_prompt():
        with open("prompt_store/summarize_system_prompt.txt", "r") as f:
            sysprompt = f.read()
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text("Current Prompt:")
            st.text_area("System Prompt View", value=sysprompt, height=textarea_height, disabled=True, label_visibility="collapsed")
        #with col2:
            # st.text("Edit Prompt:")
            # sysprompt_edited = st.text_area("System Prompt Edit", value=sysprompt, height=textarea_height, label_visibility="collapsed", key="sum_sp_edit")
            # if st.button("Save System Prompt", key="sum_sp_save"):
            #     if sysprompt_edited.strip() == "":
            #         st.warning("System Prompt cannot be empty.")
            #     else:
            #         with open("prompt_store/summarize_system_prompt.txt", "w") as f:
            #             f.write(sysprompt_edited)
            #         st.success("System Prompt saved successfully.")

    def load_summarize_up_prompt():
        with open("prompt_store/summarize_user_prompt.txt", "r") as f:
            userprompt = f.read()
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text("Current Prompt:")
            st.text_area("User Prompt View", value=userprompt, height=textarea_height, disabled=True, label_visibility="collapsed")
        # with col2:
        #     st.text("Edit Prompt:")
        #     userprompt_edited = st.text_area("User Prompt Edit", value=userprompt, height=textarea_height, label_visibility="collapsed", key="sum_up_edit")
        #     if st.button("Save User Prompt", key="sum_up_save"):
        #         if userprompt_edited.strip() == "":
        #             st.warning("User Prompt cannot be empty.")
        #         else:
        #             with open("prompt_store/summarize_user_prompt.txt", "w") as f:
        #                 f.write(userprompt_edited)
        #             st.success("User Prompt saved successfully.")

    def load_summarize_gp_prompt():
        with open("prompt_store/summarize_guardrail_prompt.txt", "r") as f:
            guardrailprompt = f.read()
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text("Current Prompt:")
            st.text_area("GuardRail Prompt View", value=guardrailprompt, height=textarea_height, disabled=True, label_visibility="collapsed")
        # with col2:
        #     st.text("Edit Prompt:")
        #     guardrailprompt_edited = st.text_area("GuardRail Prompt Edit", value=guardrailprompt, height=textarea_height, label_visibility="collapsed", key="sum_gp_edit")
        #     if st.button("Save GuardRail Prompt", key="sum_gp_save"):
        #         if guardrailprompt_edited.strip() == "":
        #             st.warning("GuardRail Prompt cannot be empty.")
        #         else:
        #             with open("prompt_store/summarize_guardrail_prompt.txt", "w") as f:
        #                 f.write(guardrailprompt_edited)
        #             st.success("GuardRail Prompt saved successfully.")

    with sum_sp_tab:
        load_summarize_sp_prompt()

    with sum_up_tab:
        load_summarize_up_prompt()

    with sum_gp_tab:
        load_summarize_gp_prompt()

# ==================== CHAT PROMPTS ====================
with main_tabs[1]:
    st.subheader("Chat Analysis Prompts")
    
    # Tabs for different chat prompt types
    chat_sp_tab, chat_up_tab, chat_gp_tab = st.tabs(["System Prompt", "User Prompt", "GuardRail Prompt"])
    
    def load_chat_sp_prompt():
        try:
            with open("prompt_store/chat_system_prompt.txt", "r") as f:
                sysprompt = f.read()
        except FileNotFoundError:
            sysprompt = ""
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text("Current Prompt:")
            st.text_area("Chat System Prompt View", value=sysprompt, height=textarea_height, disabled=True, label_visibility="collapsed")
        # with col2:
        #     st.text("Edit Prompt:")
        #     sysprompt_edited = st.text_area("Chat System Prompt Edit", value=sysprompt, height=textarea_height, label_visibility="collapsed", key="chat_sp_edit")
        #     if st.button("Save Chat System Prompt", key="chat_sp_save"):
        #         if sysprompt_edited.strip() == "":
        #             st.warning("System Prompt cannot be empty.")
        #         else:
        #             with open("prompt_store/chat_system_prompt.txt", "w") as f:
        #                 f.write(sysprompt_edited)
        #             st.success("Chat System Prompt saved successfully.")

    def load_chat_up_prompt():
        try:
            with open("prompt_store/chat_user_prompt.txt", "r") as f:
                userprompt = f.read()
        except FileNotFoundError:
            userprompt = ""
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text("Current Prompt:")
            st.text_area("Chat User Prompt View", value=userprompt, height=textarea_height, disabled=True, label_visibility="collapsed")
        # with col2:
        #     st.text("Edit Prompt:")
        #     userprompt_edited = st.text_area("Chat User Prompt Edit", value=userprompt, height=textarea_height, label_visibility="collapsed", key="chat_up_edit")
        #     if st.button("Save Chat User Prompt", key="chat_up_save"):
        #         if userprompt_edited.strip() == "":
        #             st.warning("User Prompt cannot be empty.")
        #         else:
        #             with open("prompt_store/chat_user_prompt.txt", "w") as f:
        #                 f.write(userprompt_edited)
        #             st.success("Chat User Prompt saved successfully.")

    def load_chat_gp_prompt():
        try:
            with open("prompt_store/chat_guardrail_prompt.txt", "r") as f:
                guardrailprompt = f.read()
        except FileNotFoundError:
            guardrailprompt = ""
        col1, col2 = st.columns([4, 1])
        with col1:
            st.text("Current Prompt:")
            st.text_area("Chat GuardRail Prompt View", value=guardrailprompt, height=textarea_height, disabled=True, label_visibility="collapsed")
        # with col2:
        #     st.text("Edit Prompt:")
        #     guardrailprompt_edited = st.text_area("Chat GuardRail Prompt Edit", value=guardrailprompt, height=textarea_height, label_visibility="collapsed", key="chat_gp_edit")
        #     if st.button("Save Chat GuardRail Prompt", key="chat_gp_save"):
        #         if guardrailprompt_edited.strip() == "":
        #             st.warning("GuardRail Prompt cannot be empty.")
        #         else:
        #             with open("prompt_store/chat_guardrail_prompt.txt", "w") as f:
        #                 f.write(guardrailprompt_edited)
        #             st.success("Chat GuardRail Prompt saved successfully.")

    with chat_sp_tab:
        load_chat_sp_prompt()

    with chat_up_tab:
        load_chat_up_prompt()

    with chat_gp_tab:
        load_chat_gp_prompt()


# st.code("""
# Summarize the following call transcript in {max_sentences} sentences:
# {transcript}
# """)
# st.write("This prompt is used for generating a concise summary of the entire call transcript.") 