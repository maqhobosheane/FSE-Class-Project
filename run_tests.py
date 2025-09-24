#!/usr/bin/env python3
"""Test runner script"""
import pytest
import sys
import os

def main():
    # Add the current directory to Python path
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    
    # Run pytest with custom arguments
    args = [
        "tests/",
        "-v",  # verbose
        "--tb=short",  # shorter tracebacks
        "-x",  # stop on first failure
    ]
    
    
    try:
        import pytest_cov
        args.extend([
            "--cov=app",
            "--cov-report=term-missing",
            "--cov-report=html:htmlcov"
        ])
    except ImportError:
        print("pytest-cov not installed, running without coverage")
    
    exit_code = pytest.main(args)
    sys.exit(exit_code)

if __name__ == "__main__":
    main()