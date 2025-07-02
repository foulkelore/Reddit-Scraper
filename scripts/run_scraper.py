#!/usr/bin/env python3
"""
Reddit Scraper CLI Script

This script provides a command-line interface for the Reddit Scraper.
It can be run directly or used as an entry point for the application.
"""

import os
import sys

# Add the src directory to the Python path so we can import our modules
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

# Now we can import our Reddit scraper
from reddit_scraper import main

if __name__ == "__main__":
    # Call the main function from our scraper module
    main()
