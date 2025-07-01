"""
AI Processing Helpers for Social Media Content Enhancement

This module contains helper functions for processing text using AI APIs.
It handles the interaction with AI services and provides a clean interface for the UI.
"""

import streamlit as st
from typing import Optional
from app.ai.anthropic import AnthropicAPI
from app.config import ANTHROPIC_API_KEY
from app.ui.ai_prompts import format_prompt


class AIProcessor:
    """Handler for AI text processing operations."""
    
    def __init__(self):
        """Initialize the AI processor with the configured API."""
        self.anthropic_api = None
        if ANTHROPIC_API_KEY:
            try:
                self.anthropic_api = AnthropicAPI(
                    model="claude-3-7-sonnet-20250219", 
                    temperature=0.7
                )
            except Exception as e:
                st.error(f"❌ Failed to initialize Anthropic API: {e}")
    
    def is_available(self) -> bool:
        """Check if AI processing is available."""
        return self.anthropic_api is not None
    
    def process_text(self, text: str, action: str) -> str:
        """
        Process text using the Anthropic API based on the specified action.
        
        Args:
            text (str): The text to process
            action (str): The action to perform ('improve', 'expand', 'condense', 'generate_title')
            
        Returns:
            str: The processed text or original text if processing fails
        """
        if not self.is_available():
            st.error("❌ Anthropic API not configured. Please check your API key.")
            return text
        
        if not text.strip():
            st.warning("⚠️ Please add some content first")
            return text
        
        try:
            # Get the formatted prompts
            system_prompt, user_prompt = format_prompt(action, text)
            
            if not system_prompt or not user_prompt:
                st.error(f"❌ Unknown action: {action}")
                return text
            
            # Call the API
            result = self.anthropic_api.call_prompt(
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                max_tokens=4000
            )
            
            if result:
                return result.strip()
            else:
                st.error("❌ Failed to process text with AI")
                return text
                
        except Exception as e:
            st.error(f"❌ Error processing text: {str(e)}")
            return text
    
    def get_model_info(self) -> dict:
        """Get information about the current AI model."""
        if not self.is_available():
            return {"model": "Not configured", "provider": "None"}
        
        return {
            "model": self.anthropic_api.model,
            "provider": "Anthropic",
            "temperature": self.anthropic_api.temperature
        }


# Global AI processor instance
_ai_processor = None

def get_ai_processor() -> AIProcessor:
    """Get the global AI processor instance."""
    global _ai_processor
    if _ai_processor is None:
        _ai_processor = AIProcessor()
    return _ai_processor


def process_text_with_ai(text: str, action: str) -> str:
    """
    Convenience function to process text with AI.
    
    Args:
        text (str): The text to process
        action (str): The action to perform
        
    Returns:
        str: The processed text
    """
    processor = get_ai_processor()
    return processor.process_text(text, action)


def is_ai_available() -> bool:
    """Check if AI processing is available."""
    processor = get_ai_processor()
    return processor.is_available()


def get_ai_model_info() -> dict:
    """Get information about the current AI model."""
    processor = get_ai_processor()
    return processor.get_model_info() 