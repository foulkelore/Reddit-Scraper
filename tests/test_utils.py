#!/usr/bin/env python3
"""
Tests for utility functions in Reddit Scraper
"""

import os
import sys
import tempfile
import unittest
from unittest.mock import patch

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src'))

from reddit_scraper import delete_results_files, setup_logging


class TestUtilityFunctions(unittest.TestCase):
    """Test cases for utility functions."""
    
    def test_delete_results_files_success(self):
        """Test successful deletion of results files."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            test_files = ['test1.json', 'test2.json', 'readme.txt']
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
        # Should not raise an exception
        try:
            delete_results_files('/nonexistent/directory/path/that/does/not/exist')
        except (OSError, IOError) as e:
            self.fail(f"delete_results_files raised an exception: {e}")
    
    def test_delete_results_files_with_subdirectories(self):
        """Test that subdirectories are left alone."""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create files and subdirectory
            test_files = ['test1.json', 'test2.json']
            subdir = os.path.join(temp_dir, 'subdir')
            os.makedirs(subdir)
            
            for filename in test_files:
                filepath = os.path.join(temp_dir, filename)
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write('test content')
            
            # Create file in subdirectory
            subfile = os.path.join(subdir, 'subfile.txt')
            with open(subfile, 'w', encoding='utf-8') as f:
                f.write('sub content')
            
            # Delete files
            delete_results_files(temp_dir)
            
            # Verify only top-level files are deleted
            remaining_items = os.listdir(temp_dir)
            self.assertEqual(len(remaining_items), 1)
            self.assertEqual(remaining_items[0], 'subdir')
            self.assertTrue(os.path.exists(subfile))
    
    def test_delete_results_files_with_permission_error(self):
        """Test handling of permission errors during deletion."""
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = os.path.join(temp_dir, 'test.json')
            with open(test_file, 'w', encoding='utf-8') as f:
                f.write('test content')
            
            # Mock os.remove to raise an exception
            with patch('os.remove', side_effect=PermissionError("Permission denied")):
                with patch('builtins.print') as mock_print:
                    delete_results_files(temp_dir)
                    # Should print error message but not crash
                    mock_print.assert_called()
    
    @patch('reddit_scraper.logging.basicConfig')
    def test_setup_logging(self, mock_basic_config):
        """Test logging setup configuration."""
        setup_logging()
        
        # Verify basicConfig was called with expected parameters
        mock_basic_config.assert_called_once()
        call_args = mock_basic_config.call_args
        
        # Check that handlers were included in the call
        self.assertIn('handlers', call_args.kwargs)
        self.assertIn('level', call_args.kwargs)
        self.assertIn('format', call_args.kwargs)


if __name__ == '__main__':
    unittest.main()
