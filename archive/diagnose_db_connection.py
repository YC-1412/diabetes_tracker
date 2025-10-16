#!/usr/bin/env python3
"""
Database Connection Diagnostic Script
This script helps diagnose PostgreSQL connection issues on AWS EC2
"""

import os
import sys
import socket
import subprocess
from dotenv import load_dotenv

def check_env_file():
    """Check if .env file exists and has required variables"""
    print("🔍 Checking .env file...")
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   Please create it by copying env.example:")
        print("   cp env.example .env")
        return False
    
    load_dotenv()
    
    required_vars = ['DB_HOST', 'DB_PORT', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    missing_vars = []
    
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            missing_vars.append(var)
        else:
            print(f"   ✓ {var}: {value if var != 'DB_PASSWORD' else '***'}")
    
    if missing_vars:
        print(f"   ❌ Missing variables: {', '.join(missing_vars)}")
        return False
    
    return True

def check_network_connectivity(host, port):
    """Check if we can reach the database host and port"""
    print(f"\n🌐 Checking network connectivity to {host}:{port}...")
    
    try:
        # Try to connect to the host and port
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(10)  # 10 second timeout
        result = sock.connect_ex((host, int(port)))
        sock.close()
        
        if result == 0:
            print(f"   ✓ Network connection successful")
            return True
        else:
            print(f"   ❌ Network connection failed (error code: {result})")
            return False
            
    except Exception as e:
        print(f"   ❌ Network connection error: {e}")
        return False

def check_psycopg2_connection():
    """Try to connect using psycopg2"""
    print("\n🐘 Testing psycopg2 connection...")
    
    try:
        import psycopg2
        from psycopg2 import OperationalError
        
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        dbname = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        
        conn_string = f"host={host} port={port} dbname={dbname} user={user} password={password}"
        
        print(f"   Connecting to: {host}:{port}/{dbname}")
        
        conn = psycopg2.connect(conn_string)
        conn.close()
        
        print("   ✓ psycopg2 connection successful!")
        return True
        
    except ImportError:
        print("   ❌ psycopg2 not installed. Run: pip install psycopg2-binary")
        return False
    except OperationalError as e:
        print(f"   ❌ psycopg2 connection failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def check_sqlalchemy_connection():
    """Try to connect using SQLAlchemy"""
    print("\n🔧 Testing SQLAlchemy connection...")
    
    try:
        from sqlalchemy import create_engine, text
        from sqlalchemy.exc import OperationalError
        
        host = os.getenv('DB_HOST')
        port = os.getenv('DB_PORT')
        dbname = os.getenv('DB_NAME')
        user = os.getenv('DB_USER')
        password = os.getenv('DB_PASSWORD')
        
        database_url = f"postgresql://{user}:{password}@{host}:{port}/{dbname}"
        
        engine = create_engine(database_url, echo=False)
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        
        print("   ✓ SQLAlchemy connection successful!")
        return True
        
    except ImportError as e:
        print(f"   ❌ SQLAlchemy import error: {e}")
        return False
    except OperationalError as e:
        print(f"   ❌ SQLAlchemy connection failed: {e}")
        return False
    except Exception as e:
        print(f"   ❌ Unexpected error: {e}")
        return False

def run_quick_tests():
    """Run quick connectivity tests"""
    print("\n⚡ Running quick connectivity tests...")
    
    host = os.getenv('DB_HOST')
    port = os.getenv('DB_PORT')
    
    # Test 1: ping
    try:
        result = subprocess.run(['ping', '-c', '1', host], 
                              capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print(f"   ✓ Ping to {host} successful")
        else:
            print(f"   ❌ Ping to {host} failed")
    except Exception as e:
        print(f"   ⚠️  Ping test failed: {e}")
    
    # Test 2: telnet (if available)
    try:
        result = subprocess.run(['telnet', host, port], 
                              capture_output=True, text=True, timeout=10)
        if "Connected" in result.stdout or result.returncode == 0:
            print(f"   ✓ Telnet to {host}:{port} successful")
        else:
            print(f"   ❌ Telnet to {host}:{port} failed")
    except FileNotFoundError:
        print(f"   ⚠️  Telnet not available, skipping test")
    except Exception as e:
        print(f"   ⚠️  Telnet test failed: {e}")

def main():
    """Main diagnostic function"""
    print("🔍 PostgreSQL Connection Diagnostic Tool")
    print("=" * 45)
    
    # Step 1: Check environment file
    if not check_env_file():
        print("\n❌ Please fix .env file issues first")
        return False
    
    host = os.getenv('DB_HOST')
    port = int(os.getenv('DB_PORT', 5432))
    
    # Step 2: Check network connectivity
    if not check_network_connectivity(host, port):
        print("\n🔧 Network connectivity issues detected!")
        print("   Possible solutions:")
        print("   1. Check AWS Security Group allows port 5432")
        print("   2. Check if PostgreSQL is running on EC2")
        print("   3. Check if PostgreSQL is configured for remote connections")
        print("   4. Check firewall settings on EC2")
        return False
    
    # Step 3: Run quick tests
    run_quick_tests()
    
    # Step 4: Test psycopg2 connection
    if not check_psycopg2_connection():
        print("\n🔧 psycopg2 connection issues detected!")
        return False
    
    # Step 5: Test SQLAlchemy connection
    if not check_sqlalchemy_connection():
        print("\n🔧 SQLAlchemy connection issues detected!")
        return False
    
    print("\n🎉 All connection tests passed!")
    print("   Your database connection should be working now.")
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 