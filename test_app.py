#!/usr/bin/env python3
"""
Simple test script to verify the diabetes tracker application modules work correctly.
"""

import os
import sys
import tempfile
import shutil
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_modules():
    """Test all modules to ensure they work correctly"""

    print("🧪 Testing Diabetes Tracker Modules...")

    # Create a temporary directory for testing
    test_dir = tempfile.mkdtemp()
    original_data_dir = None

    try:
        # Test imports
        print("📦 Testing imports...")
        from modules.auth import AuthManager
        from modules.database import DataManager
        from modules.ai_recommendations import AIRecommendationEngine

        print("✅ All modules imported successfully")

        # Temporarily change data directory for testing
        import modules.auth
        import modules.database

        original_data_dir = modules.auth.AuthManager.data_dir
        modules.auth.AuthManager.data_dir = test_dir
        modules.database.DataManager.data_dir = test_dir

        # Test Authentication
        print("\n🔐 Testing Authentication...")
        auth_manager = AuthManager()

        # Test user registration
        success = auth_manager.register_user("testuser", "testpass123")
        assert success, "User registration should succeed"
        print("✅ User registration works")

        # Test duplicate registration
        success = auth_manager.register_user("testuser", "testpass123")
        assert not success, "Duplicate registration should fail"
        print("✅ Duplicate registration prevention works")

        # Test login
        success = auth_manager.login_user("testuser", "testpass123")
        assert success, "Valid login should succeed"
        print("✅ Valid login works")

        # Test invalid login
        success = auth_manager.login_user("testuser", "wrongpass")
        assert not success, "Invalid login should fail"
        print("✅ Invalid login prevention works")

        # Test Data Management
        print("\n💾 Testing Data Management...")
        data_manager = DataManager()

        # Test saving entry
        entry_id = data_manager.save_entry(
            "testuser", 120.5, "Oatmeal with berries", "30 min walk", "2024-01-15"
        )
        assert entry_id, "Entry should be saved successfully"
        print("✅ Entry saving works")

        # Test getting history
        history = data_manager.get_user_history("testuser")
        assert len(history) == 1, "Should have one entry in history"
        assert history[0]["blood_sugar"] == 120.5, "Blood sugar should match"
        print("✅ History retrieval works")

        # Test getting stats
        stats = data_manager.get_user_stats("testuser")
        assert stats["total_entries"] == 1, "Should have one total entry"
        assert stats["avg_blood_sugar"] == 120.5, "Average blood sugar should match"
        print("✅ Statistics calculation works")

        # Test AI Recommendations
        print("\n🤖 Testing AI Recommendations...")
        ai_engine = AIRecommendationEngine()

        # Test basic recommendation (without API key)
        recommendation = ai_engine.get_recommendation(
            "testuser", 120.5, "Oatmeal", "Walking"
        )
        assert recommendation, "Should return a recommendation"
        assert len(recommendation) > 10, "Recommendation should be substantial"
        print("✅ Basic AI recommendations work")

        # Test blood sugar analysis
        status = ai_engine._analyze_blood_sugar(70)
        assert "Low" in status, "Low blood sugar should be detected"

        status = ai_engine._analyze_blood_sugar(120)
        assert "Normal" in status, "Normal blood sugar should be detected"

        status = ai_engine._analyze_blood_sugar(250)
        assert "High" in status, "High blood sugar should be detected"
        print("✅ Blood sugar analysis works")

        print("\n🎉 All tests passed successfully!")
        return True

    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False

    finally:
        # Clean up
        if original_data_dir:
            modules.auth.AuthManager.data_dir = original_data_dir
            modules.database.DataManager.data_dir = original_data_dir

        # Remove test directory
        try:
            shutil.rmtree(test_dir)
        except:
            pass


def test_flask_app():
    """Test if Flask app can be imported and basic routes work"""
    print("\n🌐 Testing Flask Application...")

    try:
        # Test if we can import the app
        from app import app

        print("✅ Flask app imports successfully")

        # Test if app has required routes
        with app.test_client() as client:
            # Test home route
            response = client.get("/")
            assert response.status_code == 200, "Home route should return 200"
            print("✅ Home route works")

            # Test API routes exist (should return 400 for missing data)
            response = client.post("/api/register")
            assert (
                response.status_code == 400
            ), "Register route should return 400 for missing data"
            print("✅ Register route exists")

            response = client.post("/api/login")
            assert (
                response.status_code == 400
            ), "Login route should return 400 for missing data"
            print("✅ Login route exists")

        print("✅ Flask application tests passed!")
        return True

    except Exception as e:
        print(f"❌ Flask test failed: {str(e)}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("🚀 Starting Diabetes Tracker Tests...")

    # Test modules
    modules_ok = test_modules()

    # Test Flask app
    flask_ok = test_flask_app()

    if modules_ok and flask_ok:
        print("\n🎊 All tests passed! The application is ready to run.")
        print("\nTo start the application:")
        print("1. Install dependencies: pip install -r requirements.txt")
        print("2. Set up environment variables: cp .env.example .env")
        print("3. Run the app: python app.py")
        print("4. Open browser to: http://localhost:5000")
    else:
        print("\n💥 Some tests failed. Please check the errors above.")
        sys.exit(1)
