#!/usr/bin/env python3
"""
Reddit Scraper - Complete Application
"""

import argparse
import json
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Any, Dict, List

import requests

LOG_FILE = 'reddit_scraper.log'

class RedditScraper:
    """A class to scrape Reddit posts from multiple subreddits."""
    
    def __init__(self, subreddits=None, config_file='config.json'):
        """Initialize the scraper with subreddits from config or parameters."""
        self.base_url = "https://www.reddit.com/r"
        self.headers = {
            'User-Agent': 'Reddit-Scraper/1.0 (Educational Purpose)'
        }
        self.logger = logging.getLogger(__name__)
        
        # Try to load subreddits from config file
        self.config = self._load_config(config_file)
        if subreddits is None:
            self.subreddits = self.config.get('subreddits', ['ZedEditor'])
        else:
            self.subreddits = subreddits
            
        self.default_limit = self.config.get('limit', 25)
        self.default_days_ago = self.config.get('days_ago', 7)  # Default to 7 days if not specified
        self.clear_logs = self.config.get('clear_logs', False)
    
    def _load_config(self, config_file):
        """Load configuration from JSON file."""
        try:
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    return json.load(f)
            else:
                self.logger.warning(f"Config file {config_file} not found. Using defaults.")
                return {}
        except Exception as e:
            self.logger.error(f"Error loading config: {e}")
            return {}
    
    def maybe_clear_logs(self):
        """Clear the log file if clear_logs is set to True in config."""
        if self.clear_logs and os.path.exists(LOG_FILE):
            with open(LOG_FILE, 'w'):
                pass  # Truncate the file
            print(f"Log file '{LOG_FILE}' cleared as per config.")

    def scrape_posts(self, sort_type: str = "hot", limit: int = None, time_filter: str = "week") -> Dict[str, List[Dict[str, Any]]]:
        """
        Scrape posts from multiple subreddits.
        
        Args:
            sort_type: Sorting method ('hot', 'new', 'top', 'rising')
            limit: Maximum number of posts to retrieve per subreddit
            time_filter: Time filter for posts ('hour', 'day', 'week', 'month', 'year', 'all')
                         Only applies to 'top' and 'controversial' sort types
        """
        if limit is None:
            limit = self.default_limit
            
        all_posts = {}
        
        # Calculate timestamp based on days_ago from config
        days_ago = int((datetime.now() - timedelta(days=self.default_days_ago)).timestamp())
        
        for subreddit in self.subreddits:
            # Add time filter parameter for 'top' and 'controversial' sorts
            url = f"{self.base_url}/{subreddit}/{sort_type}.json?limit={limit}"
            if sort_type in ["top", "controversial"]:
                url += f"&t={time_filter}"
            
            try:
                self.logger.info(f"Scraping r/{subreddit} - {sort_type} posts from past {self.default_days_ago} days (limit: {limit})")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                
                data = response.json()
                posts = self._extract_posts(data, days_ago)
                
                self.logger.info(f"Successfully scraped {len(posts)} posts from r/{subreddit} (past {self.default_days_ago} days)")
                all_posts[subreddit] = posts
                
                # Be nice to Reddit API - add delay between requests
                time.sleep(1)
                
            except requests.exceptions.RequestException as e:
                self.logger.error(f"Error scraping r/{subreddit}: {e}")
                all_posts[subreddit] = []
        
        return all_posts
    
    def _extract_posts(self, data: Dict, min_timestamp: int = 0) -> List[Dict[str, Any]]:
        """
        Extract relevant post information.
        
        Args:
            data: JSON data from Reddit API
            min_timestamp: Minimum UTC timestamp to include posts (0 means no filtering)
        """
        posts = []
        
        for post in data['data']['children']:
            post_data = post['data']
            post_time = post_data.get('created_utc', 0)
            
            # Skip posts older than the minimum timestamp
            if min_timestamp > 0 and post_time < min_timestamp:
                continue
                
            extracted_post = {
                'title': post_data.get('title', ''),
                'author': post_data.get('author', ''),
                'score': post_data.get('score', 0),
                'num_comments': post_data.get('num_comments', 0),
                'created_utc': post_time,
                'created_date': datetime.fromtimestamp(post_time).strftime('%Y-%m-%d %H:%M:%S'),
                'url': post_data.get('url', ''),
                'selftext': post_data.get('selftext', ''),
                'permalink': f"https://reddit.com{post_data.get('permalink', '')}",
                'flair': post_data.get('link_flair_text', ''),
                'is_video': post_data.get('is_video', False)
            }
            
            posts.append(extracted_post)
        
        return posts
    
    def save_to_json(self, posts: Dict[str, List[Dict]], output_dir: str = None) -> Dict[str, str]:
        """
        Save each subreddit's posts to its own JSON file.

        Args:
            posts: Dictionary with subreddit names as keys and post lists as values
            output_dir: Directory to save files (default: 'results' directory)

        Returns:
            Dictionary mapping subreddit names to their output filenames
        """
        # Always use 'results' directory unless output_dir is explicitly set
        if output_dir is None:
            output_dir = "results"
        os.makedirs(output_dir, exist_ok=True)

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        saved_files = {}

        for subreddit, post_list in posts.items():
            if not post_list:  # Skip empty results
                continue

            filename = f"{subreddit}_posts_{timestamp}.json"
            filename = os.path.join(output_dir, filename)

            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(post_list, f, indent=2, ensure_ascii=False)

            self.logger.info(f"Posts for r/{subreddit} saved to {filename}")
            saved_files[subreddit] = filename

        return saved_files
    
    def save_combined_json(self, posts: Dict[str, List[Dict]], filename: str = None) -> str:
        """Save all posts to a single JSON file (legacy method)."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"reddit_posts_{timestamp}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(posts, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Combined posts saved to {filename}")
        return filename

def setup_logging():
    """Configure logging for the application."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(LOG_FILE),
            logging.StreamHandler()
        ]
    )

