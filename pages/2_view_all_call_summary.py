"""View All Call Summaries with Chat and RAG Interface.

This module provides a comprehensive dashboard for viewing, managing, and chatting
about call summaries with both standard and RAG-based chat modes.
"""

import streamlit as st
import pandas as pd
import os
import json
import openai
import time
import shutil
from datetime import datetime
from src.utils import (
    save_bulk_summary,
    get_next_id,
    load_bulk_summary_chat_history,
    save_bulk_summary_chat_history,
    add_footer,
)
from src.logger import logger
from src.summarizer import chat_with_bulk_summaries, load_prompt
from src.plotter import detect_chart_request, generate_chart
from src.rag_chat import RAGChatbot
from src.config import Config, get_retriever_k


def _handle_clear_vector_store() -> None:
    """Handle the vector store clearing process with proper logging and state management."""
    try:
        with st.spinner("Clearing vector store and removing all documents..."):
            logger.info("=" * 70)
            logger.info("🗑️  VECTOR STORE CLEAR INITIATED BY USER")
            logger.info("=" * 70)

            # Verify RAG chatbot exists in session state
            if "rag_chatbot" not in st.session_state:
                logger.error("❌ No RAG chatbot in session state. Cannot clear.")
                st.error("❌ RAG chatbot not initialized. Please refresh the page.")
                return

            rag_chatbot = st.session_state.rag_chatbot
            vector_path = rag_chatbot.vector_store_manager.vector_store_path

            # Call clear_vector_store on the manager
            if rag_chatbot.vector_store_manager.clear_vector_store():
                logger.info("✅ Vector store deletion confirmed by manager")

                # Verify directory is actually gone
                if os.path.exists(vector_path):
                    logger.warning(f"⚠️  Vector store path still exists: {vector_path}")
                    logger.info("Attempting force delete...")
                    try:
                        shutil.rmtree(vector_path, ignore_errors=True)
                        logger.info(f"✅ Force delete successful: {vector_path}")
                    except Exception as e:
                        logger.error(f"❌ Force delete failed: {str(e)}")
                        st.error(f"⚠️  Could not delete all files: {str(e)}")
                        return
                else:
                    logger.info(f"✅ Verified: Vector store directory removed: {vector_path}")

                # Clear all related session state
                logger.info("Clearing related session state...")
                if "rag_chatbot" in st.session_state:
                    del st.session_state.rag_chatbot
                st.session_state.rag_chat_history = []
                st.session_state.vector_reload_status = None
                # Set flag to prevent re-initialization on next render
                st.session_state.skip_rag_initialization = True
                logger.info("✅ Session state cleared")

                logger.info("=" * 70)
                logger.info("✅ VECTOR STORE CLEARED - All documents permanently removed!")
                logger.info("=" * 70)
                st.success("✅ Vector store completely cleared! All documents removed.")
                st.balloons()
            else:
                logger.error("❌ Failed to clear vector store - manager returned False")
                st.error("❌ Failed to clear vector store. Check logs for details.")

    except Exception as e:
        error_msg = f"Vector store clear failed: {str(e)}"
        logger.error("=" * 70)
        logger.error(f"❌ CLEAR FAILED: {error_msg}")
        logger.error("=" * 70)
        logger.exception(error_msg)
        st.error(f"❌ {error_msg}")


def export_chat_history_to_csv(messages):
    """Convert chat history messages to CSV format."""
    if not messages:
        return None

    chat_data = []
    for msg in messages:
        chat_data.append(
            {
                "Role": msg.get("role", "").capitalize(),
                "Message": msg.get("content", ""),
                "Timestamp": msg.get("timestamp", "N/A"),
                "Response Time (s)": msg.get("response_time", "N/A"),
            }
        )

    df = pd.DataFrame(chat_data)
    return df.to_csv(index=False).encode("utf-8")

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


