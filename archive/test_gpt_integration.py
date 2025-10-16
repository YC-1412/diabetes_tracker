#!/usr/bin/env python3
"""
Test script for GPT API integration
"""

import os
import sys
from dotenv import load_dotenv

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Load environment variables
load_dotenv()

from diabetes_tracker.modules.ai_recommendations import AIRecommendationEngine


def test_gpt_integration():
    """Test the GPT API integration"""
    
    print("Testing GPT API Integration...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY not found in environment variables")
        print("Please set your OpenAI API key in the .env file")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Initialize the AI engine
    try:
        ai_engine = AIRecommendationEngine()
        print("✅ AI Recommendation Engine initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize AI engine: {e}")
        print("This might be due to missing API key or network issues")
        return False
    
    # Test basic recommendation
    try:
        print("\nTesting basic recommendation...")
        recommendation = ai_engine.get_recommendation(
            username="TestUser",
            blood_sugar=120.0,
            meal="Grilled chicken salad",
            exercise="30 minutes walking"
        )
        print("✅ Basic recommendation generated successfully")
        print(f"Recommendation: {recommendation[:100]}...")
    except Exception as e:
        print(f"❌ Failed to get basic recommendation: {e}")
        return False
    
    # Test meal suggestions
    try:
        print("\nTesting meal suggestions...")
        meal_suggestions = ai_engine.get_meal_suggestions(
            blood_sugar=120.0,
            preferences="Low carb, vegetarian"
        )
        print("✅ Meal suggestions generated successfully")
        print(f"Suggestions: {meal_suggestions[:100]}...")
    except Exception as e:
        print(f"❌ Failed to get meal suggestions: {e}")
        return False
    
    # Test exercise recommendations
    try:
        print("\nTesting exercise recommendations...")
        exercise_recs = ai_engine.get_exercise_recommendations(
            blood_sugar=120.0,
            current_exercise="Walking"
        )
        print("✅ Exercise recommendations generated successfully")
        print(f"Recommendations: {exercise_recs[:100]}...")
    except Exception as e:
        print(f"❌ Failed to get exercise recommendations: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All GPT API integration tests passed!")
    return True


if __name__ == "__main__":
    success = test_gpt_integration()
    sys.exit(0 if success else 1) 