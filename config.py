"""
Configuration settings for the Streamlit ChatBot application.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Config:
    """Configuration class for application settings."""
    
    # API Configuration
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = "gemini-pro"
    
    # Application Settings
    APP_TITLE = "Professional Life Assistant"
    APP_ICON = "🤖"
    MAX_CHAT_HISTORY = int(os.getenv("MAX_CHAT_HISTORY", 50))
    
    # Logging Configuration
    LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    LOG_FILE = "chatbot.log"
    
    # UI Configuration
    SIDEBAR_EXPANDED = True
    LAYOUT = "wide"
    
    # File Paths
    SYSTEM_PROMPT_FILE = "system_prompt.txt"
    CHAT_HISTORY_DIR = "chat_histories"
    
    # Response Configuration
    MAX_RESPONSE_LENGTH = 2000
    RESPONSE_TIMEOUT = 30  # seconds
    
    @classmethod
    def validate(cls):
        """Validate configuration settings."""
        if not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required but not found in environment variables")
        
        # Create directories if they don't exist
        os.makedirs(cls.CHAT_HISTORY_DIR, exist_ok=True)
        
        return True

# Validate configuration on import
Config.validate()