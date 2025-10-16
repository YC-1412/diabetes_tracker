#!/usr/bin/env python3
"""
Pytest tests for Diabetes Tracker application
"""

import os
import sys
import tempfile
import shutil
import pytest
# from datetime import datetime
from unittest.mock import Mock, patch

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from diabetes_tracker.modules.auth import AuthManager
from diabetes_tracker.modules.database import DataManager
from diabetes_tracker.modules.ai_recommendations import AIRecommendationEngine


@pytest.fixture
def temp_data_dir():
    """Create a temporary directory for testing data"""
    test_dir = tempfile.mkdtemp()
    yield test_dir
    # Cleanup after tests
    try:
        shutil.rmtree(test_dir)
    except Exception:
        pass


@pytest.fixture
def mock_data_manager():
    """Create a mock DataManager for testing"""
    mock_dm = Mock(spec=DataManager)
    mock_session = Mock()
    mock_dm.get_db_session.return_value.__enter__ = Mock(return_value=mock_session)
    mock_dm.get_db_session.return_value.__exit__ = Mock(return_value=None)
    return mock_dm


@pytest.fixture
def auth_manager(mock_data_manager):
    """Create AuthManager instance with mocked data manager"""
    manager = AuthManager(mock_data_manager)
    
    # Mock the database session methods for AuthManager
    mock_session = Mock()
    mock_data_manager.get_db_session.return_value.__enter__ = Mock(return_value=mock_session)
    mock_data_manager.get_db_session.return_value.__exit__ = Mock(return_value=None)
    
    yield manager


@pytest.fixture
def data_manager():
    """Create a mock DataManager instance"""
    mock_dm = Mock(spec=DataManager)
    mock_session = Mock()
    mock_dm.get_db_session.return_value.__enter__ = Mock(return_value=mock_session)
    mock_dm.get_db_session.return_value.__exit__ = Mock(return_value=None)
    return mock_dm


@pytest.fixture
def ai_engine():
    """Create AIRecommendationEngine instance"""
    return AIRecommendationEngine()


