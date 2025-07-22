"""
Utility functions for the Streamlit ChatBot application.
"""

import json
import os
import logging
from datetime import datetime
from typing import List, Dict, Optional
import streamlit as st
from config import Config

logger = logging.getLogger(__name__)

def sanitize_filename(filename: str) -> str:
    """Sanitize filename by removing invalid characters."""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, '_')
    return filename

def save_chat_history(chat_history: List[Dict], custom_name: Optional[str] = None) -> Optional[str]:
    """
    Save chat history to JSON file with timestamp.
    
    Args:
        chat_history: List of chat messages
        custom_name: Optional custom name for the file
    
    Returns:
        Filename if successful, None otherwise
    """
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        if custom_name:
            filename = f"{sanitize_filename(custom_name)}_{timestamp}.json"
        else:
            filename = f"chat_history_{timestamp}.json"
        
        filepath = os.path.join(Config.CHAT_HISTORY_DIR, filename)
        
        # Prepare chat data with metadata
        chat_data = {
            "timestamp": datetime.now().isoformat(),
            "message_count": len(chat_history),
            "messages": chat_history
        }
        
        with open(filepath, 'w', encoding='utf-8') as file:
            json.dump(chat_data, file, ensure_ascii=False, indent=2)
        
        logger.info(f"Chat history saved to {filepath}")
        return filename
        
    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
        return None

def load_chat_history(filename: str) -> Optional[List[Dict]]:
    """
    Load chat history from JSON file.
    
    Args:
        filename: Name of the file to load
    
    Returns:
        List of chat messages if successful, None otherwise
    """
    try:
        filepath = os.path.join(Config.CHAT_HISTORY_DIR, filename)
        
        if not os.path.exists(filepath):
            logger.warning(f"Chat history file not found: {filepath}")
            return None
        
        with open(filepath, 'r', encoding='utf-8') as file:
            chat_data = json.load(file)
        
        # Return messages if new format, otherwise return as-is for backward compatibility
        if isinstance(chat_data, dict) and "messages" in chat_data:
            return chat_data["messages"]
        else:
            return chat_data
            
    except Exception as e:
        logger.error(f"Error loading chat history: {str(e)}")
        return None

def get_saved_chat_files() -> List[str]:
    """Get list of saved chat history files."""
    try:
        if not os.path.exists(Config.CHAT_HISTORY_DIR):
            return []
        
        files = [f for f in os.listdir(Config.CHAT_HISTORY_DIR) 
                if f.endswith('.json')]
        
        # Sort by creation time (newest first)
        files.sort(key=lambda x: os.path.getctime(
            os.path.join(Config.CHAT_HISTORY_DIR, x)
        ), reverse=True)
        
        return files
        
    except Exception as e:
        logger.error(f"Error getting saved chat files: {str(e)}")
        return []

def export_chat_as_text(chat_history: List[Dict]) -> str:
    """
    Export chat history as formatted text.
    
    Args:
        chat_history: List of chat messages
    
    Returns:
        Formatted text string
    """
    if not chat_history:
        return "No chat history to export."
    
    export_text = f"Professional Life Assistant Chat Export\n"
    export_text += f"Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    export_text += "=" * 50 + "\n\n"
    
    for i, message in enumerate(chat_history, 1):
        role = "You" if message["role"] == "user" else "Assistant"
        export_text += f"[{i}] {role}:\n{message['content']}\n\n"
        export_text += "-" * 30 + "\n\n"
    
    return export_text

def validate_message(message: str) -> bool:
    """
    Validate user message.
    
    Args:
        message: User message to validate
    
    Returns:
        True if valid, False otherwise
    """
    if not message or not message.strip():
        return False
    
    if len(message.strip()) < 2:
        return False
    
    if len(message) > Config.MAX_RESPONSE_LENGTH:
        return False
    
    return True

def truncate_chat_history(chat_history: List[Dict], max_length: Optional[int] = None) -> List[Dict]:
    """
    Truncate chat history to maximum length.
    
    Args:
        chat_history: List of chat messages
        max_length: Maximum number of messages to keep
    
    Returns:
        Truncated chat history
    """
    if max_length is None:
        max_length = Config.MAX_CHAT_HISTORY
    
    if len(chat_history) > max_length:
        # Keep the most recent messages
        return chat_history[-max_length:]
    
    return chat_history

def format_response_with_language(response: str) -> str:
    """
    Format response to ensure it includes both English and Hindi/Hinglish.
    
    Args:
        response: Raw response from the model
    
    Returns:
        Formatted response
    """
    # Check if response already has Hindi/Hinglish section
    if "हिंदी" in response or "Hinglish" in response or "Hindi" in response:
        return response
    
    # If not, add a note
    formatted_response = response + "\n\n*Note: Please ask me to translate this response into Hindi/Hinglish if needed.*"
    return formatted_response

def get_chat_statistics(chat_history: List[Dict]) -> Dict:
    """
    Get statistics about the chat history.
    
    Args:
        chat_history: List of chat messages
    
    Returns:
        Dictionary with statistics
    """
    if not chat_history:
        return {
            "total_messages": 0,
            "user_messages": 0,
            "assistant_messages": 0,
            "avg_message_length": 0,
            "session_duration": "0 minutes"
        }
    
    user_messages = [msg for msg in chat_history if msg["role"] == "user"]
    assistant_messages = [msg for msg in chat_history if msg["role"] == "assistant"]
    
    total_chars = sum(len(msg["content"]) for msg in chat_history)
    avg_length = total_chars // len(chat_history) if chat_history else 0
    
    return {
        "total_messages": len(chat_history),
        "user_messages": len(user_messages),
        "assistant_messages": len(assistant_messages),
        "avg_message_length": avg_length,
        "session_duration": f"{len(chat_history) * 2} minutes (estimated)"
    }