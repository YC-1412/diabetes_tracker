#!/usr/bin/env python3
"""Debug script to test the failing routes"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from unittest.mock import patch, MagicMock

try:
    with patch('diabetes_tracker.modules.database.create_engine') as mock_create_engine:
        # Make the mock raise an exception to simulate database unavailability
        mock_create_engine.side_effect = Exception("Database not available")
        
        from diabetes_tracker.app import app, data_manager
        
        # Check if data_manager is properly initialized
        print(f"DataManager db_available: {data_manager.db_available}")
        
        with app.test_client() as client:
            print("Testing /api/history/testuser...")
            response = client.get("/api/history/testuser")
            print(f"Status code: {response.status_code}")
            print(f"Response data: {response.get_data(as_text=True)}")
            
            print("\nTesting /api/chart-data/testuser...")
            response2 = client.get("/api/chart-data/testuser")
            print(f"Status code: {response2.status_code}")
            print(f"Response data: {response2.get_data(as_text=True)}")
            
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()