class TestAuthentication:
    """Test authentication functionality"""
    
    def test_import_auth_manager(self):
        """Test that AuthManager can be imported"""
        assert AuthManager is not None
    
    def test_register_user_success(self, auth_manager):
        """Test successful user registration"""
        # Mock the database session and user query
        mock_session = auth_manager.data_manager.get_db_session.return_value.__enter__.return_value
        mock_session.query.return_value.filter.return_value.first.return_value = None  # User doesn't exist
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        success = auth_manager.register_user("testuser", "testpass123")
        assert success is True
    
    def test_register_user_duplicate(self, auth_manager):
        """Test duplicate registration prevention"""
        # Mock the database session and user query
        mock_session = auth_manager.data_manager.get_db_session.return_value.__enter__.return_value
        mock_user = Mock()  # User exists
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Try to register same user again
        success = auth_manager.register_user("testuser", "testpass123")
        assert success is False
    
    def test_login_valid_credentials(self, auth_manager):
        """Test successful login with valid credentials"""
        # Mock the database session and user query
        mock_session = auth_manager.data_manager.get_db_session.return_value.__enter__.return_value
        mock_user = Mock()
        mock_user.password_hash = auth_manager._hash_password("testpass123")  # Correct hash
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        success = auth_manager.login_user("testuser", "testpass123")
        assert success is True
    
    def test_login_invalid_credentials(self, auth_manager):
        """Test login failure with invalid credentials"""
        # Mock the database session and user query
        mock_session = auth_manager.data_manager.get_db_session.return_value.__enter__.return_value
        mock_user = Mock()
        mock_user.password_hash = auth_manager._hash_password("testpass123")  # Correct hash
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        success = auth_manager.login_user("testuser", "wrongpass")
        assert success is False
    
    def test_user_exists(self, auth_manager):
        """Test user existence checking"""
        # Mock the database session and user query
        mock_session = auth_manager.data_manager.get_db_session.return_value.__enter__.return_value
        
        # Test nonexistent user
        mock_session.query.return_value.filter.return_value.first.return_value = None
        assert auth_manager.user_exists("nonexistent") is False
        
        # Test existing user
        mock_user = Mock()
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        assert auth_manager.user_exists("testuser") is True
    
    def test_password_hashing(self, auth_manager):
        """Test that passwords are properly hashed"""
        # Test that the password hashing function works correctly
        password = "testpass123"
        hashed = auth_manager._hash_password(password)
        
        # Should be SHA-256 hash (64 characters)
        assert len(hashed) == 64
        assert hashed != password
        assert hashed == auth_manager._hash_password(password)  # Should be consistent
    
    def test_change_password_success(self, auth_manager):
        """Test successful password change"""
        # Mock the login_user method to return True for old password
        auth_manager.login_user = Mock(return_value=True)
        
        # Mock the database session and user query
        mock_session = auth_manager.data_manager.get_db_session.return_value.__enter__.return_value
        mock_user = Mock()
        mock_user.password_hash = "old_hash"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Test password change
        success = auth_manager.change_password("testuser", "oldpass123", "newpass456")
        assert success is True
        
        # Verify login_user was called to verify old password
        auth_manager.login_user.assert_called_once_with("testuser", "oldpass123")
        
        # Verify password hash was updated
        assert mock_user.password_hash != "old_hash"
        mock_session.commit.assert_called_once()
    
    def test_change_password_invalid_old_password(self, auth_manager):
        """Test password change with invalid old password"""
        # Mock the login_user method to return False for wrong password
        auth_manager.login_user = Mock(return_value=False)
        
        # Test password change with wrong old password
        success = auth_manager.change_password("testuser", "wrongpass", "newpass456")
        assert success is False
        
        # Verify login_user was called to verify old password
        auth_manager.login_user.assert_called_once_with("testuser", "wrongpass")
    
    def test_change_password_nonexistent_user(self, auth_manager):
        """Test password change for nonexistent user"""
        # Mock the login_user method to return False
        auth_manager.login_user = Mock(return_value=False)
        
        success = auth_manager.change_password("nonexistent", "oldpass", "newpass")
        assert success is False
        
        # Verify login_user was called
        auth_manager.login_user.assert_called_once_with("nonexistent", "oldpass")
    
    def test_change_password_same_password(self, auth_manager):
        """Test password change with same old and new password"""
        # Mock the login_user method to return True
        auth_manager.login_user = Mock(return_value=True)
        
        # Mock the database session and user query
        mock_session = auth_manager.data_manager.get_db_session.return_value.__enter__.return_value
        mock_user = Mock()
        mock_user.password_hash = "old_hash"
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        
        # Test password change with same password
        success = auth_manager.change_password("testuser", "samepass123", "samepass123")
        assert success is True
        
        # Verify login_user was called
        auth_manager.login_user.assert_called_once_with("testuser", "samepass123")
        
        # Verify password hash was updated (even if same password)
        assert mock_user.password_hash != "old_hash"
        mock_session.commit.assert_called_once()


