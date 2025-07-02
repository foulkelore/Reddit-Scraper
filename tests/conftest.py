#!/usr/bin/env python3
"""
Pytest configuration and fixtures for Reddit Scraper tests
"""

import json
import os
import tempfile
from datetime import datetime

import pytest


@pytest.fixture
def temp_dir():
    """Create a temporary directory for tests."""
    with tempfile.TemporaryDirectory() as td:
        yield td


@pytest.fixture
def sample_config():
    """Sample configuration for tests."""
    return {
        'subreddits': ['Python', 'javascript'],
        'limit': 10,
        'days_ago': 7,
        'clear_logs': False,
        'sleep_seconds': 0.1,
        'get_post_replies': True,
        'delete_results': False
    }


@pytest.fixture
def sample_reddit_data():
    """Sample Reddit API response data."""
    return {
        'data': {
            'children': [
                {
                    'data': {
                        'title': 'Test Post 1',
                        'author': 'test_user',
                        'score': 100,
                        'num_comments': 5,
                        'created_utc': datetime.now().timestamp(),
                        'url': 'https://reddit.com/test1',
                        'selftext': 'This is a test post',
                        'permalink': '/r/Python/comments/test1/',
                        'link_flair_text': 'Discussion',
                        'is_video': False
                    }
                },
                {
                    'data': {
                        'title': 'Test Post 2',
                        'author': 'another_user',
                        'score': 50,
                        'num_comments': 2,
                        'created_utc': datetime.now().timestamp() - 3600,
                        'url': 'https://reddit.com/test2',
                        'selftext': '',
                        'permalink': '/r/Python/comments/test2/',
                        'link_flair_text': 'Help',
                        'is_video': True
                    }
                }
            ]
        }
    }


@pytest.fixture
def config_file(temp_dir, sample_config):
    """Create a temporary config file."""
    config_path = os.path.join(temp_dir, 'config.json')
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(sample_config, f)
    return config_path
