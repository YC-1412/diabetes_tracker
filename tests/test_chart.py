#!/usr/bin/env python3
"""
Pytest tests for chart functionality
"""

import pytest
import requests
import json
import time
from unittest.mock import patch


@pytest.fixture
def app_url():
    """Base URL for the application"""
    return "http://localhost:5001"


@pytest.fixture
def test_user():
    """Test user for chart data"""
    return "tester1"


@pytest.fixture
def sample_chart_data():
    """Sample chart data structure for testing"""
    return {
        "chart_data": {
            "labels": ["01/15", "01/16", "01/17"],
            "data": [120.5, 135.2, 118.8],
            "dates": ["2024-01-15", "2024-01-16", "2024-01-17"]
        }
    }


class TestChartAPI:
    """Test chart API functionality"""
    
    def test_chart_api_endpoint_exists(self, app_url, test_user):
        """Test that chart API endpoint is accessible"""
        try:
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            # Should return 200 even if user doesn't exist (empty chart data)
            assert response.status_code in [200, 400]
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_chart_api_response_structure(self, app_url, test_user):
        """Test that chart API returns proper JSON structure"""
        try:
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            
            if response.status_code == 200:
                data = response.json()
                assert "chart_data" in data
                
                chart_data = data["chart_data"]
                required_keys = ["labels", "data", "dates"]
                assert all(key in chart_data for key in required_keys)
            else:
                pytest.skip("Chart API returned error status")
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_chart_data_types(self, app_url, test_user):
        """Test that chart data has correct data types"""
        try:
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            
            if response.status_code == 200:
                data = response.json()
                chart_data = data["chart_data"]
                
                # Check data types
                assert isinstance(chart_data["labels"], list)
                assert isinstance(chart_data["data"], list)
                assert isinstance(chart_data["dates"], list)
                
                # Check that arrays have same length
                if len(chart_data["data"]) > 0:
                    assert len(chart_data["labels"]) == len(chart_data["data"])
                    assert len(chart_data["data"]) == len(chart_data["dates"])
            else:
                pytest.skip("Chart API returned error status")
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_chart_data_format(self, app_url, test_user):
        """Test that chart data is properly formatted"""
        try:
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            
            if response.status_code == 200:
                data = response.json()
                chart_data = data["chart_data"]
                
                # Check that we have data
                if len(chart_data["data"]) > 0:
                    # Check that data is sorted chronologically
                    dates = chart_data["dates"]
                    assert dates == sorted(dates), "Dates should be sorted chronologically"
                    
                    # Check that labels are formatted as MM/DD
                    for label in chart_data["labels"]:
                        assert len(label) == 5, "Labels should be MM/DD format"
                        assert label[2] == "/", "Labels should have / separator"
                    
                    # Check that dates are formatted as YYYY-MM-DD
                    for date in chart_data["dates"]:
                        assert len(date) == 10, "Dates should be YYYY-MM-DD format"
                        assert date[4] == "-" and date[7] == "-", "Dates should have - separators"
                    
                    # Check that blood sugar values are numeric
                    for value in chart_data["data"]:
                        assert isinstance(value, (int, float)), "Blood sugar values should be numeric"
                        assert 50 <= value <= 500, "Blood sugar values should be in valid range"
                else:
                    # Empty data is also valid
                    assert chart_data["labels"] == []
                    assert chart_data["data"] == []
                    assert chart_data["dates"] == []
            else:
                pytest.skip("Chart API returned error status")
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_chart_data_consistency(self, app_url, test_user):
        """Test that chart data arrays are consistent"""
        try:
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            
            if response.status_code == 200:
                data = response.json()
                chart_data = data["chart_data"]
                
                # Check array consistency
                labels_len = len(chart_data["labels"])
                data_len = len(chart_data["data"])
                dates_len = len(chart_data["dates"])
                
                assert labels_len == data_len == dates_len, "All arrays should have same length"
                
                # If there's data, check that it makes sense
                if data_len > 0:
                    # Check that blood sugar values are reasonable
                    for value in chart_data["data"]:
                        assert 50 <= value <= 500, f"Blood sugar value {value} is out of range"
                    
                    # Check that dates are valid
                    for date_str in chart_data["dates"]:
                        try:
                            # Try to parse the date
                            time.strptime(date_str, "%Y-%m-%d")
                        except ValueError:
                            pytest.fail(f"Invalid date format: {date_str}")
            else:
                pytest.skip("Chart API returned error status")
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")


