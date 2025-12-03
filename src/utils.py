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
    return os.listdir(folderpath)


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
