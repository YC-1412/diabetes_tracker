#!/usr/bin/env python3
"""
Test runner script for Diabetes Tracker
Provides an easy way to run different types of tests
"""

import sys
import subprocess
import argparse
import os


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=False)
        print(f"\n{description} completed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n{description} failed with exit code {e.returncode}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Run Diabetes Tracker tests")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "app", "chart", "coverage", "fast"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Verbose output"
    )
    parser.add_argument(
        "--watch",
        action="store_true",
        help="Run tests in watch mode"
    )
    parser.add_argument(
        "--html",
        action="store_true",
        help="Generate HTML report"
    )
    
    args = parser.parse_args()
    
    # Ensure we're in the project root
    if not os.path.exists("main.py"):
        print("Error: Please run this script from the project root directory")
        sys.exit(1)
    
    # Build pytest command
    pytest_cmd = "python -m pytest"
    
    if args.verbose:
        pytest_cmd += " -v"
    
    # Add coverage if requested
    if args.type == "coverage":
        pytest_cmd += " --cov=src/diabetes_tracker --cov-report=html --cov-report=term-missing --cov-fail-under=80"
    
    # Add HTML report if requested
    if args.html:
        pytest_cmd += " --html=reports/test_report.html --self-contained-html"
    
    # Determine test path based on type
    if args.type == "all":
        test_path = "tests/"
    elif args.type == "unit":
        test_path = "tests/ -m 'not integration'"
    elif args.type == "integration":
        test_path = "tests/ -m 'integration'"
    elif args.type == "app":
        test_path = "tests/test_app.py"
    elif args.type == "chart":
        test_path = "tests/test_chart.py"
    elif args.type == "fast":
        pytest_cmd += " -x --tb=short"
        test_path = "tests/"
    else:
        test_path = "tests/"
    
    pytest_cmd += f" {test_path}"
    
    # Run in watch mode if requested
    if args.watch:
        watch_cmd = f"ptw {test_path} -- -v"
        print(f"\nStarting test watch mode...")
        print(f"Command: {watch_cmd}")
        print(f"Press Ctrl+C to stop")
        try:
            subprocess.run(watch_cmd, shell=True)
        except KeyboardInterrupt:
            print("\nTest watch mode stopped")
        return
    
    # Run the tests
    success = run_command(pytest_cmd, f"Running {args.type} tests")
    
    if success:
        print(f"\nAll {args.type} tests passed!")
        sys.exit(0)
    else:
        print(f"\nSome {args.type} tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    main() 