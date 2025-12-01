import hashlib
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError, IntegrityError
from sqlalchemy import func
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

    def _normalize_username(self, username: str) -> str:
        """Normalize username to lowercase for case-insensitive comparison"""
        return username.lower().strip() if username else ""

    def _hash_password(self, password: str) -> str:
        """Hash a password using SHA-256"""
        return hashlib.sha256(password.encode()).hexdigest()

    def register_user(self, username: str, password: str) -> bool:
        """Register a new user"""
        if not username or not password:
            logger.error("Username and password are required")
            return False
            
        # Normalize username
        normalized_username = self._normalize_username(username)
        logger.info(f"Attempting to register user: '{username}' (normalized: '{normalized_username}')")
        
        try:
            # Check if user already exists (case-insensitive)
            try:
                if self.user_exists(username):
                    logger.warning(f"User already exists (case-insensitive match): '{username}'")
                    return False
            except (SQLAlchemyError, Exception) as e:
                # If we can't check, log but continue - the unique constraint will catch duplicates
                logger.warning(f"Could not verify user existence, proceeding with registration: {e}")

            # Import User model from database module
            from .database import User
            from sqlalchemy import text
            
            # Check if normalized username already exists as exact match (in case of case conflicts)
            session = self.get_db_session()
            try:
                with session:
                    try:
                        existing = session.query(User).filter(User.username == normalized_username).first()
                        if existing:
                            logger.warning(f"User with normalized username already exists: '{normalized_username}'")
                            return False
                    except Exception as e:
                        if 'preferred_units' in str(e).lower():
                            # Column doesn't exist, rollback and use raw SQL
                            session.rollback()
                            result = session.execute(
                                text("SELECT username FROM users WHERE username = :username"),
                                {"username": normalized_username}
                            )
                            if result.fetchone():
                                logger.warning(f"User with normalized username already exists: '{normalized_username}'")
                                return False
                        else:
                            raise
                    
                    # Create new user with normalized username
                    # Use raw SQL if preferred_units column doesn't exist
                    password_hash = self._hash_password(password)
                    created_at = datetime.utcnow()
                    
                    try:
                        new_user = User(
                            username=normalized_username,
                            password_hash=password_hash,
                            created_at=created_at
                        )
                        session.add(new_user)
                        session.commit()
                    except Exception as e:
                        if 'preferred_units' in str(e).lower():
                            # Column doesn't exist, rollback and use raw SQL
                            session.rollback()
                            session.execute(
                                text("""
                                    INSERT INTO users (username, password_hash, created_at) 
                                    VALUES (:username, :password_hash, :created_at)
                                """),
                                {
                                    "username": normalized_username,
                                    "password_hash": password_hash,
                                    "created_at": created_at
                                }
                            )
                            session.commit()
                        else:
                            raise
                    
                    logger.info(f"User registered successfully: '{normalized_username}'")
                    return True
            finally:
                session.close()

        except IntegrityError as e:
            # This handles unique constraint violations (user already exists)
            error_msg = str(e).lower()
            if 'unique' in error_msg or 'duplicate' in error_msg or 'violates unique constraint' in error_msg:
                logger.warning(f"User already exists (integrity constraint): '{normalized_username}' - {e}")
            else:
                logger.error(f"Integrity error during registration: {e}")
            return False
        except SQLAlchemyError as e:
            logger.error(f"Database error registering user: {e}")
            return False
        except Exception as e:
            logger.error(f"Error registering user: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def login_user(self, username: str, password: str) -> bool:
        """Authenticate a user"""
        if not username or not password:
            logger.warning("Login attempted with empty username or password")
            return False
            
        # Normalize username for case-insensitive lookup
        normalized_username = self._normalize_username(username)
        logger.info(f"Attempting login for username: '{username}' (normalized: '{normalized_username}')")
        
        try:
            from .database import User
            from sqlalchemy import text
            
            session = self.get_db_session()
            try:
                with session:
                    # Try to query with ORM first, but fall back to raw SQL if preferred_units column doesn't exist
                    user = None
                    stored_hash = None
                    
                    try:
                        all_users = session.query(User).all()
                        # Get all users and find matching one case-insensitively
                        for u in all_users:
                            user_normalized = self._normalize_username(u.username)
                            if user_normalized == normalized_username:
                                user = u
                                stored_hash = u.password_hash
                                break
                    except Exception as e:
                        if 'preferred_units' in str(e).lower():
                            # Column doesn't exist, rollback and use raw SQL
                            session.rollback()
                            logger.debug("preferred_units column not found, using raw SQL query")
                            result = session.execute(
                                text("SELECT username, password_hash FROM users")
                            )
                            for row in result.fetchall():
                                db_username = row[0]
                                user_normalized = self._normalize_username(db_username)
                                if user_normalized == normalized_username:
                                    stored_hash = row[1]
                                    # Create a simple object for the user
                                    class SimpleUser:
                                        def __init__(self, username):
                                            self.username = username
                                    user = SimpleUser(db_username)
                                    break
                        else:
                            raise

                    if not user or not stored_hash:
                        logger.warning(f"User not found: '{username}' (normalized: '{normalized_username}')")
                        return False

                    logger.debug(f"Found user in database: '{user.username}'")
                    input_hash = self._hash_password(password)
                    
                    logger.debug(f"Password hash comparison - stored: {stored_hash[:10]}..., input: {input_hash[:10]}...")

                    if stored_hash == input_hash:
                        logger.info(f"Login successful for user: '{user.username}'")
                        return True
                    else:
                        logger.warning(f"Invalid password for user: '{user.username}'")
                        logger.debug(f"Full stored hash: {stored_hash}")
                        logger.debug(f"Full input hash: {input_hash}")
                        return False
            finally:
                session.close()

        except SQLAlchemyError as e:
            logger.error(f"Database error during login: {e}")
            return False
        except Exception as e:
            logger.error(f"Error during login: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

    def user_exists(self, username: str) -> bool:
        """Check if a user exists (case-insensitive)"""
        if not username:
            return False
            
        # Normalize username for comparison
        normalized_username = self._normalize_username(username)
        logger.debug(f"Checking if user exists: '{username}' (normalized: '{normalized_username}')")
        
        try:
            from .database import User
            from sqlalchemy import text
            
            session = self.get_db_session()
            try:
                with session:
                    # Try to query with ORM first, but fall back to raw SQL if preferred_units column doesn't exist
                    try:
                        all_users = session.query(User).all()
                        # Get all users and check case-insensitively in Python
                        for user in all_users:
                            user_normalized = self._normalize_username(user.username)
                            if user_normalized == normalized_username:
                                logger.debug(f"User exists: '{user.username}' (matched case-insensitively for '{username}')")
                                return True
                        logger.debug(f"User does not exist: '{username}'")
                        return False
                    except Exception as e:
                        if 'preferred_units' in str(e).lower():
                            # Column doesn't exist, rollback and use raw SQL
                            session.rollback()
                            logger.debug("preferred_units column not found, using raw SQL query")
                            result = session.execute(text("SELECT username FROM users"))
                            usernames = [row[0] for row in result.fetchall()]
                            for db_username in usernames:
                                user_normalized = self._normalize_username(db_username)
                                if user_normalized == normalized_username:
                                    logger.debug(f"User exists: '{db_username}' (matched case-insensitively for '{username}')")
                                    return True
                            logger.debug(f"User does not exist: '{username}'")
                            return False
                        else:
                            raise
            finally:
                session.close()

        except SQLAlchemyError as e:
            # Log the error but don't silently fail - this could mask real issues
            logger.error(f"Database error checking user existence for '{username}': {e}")
            # Re-raise to let the caller handle it appropriately
            raise
        except Exception as e:
            logger.error(f"Error checking user existence for '{username}': {e}")
            raise

    def get_user_info(self, username: str) -> Optional[dict]:
        """Get user information"""
        if not username:
            return None
            
        # Normalize username
        normalized_username = self._normalize_username(username)
        
        try:
            from .database import User
            
            with self.get_db_session() as session:
                # Use case-insensitive comparison
                user = session.query(User)\
                    .filter(func.lower(User.username) == normalized_username)\
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
        if not username or not old_password or not new_password:
            return False
            
        # Normalize username
        normalized_username = self._normalize_username(username)
        
        try:
            # First verify old password
            if not self.login_user(normalized_username, old_password):
                return False

            from .database import User
            
            with self.get_db_session() as session:
                # Use case-insensitive comparison
                user = session.query(User)\
                    .filter(func.lower(User.username) == normalized_username)\
                    .first()
                
                if user:
                    user.password_hash = self._hash_password(new_password)
                    session.commit()
                    logger.info(f"Password changed successfully for user: {normalized_username}")
                    return True
                else:
                    logger.warning(f"User not found for password change: {normalized_username}")
                    return False

        except SQLAlchemyError as e:
            logger.error(f"Database error changing password: {e}")
            return False
        except Exception as e:
            logger.error(f"Error changing password: {e}")
            return False
