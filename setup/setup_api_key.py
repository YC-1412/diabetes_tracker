#!/usr/bin/env python3
"""
Interactive script to set up OpenAI API key
"""

import os
import sys
from pathlib import Path


def setup_api_key():
    """Interactive setup for OpenAI API key"""
    
    print("🔑 OpenAI API Key Setup")
    print("=" * 50)
    
    # Check if .env file exists
    env_file = Path(".env")
    if not env_file.exists():
        print("Creating .env file from template...")
        try:
            # Copy from env.example
            example_file = Path(".env.example")
            if example_file.exists():
                with open(example_file, 'r') as f:
                    content = f.read()
                with open(env_file, 'w') as f:
                    f.write(content)
                print("Created .env file from template")
            else:
                print(".env.example not found")
                return False
        except Exception as e:
            print(f"Failed to create .env file: {e}")
            return False
    
    # Read current .env content
    try:
        with open(env_file, 'r') as f:
            content = f.read()
    except Exception as e:
        print(f"Failed to read .env file: {e}")
        return False
    
    # Check if API key is already set
    if "OPENAI_API_KEY=" in content and not "OPENAI_API_KEY=your-openai-api-key" in content:
        print("OpenAI API key is already configured")
        return True
    
    print("\nTo get your OpenAI API key:")
    print("1. Go to https://platform.openai.com/")
    print("2. Sign in or create an account")
    print("3. Click on your profile → 'API Keys'")
    print("4. Click 'Create new secret key'")
    print("5. Copy the key (it starts with 'sk-')")
    print("\n" + "=" * 50)
    
    # Get API key from user
    api_key = input("Enter your OpenAI API key (or press Enter to skip): ").strip()
    
    if not api_key:
        print("Skipping API key setup")
        return True
    
    # Validate API key format
    if not api_key.startswith("sk-"):
        print("Invalid API key format. API keys should start with 'sk-'")
        return False
    
    # Update .env file
    try:
        # Replace placeholder or add new line
        if "OPENAI_API_KEY=your-openai-api-key" in content:
            new_content = content.replace("OPENAI_API_KEY=your-openai-api-key", f"OPENAI_API_KEY={api_key}")
        elif "OPENAI_API_KEY=" in content:
            # Replace existing key
            lines = content.split('\n')
            new_lines = []
            for line in lines:
                if line.startswith("OPENAI_API_KEY="):
                    new_lines.append(f"OPENAI_API_KEY={api_key}")
                else:
                    new_lines.append(line)
            new_content = '\n'.join(new_lines)
        else:
            # Add new line
            new_content = content + f"\nOPENAI_API_KEY={api_key}"
        
        with open(env_file, 'w') as f:
            f.write(new_content)
        
        print("API key saved to .env file")
        return True
        
    except Exception as e:
        print(f"Failed to save API key: {e}")
        return False


def test_setup():
    """Test the API key setup"""
    
    print("\nTesting API key setup...")
    
    # Load environment variables
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("python-dotenv not installed. Run: pip install python-dotenv")
        return False
    
    # Check if API key is loaded
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key or api_key == "your-openai-api-key":
        print("API key not found or not properly set")
        return False
    
    print(f"API key loaded: {api_key[:10]}...")
    
    # Test AI engine initialization
    try:
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))
        from diabetes_tracker.modules.ai_recommendations import AIRecommendationEngine
        
        ai_engine = AIRecommendationEngine()
        print("AI Recommendation Engine initialized successfully")
        
        # Test a simple recommendation
        recommendation = ai_engine.get_recommendation(
            username="TestUser",
            blood_sugar=120.0,
            meal="Test meal",
            exercise="Test exercise"
        )
        
        if recommendation and len(recommendation) > 10:
            print("API call successful!")
            print(f"Sample response: {recommendation[:100]}...")
            return True
        else:
            print("API call failed or returned empty response")
            return False
            
    except Exception as e:
        print(f"Failed to test AI engine: {e}")
        return False


if __name__ == "__main__":
    print("Diabetes Tracker - OpenAI API Setup")
    print("=" * 50)
    
    # Setup API key
    if setup_api_key():
        print("\n" + "=" * 50)
        
        # Test the setup
        if test_setup():
            print("\nSetup completed successfully!")
            print("You can now run: python test_gpt_integration.py")
        else:
            print("\nSetup completed but testing failed")
            print("Check your API key and internet connection")
    else:
        print("\nSetup failed")
        sys.exit(1) 