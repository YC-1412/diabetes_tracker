#!/usr/bin/env python3
"""
Simple database connection test script
"""

import os
import sys
from dotenv import load_dotenv

# Add src to path
sys.path.append('src')

def test_connection():
    """Test database connection"""
    try:
        # Load environment variables
        load_dotenv()
        
        print("Testing database connection...")
        print(f"Host: {os.getenv('DB_HOST', 'localhost')}")
        print(f"Port: {os.getenv('DB_PORT', '5432')}")
        print(f"Database: {os.getenv('DB_NAME', 'diabetes_tracker')}")
        print(f"User: {os.getenv('DB_USER', 'postgres')}")
        
        # Try to import and initialize modules
        from diabetes_tracker.modules.database import DataManager
        from diabetes_tracker.modules.auth import AuthManager
        
        print("\nInitializing DataManager...")
        data_manager = DataManager()
        print("DataManager initialized successfully")
        
        print("\nInitializing AuthManager...")
        auth_manager = AuthManager()
        print("AuthManager initialized successfully")
        
        print("\nDatabase connection successful!")
        return True
        
    except Exception as e:
        print(f"\nDatabase connection failed: {e}")
        print("\nPlease check:")
        print("1. Your .env file exists and has correct database credentials")
        print("2. PostgreSQL is running and accessible")
        print("3. Database exists and user has proper permissions")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1) 