def _render_standard_chat(summaries):
    """Render the standard chat interface with chart features."""
    
    # Initialize session state for bulk summary chat
    if 'bulk_summary_chat_history' not in st.session_state:
        st.session_state.bulk_summary_chat_history = load_bulk_summary_chat_history()
    
    if 'chart_images' not in st.session_state:
        st.session_state.chart_images = {}
    
    # Get API key and model settings from session state (sidebar), with Config as fallback
    api_key = st.session_state.get('openai_api_key')
    model = st.session_state.get('model_choice') or Config.MODEL_NAME
    temperature = st.session_state.get('temperature') if st.session_state.get('temperature') is not None else Config.TEMPERATURE
    max_tokens = st.session_state.get('max_tokens') or Config.MAX_TOKENS
    
    # Check if API key is available
    if not api_key or api_key.strip() == "" or api_key == "your_api_key_here":
        st.warning("Please enter your OpenAI API key in the main app page first!")
        return
    
    # Set the API key for this session
    openai.api_key = api_key
    
    # Display chat history (scrollable) - with chart images
    chat_container = st.container(height=600, border=True)
    with chat_container:
        for idx, message in enumerate(st.session_state.bulk_summary_chat_history):
            with st.chat_message(message['role']):
                st.markdown(message['content'])
                
                # Display timestamp and response time if available
                if "timestamp" in message:
                    if "response_time" in message:
                        st.caption(f"🕐 {message['timestamp']} | ⏱️ Response time: {message['response_time']:.2f}s")
                    else:
                        st.caption(f"🕐 {message['timestamp']}")
                
                # Check if this message has a chart image
                if f"chart_{idx}" in st.session_state.chart_images:
                    chart_image = st.session_state.chart_images[f"chart_{idx}"]
                    st.image(f"data:image/png;base64,{chart_image}", width=600)
        
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
        # Add user message to history with timestamp
        user_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.bulk_summary_chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": user_timestamp
        })
        
        # Display user message in container
        with chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption(f"🕐 {user_timestamp}")
        
        # Get summaries context for LLM
        summaries_context = format_summaries_for_context(summaries)
        
        # Check if user is requesting a chart
        chart_type = detect_chart_request(prompt)
        
        if chart_type:
            # Generate chart
            with st.spinner("Generating chart..."):
                chart_start = time.time()
                chart_image, chart_summary = generate_chart(chart_type, summaries)
                chart_end = time.time()
                chart_time = chart_end - chart_start
            
            if chart_image:
                # Store chart image with message index
                chart_idx = len(st.session_state.bulk_summary_chat_history)
                st.session_state.chart_images[f"chart_{chart_idx}"] = chart_image
                
                # Get current timestamp for chart response
                chart_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
                # Add to history with chart marker, timestamp, and response time
                st.session_state.bulk_summary_chat_history.append({
                    "role": "assistant",
                    "content": f"📊 **{chart_type.title()} Chart**\n\n{chart_summary}",
                    "timestamp": chart_timestamp,
                    "response_time": chart_time
                })
                
                logger.info(f"Generated {chart_type} chart for user request in {chart_time:.2f}s")
            else:
                # Add error message to history with timestamp
                error_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                st.session_state.bulk_summary_chat_history.append({
                    "role": "assistant",
                    "content": f"❌ Could not generate chart: {chart_summary}",
                    "timestamp": error_timestamp
                })
        else:
            # Get response from LLM using chat prompts with full conversation history with streaming
            # Track response time
            response_start = time.time()
            
            # Build clean chat history for LLM (excluding current user message and metadata)
            clean_chat_history = []
            for msg in st.session_state.bulk_summary_chat_history[:-1]:
                clean_chat_history.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            # Get current timestamp for assistant response
            response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            logger.debug(f"LLM chat with {len(clean_chat_history)} previous messages in history")
            
            # Build messages for streaming
            chat_system_prompt = load_prompt('chat_system_prompt.txt')
            chat_user_prompt = load_prompt('chat_user_prompt.txt')
            chat_guardrail_prompt = load_prompt('chat_guardrail_prompt.txt')
            formatted_user_prompt = chat_user_prompt.replace('{{PASTE ENTIRE SUMMARY HERE}}', summaries_context) if chat_user_prompt else summaries_context
            full_system_prompt = f"{chat_system_prompt}\n\n{chat_guardrail_prompt}" if chat_system_prompt and chat_guardrail_prompt else chat_system_prompt
            
            messages = [{"role": "system", "content": full_system_prompt}]
            messages.extend(clean_chat_history)
            messages.append({"role": "user", "content": f"{formatted_user_prompt}\n\nUser Question: {prompt}"})
            
            # Display streaming response inside container
            with chat_container:
                with st.chat_message("assistant"):
                    message_placeholder = st.empty()
                    full_response = ""
                    
                    # Stream the response
                    stream = openai.chat.completions.create(
                        model=model,
                        messages=messages,
                        temperature=temperature,
                        max_tokens=max_tokens,
                        stream=True
                    )
                    
                    for chunk in stream:
                        if chunk.choices[0].delta.content is not None:
                            full_response += chunk.choices[0].delta.content
                            message_placeholder.markdown(full_response + "▌")
                    
                    # Final response without cursor
                    message_placeholder.markdown(full_response)
                    
                    # Calculate response time and display metadata
                    response_time = time.time() - response_start
                    st.caption(f"🕐 {response_timestamp} | ⏱️ Response time: {response_time:.2f}s")
            
            # Add to history
            st.session_state.bulk_summary_chat_history.append({
                "role": "assistant",
                "content": full_response,
                "timestamp": response_timestamp,
                "response_time": response_time
            })
            
            logger.info("LLM streaming response generated successfully")
    
    # Chat history management buttons
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("Clear Chat History", key="clear_bulk_chat_btn"):
            st.session_state.bulk_summary_chat_history = []
            save_bulk_summary_chat_history([])
            st.success("Chat history cleared!")
            st.rerun()
    
    with col2:
        if st.session_state.bulk_summary_chat_history:
            chat_csv = export_chat_history_to_csv(st.session_state.bulk_summary_chat_history)
            if chat_csv:
                st.download_button(
                    label="📥 Download Chat History",
                    data=chat_csv,
                    file_name=f'chat_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv',
                    key="download_bulk_chat_btn"
                )


