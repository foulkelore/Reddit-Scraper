"""
Reddit Scraper Package

A Python package for scraping Reddit posts from multiple subreddits.
"""

from .reddit_scraper import (RedditScraper, delete_results_files, main,
                             setup_logging)

__version__ = "1.0.0"
__author__ = "Reddit Scraper Team"

__all__ = [
    "RedditScraper",
    "setup_logging", 
    "delete_results_files",
    "main"
]
