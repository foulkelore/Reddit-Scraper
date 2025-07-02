#!/usr/bin/env python3
"""
Integration tests for Reddit Scraper - tests basic functionality without mocking
"""

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import mock_open, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from reddit_scraper import RedditScraper


class TestRedditScraperIntegration(unittest.TestCase):
    """Integration tests that don't require external libraries."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            'subreddits': ['Python'],
            'limit': 5,
            'days_ago': 7,
            'clear_logs': False,
            'sleep_seconds': 0,
            'get_post_replies': False,
            'delete_results': False
        }
    
    def test_initialization_defaults(self):
        """Test scraper initialization with defaults."""
        with patch('os.path.exists', return_value=False):
            scraper = RedditScraper()
            self.assertEqual(scraper.subreddits, ['Python'])
            self.assertEqual(scraper.default_limit, 25)
            self.assertEqual(scraper.default_days_ago, 7)
    
    def test_initialization_with_config(self):
        """Test scraper initialization with config."""
        config_json = json.dumps(self.test_config)
        with patch('builtins.open', mock_open(read_data=config_json)):
            with patch('os.path.exists', return_value=True):
                scraper = RedditScraper()
                self.assertEqual(scraper.subreddits, ['Python'])
                self.assertEqual(scraper.default_limit, 5)
                self.assertEqual(scraper.default_days_ago, 7)
    
    def test_initialization_with_subreddits_override(self):
        """Test scraper initialization with subreddits override."""
        config_json = json.dumps(self.test_config)
        custom_subreddits = ['javascript', 'nodejs']
        
        with patch('builtins.open', mock_open(read_data=config_json)):
            with patch('os.path.exists', return_value=True):
                scraper = RedditScraper(subreddits=custom_subreddits)
                self.assertEqual(scraper.subreddits, custom_subreddits)
    
    def test_config_loading_with_invalid_json(self):
        """Test config loading with invalid JSON."""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with patch('os.path.exists', return_value=True):
                with patch('reddit_scraper.logging'):
                    scraper = RedditScraper()
                    # Should fall back to defaults
                    self.assertEqual(scraper.subreddits, ['Python'])
    
    def test_save_to_json_functionality(self):
        """Test JSON saving without external dependencies."""
        scraper = RedditScraper()
        test_posts = {
            'Python': [
                {
                    'title': 'Test Post',
                    'author': 'test_user',
                    'score': 10,
                    'num_comments': 5,
                    'created_utc': 1640995200,
                    'created_date': '2022-01-01 00:00:00',
                    'url': 'https://example.com',
                    'selftext': 'Test content',
                    'permalink': 'https://reddit.com/test',
                    'flair': 'Discussion',
                    'is_video': False,
                    'replies': []
                }
            ]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            saved_files = scraper.save_to_json(test_posts, temp_dir)
            
            # Verify file was created
            self.assertIn('Python', saved_files)
            self.assertTrue(os.path.exists(saved_files['Python']))
            
            # Verify content
            with open(saved_files['Python'], 'r', encoding='utf-8') as f:
                loaded_data = json.load(f)
                self.assertEqual(len(loaded_data), 1)
                self.assertEqual(loaded_data[0]['title'], 'Test Post')
                self.assertEqual(loaded_data[0]['author'], 'test_user')
    
    def test_save_to_json_empty_subreddits(self):
        """Test saving with empty subreddits."""
        scraper = RedditScraper()
        test_posts = {
            'Python': [],
            'javascript': [{'title': 'JS Post', 'author': 'js_user'}]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            saved_files = scraper.save_to_json(test_posts, temp_dir)
            
            # Only non-empty subreddits should be saved
            self.assertNotIn('Python', saved_files)
            self.assertIn('javascript', saved_files)
    
    def test_save_combined_json(self):
        """Test combined JSON saving."""
        scraper = RedditScraper()
        test_posts = {
            'Python': [{'title': 'Python Post'}],
            'javascript': [{'title': 'JS Post'}]
        }
        
        with tempfile.TemporaryDirectory() as temp_dir:
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                filename = scraper.save_combined_json(test_posts)
                
                self.assertTrue(os.path.exists(filename))
                
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_data = json.load(f)
                    self.assertIn('Python', loaded_data)
                    self.assertIn('javascript', loaded_data)
                    self.assertEqual(len(loaded_data['Python']), 1)
                    self.assertEqual(len(loaded_data['javascript']), 1)
            finally:
                os.chdir(original_cwd)
    
    def test_clear_logs_functionality(self):
        """Test log clearing functionality."""
        config_with_clear = self.test_config.copy()
        config_with_clear['clear_logs'] = True
        
        config_json = json.dumps(config_with_clear)
        
        with patch('builtins.open', mock_open(read_data=config_json)):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open()) as mock_file:
                    scraper = RedditScraper()
                    scraper.maybe_clear_logs()
                    
                    # Verify file operations occurred
                    mock_file.assert_called()


if __name__ == '__main__':
    unittest.main()
