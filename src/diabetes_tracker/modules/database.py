import os
import uuid
from datetime import datetime, timedelta
from sqlalchemy import create_engine, Column, String, Float, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

Base = declarative_base()


class User(Base):
    """User model for PostgreSQL database"""
    __tablename__ = 'users'
    
    username = Column(String(50), primary_key=True)
    password_hash = Column(String(255), nullable=False)
    preferred_units = Column(String(10), default='mg/dL')  # 'mg/dL' or 'mmol/L'
    created_at = Column(DateTime, default=datetime.utcnow)


class DiabetesEntry(Base):
    """Diabetes entry model for PostgreSQL database"""
    __tablename__ = 'diabetes_entries'
    
    entry_id = Column(String(36), primary_key=True)
    username = Column(String(50), nullable=False)
    blood_sugar = Column(Float, nullable=False)
    meal = Column(Text, nullable=False)
    exercise = Column(Text, nullable=False)
    date = Column(DateTime, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class DataManager:
    """Manages data storage and retrieval using PostgreSQL database"""

    def __init__(self):
        # Get database connection details from environment variables
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'diabetes_tracker')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', '')
        
        # Create database URL
        self.database_url = f"postgresql://{self.db_user}:{self.db_password}@{self.db_host}:{self.db_port}/{self.db_name}"
        
        # Initialize database connection
        self.engine = None
        self.SessionLocal = None
        self.db_available = False
        
        # Fallback storage for when database is not available
        self._fallback_user_units = {}
        
        self._initialize_database()

    def _initialize_database(self):
        """Initialize database connection and create tables"""
        try:
            self.engine = create_engine(self.database_url, echo=False)
            self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
            
            # Create tables
            Base.metadata.create_all(bind=self.engine)
            self.db_available = True
            logger.info("Database initialized successfully")
            
        except Exception as e:
            logger.warning(f"Failed to initialize database: {e}")
            logger.info("Falling back to in-memory storage for user preferences")
            self.db_available = False

    def get_db_session(self):
        """Get a database session context manager"""
        if not self.db_available:
            # Return a context manager that raises SQLAlchemyError when used
            class MockSession:
                def __enter__(self):
                    raise SQLAlchemyError("Database not available")
                def __exit__(self, exc_type, exc_val, exc_tb):
                    pass
            return MockSession()
        return self.SessionLocal()

    def get_user_preferred_units(self, username: str) -> str:
        """Get user's preferred units"""
        # Check fallback storage first (most reliable)
        if username in self._fallback_user_units:
            return self._fallback_user_units[username]
        
        # Try to get from database if available
        if self.db_available:
            try:
                with self.get_db_session() as session:
                    user = session.query(User).filter(User.username == username).first()
                    if user and user.preferred_units:
                        # Cache in fallback storage for future use
                        self._fallback_user_units[username] = user.preferred_units
                        return user.preferred_units
            except Exception as e:
                logger.warning(f"Could not get units from database for {username}: {e}")
        
        # Default fallback
        return 'mg/dL'

    def update_user_preferred_units(self, username: str, units: str) -> bool:
        """Update user's preferred units"""
        # Always use fallback storage for unit preferences
        # This ensures unit switching works regardless of database status
        self._fallback_user_units[username] = units
        logger.info(f"Updated preferred units for {username} in fallback storage: {units}")
        
        # Try to sync with database if available, but don't fail if it's not
        if self.db_available:
            try:
                with self.get_db_session() as session:
                    user = session.query(User).filter(User.username == username).first()
                    if user:
                        user.preferred_units = units
                        session.commit()
                        logger.info(f"Synced preferred units for {username} to database: {units}")
                    else:
                        logger.info(f"User {username} not found in database, using fallback storage only")
            except Exception as e:
                logger.warning(f"Could not sync units to database for {username}: {e}")
                # Don't fail - we have fallback storage
        
        return True

    def save_entry(
        self, username: str, blood_sugar: float, meal: str, exercise: str, date: str
    ) -> str:
        """Save a new diabetes entry"""
        entry_id = str(uuid.uuid4())
        
        try:
            # Parse date string to datetime
            entry_date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            
            new_entry = DiabetesEntry(
                entry_id=entry_id,
                username=username,
                blood_sugar=blood_sugar,
                meal=meal,
                exercise=exercise,
                date=entry_date,
                created_at=datetime.utcnow()
            )
            
            with self.get_db_session() as session:
                session.add(new_entry)
                session.commit()
                
            logger.info(f"Entry saved successfully: {entry_id}")
            return entry_id
            
        except SQLAlchemyError as e:
            logger.error(f"Database error saving entry: {e}")
            raise
        except Exception as e:
            logger.error(f"Error saving entry: {e}")
            raise

    def get_user_history(self, username: str) -> list[dict]:
        """Get all entries for a specific user"""
        try:
            with self.get_db_session() as session:
                entries = session.query(DiabetesEntry)\
                    .filter(DiabetesEntry.username == username)\
                    .order_by(DiabetesEntry.date.desc())\
                    .all()
                
                return [
                    {
                        "entry_id": entry.entry_id,
                        "username": entry.username,
                        "blood_sugar": entry.blood_sugar,
                        "meal": entry.meal,
                        "exercise": entry.exercise,
                        "date": entry.date.isoformat(),
                        "created_at": entry.created_at.isoformat()
                    }
                    for entry in entries
                ]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user history: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting user history: {e}")
            return []

    def get_recent_entries(self, username: str, limit: int = 5) -> list[dict]:
        """Get recent entries for a user"""
        try:
            with self.get_db_session() as session:
                entries = session.query(DiabetesEntry)\
                    .filter(DiabetesEntry.username == username)\
                    .order_by(DiabetesEntry.date.desc())\
                    .limit(limit)\
                    .all()
                
                return [
                    {
                        "entry_id": entry.entry_id,
                        "username": entry.username,
                        "blood_sugar": entry.blood_sugar,
                        "meal": entry.meal,
                        "exercise": entry.exercise,
                        "date": entry.date.isoformat(),
                        "created_at": entry.created_at.isoformat()
                    }
                    for entry in entries
                ]
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting recent entries: {e}")
            return []
        except Exception as e:
            logger.error(f"Error getting recent entries: {e}")
            return []

    def get_user_stats(self, username: str) -> dict:
        """Get statistics for a user"""
        try:
            with self.get_db_session() as session:
                # Get total entries
                total_entries = session.query(DiabetesEntry)\
                    .filter(DiabetesEntry.username == username)\
                    .count()
                
                if total_entries == 0:
                    return {"total_entries": 0, "avg_blood_sugar": 0, "entries_this_week": 0}
                
                # Get average blood sugar
                avg_blood_sugar = session.query(DiabetesEntry.blood_sugar)\
                    .filter(DiabetesEntry.username == username)\
                    .all()
                avg_blood_sugar = sum([entry[0] for entry in avg_blood_sugar]) / len(avg_blood_sugar)
                
                # Get entries this week
                week_ago = datetime.utcnow() - timedelta(days=7)
                entries_this_week = session.query(DiabetesEntry)\
                    .filter(DiabetesEntry.username == username)\
                    .filter(DiabetesEntry.date >= week_ago)\
                    .count()
                
                return {
                    "total_entries": total_entries,
                    "avg_blood_sugar": round(avg_blood_sugar, 1),
                    "entries_this_week": entries_this_week,
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting user stats: {e}")
            return {"total_entries": 0, "avg_blood_sugar": 0, "entries_this_week": 0}
        except Exception as e:
            logger.error(f"Error getting user stats: {e}")
            return {"total_entries": 0, "avg_blood_sugar": 0, "entries_this_week": 0}

    def get_chart_data(self, username: str) -> dict:
        """Get blood sugar data formatted for charting"""
        try:
            with self.get_db_session() as session:
                entries = session.query(DiabetesEntry)\
                    .filter(DiabetesEntry.username == username)\
                    .order_by(DiabetesEntry.date.asc())\
                    .all()
                
                if not entries:
                    return {"labels": [], "data": [], "dates": []}
                
                # Format data for charting
                labels = [entry.date.strftime("%m/%d") for entry in entries]
                data = [entry.blood_sugar for entry in entries]
                dates = [entry.date.strftime("%Y-%m-%d") for entry in entries]
                
                return {
                    "labels": labels,
                    "data": data,
                    "dates": dates
                }
                
        except SQLAlchemyError as e:
            logger.error(f"Database error getting chart data: {e}")
            return {"labels": [], "data": [], "dates": []}
        except Exception as e:
            logger.error(f"Error getting chart data: {e}")
            return {"labels": [], "data": [], "dates": []}

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a specific entry"""
        try:
            with self.get_db_session() as session:
                entry = session.query(DiabetesEntry)\
                    .filter(DiabetesEntry.entry_id == entry_id)\
                    .first()
                
                if entry:
                    session.delete(entry)
                    session.commit()
                    logger.info(f"Entry deleted successfully: {entry_id}")
                    return True
                else:
                    logger.warning(f"Entry not found for deletion: {entry_id}")
                    return False
                    
        except SQLAlchemyError as e:
            logger.error(f"Database error deleting entry: {e}")
            return False
        except Exception as e:
            logger.error(f"Error deleting entry: {e}")
            return False
