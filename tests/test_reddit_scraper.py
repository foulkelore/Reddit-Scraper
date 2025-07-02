#!/usr/bin/env python3
"""
Unit tests for Reddit Scraper
"""

import json
import os
import sys
import tempfile
import unittest
from datetime import datetime, timedelta
from unittest.mock import mock_open, patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

try:
    import responses
    HAS_RESPONSES = True
except ImportError:
    HAS_RESPONSES = False

from reddit_scraper import RedditScraper, delete_results_files, setup_logging


class TestRedditScraper(unittest.TestCase):
    """Test cases for the RedditScraper class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_config = {
            'subreddits': ['Python', 'javascript'],
            'limit': 10,
            'days_ago': 7,
            'clear_logs': False,
            'sleep_seconds': 0.1,  # Faster for tests
            'get_post_replies': True,
            'delete_results': False
        }
        
        self.sample_reddit_data = {
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
                            'created_utc': datetime.now().timestamp() - 3600,  # 1 hour ago
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
        
        self.sample_comments_data = [
            {},  # First element is post data (not used)
            {
                'data': {
                    'children': [
                        {
                            'kind': 't1',
                            'data': {
                                'author': 'commenter1',
                                'body': 'Great post!',
                                'score': 10,
                                'created_utc': datetime.now().timestamp(),
                                'permalink': '/r/Python/comments/test1/comment1/'
                            }
                        },
                        {
                            'kind': 't1',
                            'data': {
                                'author': 'commenter2',
                                'body': 'Thanks for sharing',
                                'score': 5,
                                'created_utc': datetime.now().timestamp() - 1800,
                                'permalink': '/r/Python/comments/test1/comment2/'
                            }
                        }
                    ]
                }
            }
        ]

    def test_init_with_config_file(self):
        """Test initialization with config file."""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_config))):
            with patch('os.path.exists', return_value=True):
                scraper = RedditScraper(config_file='test_config.json')
                
                self.assertEqual(scraper.subreddits, ['Python', 'javascript'])
                self.assertEqual(scraper.default_limit, 10)
                self.assertEqual(scraper.default_days_ago, 7)
                self.assertEqual(scraper.sleep_seconds, 0.1)

    def test_init_with_subreddits_parameter(self):
        """Test initialization with subreddits parameter."""
        with patch('builtins.open', mock_open(read_data=json.dumps(self.test_config))):
            with patch('os.path.exists', return_value=True):
                custom_subreddits = ['nodejs', 'react']
                scraper = RedditScraper(subreddits=custom_subreddits)
                
                self.assertEqual(scraper.subreddits, custom_subreddits)

    def test_init_with_missing_config(self):
        """Test initialization when config file doesn't exist."""
        with patch('os.path.exists', return_value=False):
            with patch('reddit_scraper.logging'):
                scraper = RedditScraper()
                
                self.assertEqual(scraper.subreddits, ['Python'])  # Default value
                self.assertEqual(scraper.default_limit, 25)  # Default value

    def test_load_config_invalid_json(self):
        """Test _load_config with invalid JSON."""
        with patch('builtins.open', mock_open(read_data='invalid json')):
            with patch('os.path.exists', return_value=True):
                with patch('reddit_scraper.logging'):
                    scraper = RedditScraper()
                    
                    # Should use defaults when config loading fails
                    self.assertEqual(scraper.subreddits, ['Python'])

    def test_maybe_clear_logs(self):
        """Test log clearing functionality."""
        config_with_clear = self.test_config.copy()
        config_with_clear['clear_logs'] = True
        
        with patch('builtins.open', mock_open(read_data=json.dumps(config_with_clear))):
            with patch('os.path.exists', return_value=True):
                with patch('builtins.open', mock_open()) as mock_file:
                    scraper = RedditScraper()
                    scraper.maybe_clear_logs()
                    
                    # Verify that the log file was opened for writing (clearing)
                    mock_file.assert_called()

    def _add_responses_decorator(self, func):
        """Helper to conditionally add responses.activate decorator."""
        if HAS_RESPONSES:
            return responses.activate(func)
        return func

    @unittest.skipUnless(HAS_RESPONSES, "responses library not available")
    @responses.activate
    def test_scrape_posts_success(self):
        """Test successful post scraping."""
        # Mock the Reddit API response
        responses.add(
            responses.GET,
            'https://www.reddit.com/r/Python/hot.json?limit=10',
            json=self.sample_reddit_data,
            status=200
        )
        
        # Mock comments response
        responses.add(
            responses.GET,
            'https://www.reddit.com/r/Python/comments/test1.json?limit=10',
            json=self.sample_comments_data,
            status=200
        )
        
        responses.add(
            responses.GET,
            'https://www.reddit.com/r/Python/comments/test2.json?limit=10',
            json=self.sample_comments_data,
            status=200
        )

        with patch('builtins.open', mock_open(read_data=json.dumps({'subreddits': ['Python'], 'limit': 10}))):
            with patch('os.path.exists', return_value=True):
                scraper = RedditScraper()
                posts = scraper.scrape_posts(sort_type='hot', limit=10)
                
                self.assertIn('Python', posts)
                self.assertEqual(len(posts['Python']), 2)
                self.assertEqual(posts['Python'][0]['title'], 'Test Post 1')
                self.assertEqual(posts['Python'][0]['author'], 'test_user')
                self.assertEqual(posts['Python'][0]['score'], 100)

    @unittest.skipUnless(HAS_RESPONSES, "responses library not available")
    @responses.activate
    def test_scrape_posts_with_time_filter(self):
        """Test scraping posts with time filter."""
        responses.add(
            responses.GET,
            'https://www.reddit.com/r/Python/top.json?limit=10&t=month',
            json=self.sample_reddit_data,
            status=200
        )

        with patch('builtins.open', mock_open(read_data=json.dumps({'subreddits': ['Python']}))):
            with patch('os.path.exists', return_value=True):
                scraper = RedditScraper()
                scraper.get_post_replies = False  # Disable replies for this test
                posts = scraper.scrape_posts(sort_type='top', limit=10, time_filter='month')
                
                self.assertIn('Python', posts)

    @unittest.skipUnless(HAS_RESPONSES, "responses library not available")
    @responses.activate
    def test_scrape_posts_request_error(self):
        """Test handling of request errors."""
        responses.add(
            responses.GET,
            'https://www.reddit.com/r/Python/hot.json?limit=10',
            status=500
        )

        with patch('builtins.open', mock_open(read_data=json.dumps({'subreddits': ['Python']}))):
            with patch('os.path.exists', return_value=True):
                with patch('reddit_scraper.logging'):
                    scraper = RedditScraper()
                    posts = scraper.scrape_posts(sort_type='hot', limit=10)
                    
                    self.assertIn('Python', posts)
                    self.assertEqual(posts['Python'], [])  # Should be empty due to error

    def test_extract_posts_with_time_filter(self):
        """Test post extraction with timestamp filtering."""
        scraper = RedditScraper(subreddits=['Python'])
        
        # Create posts with different timestamps
        old_timestamp = (datetime.now() - timedelta(days=10)).timestamp()
        recent_timestamp = datetime.now().timestamp()
        
        test_data = {
            'data': {
                'children': [
                    {
                        'data': {
                            'title': 'Old Post',
                            'created_utc': old_timestamp,
                            'author': 'user1',
                            'score': 10,
                            'num_comments': 1,
                            'url': 'http://example.com',
                            'selftext': '',
                            'permalink': '/test/',
                            'link_flair_text': '',
                            'is_video': False
                        }
                    },
                    {
                        'data': {
                            'title': 'Recent Post',
                            'created_utc': recent_timestamp,
                            'author': 'user2',
                            'score': 20,
                            'num_comments': 2,
                            'url': 'http://example.com',
                            'selftext': '',
                            'permalink': '/test/',
                            'link_flair_text': '',
                            'is_video': False
                        }
                    }
                ]
            }
        }
        
        # Filter posts from the last 7 days
        seven_days_ago = int((datetime.now() - timedelta(days=7)).timestamp())
        posts = scraper._extract_posts(test_data, seven_days_ago)
        
        # Should only include the recent post
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['title'], 'Recent Post')

    @unittest.skipUnless(HAS_RESPONSES, "responses library not available")
    @responses.activate
    def test_fetch_replies_success(self):
        """Test successful reply fetching."""
        responses.add(
            responses.GET,
            'https://www.reddit.com/r/Python/comments/test123.json?limit=5',
            json=self.sample_comments_data,
            status=200
        )

        scraper = RedditScraper(subreddits=['Python'])
        replies = scraper._fetch_replies('Python', 'test123', 5)
        
        self.assertEqual(len(replies), 2)
        self.assertEqual(replies[0]['author'], 'commenter1')
        self.assertEqual(replies[0]['body'], 'Great post!')
        self.assertEqual(replies[1]['author'], 'commenter2')

    @unittest.skipUnless(HAS_RESPONSES, "responses library not available")
    @responses.activate
    def test_fetch_replies_error(self):
        """Test reply fetching with error."""
        responses.add(
            responses.GET,
            'https://www.reddit.com/r/Python/comments/test123.json?limit=5',
            status=404
        )

        with patch('reddit_scraper.logging'):
            scraper = RedditScraper(subreddits=['Python'])
            replies = scraper._fetch_replies('Python', 'test123', 5)
            
            self.assertEqual(replies, [])

    def test_save_to_json(self):
        """Test saving posts to JSON files."""
        posts_data = {
            'Python': [
                {'title': 'Test Post', 'author': 'user1', 'score': 10}
            ],
            'javascript': [
                {'title': 'JS Post', 'author': 'user2', 'score': 5}
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            scraper = RedditScraper(subreddits=['Python', 'javascript'])
            saved_files = scraper.save_to_json(posts_data, temp_dir)
            
            self.assertEqual(len(saved_files), 2)
            self.assertIn('Python', saved_files)
            self.assertIn('javascript', saved_files)
            
            # Verify files were created
            for filename in saved_files.values():
                self.assertTrue(os.path.exists(filename))
                
                # Verify content
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.assertIsInstance(data, list)
                    self.assertGreater(len(data), 0)

    def test_save_to_json_empty_posts(self):
        """Test saving empty posts to JSON."""
        posts_data = {
            'Python': [],
            'javascript': [
                {'title': 'JS Post', 'author': 'user2', 'score': 5}
            ]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            scraper = RedditScraper(subreddits=['Python', 'javascript'])
            saved_files = scraper.save_to_json(posts_data, temp_dir)
            
            # Only non-empty subreddits should have files
            self.assertEqual(len(saved_files), 1)
            self.assertIn('javascript', saved_files)
            self.assertNotIn('Python', saved_files)

    def test_save_combined_json(self):
        """Test saving combined JSON file."""
        posts_data = {
            'Python': [{'title': 'Test Post'}],
            'javascript': [{'title': 'JS Post'}]
        }

        with tempfile.TemporaryDirectory() as temp_dir:
            scraper = RedditScraper(subreddits=['Python', 'javascript'])
            
            # Change to temp directory
            original_cwd = os.getcwd()
            os.chdir(temp_dir)
            
            try:
                filename = scraper.save_combined_json(posts_data)
                
                self.assertTrue(os.path.exists(filename))
                
                with open(filename, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.assertIn('Python', data)
                    self.assertIn('javascript', data)
                    self.assertEqual(len(data['Python']), 1)
                    self.assertEqual(len(data['javascript']), 1)
            finally:
                os.chdir(original_cwd)


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_delete_results_files(self):
        """Test deletion of results files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create some test files
            test_files = ['test1.json', 'test2.json', 'test3.txt']
            for filename in test_files:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('test content')
            
            # Verify files exist
            for filename in test_files:
                self.assertTrue(os.path.exists(os.path.join(temp_dir, filename)))
            
            # Delete files
            delete_results_files(temp_dir)
            
            # Verify files are deleted
            remaining_files = os.listdir(temp_dir)
            self.assertEqual(len(remaining_files), 0)

    def test_delete_results_files_nonexistent_directory(self):
        """Test deletion when directory doesn't exist."""
        # Should not raise an error
        delete_results_files('/nonexistent/directory')

    @patch('reddit_scraper.logging.basicConfig')
    def test_setup_logging(self, mock_basic_config):
        """Test logging setup."""
        setup_logging()
        # Verify that basicConfig was called
        mock_basic_config.assert_called_once()


if __name__ == '__main__':
    unittest.main()
