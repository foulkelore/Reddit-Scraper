# Reddit Scraper

A Python tool to scrape posts from the a list of subreddits on Reddit.

## Features

- Scrape posts from a list of subreddits
- Support for different sorting methods (hot, new, rising, top)
- Configurable post limit
- JSON output with post details
- Logging functionality

## Installation

1. Clone or download this project
2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

Basic usage:
```bash
python reddit_scraper.py
```

With options:
```bash
python reddit_scraper.py --sort new --limit 50 --output my_posts.json
```

### Command Line Arguments

- `--sort`: Sort type for posts (hot, new, rising, top) - default: hot
- `--limit`: Number of posts to scrape - default: 25
- `--output`: Output filename - auto-generated if not specified

## Output

The scraper saves data in JSON format with the following fields for each post:
- title
- author
- score (upvotes - downvotes)
- num_comments
- created_utc (timestamp)
- url
- selftext (post content)
- permalink
- flair
- is_video

## Logs

Logs are saved to `reddit_scraper.log` and also displayed in the console.

## Note

This tool is for educational purposes. Please respect Reddit's terms of service and rate limits.
