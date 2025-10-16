#!/usr/bin/env python3
"""
Script to recreate database tables with correct ownership and permissions.
This script will drop existing tables and recreate them with proper permissions.
"""

import os
import psycopg2
from dotenv import load_dotenv

def recreate_tables():
    """Recreate database tables with correct permissions"""
    
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
        
        # Drop existing tables if they exist
        print("Dropping existing tables...")
        cursor.execute("DROP TABLE IF EXISTS diabetes_entries CASCADE;")
        cursor.execute("DROP TABLE IF EXISTS users CASCADE;")
        
        # Create users table
        print("Creating users table...")
        cursor.execute("""
            CREATE TABLE users (
                username VARCHAR(50) PRIMARY KEY,
                password_hash VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)
        
        # Create diabetes_entries table
        print("Creating diabetes_entries table...")
        cursor.execute("""
            CREATE TABLE diabetes_entries (
                entry_id VARCHAR(36) PRIMARY KEY,
                username VARCHAR(50) NOT NULL,
                blood_sugar FLOAT NOT NULL,
                meal TEXT NOT NULL,
                exercise TEXT NOT NULL,
                date TIMESTAMP NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
            );
        """)
        
        # Grant all permissions to the current user
        print("Granting permissions...")
        cursor.execute("GRANT ALL PRIVILEGES ON users TO diabetes_app_user;")
        cursor.execute("GRANT ALL PRIVILEGES ON diabetes_entries TO diabetes_app_user;")
        cursor.execute("GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO diabetes_app_user;")
        
        # Commit the changes
        conn.commit()
        
        print("✅ Tables recreated successfully!")
        
        # Test the permissions
        print("Testing table access...")
        cursor.execute("SELECT COUNT(*) FROM users;")
        user_count = cursor.fetchone()[0]
        print(f"Users table accessible. Current user count: {user_count}")
        
        cursor.execute("SELECT COUNT(*) FROM diabetes_entries;")
        entry_count = cursor.fetchone()[0]
        print(f"Diabetes entries table accessible. Current entry count: {entry_count}")
        
        # Test inserting a user
        print("Testing user insertion...")
        cursor.execute("""
            INSERT INTO users (username, password_hash) 
            VALUES ('testuser', 'testhash') 
            ON CONFLICT (username) DO NOTHING;
        """)
        conn.commit()
        print("✅ User insertion test successful!")
        
        # Clean up test user
        cursor.execute("DELETE FROM users WHERE username = 'testuser';")
        conn.commit()
        print("✅ Test user cleaned up!")
        
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
    print("Database Tables Recreation Script")
    print("=" * 40)
    
    if recreate_tables():
        print("\n🎉 Tables have been recreated successfully!")
        print("You should now be able to register and login users.")
    else:
        print("\n❌ Failed to recreate tables.")
        print("Please check your database configuration and try again.") 