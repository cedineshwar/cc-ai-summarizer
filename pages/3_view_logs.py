"""
View Logs Page

This page allows users to:
- View list of available log files
- Select and view log file contents
- Clear current day's log file
- Download log files (disabled)
"""

import streamlit as st
import os
from datetime import datetime
from src.logger import get_logs_dir, get_all_log_files, get_today_log_file, clear_today_log


def load_log_file(log_filepath: str) -> str:
    """Load and return log file contents."""
    try:
        with open(log_filepath, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        return "❌ Log file not found."
    except Exception as e:
        return f"❌ Error reading log file: {str(e)}"


def get_log_date_from_filename(filename: str) -> str:
    """Extract and format date from log filename."""
    # Format: log_YYYYMMDD.txt
    try:
        date_str = filename.replace('log_', '').replace('.txt', '')
        # Parse YYYYMMDD format
        date_obj = datetime.strptime(date_str, '%Y%m%d')
        return date_obj.strftime('%B %d, %Y (%A)')
    except:
        return filename


def main():
    st.set_page_config(page_title="View Logs", page_icon="📋", layout="wide")
    st.title("📋 Application Logs")
    
    # Initialize session state for refresh tracking
    if 'log_refresh_counter' not in st.session_state:
        st.session_state.log_refresh_counter = 0
    
    # Get logs directory and files
    logs_dir = get_logs_dir()
    log_files = get_all_log_files()
    today_log_file = get_today_log_file()
    today_log_filename = os.path.basename(today_log_file)
    
    if not log_files:
        st.info("No log files available yet. Logs will appear here once the application generates them.")
        return
    
    # ==================== CONTROL PANEL ====================
    st.subheader("🎛️ Log Management")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Log Files", len(log_files))
    
    with col2:
        is_today_log_exists = today_log_filename in log_files
        status = "✅ Active" if is_today_log_exists else "⏸️ Inactive"
        st.metric("Today's Log", status)
    
    with col3:
        if st.button("🔄 Refresh", use_container_width=True):
            st.session_state.log_refresh_counter += 1
            st.rerun()
    
    with col4:
        if st.button("🗑️ Clear Today's Log", use_container_width=True, type="secondary"):
            if clear_today_log():
                st.success("✅ Today's log file cleared successfully!")
                # Force refresh counter to invalidate all cached widgets
                st.session_state.log_refresh_counter += 1
                st.rerun()
            else:
                st.error("❌ Failed to clear log file")
    
    # Divider
    st.divider()
    
    # ==================== LOG FILE SELECTION ====================
    st.subheader("📂 Available Log Files")
    
    # Create a dictionary for easier selection (display name -> file path)
    log_file_dict = {}
    for log_file in log_files:
        log_filepath = os.path.join(logs_dir, log_file)
        # Get file size
        file_size = os.path.getsize(log_filepath)
        size_kb = file_size / 1024
        
        # Format display name with date and file size
        date_display = get_log_date_from_filename(log_file)
        if log_file == today_log_filename:
            display_name = f"📅 Today - {date_display} ({size_kb:.1f} KB) ⭐ ACTIVE"
        else:
            display_name = f"📅 {date_display} ({size_kb:.1f} KB)"
        
        log_file_dict[display_name] = log_filepath
    
    # Select log file
    selected_log_display = st.selectbox(
        "Select a log file to view:",
        options=list(log_file_dict.keys()),
        index=0  # Select today's log by default
    )
    
    selected_log_filepath = log_file_dict[selected_log_display]
    
    # ==================== LOG CONTENT VIEWER ====================
    st.subheader("📝 Log Content")
    
    # Get log content
    log_content = load_log_file(selected_log_filepath)
    
    # Create tabs for different views
    tab1, tab2, tab3 = st.tabs(["📄 Full View", "🔍 Search", "📊 Stats"])
    
    with tab1:
        # Display log with monospace font
        # Use dynamic key based on selected file AND refresh counter to force widget recreation
        text_area_key = f"log_viewer_{selected_log_filepath}_{st.session_state.log_refresh_counter}"
        st.text_area(
            "Log Content:",
            value=log_content,
            height=400,
            disabled=True,
            key=text_area_key
        )
        
        # Download button
        # st.download_button(
        #     label="⬇️ Download Log File",
        #     data=log_content,
        #     file_name=os.path.basename(selected_log_filepath),
        #     mime="text/plain",
        #     use_container_width=True
        # )
    
    with tab2:
        # Search functionality
        st.write("Search within this log file:")
        search_term = st.text_input("Search for:", placeholder="e.g., 'error', 'warning', etc.")
        
        if search_term:
            # Perform case-insensitive search
            search_term_lower = search_term.lower()
            lines = log_content.split('\n')
            matching_lines = [
                (i + 1, line) for i, line in enumerate(lines)
                if search_term_lower in line.lower()
            ]
            
            if matching_lines:
                st.success(f"Found {len(matching_lines)} matching lines")
                
                # Display matching lines with context
                for line_num, line in matching_lines:
                    st.code(f"Line {line_num}: {line}", language="text")
            else:
                st.info(f"No matches found for '{search_term}'")
    
    with tab3:
        # Log statistics
        lines = log_content.split('\n')
        total_lines = len([l for l in lines if l.strip()])
        
        # Count log levels
        info_count = sum(1 for line in lines if ' - INFO - ' in line)
        debug_count = sum(1 for line in lines if ' - DEBUG - ' in line)
        warning_count = sum(1 for line in lines if ' - WARNING - ' in line)
        error_count = sum(1 for line in lines if ' - ERROR - ' in line)
        critical_count = sum(1 for line in lines if ' - CRITICAL - ' in line)
        
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Lines", total_lines)
        with col2:
            st.metric("ℹ️ Info", info_count)
        with col3:
            st.metric("🐛 Debug", debug_count)
        with col4:
            st.metric("⚠️ Warning", warning_count)
        with col5:
            st.metric("❌ Error", error_count)
        
        if critical_count > 0:
            st.metric("🔴 Critical", critical_count)
        
        # Show file info
        st.divider()
        st.write("**File Information:**")
        file_size = os.path.getsize(selected_log_filepath)
        file_modified = os.path.getmtime(selected_log_filepath)
        mod_time = datetime.fromtimestamp(file_modified).strftime('%Y-%m-%d %H:%M:%S')
        
        info_col1, info_col2, info_col3 = st.columns(3)
        with info_col1:
            st.write(f"**File Name:** {os.path.basename(selected_log_filepath)}")
        with info_col2:
            st.write(f"**File Size:** {file_size / 1024:.2f} KB")
        with info_col3:
            st.write(f"**Last Modified:** {mod_time}")
    
    # ==================== LOG MANAGEMENT SECTION ====================
    st.divider()
    st.subheader("⚙️ Log Management Options")
    
    col1, col2 = st.columns(2)
    
    # with col1:
    #     if st.button("🔍 Open Logs Folder", use_container_width=True):
    #         st.info(f"Log files are stored in: `{logs_dir}`")
    
    with col1:
        if st.button("📊 Analyze All Logs", use_container_width=True):
            st.write("**Analyzing all log files...**")
            
            total_all_lines = 0
            total_errors = 0
            
            for log_file in log_files:
                log_path = os.path.join(logs_dir, log_file)
                with open(log_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    lines = content.split('\n')
                    total_all_lines += len([l for l in lines if l.strip()])
                    total_errors += sum(1 for line in lines if ' - ERROR - ' in line)
            
            col_a, col_b = st.columns(2)
            with col_a:
                st.metric("Total Log Lines (All Files)", total_all_lines)
            with col_b:
                st.metric("Total Errors (All Files)", total_errors)
    
    with col2:
        if st.button("🗑️ Delete Old Logs (>30 days)", use_container_width=True, type="secondary"):
            from datetime import timedelta
            
            deleted_count = 0
            current_date = datetime.now()
            
            for log_file in log_files:
                log_path = os.path.join(logs_dir, log_file)
                file_date_str = log_file.replace('log_', '').replace('.txt', '')
                
                try:
                    file_date = datetime.strptime(file_date_str, '%Y%m%d')
                    
                    # Delete if older than 30 days
                    if (current_date - file_date).days > 30:
                        os.remove(log_path)
                        deleted_count += 1
                except:
                    pass
            
            if deleted_count > 0:
                st.success(f"✅ Deleted {deleted_count} log files older than 30 days")
                st.rerun()
            else:
                st.info("No log files older than 30 days found")


if __name__ == "__main__":
    main()