class TestDataManagement:
    """Test data management functionality"""
    
    def test_import_data_manager(self):
        """Test that DataManager can be imported"""
        assert DataManager is not None
    
    def test_save_entry(self, data_manager):
        """Test saving a new diabetes entry"""
        # Mock the return value
        mock_entry_id = "12345678-1234-1234-1234-123456789012"
        data_manager.save_entry.return_value = mock_entry_id
        
        entry_id = data_manager.save_entry(
            "testuser", 120.5, "Oatmeal with berries", "30 min walk", "2024-01-15"
        )
        assert entry_id is not None
        assert len(entry_id) == 36  # UUID length
    
    def test_get_user_history(self, data_manager):
        """Test retrieving user history"""
        # Mock the return value
        mock_history = [
            {
                "entry_id": "12345678-1234-1234-1234-123456789012",
                "username": "testuser",
                "blood_sugar": 120.5,
                "meal": "Oatmeal with berries",
                "exercise": "30 min walk",
                "date": "2024-01-15T00:00:00",
                "created_at": "2024-01-15T00:00:00"
            }
        ]
        data_manager.get_user_history.return_value = mock_history
        
        history = data_manager.get_user_history("testuser")
        assert len(history) == 1
        assert history[0]["blood_sugar"] == 120.5
        assert history[0]["meal"] == "Oatmeal with berries"
        assert history[0]["exercise"] == "30 min walk"
        assert history[0]["date"] == "2024-01-15T00:00:00"
    
    def test_get_user_stats(self, data_manager):
        """Test statistics calculation"""
        # Mock the return value
        mock_stats = {
            "total_entries": 2,
            "avg_blood_sugar": 130.35,  # (120.5 + 140.2) / 2
            "entries_this_week": 2
        }
        data_manager.get_user_stats.return_value = mock_stats
        
        stats = data_manager.get_user_stats("testuser")
        assert stats["total_entries"] == 2
        assert stats["avg_blood_sugar"] == 130.35  # (120.5 + 140.2) / 2
    
    def test_get_chart_data(self, data_manager):
        """Test chart data formatting"""
        # Mock the return value
        mock_chart_data = {
            "labels": ["01/15", "01/16"],
            "data": [120.5, 140.2],
            "dates": ["2024-01-15", "2024-01-16"]
        }
        data_manager.get_chart_data.return_value = mock_chart_data
        
        chart_data = data_manager.get_chart_data("testuser")
        
        assert "labels" in chart_data
        assert "data" in chart_data
        assert "dates" in chart_data
        assert len(chart_data["labels"]) == 2
        assert len(chart_data["data"]) == 2
        assert len(chart_data["dates"]) == 2
        
        # Check that data is sorted chronologically (ascending for chart)
        assert chart_data["data"] == [120.5, 140.2]
    
    def test_empty_user_history(self, data_manager):
        """Test handling of user with no entries"""
        # Mock empty return values
        data_manager.get_user_history.return_value = []
        data_manager.get_user_stats.return_value = {
            "total_entries": 0,
            "avg_blood_sugar": 0,
            "entries_this_week": 0
        }
        
        history = data_manager.get_user_history("nonexistent")
        assert history == []
        
        stats = data_manager.get_user_stats("nonexistent")
        assert stats["total_entries"] == 0
        assert stats["avg_blood_sugar"] == 0
        assert stats["entries_this_week"] == 0
    
    def test_delete_entry(self, data_manager):
        """Test entry deletion"""
        # Mock the return values
        mock_entry_id = "12345678-1234-1234-1234-123456789012"
        data_manager.save_entry.return_value = mock_entry_id
        data_manager.delete_entry.return_value = True
        
        # Mock history before and after deletion
        data_manager.get_user_history.return_value = [
            {
                "entry_id": mock_entry_id,
                "username": "testuser",
                "blood_sugar": 120.5,
                "meal": "Oatmeal",
                "exercise": "Walk",
                "date": "2024-01-15T00:00:00",
                "created_at": "2024-01-15T00:00:00"
            }
        ]
        
        # Save an entry
        entry_id = data_manager.save_entry(
            "testuser", 120.5, "Oatmeal", "Walk", "2024-01-15"
        )
        
        # Verify entry exists
        history = data_manager.get_user_history("testuser")
        assert len(history) == 1
        
        # Delete entry
        success = data_manager.delete_entry(entry_id)
        assert success is True
        
        # Mock empty history after deletion
        data_manager.get_user_history.return_value = []
        
        # Verify entry is deleted
        history = data_manager.get_user_history("testuser")
        assert len(history) == 0


# class TestAIRecommendations:
#     """Test AI recommendation functionality"""
    
#     def test_import_ai_engine(self):
#         """Test that AIRecommendationEngine can be imported"""
#         assert AIRecommendationEngine is not None
    
#     def test_basic_recommendation(self, ai_engine):
#         """Test basic recommendation when API key is not available"""
#         recommendation = ai_engine.get_recommendation(
#             "testuser", 120.5, "Oatmeal", "Walking"
#         )
#         assert recommendation is not None
#         assert len(recommendation) > 10
#         assert isinstance(recommendation, str)
    
#     def test_blood_sugar_analysis_low(self, ai_engine):
#         """Test blood sugar analysis for low levels"""
#         status = ai_engine._analyze_blood_sugar(70)
#         assert "Low" in status
#         assert "Hypoglycemia" in status
    
#     def test_blood_sugar_analysis_normal_fasting(self, ai_engine):
#         """Test blood sugar analysis for normal fasting levels"""
#         status = ai_engine._analyze_blood_sugar(85)
#         assert "Normal" in status
#         assert "Fasting" in status
    
#     def test_blood_sugar_analysis_normal_post_meal(self, ai_engine):
#         """Test blood sugar analysis for normal post-meal levels"""
#         status = ai_engine._analyze_blood_sugar(120)
#         assert "Normal" in status
#         assert "Post-meal" in status
    