def _render_rag_chat():
    """Render the RAG-based chat interface with vector search."""
    
    # Get API key and model settings from session state (sidebar), with Config as fallback
    api_key = st.session_state.get('openai_api_key')
    model = st.session_state.get('model_choice') or Config.MODEL_NAME
    temperature = st.session_state.get('temperature') if st.session_state.get('temperature') is not None else Config.TEMPERATURE
    max_tokens = st.session_state.get('max_tokens') or Config.MAX_TOKENS
    
    # Check if API key is available
    if not api_key or api_key.strip() == "" or api_key == "your_api_key_here":
        st.warning("Please enter your OpenAI API key in the main app page first!")
        return
    
    # Initialize RAG chatbot ONCE and keep it in session state (CRITICAL FIX)
    # Check if we just cleared the vector store (skip re-initialization)
    should_skip_init = st.session_state.get('skip_rag_initialization', False)
    
    if 'rag_chatbot' not in st.session_state and not should_skip_init:
        logger.info("=" * 70)
        logger.info("🆕 FIRST TIME RAG INITIALIZATION - Creating RAG chatbot and vector store")
        logger.info("=" * 70)
        with st.spinner("Initializing RAG Chatbot and vector store (first time only)..."):
            rag_chatbot = RAGChatbot(api_key=api_key)
            if rag_chatbot.initialize(model=model, temperature=temperature, max_tokens=max_tokens, force_recreate=False):
                st.session_state.rag_chatbot = rag_chatbot
                logger.info("✅ RAG Chatbot created and stored in session state")
                st.success("✅ RAG Chatbot initialized successfully!")
            else:
                logger.error("❌ Failed to initialize RAG Chatbot")
                st.error("❌ Failed to initialize RAG Chatbot. Please check API key and logs.")
                return
    elif should_skip_init:
        logger.info("⏭️  Skipping RAG initialization - vector store was just cleared")
        # Reset the flag for next render
        st.session_state.skip_rag_initialization = False
    else:
        logger.debug("✅ Using existing RAG chatbot from session state (no recreation needed)")
    
    # Initialize RAG chat history in session state
    if 'rag_chat_history' not in st.session_state:
        st.session_state.rag_chat_history = []
    
    # Initialize reload status tracking
    if 'vector_reload_status' not in st.session_state:
        st.session_state.vector_reload_status = None
    
    # Display persistent reload status message if exists
    if st.session_state.vector_reload_status:
        if st.session_state.vector_reload_status == 'success':
            st.success("✅ Vector store reloaded successfully! New summaries are now indexed and searchable.")
        elif st.session_state.vector_reload_status == 'error':
            st.error("❌ Failed to reload vector store. Please check logs and try again.")
    
    # Display chat history (scrollable)
    rag_chat_container = st.container(height=600, border=True)
    with rag_chat_container:
        for message in st.session_state.rag_chat_history:
            with st.chat_message(message['role']):
                st.markdown(message['content'])
                
                # Display timestamp and response time if available
                if "timestamp" in message:
                    if "response_time" in message:
                        st.caption(f"🕐 {message['timestamp']} | ⏱️ Response time: {message['response_time']:.2f}s")
                    else:
                        st.caption(f"🕐 {message['timestamp']}")
        
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
    
    # Check if vector store was just cleared - if so, don't process any prompts
    if st.session_state.get('skip_rag_initialization'):
        st.info("✅ Vector store cleared successfully! You can reload it by clicking 'Reload Vector Store' or refresh the page to start fresh.")
        return
    
    # Chat input
    prompt = st.chat_input("Ask anything about the call summaries (powered by vector search)...", key="rag_chat_input")
    
    # Predefined RAG questions
    st.markdown("**Sample Questions:**")
    col1, col2, col3 = st.columns(3)
    
    rag_questions = [
        "Which agents have the highest scores?",
        "What are common customer issues?",
        "Summarize unresolved issues",
        "What agent got the best ratings?",
        "Analyze customer sentiment patterns",
        "Which department needs improvement?",
    ]
    
    question_clicked = None
    
    # Display questions in columns
    for idx, question in enumerate(rag_questions):
        col = col1 if idx % 3 == 0 else (col2 if idx % 3 == 1 else col3)
        if col.button(question, key=f"rag_q_{idx}", width="stretch"):
            question_clicked = question
    
    # Use clicked question if available, otherwise use chat input
    if question_clicked:
        prompt = question_clicked
    
    # Process the prompt
    if prompt:
        # Clear reload status when new prompt is entered
        st.session_state.vector_reload_status = None
        
        # Add user message to history with timestamp
        user_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        st.session_state.rag_chat_history.append({
            "role": "user",
            "content": prompt,
            "timestamp": user_timestamp
        })
        
        # Display user message in container
        with rag_chat_container:
            with st.chat_message("user"):
                st.markdown(prompt)
                st.caption(f"🕐 {user_timestamp}")
        
        # Get RAG response with streaming
        rag_chatbot = st.session_state.get('rag_chatbot')
        if rag_chatbot:
            # Track response time
            response_start = time.time()
            
            # Get current timestamp for assistant response
            response_timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            try:
                # Display streaming response inside container
                with rag_chat_container:
                    with st.chat_message("assistant"):
                        message_placeholder = st.empty()
                        full_response = ""
                        
                        # Get streaming response from RAG chatbot
                        stream = rag_chatbot.get_rag_response_stream(
                            user_message=prompt,
                            chat_history=st.session_state.rag_chat_history[:-1]
                        )
                        
                        for chunk in stream:
                            full_response += chunk
                            message_placeholder.markdown(full_response + "▌")
                        
                        # Final response without cursor
                        message_placeholder.markdown(full_response)
                        
                        # Calculate response time and display metadata
                        response_time = time.time() - response_start
                        st.caption(f"🕐 {response_timestamp} | ⏱️ Response time: {response_time:.2f}s")
                
                # Add to history
                st.session_state.rag_chat_history.append({
                    "role": "assistant",
                    "content": full_response,
                    "timestamp": response_timestamp,
                    "response_time": response_time
                })
                
                logger.info("RAG streaming response generated successfully")
            except AttributeError:
                # Fallback to non-streaming if get_rag_response_stream is not available
                with st.spinner("Searching vector store and generating response..."):
                    response = rag_chatbot.get_rag_response(
                        user_message=prompt,
                        chat_history=st.session_state.rag_chat_history[:-1]
                    )
                    response_time = time.time() - response_start
                
                if response:
                    st.session_state.rag_chat_history.append({
                        "role": "assistant",
                        "content": response,
                        "timestamp": response_timestamp,
                        "response_time": response_time
                    })
                    logger.info("RAG response generated successfully (non-streaming fallback)")
                else:
                    error_msg = "Failed to generate RAG response. Please check logs."
                    st.session_state.rag_chat_history.append({
                        "role": "assistant",
                        "content": f"❌ {error_msg}",
                        "timestamp": response_timestamp
                    })
                    logger.error(error_msg)
    
    # Chat history and vector store management buttons
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("Clear RAG Chat History", key="clear_rag_chat_btn", width="stretch"):
            st.session_state.rag_chat_history = []
            st.session_state.vector_reload_status = None
            st.success("RAG chat history cleared!")
            st.rerun()
    
    with col2:
        if st.session_state.rag_chat_history:
            chat_csv = export_chat_history_to_csv(st.session_state.rag_chat_history)
            if chat_csv:
                st.download_button(
                    label="📥 Download Chat History",
                    data=chat_csv,
                    file_name=f'rag_chat_history_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv',
                    mime='text/csv',
                    key="download_rag_chat_btn",
                    width="stretch"
                )
    
    with col3:
        if st.button("🔄 Reload Vector Store", key="reload_vector_btn", width="stretch"):
            try:
                with st.spinner("🔄 Reloading vector store and indexing new summaries..."):
                    logger.info("=" * 70)
                    logger.info("🔄 VECTOR STORE RELOAD INITIATED BY USER")
                    logger.info("=" * 70)
                    
                    # Get fresh API key and settings
                    api_key = st.session_state.get('openai_api_key')
                    
                    # Get the EXISTING RAG chatbot from session state
                    if 'rag_chatbot' not in st.session_state:
                        logger.error("❌ No RAG chatbot in session state. Cannot reload.")
                        st.error("❌ RAG chatbot not initialized. Please refresh the page.")
                        st.rerun()
                        return
                    
                    rag_chatbot = st.session_state.rag_chatbot
                    
                    # Call reload_vector_store on the existing chatbot with force_recreate=True
                    logger.info("🔄 Reloading vector store in existing chatbot instance...")
                    if rag_chatbot.vector_store_manager.create_vector_store(api_key, force_recreate=True):
                        logger.info("✅ Vector store reloaded successfully")
                        
                        # Reinitialize retriever with configured k value
                        rag_chatbot.vector_store_manager.retriever = rag_chatbot.vector_store_manager.vector_store.as_retriever(search_kwargs={"k": rag_chatbot.vector_store_manager.retriever_k})
                        
                        # Check vector store info after reload
                        vs_info = rag_chatbot.vector_store_manager.get_vector_store_info()
                        logger.info(f"📊 Vector Store after reload: {vs_info}")
                        
                        st.session_state.vector_reload_status = 'success'
                        logger.info("=" * 70)
                        logger.info(f"✅ VECTOR STORE RELOAD COMPLETE - {vs_info.get('document_count', 0)} documents indexed!")
                        logger.info("=" * 70)
                    else:
                        logger.error("❌ Failed to reload vector store")
                        st.session_state.vector_reload_status = 'error'
                        logger.info("=" * 70)
                    
                    st.rerun()
            except Exception as e:
                st.session_state.vector_reload_status = 'error'
                error_details = f"Vector store reload failed: {str(e)}"
                logger.error("=" * 70)
                logger.error(f"❌ RELOAD FAILED: {error_details}")
                logger.error("=" * 70, exc_info=True)
                st.error(f"❌ {error_details}")
                st.rerun()
    
    with col4:
        ""
        # if st.button(
        #     "🗑️ Clear Vector Store",
        #     key="clear_vector_btn",
        #     width="stretch",
        # ):
        #     _handle_clear_vector_store()
    
    
