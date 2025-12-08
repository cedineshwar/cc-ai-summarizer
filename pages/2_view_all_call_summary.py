#Read the summary from a file and display it as table with filters and download option as needed
import streamlit as st
import pandas as pd
import os
import json
import openai
from src.utils import save_bulk_summary, get_next_id, load_bulk_summary_chat_history, save_bulk_summary_chat_history
from src.logger import logger
from src.summarizer import chat_with_bulk_summaries
from src.plotter import detect_chart_request, generate_chart

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

# page refresh then clear chat history
# if  st.rerun:    
#     st.session_state.bulk_summary_chat_history = []
#     save_bulk_summary_chat_history([])  
    
    
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
    
    if 'chart_images' not in st.session_state:
        st.session_state.chart_images = {}
    
    # Get API key and model settings from session state
    api_key = st.session_state.get('openai_api_key')
    model = st.session_state.get('model_choice', 'gpt-4.1-mini-2025-04-14')
    temperature = st.session_state.get('temperature', 0.0)
    max_tokens = st.session_state.get('max_tokens', 600)
    
    # Check if API key is available
    if not api_key or api_key.strip() == "" or api_key == "your_api_key_here":
        st.warning("Please enter your OpenAI API key in the main app page first!")
        return
    
    # Set the API key for this session
    openai.api_key = api_key
    
    # Display chat history (scrollable) - with chart images
    with st.container(height=400, border=True):
        for idx, message in enumerate(st.session_state.bulk_summary_chat_history):
            with st.chat_message(message['role']):
                st.markdown(message['content'])
                
                # Check if this message has a chart image
                if f"chart_{idx}" in st.session_state.chart_images:
                    chart_image = st.session_state.chart_images[f"chart_{idx}"]
                    st.image(f"data:image/png;base64,{chart_image}", width="stretch")
        
        # Auto-scroll to bottom when new messages arrive
        st.markdown("""
        <script>
        setTimeout(function() {
            const scrollableContainer = window.parent.document.querySelector('[data-testid="stVerticalBlock"]');
            if (scrollableContainer) {
                scrollableContainer.scrollTop = scrollableContainer.scrollHeight;
            }
        }, 100);
        </script>
        """, unsafe_allow_html=True)
    
    # Chat input
    prompt = st.chat_input("Ask about the summaries or request a chart (e.g., 'show agent performance chart')...", key="bulk_summary_chat_input")
    
    # Predefined questions
    st.markdown("**Quick Questions:**")
    col1, col2, col3 = st.columns(3)
    
    predefined_questions = [
        "📊 Show agent performance",
        "😊 What's the sentiment distribution?",
        "⭐ What are the agent ratings?",
        "✅ What's the resolution rate?",
        "⏱️ How long are the calls?",
        "🎯 Which agent handled the most calls?",
    ]
    
    question_clicked = None
    
    # Display questions in columns
    for idx, question in enumerate(predefined_questions):
        col = col1 if idx % 3 == 0 else (col2 if idx % 3 == 1 else col3)
        if col.button(question, key=f"predefined_q_{idx}", width= "stretch"):
            question_clicked = question.split(" ", 1)[1] if " " in question else question
    
    # Use clicked question if available, otherwise use chat input
    if question_clicked:
        prompt = question_clicked
    
    # Process the prompt
    if prompt:
        # Add user message to history
        st.session_state.bulk_summary_chat_history.append({
            "role": "user",
            "content": prompt
        })
        
        # Get summaries context for LLM
        summaries_context = format_summaries_for_context(summaries)
        
        # Check if user is requesting a chart
        chart_type = detect_chart_request(prompt)
        
        if chart_type:
            # Generate chart
            with st.spinner("Generating chart..."):
                chart_image, chart_summary = generate_chart(chart_type, summaries)
            
            if chart_image:
                # Store chart image with message index
                chart_idx = len(st.session_state.bulk_summary_chat_history)
                st.session_state.chart_images[f"chart_{chart_idx}"] = chart_image
                
                # Add to history with chart marker
                st.session_state.bulk_summary_chat_history.append({
                    "role": "assistant",
                    "content": f"📊 **{chart_type.title()} Chart**\n\n{chart_summary}"
                })
                
                logger.info(f"Generated {chart_type} chart for user request")
            else:
                # Add error message to history
                st.session_state.bulk_summary_chat_history.append({
                    "role": "assistant",
                    "content": f"❌ Could not generate chart: {chart_summary}"
                })
        else:
            # Get response from LLM using chat prompts with full conversation history
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
                
                logger.info("LLM response generated successfully")
            else:
                st.error("Failed to get response from LLM. Please check logs.")
        
        # Save updated history
        # save_bulk_summary_chat_history(st.session_state.bulk_summary_chat_history)
        
        # Rerun to display updated chat
        st.rerun()
    
    # Clear chat history button
    if st.button("Clear Chat History", key="clear_bulk_chat_btn"):
        st.session_state.bulk_summary_chat_history = []
        save_bulk_summary_chat_history([])
        st.success("Chat history cleared!")
        st.rerun()

if __name__ == "__main__":
    main()