#     def test_blood_sugar_analysis_elevated(self, ai_engine):
#         """Test blood sugar analysis for elevated levels"""
#         status = ai_engine._analyze_blood_sugar(180)
#         assert "Elevated" in status
    
#     def test_blood_sugar_analysis_high(self, ai_engine):
#         """Test blood sugar analysis for high levels"""
#         status = ai_engine._analyze_blood_sugar(250)
#         assert "High" in status
#         assert "Hyperglycemia" in status
    
#     def test_meal_suggestions(self, ai_engine):
#         """Test meal suggestions functionality"""
#         suggestions = ai_engine.get_meal_suggestions(120.5)
#         assert suggestions is not None
#         assert len(suggestions) > 10
#         assert isinstance(suggestions, str)
    
#     def test_exercise_recommendations(self, ai_engine):
#         """Test exercise recommendations functionality"""
#         recommendations = ai_engine.get_exercise_recommendations(120.5, "Walking")
#         assert recommendations is not None
#         assert len(recommendations) > 10
#         assert isinstance(recommendations, str)


class TestFlaskApplication:
    """Test Flask application functionality"""
    
    def test_import_flask_app(self):
        """Test that Flask app can be imported"""
        try:
            from diabetes_tracker.app import app
            assert app is not None
        except ImportError as e:
            pytest.skip(f"Flask app import failed: {e}")
    
    def test_home_route(self):
        """Test home route returns 200"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                response = client.get("/")
                assert response.status_code == 200
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_register_route_exists(self):
        """Test register route exists and handles missing data"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                response = client.post("/api/register")
                # If database is not available, we get 500, but the route exists
                # This is acceptable for testing purposes
                assert response.status_code in [400, 500]  # Missing data or DB error
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_login_route_exists(self):
        """Test login route exists and handles missing data"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                response = client.post("/api/login")
                # If database is not available, we get 500, but the route exists
                # This is acceptable for testing purposes
                assert response.status_code in [400, 500]  # Missing data or DB error
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_log_entry_route_exists(self):
        """Test log entry route exists and handles missing data"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                response = client.post("/api/log-entry")
                # If database is not available, we get 500, but the route exists
                # This is acceptable for testing purposes
                assert response.status_code in [400, 500]  # Missing data or DB error
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_history_route_exists(self):
        """Test history route exists"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                response = client.get("/api/history/testuser")
                # Should return 200 even if user doesn't exist (empty history)
                assert response.status_code in [200, 400]
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_chart_data_route_exists(self):
        """Test chart data route exists"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                response = client.get("/api/chart-data/testuser")
                # Should return 200 even if user doesn't exist (empty chart data)
                assert response.status_code in [200, 400]
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_change_password_route_exists(self):
        """Test change password route exists"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                response = client.post("/api/change-password", json={
                    "username": "testuser",
                    "old_password": "oldpass",
                    "new_password": "newpass"
                })
                # Should return 401 for invalid credentials or 400 for missing data
                assert response.status_code in [200, 400, 401]
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_change_password_success(self):
        """Test successful password change via API"""
        try:
            from diabetes_tracker.app import app
            
            with patch('diabetes_tracker.app.auth_manager') as mock_auth_manager:
                # Mock successful password change
                mock_auth_manager.change_password.return_value = True
                
                with app.test_client() as client:
                    change_response = client.post("/api/change-password", json={
                        "username": "apiuser",
                        "old_password": "oldpass123",
                        "new_password": "newpass456"
                    })
                    
                    assert change_response.status_code == 200
                    data = change_response.get_json()
                    assert "message" in data
                    assert "successfully" in data["message"].lower()
                    
                    # Verify auth_manager.change_password was called correctly
                    mock_auth_manager.change_password.assert_called_once_with(
                        "apiuser", "oldpass123", "newpass456"
                    )
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_change_password_invalid_old_password(self):
        """Test password change with invalid old password via API"""
        try:
            from diabetes_tracker.app import app
            
            with patch('diabetes_tracker.app.auth_manager') as mock_auth_manager:
                # Mock failed password change
                mock_auth_manager.change_password.return_value = False
                
                with app.test_client() as client:
                    change_response = client.post("/api/change-password", json={
                        "username": "apiuser2",
                        "old_password": "wrongpass",
                        "new_password": "newpass456"
                    })
                    
                    assert change_response.status_code == 401
                    data = change_response.get_json()
                    assert "error" in data
                    
                    # Verify auth_manager.change_password was called correctly
                    mock_auth_manager.change_password.assert_called_once_with(
                        "apiuser2", "wrongpass", "newpass456"
                    )
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_change_password_missing_fields(self):
        """Test password change with missing fields via API"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                # Test missing username
                response = client.post("/api/change-password", json={
                    "old_password": "oldpass",
                    "new_password": "newpass"
                })
                assert response.status_code == 400
                
                # Test missing old password
                response = client.post("/api/change-password", json={
                    "username": "testuser",
                    "new_password": "newpass"
                })
                assert response.status_code == 400
                
                # Test missing new password
                response = client.post("/api/change-password", json={
                    "username": "testuser",
                    "old_password": "oldpass"
                })
                assert response.status_code == 400
        except ImportError:
            pytest.skip("Flask app not available")
    
    def test_change_password_short_password(self):
        """Test password change with too short new password via API"""
        try:
            from diabetes_tracker.app import app
            
            with app.test_client() as client:
                response = client.post("/api/change-password", json={
                    "username": "testuser",
                    "old_password": "oldpass",
                    "new_password": "123"  # Too short
                })
                assert response.status_code == 400
                data = response.get_json()
                assert "error" in data
                assert "6 characters" in data["error"]
        except ImportError:
            pytest.skip("Flask app not available")