def main():
    """Main function to run the Reddit scraper."""
    parser = argparse.ArgumentParser(description='Reddit Scraper')
    parser.add_argument('--sort', type=str, default='hot', 
                       choices=['hot', 'new', 'rising', 'top', 'controversial'],
                       help='Sort type for posts (default: hot)')
    parser.add_argument('--limit', type=int,
                       help='Number of posts to scrape (default: from config.json or 25)')
    parser.add_argument('--output-dir', type=str, 
                       help='Directory to save output files (default: current directory)')
    parser.add_argument('--combined', action='store_true',
                       help='Save a combined JSON file with all subreddit data')
    parser.add_argument('--combined-filename', type=str,
                       help='Filename for combined output (only used with --combined)')
    parser.add_argument('--config', type=str, default='config.json',
                       help='Path to config file (default: config.json)')
    parser.add_argument('--time-filter', type=str, default='week',
                      choices=['hour', 'day', 'week', 'month', 'year', 'all'],
                      help='Time filter for posts (default: week, only applies to top/controversial sorts)')
    
    args = parser.parse_args()
    
    # Load config to check clear_logs before setting up logging
    config_path = args.config if hasattr(args, 'config') else 'config.json'
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
    except Exception:
        config = {}
    clear_logs = config.get('clear_logs', False)
    if clear_logs and os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'w'):
            pass  # Truncate the file
        print(f"Log file '{LOG_FILE}' cleared as per config.")

    setup_logging()
    logging.info("Starting Reddit scraper")
    
    scraper = RedditScraper(config_file=args.config)
    posts = scraper.scrape_posts(sort_type=args.sort, limit=args.limit, time_filter=args.time_filter)
    
    # Count total posts scraped across all subreddits
    total_posts = sum(len(post_list) for post_list in posts.values())
    
    if total_posts > 0:
        # Save individual files for each subreddit
        saved_files = scraper.save_to_json(posts, args.output_dir)
        
        # Optionally save combined file if requested
        if args.combined:
            combined_filename = scraper.save_combined_json(posts, args.combined_filename)
            print(f"Combined data saved to: {combined_filename}")
        
        print(f"Scraped {total_posts} posts from the past {scraper.default_days_ago} days across {len(scraper.subreddits)} subreddits")
        print("Posts per subreddit:")
        for subreddit, post_list in posts.items():
            file_info = f" (saved to {saved_files.get(subreddit, 'no file')})" if post_list else ""
            print(f"  - r/{subreddit}: {len(post_list)} posts{file_info}")
    else:
        print(f"No posts were scraped from the past {scraper.default_days_ago} days")

if __name__ == "__main__":
    main()
