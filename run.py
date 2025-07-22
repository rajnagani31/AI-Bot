#!/usr/bin/env python3
"""
Production runner script for the Streamlit ChatBot application.
This script handles environment setup, logging configuration, and application startup.
"""

import os
import sys
import logging
import subprocess
from pathlib import Path
from config import Config

def setup_logging():
    """Setup logging configuration for production."""
    try:
        log_level = getattr(logging, Config.LOG_LEVEL)
    except AttributeError:
        log_level = logging.INFO
    
    logging.basicConfig(
        level=log_level,
        format=Config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(Config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Check if all required dependencies are installed."""
    required_packages = [
        'streamlit',
        'google-generativeai',
        'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
        except ImportError:
            missing_packages.append(package)
    
    if missing_packages:
        print(f"Missing required packages: {', '.join(missing_packages)}")
        print("Please install them using: pip install -r requirements.txt")
        sys.exit(1)

def create_required_files():
    """Create required files and directories if they don't exist."""
    # Create chat histories directory
    os.makedirs(Config.CHAT_HISTORY_DIR, exist_ok=True)
    
    # Create .env file if it doesn't exist
    if not os.path.exists('.env'):
        print("Creating .env file template...")
        with open('.env', 'w') as f:
            f.write("GEMINI_API_KEY=your_gemini_api_key_here\n")
        print("Please update .env file with your actual Gemini API key")
    
    # Create system_prompt.txt if it doesn't exist
    if not os.path.exists(Config.SYSTEM_PROMPT_FILE):
        print(f"Warning: {Config.SYSTEM_PROMPT_FILE} not found. The application will use a default prompt.")

def validate_environment():
    """Validate the environment configuration."""
    try:
        Config.validate()
        print("✓ Environment configuration is valid")
    except ValueError as e:
        print(f"✗ Environment validation failed: {e}")
        sys.exit(1)

def run_streamlit_app(port=8501, host="localhost", development=False):
    """
    Run the Streamlit application.
    
    Args:
        port: Port to run the application on
        host: Host to bind the application to
        development: Whether to run in development mode
    """
    cmd = [
        "streamlit", "run", "main.py",
        "--server.port", str(port),
        "--server.address", host,
        "--server.headless", "true" if not development else "false",
        "--browser.gatherUsageStats", "false",
        "--server.fileWatcherType", "poll" if not development else "auto"
    ]
    
    if not development:
        cmd.extend([
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
    
    print(f"Starting Streamlit application on {host}:{port}")
    print(f"Mode: {'Development' if development else 'Production'}")
    
    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Error running Streamlit application: {e}")
        sys.exit(1)

def main():
    """Main function to start the application."""
    print("🤖 Professional Life Assistant ChatBot")
    print("=" * 50)
    
    # Setup logging
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("Starting ChatBot application...")
    
    # Check dependencies
    print("Checking dependencies...")
    check_dependencies()
    print("✓ All dependencies are installed")
    
    # Create required files
    print("Setting up required files...")
    create_required_files()
    
    # Validate environment
    print("Validating environment...")
    validate_environment()
    
    # Parse command line arguments
    development = "--dev" in sys.argv
    port = 8501
    host = "localhost"
    
    if "--port" in sys.argv:
        try:
            port_index = sys.argv.index("--port")
            port = int(sys.argv[port_index + 1])
        except (IndexError, ValueError):
            print("Invalid port specified. Using default port 8501.")
    
    if "--host" in sys.argv:
        try:
            host_index = sys.argv.index("--host")
            host = sys.argv[host_index + 1]
        except IndexError:
            print("Invalid host specified. Using default host localhost.")
    
    # Run the application
    logger.info(f"Starting application on {host}:{port}")
    run_streamlit_app(port=port, host=host, development=development)

if __name__ == "__main__":
    main()