def main():
    st.set_page_config(page_title="View Summaries", page_icon="📋", layout="wide")
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
    
    # Create columns for download and clear buttons
    col1, col2 = st.columns(2)
    
    with col1:
        st.download_button(
            label="Download summaries as CSV",
            data=csv,
            file_name='summaries.csv',
            mime='text/csv',
            width="stretch"
        )
    
    with col2:
        if st.button("🗑️ Clear All Summaries", key="clear_summaries_btn", width="stretch"):
            try:
                # Delete the bulk_summaries.json file
                summaries_file = os.path.join('output_data', 'bulk_summaries.json')
                if os.path.exists(summaries_file):
                    os.remove(summaries_file)
                    logger.info("✅ Bulk summaries file cleared successfully")
                    
                    # Reset last_id in metadata JSON
                    metadata_file = os.path.join('output_data', 'bulk_summary_metadata.json')
                    if os.path.exists(metadata_file):
                        try:
                            metadata = {
                                "last_id": 0,
                                "last_updated": datetime.now().isoformat(),
                                "total_summaries": 0
                            }
                            with open(metadata_file, 'w', encoding='utf-8') as f:
                                json.dump(metadata, f, indent=2)
                            logger.info("✅ Metadata reset: last_id set to 0")
                        except Exception as e:
                            logger.error(f"Error resetting metadata: {str(e)}")
                    
                    # Clear vector store since summaries are now gone
                    logger.info("🔄 Clearing vector store since summaries have been deleted...")
                    if 'rag_chatbot' in st.session_state:
                        rag_chatbot = st.session_state.rag_chatbot
                        if rag_chatbot.vector_store_manager.clear_vector_store():
                            logger.info("✅ Vector store cleared successfully after clearing summaries")
                            # Clear related session state
                            del st.session_state.rag_chatbot
                            st.session_state.rag_chat_history = []
                            st.session_state.vector_reload_status = None
                            st.session_state.skip_rag_initialization = True
                        else:
                            logger.error("❌ Failed to clear vector store after clearing summaries")
                            st.session_state.vector_reload_status = 'error'
                    
                    st.success("✅ All summaries, metadata, and vector store cleared! You can now start fresh.")
                    # Clear session state
                    if 'bulk_summaries' in st.session_state:
                        del st.session_state.bulk_summaries
                    st.rerun()
                else:
                    st.info("No summaries file to clear.")
            except Exception as e:
                logger.error(f"Error clearing summaries: {str(e)}")
                st.error(f"Error clearing summaries: {str(e)}")
    
    # Divider
    st.divider()
    
    # ==================== BOTTOM SECTION: CHAT INTERFACE WITH TABS ====================
    st.subheader("💬 Chat with Summaries")
    
    # Create tabs for different chat modes
    tab1, tab2 = st.tabs(["📊 Standard Chat (with Charts)", "🤖 RAG-Based Chat (Vector Search)"])
    
    # ==================== TAB 1: EXISTING CHAT WITH CHARTS ====================
    with tab1:
        _render_standard_chat(summaries)
    
    # ==================== TAB 2: RAG-BASED CHAT ====================
    with tab2:
        _render_rag_chat()

if __name__ == "__main__":
    main()

# Add footer to the page
add_footer()


