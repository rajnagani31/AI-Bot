#!/usr/bin/env python3
"""
Test script to verify Gemini API connectivity with gemini-2.0-flash model.
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

def test_gemini_api():
    """Test Gemini API connection and model availability."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        print("❌ GEMINI_API_KEY not found in environment variables")
        print("Please add your API key to .env file:")
        print("GEMINI_API_KEY=your_api_key_here")
        return False
    
    try:
        # Configure Gemini
        genai.configure(api_key=api_key)
        print("✅ API key configured successfully")
        
        # Test available models
        print("\n📋 Available models:")
        models = genai.list_models()
        available_models = []
        
        for model in models:
            model_name = model.name.replace('models/', '')
            available_models.append(model_name)
            print(f"  - {model_name}")
        
        # Check if gemini-2.0-flash is available
        if 'gemini-2.0-flash' in available_models:
            print("\n✅ gemini-2.0-flash model is available")
        else:
            print("\n⚠️  gemini-2.0-flash not found in available models")
            print("Available flash models:")
            flash_models = [m for m in available_models if 'flash' in m.lower()]
            for model in flash_models:
                print(f"  - {model}")
            
            if flash_models:
                print(f"\nYou can use: {flash_models[0]}")
            return False
        
        # Test the model
        print("\n🧪 Testing gemini-2.0-flash model...")
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Simple test prompt
        test_prompt = "Hello! Can you respond in both English and Hindi? This is a test."
        
        response = model.generate_content(test_prompt)
        
        if response and response.text:
            print("✅ Model test successful!")
            print("\n📝 Test Response:")
            print("-" * 50)
            print(response.text)
            print("-" * 50)
            return True
        else:
            print("❌ Model test failed - no response generated")
            return False
            
    except Exception as e:
        print(f"❌ Error testing API: {str(e)}")
        
        # Common error handling
        error_str = str(e).lower()
        
        if "api_key" in error_str or "authentication" in error_str:
            print("\n💡 This looks like an API key issue:")
            print("1. Make sure your API key is correct")
            print("2. Check if your API key has the necessary permissions")
            print("3. Verify your API key at: https://aistudio.google.com/app/apikey")
        
        elif "quota" in error_str or "limit" in error_str:
            print("\n💡 This looks like a quota/rate limit issue:")
            print("1. Check your API usage at Google AI Studio")
            print("2. Wait a few minutes and try again")
            print("3. Verify your billing/usage limits")
        
        elif "model" in error_str:
            print("\n💡 This looks like a model availability issue:")
            print("1. The gemini-2.0-flash model might not be available in your region")
            print("2. Try using 'gemini-1.5-flash' instead")
            print("3. Check Google AI Studio for available models")
        
        return False

def get_recommended_model():
    """Get recommended model based on availability."""
    try:
        load_dotenv()
        api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            return None
        
        genai.configure(api_key=api_key)
        models = genai.list_models()
        available_models = [model.name.replace('models/', '') for model in models]
        
        # Priority order for models
        preferred_models = [
            'gemini-2.0-flash',
            'gemini-1.5-flash',
            'gemini-1.5-pro',
            'gemini-pro'
        ]
        
        for model in preferred_models:
            if model in available_models:
                return model
        
        # If none of the preferred models, return the first available
        if available_models:
            return available_models[0]
        
        return None
        
    except Exception:
        return None

if __name__ == "__main__":
    print("🤖 Gemini API Test Script")
    print("=" * 50)
    
    success = test_gemini_api()
    
    if not success:
        print("\n🔧 Troubleshooting suggestions:")
        recommended_model = get_recommended_model()
        
        if recommended_model and recommended_model != 'gemini-2.0-flash':
            print(f"\n💡 Try using '{recommended_model}' instead of 'gemini-2.0-flash'")
            print(f"Update your code to use: genai.GenerativeModel('{recommended_model}')")
        
        print("\n📚 Helpful links:")
        print("- Get API key: https://aistudio.google.com/app/apikey")
        print("- API documentation: https://ai.google.dev/docs")
        print("- Pricing: https://ai.google.dev/pricing")
    
    print(f"\n{'✅ All tests passed!' if success else '❌ Tests failed'}")