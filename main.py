#!/usr/bin/env python3
"""
Main entry point for the Diabetes Tracker application.

This script imports the Flask app from the src package and runs it.
"""

from src.diabetes_tracker.app import app

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5001) 