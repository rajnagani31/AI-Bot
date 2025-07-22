import streamlit as st
import os
from dotenv import load_dotenv
import google.generativeai as genai
import logging
from typing import List, Dict, Optional
from datetime import datetime
import json

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('chatbot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class GeminiChatBot:
    """Production-level Gemini ChatBot class with error handling and session management."""
    
    def __init__(self):
        """Initialize the chatbot with API configuration."""
        self.api_key = os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY not found in environment variables")
        
        try:
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            self.system_prompt = self._load_system_prompt()
            logger.info("Gemini ChatBot initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini ChatBot: {str(e)}")
            raise
    
    def _load_system_prompt(self) -> str:
        """Load system prompt from external file."""
        try:
            with open('system_prompt.txt', 'r', encoding='utf-8') as file:
                return file.read().strip()
        except FileNotFoundError:
            logger.warning("system_prompt.txt not found, using default prompt")
            return """You are a professional life problem-solving assistant. 
            Provide helpful, accurate, and practical solutions to professional challenges.
            Always respond in both English and Hindi (Hinglish) format.
            Be empathetic, professional, and solution-oriented in your responses."""
    
    def generate_response(self, user_message: str, chat_history: List[Dict]) -> Optional[str]:
        """Generate response using Gemini API with error handling."""
        try:
            # Prepare conversation context
            conversation_context = self._prepare_conversation_context(user_message, chat_history)
            
            # Generate response
            response = self.model.generate_content(conversation_context)
            
            if response and response.text:
                logger.info(f"Generated response for message: {user_message[:50]}...")
                return response.text
            else:
                logger.warning("Empty response received from Gemini API")
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}. Please try again later."
    
    def _prepare_conversation_context(self, user_message: str, chat_history: List[Dict]) -> str:
        """Prepare conversation context with system prompt and history."""
        context = f"System Instructions: {self.system_prompt}\n\n"
        
        # Add recent chat history (last 10 messages to manage token limit)
        recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
        
        for msg in recent_history:
            role = "Human" if msg["role"] == "user" else "Assistant"
            context += f"{role}: {msg['content']}\n"
        
        context += f"Human: {user_message}\nAssistant:"
        return context

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chatbot" not in st.session_state:
        try:
            st.session_state.chatbot = GeminiChatBot()
        except Exception as e:
            st.error(f"Failed to initialize chatbot: {str(e)}")
            st.stop()

def save_chat_history():
    """Save chat history to file for persistence."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(st.session_state.chat_history, file, ensure_ascii=False, indent=2)
        
        return filename
    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
        return None

def display_chat_history():
    """Display chat history in the main interface."""
    for message in st.session_state.chat_history:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

def main():
    """Main Streamlit application."""
    # Page configuration
    st.set_page_config(
        page_title="Professional Life Assistant",
        page_icon="🤖",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    # Initialize session state
    initialize_session_state()
    
    # Sidebar
    with st.sidebar:
        st.title("🤖 ChatBot Assistant")
        
        with st.expander("Information about chat bot"):
            st.write("""
            1. Give all answers the question\n
            2. Give answer in Both Language English and Hindi(hinglish)\n
            3. Chat bot Train for solve professional life problem
            """)

        st.markdown("---")
        "[![Open in GitHub ](https://github.com/codespaces/badge.svg)](https://github.com/rajnagani31/Ai-chat-bot)"
        
        # Chat controls
        st.subheader("Chat Controls")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("💾 Save Chat History"):
            if st.session_state.chat_history:
                filename = save_chat_history()
                if filename:
                    st.success(f"Chat saved as {filename}")
                else:
                    st.error("Failed to save chat history")
            else:
                st.warning("No chat history to save")
        
        # Statistics
        if st.session_state.chat_history:
            st.markdown("---")
            st.subheader("Chat Statistics")
            total_messages = len(st.session_state.chat_history)
            user_messages = len([msg for msg in st.session_state.chat_history if msg["role"] == "user"])
            st.metric("Total Messages", total_messages)
            st.metric("Your Messages", user_messages)
            st.metric("Bot Responses", total_messages - user_messages)
    
    # Main content area
    st.title("🤖 Professional Life Assistant ChatBot")
    st.markdown("Ask me anything about your professional challenges, and I'll help you with solutions in both English and Hindi!")
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Add user message to history
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        
        # Generate and display bot response
        with st.chat_message("assistant"):
            with st.spinner("Thinking... 🤔"):
                response = st.session_state.chatbot.generate_response(
                    prompt, 
                    st.session_state.chat_history[:-1]  # Exclude the current message
                )
            
            if response:
                st.markdown(response)
                # Add bot response to history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            else:
                st.error("Failed to generate response. Please try again.")
    
    # Footer
    st.markdown("---")
    st.markdown(
        "<div style='text-align: center; color: #666;'>"
        "🤖 Powered by Google Gemini AI | Built with Streamlit"
        "</div>",
        unsafe_allow_html=True
    )

if __name__ == "__main__":
    main()