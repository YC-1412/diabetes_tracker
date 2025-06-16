import pandas as pd
import os
import uuid
from datetime import datetime
from typing import List, Dict, Optional


class DataManager:
    """Manages data storage and retrieval using CSV files"""

    def __init__(self):
        self.data_dir = "data"
        self.users_file = os.path.join(self.data_dir, "users.csv")
        self.entries_file = os.path.join(self.data_dir, "diabetes_entries.csv")
        self._ensure_data_directory()
        self._initialize_files()

    def _ensure_data_directory(self):
        """Create data directory if it doesn't exist"""
        if not os.path.exists(self.data_dir):
            os.makedirs(self.data_dir)

    def _initialize_files(self):
        """Initialize CSV files with headers if they don't exist"""
        # Initialize users file
        if not os.path.exists(self.users_file):
            users_df = pd.DataFrame(columns=["username", "password_hash", "created_at"])
            users_df.to_csv(self.users_file, index=False)

        # Initialize entries file
        if not os.path.exists(self.entries_file):
            entries_df = pd.DataFrame(
                columns=[
                    "entry_id",
                    "username",
                    "blood_sugar",
                    "meal",
                    "exercise",
                    "date",
                    "created_at",
                ]
            )
            entries_df.to_csv(self.entries_file, index=False)

    def save_entry(
        self, username: str, blood_sugar: float, meal: str, exercise: str, date: str
    ) -> str:
        """Save a new diabetes entry"""
        entry_id = str(uuid.uuid4())
        created_at = datetime.now().isoformat()

        new_entry = {
            "entry_id": entry_id,
            "username": username,
            "blood_sugar": blood_sugar,
            "meal": meal,
            "exercise": exercise,
            "date": date,
            "created_at": created_at,
        }

        # Read existing data
        try:
            df = pd.read_csv(self.entries_file)
        except FileNotFoundError:
            df = pd.DataFrame(
                columns=[
                    "entry_id",
                    "username",
                    "blood_sugar",
                    "meal",
                    "exercise",
                    "date",
                    "created_at",
                ]
            )

        # Add new entry
        df = pd.concat([df, pd.DataFrame([new_entry])], ignore_index=True)
        df.to_csv(self.entries_file, index=False)

        return entry_id

    def get_user_history(self, username: str) -> List[Dict]:
        """Get all entries for a specific user"""
        try:
            df = pd.read_csv(self.entries_file)
            user_entries = df[df["username"] == username].copy()

            # Sort by date (most recent first)
            user_entries["date"] = pd.to_datetime(user_entries["date"])
            user_entries = user_entries.sort_values("date", ascending=False)

            return user_entries.to_dict("records")
        except FileNotFoundError:
            return []

    def get_recent_entries(self, username: str, limit: int = 5) -> List[Dict]:
        """Get recent entries for a user"""
        history = self.get_user_history(username)
        return history[:limit]

    def get_user_stats(self, username: str) -> Dict:
        """Get statistics for a user"""
        history = self.get_user_history(username)

        if not history:
            return {"total_entries": 0, "avg_blood_sugar": 0, "entries_this_week": 0}

        df = pd.DataFrame(history)
        df["date"] = pd.to_datetime(df["date"])

        # Calculate statistics
        total_entries = len(df)
        avg_blood_sugar = df["blood_sugar"].mean()

        # Entries this week
        week_ago = datetime.now() - pd.Timedelta(days=7)
        entries_this_week = len(df[df["date"] >= week_ago])

        return {
            "total_entries": total_entries,
            "avg_blood_sugar": round(avg_blood_sugar, 1),
            "entries_this_week": entries_this_week,
        }

    def delete_entry(self, entry_id: str) -> bool:
        """Delete a specific entry"""
        try:
            df = pd.read_csv(self.entries_file)
            original_length = len(df)

            df = df[df["entry_id"] != entry_id]

            if len(df) < original_length:
                df.to_csv(self.entries_file, index=False)
                return True
            return False
        except FileNotFoundError:
            return False
