#!/usr/bin/env python3
"""
CSV to PostgreSQL Migration Script
This script migrates existing CSV data to the PostgreSQL database.
"""

import os
import sys
import pandas as pd
from dotenv import load_dotenv
from datetime import datetime

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from diabetes_tracker.modules.database import DataManager, User, DiabetesEntry
from diabetes_tracker.modules.auth import AuthManager
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_users_csv():
    """Migrate users from CSV to PostgreSQL"""
    try:
        csv_file = "data/users.csv"
        if not os.path.exists(csv_file):
            logger.info("No users.csv file found. Skipping user migration.")
            return True
        
        logger.info("Migrating users from CSV...")
        df = pd.read_csv(csv_file)
        
        auth_manager = AuthManager()
        migrated_count = 0
        
        for _, row in df.iterrows():
            username = row['username']
            password_hash = row['password_hash']
            created_at = datetime.fromisoformat(row['created_at'])
            
            # Check if user already exists
            if not auth_manager.user_exists(username):
                # Create user in database
                from diabetes_tracker.modules.database import User
                with auth_manager.get_db_session() as session:
                    new_user = User(
                        username=username,
                        password_hash=password_hash,
                        created_at=created_at
                    )
                    session.add(new_user)
                    session.commit()
                    migrated_count += 1
                    logger.info(f"Migrated user: {username}")
            else:
                logger.info(f"User already exists, skipping: {username}")
        
        logger.info(f"User migration completed. {migrated_count} users migrated.")
        return True
        
    except Exception as e:
        logger.error(f"Error migrating users: {e}")
        return False

def migrate_entries_csv():
    """Migrate diabetes entries from CSV to PostgreSQL"""
    try:
        csv_file = "data/diabetes_entries.csv"
        if not os.path.exists(csv_file):
            logger.info("No diabetes_entries.csv file found. Skipping entries migration.")
            return True
        
        logger.info("Migrating diabetes entries from CSV...")
        df = pd.read_csv(csv_file)
        
        data_manager = DataManager()
        migrated_count = 0
        
        for _, row in df.iterrows():
            entry_id = row['entry_id']
            username = row['username']
            blood_sugar = row['blood_sugar']
            meal = row['meal']
            exercise = row['exercise']
            date = datetime.fromisoformat(row['date'])
            created_at = datetime.fromisoformat(row['created_at'])
            
            # Check if entry already exists
            with data_manager.get_db_session() as session:
                existing_entry = session.query(DiabetesEntry)\
                    .filter(DiabetesEntry.entry_id == entry_id)\
                    .first()
                
                if not existing_entry:
                    # Create entry in database
                    new_entry = DiabetesEntry(
                        entry_id=entry_id,
                        username=username,
                        blood_sugar=blood_sugar,
                        meal=meal,
                        exercise=exercise,
                        date=date,
                        created_at=created_at
                    )
                    session.add(new_entry)
                    session.commit()
                    migrated_count += 1
                    logger.info(f"Migrated entry: {entry_id}")
                else:
                    logger.info(f"Entry already exists, skipping: {entry_id}")
        
        logger.info(f"Entries migration completed. {migrated_count} entries migrated.")
        return True
        
    except Exception as e:
        logger.error(f"Error migrating entries: {e}")
        return False

def backup_csv_files():
    """Create backup of CSV files before migration"""
    try:
        backup_dir = "data/backup"
        if not os.path.exists(backup_dir):
            os.makedirs(backup_dir)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # Backup users.csv
        if os.path.exists("data/users.csv"):
            backup_file = f"{backup_dir}/users_{timestamp}.csv"
            import shutil
            shutil.copy2("data/users.csv", backup_file)
            logger.info(f"Backed up users.csv to {backup_file}")
        
        # Backup diabetes_entries.csv
        if os.path.exists("data/diabetes_entries.csv"):
            backup_file = f"{backup_dir}/diabetes_entries_{timestamp}.csv"
            import shutil
            shutil.copy2("data/diabetes_entries.csv", backup_file)
            logger.info(f"Backed up diabetes_entries.csv to {backup_file}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error creating backup: {e}")
        return False

def run_migration():
    """Run the complete migration process"""
    try:
        # Load environment variables
        load_dotenv()
        
        logger.info("Starting CSV to PostgreSQL migration...")
        
        # Check database connection
        data_manager = DataManager()
        auth_manager = AuthManager()
        
        # Create backup
        if not backup_csv_files():
            logger.error("Failed to create backup. Aborting migration.")
            return False
        
        # Migrate users
        if not migrate_users_csv():
            logger.error("Failed to migrate users.")
            return False
        
        # Migrate entries
        if not migrate_entries_csv():
            logger.error("Failed to migrate entries.")
            return False
        
        logger.info("Migration completed successfully!")
        return True
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        return False

if __name__ == "__main__":
    print("CSV to PostgreSQL Migration Tool")
    print("=" * 35)
    
    # Check if .env file exists
    if not os.path.exists('.env'):
        print("Error: .env file not found!")
        print("Please create a .env file with your database configuration.")
        sys.exit(1)
    
    # Check if data directory exists
    if not os.path.exists('data'):
        print("No data directory found. Nothing to migrate.")
        sys.exit(0)
    
    # Run migration
    if run_migration():
        print("Migration completed successfully!")
        print("Your CSV data has been migrated to PostgreSQL.")
        print("Original CSV files have been backed up in data/backup/")
    else:
        print("Migration failed!")
        sys.exit(1) 