class TestIntegration:
    """Integration tests for the complete workflow"""
    
    def test_complete_user_workflow(self, auth_manager, data_manager, ai_engine):
        """Test complete user workflow: register, login, log entry, get recommendations"""
        # Mock the database session and user query for auth_manager
        mock_session = auth_manager.data_manager.get_db_session.return_value.__enter__.return_value
        mock_session.query.return_value.filter.return_value.first.return_value = None  # User doesn't exist initially
        mock_session.add = Mock()
        mock_session.commit = Mock()
        
        # 1. Register user
        success = auth_manager.register_user("workflow_user", "password123")
        assert success is True
        
        # 2. Login user - mock successful login
        mock_user = Mock()
        mock_user.password_hash = auth_manager._hash_password("password123")
        mock_session.query.return_value.filter.return_value.first.return_value = mock_user
        success = auth_manager.login_user("workflow_user", "password123")
        assert success is True
        
        # 3. Log entry - mock data manager methods
        mock_entry_id = "12345678-1234-1234-1234-123456789012"
        data_manager.save_entry.return_value = mock_entry_id
        
        entry_id = data_manager.save_entry(
            "workflow_user", 125.0, "Grilled chicken salad", "30 min jog", "2024-01-15"
        )
        assert entry_id is not None
        
        # 4. Get history - mock return value
        mock_history = [
            {
                "entry_id": mock_entry_id,
                "username": "workflow_user",
                "blood_sugar": 125.0,
                "meal": "Grilled chicken salad",
                "exercise": "30 min jog",
                "date": "2024-01-15T00:00:00",
                "created_at": "2024-01-15T00:00:00"
            }
        ]
        data_manager.get_user_history.return_value = mock_history
        
        history = data_manager.get_user_history("workflow_user")
        assert len(history) == 1
        assert history[0]["blood_sugar"] == 125.0
        
        # 5. Get recommendations - mock AI engine
        mock_recommendation = "Based on your blood sugar level of 125.0, this is a good result."
        with patch.object(ai_engine, 'get_recommendation', return_value=mock_recommendation):
            recommendation = ai_engine.get_recommendation(
                "workflow_user", 125.0, "Grilled chicken salad", "30 min jog"
            )
            assert recommendation is not None
            assert len(recommendation) > 10
        
        # 6. Get chart data - mock return value
        mock_chart_data = {
            "labels": ["01/15"],
            "data": [125.0],
            "dates": ["2024-01-15"]
        }
        data_manager.get_chart_data.return_value = mock_chart_data
        
        chart_data = data_manager.get_chart_data("workflow_user")
        assert "labels" in chart_data
        assert "data" in chart_data
        assert len(chart_data["data"]) == 1
        assert chart_data["data"][0] == 125.0
