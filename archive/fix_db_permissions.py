#!/usr/bin/env python3
"""
Script to fix database permissions for the diabetes tracker application.
This script grants the necessary permissions to the diabetes_app_user.
"""

import os
import psycopg2
from dotenv import load_dotenv

def fix_database_permissions():
    """Fix database permissions for diabetes_app_user"""
    
    # Load environment variables
    load_dotenv()
    
    # Get database connection details
    db_host = os.getenv('DB_HOST')
    db_port = os.getenv('DB_PORT', '5432')
    db_name = os.getenv('DB_NAME')
    db_user = os.getenv('DB_USER')
    db_password = os.getenv('DB_PASSWORD')
    
    print(f"Connecting to database: {db_host}:{db_port}/{db_name}")
    print(f"User: {db_user}")
    
    try:
        # Connect to the database
        conn = psycopg2.connect(
            host=db_host,
            port=db_port,
            database=db_name,
            user=db_user,
            password=db_password
        )
        
        cursor = conn.cursor()
        
        # Grant permissions on users table
        print("Granting permissions on users table...")
        cursor.execute("""
            GRANT SELECT, INSERT, UPDATE, DELETE ON users TO diabetes_app_user;
        """)
        
        # Grant permissions on diabetes_entries table
        print("Granting permissions on diabetes_entries table...")
        cursor.execute("""
            GRANT SELECT, INSERT, UPDATE, DELETE ON diabetes_entries TO diabetes_app_user;
        """)
        
        # Grant usage on sequences if they exist
        print("Granting permissions on sequences...")
        cursor.execute("""
            GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO diabetes_app_user;
        """)
        
        # Commit the changes
        conn.commit()
        
        print("✅ Database permissions fixed successfully!")
        
        # Test the permissions
        print("Testing permissions...")
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"Users table accessible. Current user count: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM diabetes_entries;")
        entry_count = cursor.fetchone()[0]
        print(f"Diabetes entries table accessible. Current entry count: {entry_count}")
        
    except psycopg2.Error as e:
        print(f"❌ Database error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()
    
    return True

if __name__ == "__main__":
    print("Database Permissions Fix Script")
    print("=" * 40)
    
    if fix_database_permissions():
        print("\n🎉 All permissions have been fixed!")
        print("You should now be able to register and login users.")
    else:
        print("\n❌ Failed to fix permissions.")
        print("Please check your database configuration and try again.") 