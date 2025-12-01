#!/usr/bin/env python3
"""
Main entry point for the Diabetes Tracker application.

This script imports the Flask app from the src package and runs it.
"""

import sys
import logging

# Configure logging to see what's happening
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

try:
    logger.info("Importing Flask app...")
    from src.diabetes_tracker.app import app
    logger.info("Flask app imported successfully")
except Exception as e:
    logger.error(f"Failed to import Flask app: {e}", exc_info=True)
    sys.exit(1)

if __name__ == "__main__":
    try:
        app.run(debug=True, host="0.0.0.0", port=5001)
    except KeyboardInterrupt:
        logger.info("Server stopped by user")
    except Exception as e:
        logger.error(f"Error running Flask app: {e}", exc_info=True)
        sys.exit(1) 