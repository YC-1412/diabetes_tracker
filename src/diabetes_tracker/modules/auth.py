import os
import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AuthManager:
    """Manages user authentication using PostgreSQL database"""

    def __init__(self, data_manager=None):
        # Use the provided data manager or create a new one
        if data_manager:
            self.data_manager = data_manager
        else:
            from .database import DataManager
            self.data_manager = DataManager()
        
        logger.info("AuthManager initialized successfully")

    def get_db_session(self) -> Session:
        """Get a database session"""
        return self.data_manager.get_db_session()

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> bool:
        """Register a new user"""
        try:
            # Check if user already exists
            if self.user_exists(username):
                return False

            # Import User model from database module
            from .database import User
            
            # Create new user
            new_user = User(
                username=username,
                password_hash=self._hash_password(password),
                created_at=datetime.utcnow()
            )

            with self.get_db_session() as session:
                session.add(new_user)
                session.commit()

            logger.info(f"User registered successfully: {username}")
            return True

        except SQLAlchemyError as e:
            logger.error(f"Database error registering user: {e}")
            return False
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            return False

    def login_user(self, username: str, password: str) -> bool:
        """Authenticate a user"""
        try:
            from .database import User
            
            with self.get_db_session() as session:
                user = session.query(User)\
                    .filter(User.username == username)\
                    .first()

                if not user:
                    return False

                stored_hash = user.password_hash
                input_hash = self._hash_password(password)

                return stored_hash == input_hash

        except SQLAlchemyError as e:
            logger.error(f"Database error during login: {e}")
            return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            return False

    def user_exists(self, username: str) -> bool:
        """Check if a user exists"""
        try:
            from .database import User
            
            with self.get_db_session() as session:
                user = session.query(User)\
                    .filter(User.username == username)\
                    .first()
                
                return user is not None

        except SQLAlchemyError as e:
            logger.error(f"Database error checking user existence: {e}")
            return False
        except Exception as e:
            logger.error(f"Error checking user existence: {e}")
            return False

    def get_user_info(self, username: str) -> Optional[dict]:
        """Get user information"""
        try:
            from .database import User
            
            with self.get_db_session() as session:
                user = session.query(User)\
                    .filter(User.username == username)\
                    .first()

                if not user:
                    return None

                return {
                    "username": user.username,
                    "created_at": user.created_at.isoformat(),
                }

        except SQLAlchemyError as e:
            logger.error(f"Database error getting user info: {e}")
            return None
        except Exception as e:
            logger.error(f"Error getting user info: {e}")
            return None

    def change_password(
        self, username: str, old_password: str, new_password: str
    ) -> bool:
        """Change user password"""
        try:
            # First verify old password
            if not self.login_user(username, old_password):
                return False

            from .database import User
            
            with self.get_db_session() as session:
                user = session.query(User)\
                    .filter(User.username == username)\
                    .first()
                
                if user:
                    user.password_hash = self._hash_password(new_password)
                    session.commit()
                    logger.info(f"Password changed successfully for user: {username}")
                    return True
                else:
                    logger.warning(f"User not found for password change: {username}")
                    return False

        except SQLAlchemyError as e:
            logger.error(f"Database error changing password: {e}")
            return False
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False
