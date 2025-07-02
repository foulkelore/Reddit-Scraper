#!/usr/bin/env python3
"""
Reddit Scraper Library Example

This script demonstrates how to use the Reddit Scraper as a Python library.
"""

import os
import sys

# Add the src directory to the Python path
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
src_path = os.path.join(project_root, 'src')
sys.path.insert(0, src_path)

from reddit_scraper import RedditScraper, setup_logging


def example_library_usage():
    """Example of using the Reddit Scraper as a library."""
    
    # Set up logging
    setup_logging()
    
    # Create scraper instance with custom configuration
    scraper = RedditScraper(
        subreddits=['Python', 'programming'],
        config_file='config.json'
    )
    
    print("🚀 Starting Reddit scraper...")
    print(f"📂 Scraping subreddits: {scraper.subreddits}")
    print(f"📊 Posts per subreddit: {scraper.default_limit}")
    print(f"📅 Looking back {scraper.default_days_ago} days")
    print()
    
    # Scrape posts
    posts = scraper.scrape_posts(sort_type='hot', limit=5)
    
    # Display results summary
    total_posts = sum(len(post_list) for post_list in posts.values())
    print(f"✅ Scraped {total_posts} posts total:")
    
    for subreddit, post_list in posts.items():
        if post_list:
            print(f"  📝 r/{subreddit}: {len(post_list)} posts")
            # Show first post as example
            first_post = post_list[0]
            print(f"    🔗 Latest: \"{first_post['title'][:60]}...\"")
            print(f"    👤 Author: {first_post['author']}")
            print(f"    ⬆️  Score: {first_post['score']}")
            print(f"    💬 Comments: {first_post['num_comments']}")
            print()
        else:
            print(f"  📝 r/{subreddit}: No posts found")
    
    # Save results
    if total_posts > 0:
        saved_files = scraper.save_to_json(posts)
        print("💾 Files saved:")
        for subreddit, filename in saved_files.items():
            print(f"  📄 {filename}")
    
    return posts


if __name__ == "__main__":
    example_library_usage()
