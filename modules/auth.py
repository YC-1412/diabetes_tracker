import pandas as pd
import os
import hashlib
from datetime import datetime
from typing import Optional

class AuthManager:
    """Manages user authentication using CSV file storage"""
    
    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.csv")
        self._ensure_data_directory()
        self._initialize_users_file()
    
    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)
    
    def _initialize_users_file(self):
        """Initialize users CSV file with headers if it doesn't exist"""
        if not os.path.exists(self.users_file):
            users_df = pd.DataFrame(columns=['username', 'password_hash', 'created_at'])
            users_df.to_csv(self.users_file, index=False)
    
    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def register_user(self, username: str, password: str) -> bool:
        """Register a new user"""
        try:
            # Check if user already exists
            if self.user_exists(username):
                return False
            
            # Read existing users
            try:
                df = pd.read_csv(self.users_file)
            except FileNotFoundError:
                df = pd.DataFrame(columns=['username', 'password_hash', 'created_at'])
            
            # Create new user
            new_user = {
                'username': username,
                'password_hash': self._hash_password(password),
                'created_at': datetime.now().isoformat()
            }
            
            # Add user to dataframe
            df = pd.concat([df, pd.DataFrame([new_user])], ignore_index=True)
            df.to_csv(self.users_file, index=False)
            
            return True
            
        except Exception as e:
            print(f"Error registering user: {e}")
            return False
    
    def login_user(self, username: str, password: str) -> bool:
        """Authenticate a user"""
        try:
            if not os.path.exists(self.users_file):
                return False
            
            df = pd.read_csv(self.users_file)
            user_row = df[df['username'] == username]
            
            if user_row.empty:
                return False
            
            stored_hash = user_row.iloc[0]['password_hash']
            input_hash = self._hash_password(password)
            
            return stored_hash == input_hash
            
        except Exception as e:
            print(f"Error during login: {e}")
            return False
    
    def user_exists(self, username: str) -> bool:
        """Check if a user exists"""
        try:
            if not os.path.exists(self.users_file):
                return False
            
            df = pd.read_csv(self.users_file)
            return not df[df['username'] == username].empty
            
        except Exception as e:
            print(f"Error checking user existence: {e}")
            return False
    
    def get_user_info(self, username: str) -> Optional[dict]:
        """Get user information"""
        try:
            if not os.path.exists(self.users_file):
                return None
            
            df = pd.read_csv(self.users_file)
            user_row = df[df['username'] == username]
            
            if user_row.empty:
                return None
            
            user_data = user_row.iloc[0]
            return {
                'username': user_data['username'],
                'created_at': user_data['created_at']
            }
            
        except Exception as e:
            print(f"Error getting user info: {e}")
            return None
    
    def change_password(self, username: str, old_password: str, new_password: str) -> bool:
        """Change user password"""
        try:
            # First verify old password
            if not self.login_user(username, old_password):
                return False
            
            # Read users file
            df = pd.read_csv(self.users_file)
            
            # Update password
            user_mask = df['username'] == username
            df.loc[user_mask, 'password_hash'] = self._hash_password(new_password)
            
            # Save updated data
            df.to_csv(self.users_file, index=False)
            
            return True
            
        except Exception as e:
            print(f"Error changing password: {e}")
            return False 