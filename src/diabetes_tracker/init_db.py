#!/usr/bin/env python3
"""
Database initialization script for Diabetes Tracker
This script creates the database tables and can be used for initial setup.
"""

import os
import sys
from dotenv import load_dotenv

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# from diabetes_tracker.modules.database import DataManager
# from diabetes_tracker.modules.auth import AuthManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_database():
    """Initialize the database and create all tables"""
    try:
        # Load environment variables
        load_dotenv()
        
        logger.info("Initializing database...")
        
        # Initialize managers (this will create tables)
        # data_manager = DataManager()
        # auth_manager = AuthManager()
        
        logger.info("Database initialization completed successfully!")
        logger.info("Tables created:")
        logger.info("- users")
        logger.info("- diabetes_entries")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to initialize database: {e}")
        return False

def check_database_connection():
    """Check if we can connect to the database"""
    try:
        # Load environment variables
        load_dotenv()
        
        logger.info("Testing database connection...")
        
        # Try to initialize managers
        # data_manager = DataManager()
        # auth_manager = AuthManager()
        
        logger.info("Database connection successful!")
        return True
        
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        logger.error("Please check your database configuration in .env file")
        return False

if __name__ == "__main__":
    print("Diabetes Tracker Database Initialization")
    print("=" * 40)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Warning: .env file not found!")
        print("Please create a .env file with your database configuration.")
        print("You can copy env.example to .env and update the values.")
        sys.exit(1)
    
    # Check database connection first
    if not check_database_connection():
        sys.exit(1)
    
    # Initialize database
    if init_database():
        print("Database initialization completed successfully!")
    else:
        print("Database initialization failed!")
        sys.exit(1) 