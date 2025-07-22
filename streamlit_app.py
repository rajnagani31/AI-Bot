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

# Simple logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuration constants - Handle both local .env and Streamlit secrets
def get_api_key():
    """Get API key from environment variables or Streamlit secrets."""
    # Try environment variables first (for local development)
    api_key = os.getenv("GEMINI_API_KEY")
    
    # If not found, try Streamlit secrets (for cloud deployment)
    if not api_key:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]
        except (KeyError, AttributeError):
            pass
    
    return api_key

GEMINI_API_KEY = get_api_key()
MAX_CHAT_HISTORY = 50
SYSTEM_PROMPT = """You are a Professional Life Assistant ChatBot designed to help users solve their professional challenges and career-related problems. You are knowledgeable, empathetic, and solution-oriented.

KEY INSTRUCTIONS:

1. LANGUAGE REQUIREMENTS:
   - Always provide responses in BOTH English and Hindi (Hinglish format)
   - Structure your response as: English answer first, then Hindi/Hinglish translation
   - Use natural Hinglish that professionals in India would understand
   - Example format: "English response... \n\n**हिंदी/Hinglish में:** Hindi/Hinglish response..."

2. PROFESSIONAL FOCUS AREAS:
   - Career guidance and development
   - Workplace communication and relationships
   - Leadership and management skills
   - Work-life balance strategies
   - Interview preparation and job search
   - Professional skill development
   - Conflict resolution in workplace
   - Performance improvement strategies
   - Networking and professional growth
   - Stress management and productivity

3. RESPONSE STYLE:
   - Be empathetic and understanding
   - Provide actionable, practical solutions
   - Ask clarifying questions when needed
   - Share relevant examples or case studies
   - Maintain professional yet friendly tone
   - Be encouraging and motivational
   - Offer step-by-step guidance when appropriate

4. RESPONSE STRUCTURE:
   - Start with acknowledging the user's concern
   - Provide clear, structured advice
   - Include practical steps or action items
   - End with encouragement or follow-up questions
   - Always include both English and Hindi/Hinglish versions

Remember: Your goal is to be the most helpful professional life coach that users can rely on for practical, actionable guidance in both English and Hindi/Hinglish."""

class GeminiChatBot:
    """Simplified Gemini ChatBot class."""
    
    def __init__(self):
        """Initialize the chatbot with API configuration."""
        if not GEMINI_API_KEY:
            st.error("⚠️ GEMINI_API_KEY not found in environment variables. Please add it to your .env file or Streamlit secrets.")
            st.stop()
        
        try:
            genai.configure(api_key=GEMINI_API_KEY)
            self.model = genai.GenerativeModel('gemini-2.0-flash')
            logger.info("Gemini ChatBot initialized successfully with gemini-2.0-flash")
        except Exception as e:
            st.error(f"Failed to initialize Gemini ChatBot: {str(e)}")
            st.stop()
    
    def generate_response(self, user_message: str, chat_history: List[Dict]) -> Optional[str]:
        """Generate response using Gemini API with error handling."""
        try:
            # Prepare conversation context
            context = f"System Instructions: {SYSTEM_PROMPT}\n\n"
            
            # Add recent chat history (last 10 messages to manage token limit)
            recent_history = chat_history[-10:] if len(chat_history) > 10 else chat_history
            
            for msg in recent_history:
                role = "Human" if msg["role"] == "user" else "Assistant"
                context += f"{role}: {msg['content']}\n"
            
            context += f"Human: {user_message}\nAssistant:"
            
            # Generate response
            response = self.model.generate_content(context)
            
            if response and response.text:
                logger.info(f"Generated response for message: {user_message[:50]}...")
                return response.text
            else:
                return "I apologize, but I couldn't generate a response. Please try again."
                
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return f"Sorry, I encountered an error: {str(e)}. Please try again later."

def save_chat_history(chat_history: List[Dict]) -> Optional[str]:
    """Save chat history to file."""
    try:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"chat_history_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(chat_history, file, ensure_ascii=False, indent=2)
        
        return filename
    except Exception as e:
        logger.error(f"Error saving chat history: {str(e)}")
        return None

def initialize_session_state():
    """Initialize Streamlit session state variables."""
    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []
    if "chatbot" not in st.session_state:
        st.session_state.chatbot = GeminiChatBot()

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
        
        # Chat controls
        st.subheader("Chat Controls")
        
        if st.button("🗑️ Clear Chat History"):
            st.session_state.chat_history = []
            st.rerun()
        
        if st.button("💾 Save Chat History"):
            if st.session_state.chat_history:
                filename = save_chat_history(st.session_state.chat_history)
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
        
        # API Status
        st.markdown("---")
        st.subheader("API Status")
        if GEMINI_API_KEY:
            st.success("✅ API Key Configured")
        else:
            st.error("❌ API Key Missing")
            st.error("Please add GEMINI_API_KEY to Streamlit secrets or .env file")
    
    # Main content area
    st.title("🤖 Professional Life Assistant ChatBot")
    st.markdown("Ask me anything about your professional challenges, and I'll help you with solutions in both English and Hindi!")
    
    # Display chat history
    display_chat_history()
    
    # Chat input
    if prompt := st.chat_input("Type your message here..."):
        # Validate input
        if not prompt.strip():
            st.error("Please enter a valid message.")
            return
        
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
        
        # Limit chat history length
        if len(st.session_state.chat_history) > MAX_CHAT_HISTORY:
            st.session_state.chat_history = st.session_state.chat_history[-MAX_CHAT_HISTORY:]
    
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