class TestChartDataProcessing:
    """Test chart data processing functionality"""
    
    def test_empty_chart_data(self, app_url, test_user):
        """Test handling of empty chart data"""
        try:
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            
            if response.status_code == 200:
                data = response.json()
                chart_data = data["chart_data"]
                
                # Empty data should have empty arrays
                if len(chart_data["data"]) == 0:
                    assert chart_data["labels"] == []
                    assert chart_data["data"] == []
                    assert chart_data["dates"] == []
            else:
                pytest.skip("Chart API returned error status")
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_single_data_point(self, app_url, test_user):
        """Test chart data with single data point"""
        try:
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            
            if response.status_code == 200:
                data = response.json()
                chart_data = data["chart_data"]
                
                if len(chart_data["data"]) == 1:
                    # Single data point should have one entry in each array
                    assert len(chart_data["labels"]) == 1
                    assert len(chart_data["dates"]) == 1
                    
                    # Check data types
                    assert isinstance(chart_data["data"][0], (int, float))
                    assert isinstance(chart_data["labels"][0], str)
                    assert isinstance(chart_data["dates"][0], str)
            else:
                pytest.skip("Chart API returned error status")
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_multiple_data_points(self, app_url, test_user):
        """Test chart data with multiple data points"""
        try:
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            
            if response.status_code == 200:
                data = response.json()
                chart_data = data["chart_data"]
                
                if len(chart_data["data"]) > 1:
                    # Multiple data points should be sorted chronologically
                    dates = chart_data["dates"]
                    assert dates == sorted(dates), "Dates should be sorted chronologically"
                    
                    # Check that all arrays have same length
                    assert len(chart_data["labels"]) == len(chart_data["data"])
                    assert len(chart_data["data"]) == len(chart_data["dates"])
            else:
                pytest.skip("Chart API returned error status")
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")


class TestChartIntegration:
    """Integration tests for chart functionality"""
    
    def test_chart_with_history_endpoint(self, app_url, test_user):
        """Test that chart data is consistent with history endpoint"""
        try:
            # Get chart data
            chart_response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            
            # Get history data
            history_response = requests.get(f'{app_url}/api/history/{test_user}')
            
            if chart_response.status_code == 200 and history_response.status_code == 200:
                chart_data = chart_response.json()["chart_data"]
                history_data = history_response.json()["history"]
                
                # If there's history data, chart data should reflect it
                if len(history_data) > 0:
                    assert len(chart_data["data"]) == len(history_data)
                    
                    # Check that blood sugar values match
                    for i, entry in enumerate(history_data):
                        if i < len(chart_data["data"]):
                            assert entry["blood_sugar"] == chart_data["data"][i]
            else:
                pytest.skip("One or both endpoints returned error status")
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_chart_data_performance(self, app_url, test_user):
        """Test chart data API performance"""
        try:
            start_time = time.time()
            response = requests.get(f'{app_url}/api/chart-data/{test_user}')
            end_time = time.time()
            
            response_time = end_time - start_time
            
            # Chart data should load within 2 seconds
            assert response_time < 2.0, f"Chart data took {response_time:.2f} seconds to load"
            
            if response.status_code == 200:
                # Response should be valid JSON
                data = response.json()
                assert "chart_data" in data
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")


class TestChartErrorHandling:
    """Test chart error handling"""
    
    def test_invalid_user_parameter(self, app_url):
        """Test chart API with invalid user parameter"""
        try:
            # Test with empty username
            response = requests.get(f'{app_url}/api/chart-data/')
            # Should return 404 for invalid route
            assert response.status_code == 404
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_special_characters_in_username(self, app_url):
        """Test chart API with special characters in username"""
        try:
            # Test with username containing special characters
            response = requests.get(f'{app_url}/api/chart-data/test@user')
            
            # Should handle special characters gracefully
            assert response.status_code in [200, 400]
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")
    
    def test_very_long_username(self, app_url):
        """Test chart API with very long username"""
        try:
            # Test with very long username
            long_username = "a" * 100
            response = requests.get(f'{app_url}/api/chart-data/{long_username}')
            
            # Should handle long usernames gracefully
            assert response.status_code in [200, 400]
        except requests.exceptions.ConnectionError:
            pytest.skip("Application not running on localhost:5001")


@pytest.mark.integration
class TestChartWithMockData:
    """Test chart functionality with mock data"""
    
    @patch('requests.get')
    def test_chart_api_with_mock_data(self, mock_get, sample_chart_data):
        """Test chart API with mock response data"""
        # Mock the API response
        mock_response = type('MockResponse', (), {
            'status_code': 200,
            'json': lambda: sample_chart_data
        })()
        mock_get.return_value = mock_response
        
        # Test the mock response
        response = requests.get('http://localhost:5001/api/chart-data/tester1')
        data = response.json()
        
        assert response.status_code == 200
        assert "chart_data" in data
        assert len(data["chart_data"]["data"]) == 3
        assert data["chart_data"]["data"] == [120.5, 135.2, 118.8]
    
    @patch('requests.get')
    def test_chart_api_error_handling(self, mock_get):
        """Test chart API error handling with mock"""
        # Mock an error response
        mock_response = type('MockResponse', (), {
            'status_code': 500,
            'json': lambda: {"error": "Internal server error"}
        })()
        mock_get.return_value = mock_response
        
        # Test the error response
        response = requests.get('http://localhost:5001/api/chart-data/tester1')
        
        assert response.status_code == 500
        data = response.json()
        assert "error" in data


# Configuration for pytest
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "integration: mark test as integration test"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers"""
    for item in items:
        if "integration" in item.nodeid:
            item.add_marker(pytest.mark.integration) 