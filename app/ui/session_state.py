"""
Session State Management for Social Media Scheduler

This module handles the initialization and management of Streamlit session state
for the social media scheduler application.
"""

import streamlit as st


def initialize_session_state():
    """Initialize all session state variables with their default values."""
    
    # Content state
    if 'title' not in st.session_state:
        st.session_state.title = ""
    if 'text' not in st.session_state:
        st.session_state.text = ""
    
    # UI preferences
    if 'selected_platforms' not in st.session_state:
        st.session_state.selected_platforms = ["Facebook"]
    if 'ai_provider' not in st.session_state:
        st.session_state.ai_provider = "Anthropic"
    if 'post_now' not in st.session_state:
        st.session_state.post_now = True
    
    # Operation states
    if 'posting_in_progress' not in st.session_state:
        st.session_state.posting_in_progress = False
    if 'ai_processing' not in st.session_state:
        st.session_state.ai_processing = False
    
    # UI state management
    if 'clear_counter' not in st.session_state:
        st.session_state.clear_counter = 0


def clear_content():
    """Clear all content from the form (title and text)."""
    st.session_state.title = ""
    st.session_state.text = ""
    st.session_state.clear_counter += 1


def set_posting_state(is_posting: bool):
    """Set the posting in progress state."""
    st.session_state.posting_in_progress = is_posting


def set_ai_processing_state(is_processing: bool):
    """Set the AI processing state."""
    st.session_state.ai_processing = is_processing


def update_text_content(new_text: str):
    """Update the text content and force UI refresh."""
    st.session_state.text = new_text
    st.session_state.clear_counter += 1


def update_title_content(new_title: str):
    """Update the title content and force UI refresh."""
    st.session_state.title = new_title
    st.session_state.clear_counter += 1


def is_any_operation_in_progress() -> bool:
    """Check if any operation (posting or AI processing) is in progress."""
    return (st.session_state.posting_in_progress or 
            st.session_state.ai_processing)


def get_form_key_suffix() -> str:
    """Get a suffix for form input keys to force refresh when needed."""
    return f"_{st.session_state.clear_counter}"


def get_session_debug_info() -> dict:
    """Get debug information about the current session state."""
    return {
        "mode": "Post Now" if st.session_state.post_now else "Schedule",
        "selected_platforms": st.session_state.selected_platforms,
        "ai_provider": st.session_state.ai_provider,
        "posting_in_progress": st.session_state.posting_in_progress,
        "ai_processing": st.session_state.ai_processing,
        "clear_counter": st.session_state.clear_counter,
        "content_length": len(st.session_state.text),
        "title_length": len(st.session_state.title)
    } 