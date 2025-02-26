#!/usr/bin/env python3
"""
Command-line script for video classification.
"""
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.main import main

if __name__ == '__main__':
    main()
