import os
import json
from datetime import datetime
from src.logger import logger

def load_sample_call() -> str:
    return open('sample_data/example_call.txt', 'r', encoding='utf-8').read()

def load_file(filename) -> str:
    return open('input_data/'+filename, 'r', encoding='utf-8').read()


def write_file(filename) -> str:
    return open('input_data/'+filename, 'w', encoding='utf-8').writelines()


def list_files(folderpath: str) -> list:
    """
    List only .txt files in the specified folder, excluding directories.
    """
    try:
        all_items = os.listdir(folderpath)
        # Filter to only include .txt files, exclude directories
        txt_files = [f for f in all_items if f.endswith('.txt') and os.path.isfile(os.path.join(folderpath, f))]
        return sorted(txt_files)
    except Exception as e:
        logger.error(f"Error listing files in {folderpath}: {e}")
        return []


def get_next_id() -> int:
    """
    Get the next ID for bulk summaries by reading the last ID from metadata file.
    """
    metadata_file = 'output_data/bulk_summary_metadata.json'
    
    try:
        if os.path.exists(metadata_file):
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                return metadata.get('last_id', 0) + 1
        else:
            return 1
    except Exception as e:
        logger.error(f"Error reading metadata file: {e}")
        return 1


def save_bulk_summary(summaries: list) -> None:
    """
    Save bulk summaries to output_data folder and update metadata with last ID.
    Appends to existing file if it exists.
    """
    output_dir = 'output_data'
    summaries_file = os.path.join(output_dir, 'bulk_summaries.json')
    metadata_file = os.path.join(output_dir, 'bulk_summary_metadata.json')
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Load existing summaries if file exists
        all_summaries = []
        if os.path.exists(summaries_file):
            try:
                with open(summaries_file, 'r', encoding='utf-8') as f:
                    all_summaries = json.load(f)
            except json.JSONDecodeError:
                logger.warning("Existing summaries file is corrupted, starting fresh")
                all_summaries = []
        
        # Append new summaries
        all_summaries.extend(summaries)
        
        # Save updated summaries
        with open(summaries_file, 'w', encoding='utf-8') as f:
            json.dump(all_summaries, f, indent=2)
        
        # Update metadata with last ID and timestamp
        last_id = max([summary.get('id', 0) for summary in all_summaries], default=0)
        metadata = {
            'last_id': last_id,
            'last_updated': datetime.now().isoformat(),
            'total_summaries': len(all_summaries)
        }
        
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, indent=2)
        
        logger.info(f"Saved {len(summaries)} summaries to {summaries_file}")
        logger.info(f"Updated metadata: last_id={last_id}")
        
    except Exception as e:
        logger.error(f"Error saving bulk summaries: {e}", exc_info=True)


def load_chat_history() -> list:
    """
    Load chat history from output_data folder.
    Returns a list of chat messages.
    """
    chat_file = 'output_data/app_chat_history.json'
    
    try:
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Handle empty file
                if not content:
                    logger.info("Chat history file is empty, starting fresh")
                    return []
                history = json.loads(content)
                logger.info(f"Loaded chat history with {len(history)} messages")
                return history
        else:
            logger.info("No previous chat history found")
            return []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding chat history JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading chat history: {e}")
        return []


def save_chat_history(messages: list) -> None:
    """
    Save chat history to output_data folder.
    Appends new messages to existing history.
    """
    output_dir = 'output_data'
    chat_file = os.path.join(output_dir, 'app_chat_history.json')
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save chat history
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2)
        
        logger.info(f"Saved chat history with {len(messages)} messages")
        
    except Exception as e:
        logger.error(f"Error saving chat history: {e}", exc_info=True)


def load_bulk_summary_chat_history() -> list:
    """
    Load chat history for bulk summary analysis from output_data folder.
    Returns a list of chat messages.
    """
    chat_file = 'output_data/bulk_summary_chat_history.json'
    
    try:
        if os.path.exists(chat_file):
            with open(chat_file, 'r', encoding='utf-8') as f:
                content = f.read().strip()
                # Handle empty file
                if not content:
                    logger.info("Bulk summary chat history file is empty, starting fresh")
                    return []
                history = json.loads(content)
                logger.info(f"Loaded bulk summary chat history with {len(history)} messages")
                return history
        else:
            logger.info("No previous bulk summary chat history found")
            return []
    except json.JSONDecodeError as e:
        logger.error(f"Error decoding bulk summary chat history JSON: {e}")
        return []
    except Exception as e:
        logger.error(f"Error loading bulk summary chat history: {e}")
        return []


def save_bulk_summary_chat_history(messages: list) -> None:
    """
    Save chat history for bulk summary analysis to output_data folder.
    """
    output_dir = 'output_data'
    chat_file = os.path.join(output_dir, 'bulk_summary_chat_history.json')
    
    try:
        # Ensure output directory exists
        os.makedirs(output_dir, exist_ok=True)
        
        # Save chat history
        with open(chat_file, 'w', encoding='utf-8') as f:
            json.dump(messages, f, indent=2)
        
        logger.info(f"Saved bulk summary chat history with {len(messages)} messages")
        
    except Exception as e:
        logger.error(f"Error saving bulk summary chat history: {e}", exc_info=True)


def add_footer():
    """
    Add a dynamic footer to the page with current year, app name, and author.
    """
    import streamlit as st
    
    current_year = datetime.now().year
    
    # Add some spacing
    st.divider()
    
    # Create footer with centered text
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(
            f"""
            <div style="
                text-align: center;
                padding: 20px 0;
                font-size: 12px;
                color: #999;
            ">
                © {current_year} CC AI Summarizer | Dineshwar Elanchezhian
            </div>
            """,
            unsafe_allow_html=True
        )

