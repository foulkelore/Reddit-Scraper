# Reddit Scraper

A Python tool to scrape posts and replies from a list of subreddits on Reddit.

## Features

- Scrape posts from a configurable list of subreddits (see `config.json`)
- Download replies (comments) for each post (up to the same limit as posts, configurable)
- Support for different sorting methods (`hot`, `new`, `rising`, `top`, `controversial`)
- Configurable post and reply limit
- Configurable time window for posts (e.g., last N days)
- JSON output with post and reply details, saved in a `results` directory
- Logging functionality with optional log clearing
- Optionally delete all files in the `results` directory at the start of each run

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
python reddit_scraper.py --sort new --limit 50
```

### Command Line Arguments

- `--sort`: Sort type for posts (`hot`, `new`, `rising`, `top`, `controversial`) - default: hot
- `--limit`: Number of posts (and replies per post) to scrape per subreddit - default: value from `config.json` or 25
- `--output-dir`: Directory to save output files (default: `results`)
- `--combined`: Also save a combined JSON file with all subreddit data
- `--combined-filename`: Filename for combined output (only used with `--combined`)
- `--config`: Path to config file (default: `config.json`)
- `--time-filter`: Time filter for posts (`hour`, `day`, `week`, `month`, `year`, `all`) - default: week (only applies to `top`/`controversial` sorts)

## Configuration

Edit `config.json` to set:
- `subreddits`: List of subreddit names to scrape
- `limit`: Number of posts (and replies) per subreddit
- `days_ago`: Only include posts from the last N days
- `clear_logs`: Set to `true` to clear the log file at the start of each run
- `sleep_seconds`: Number of seconds to sleep between requests (default: 2)
- `get_post_replies`: Set to `true` to fetch replies for each post, `false` to skip replies
- `delete_results`: Set to `true` to delete all files in the `results` directory at the start of each run

Example:
```json
{
  "subreddits": [
    "vscode",
    "node",
    "typescript",
    "Python"
  ],
  "limit": 25,
  "days_ago": 7,
  "clear_logs": true,
  "sleep_seconds": 1,
  "get_post_replies": true,
  "delete_results": true
}
```

## Output

Each subreddit's posts are saved as a separate JSON file in the `results` directory.  
Each post includes:
- title
- author
- score
- num_comments
- created_utc (timestamp)
- created_date (human-readable)
- url
- selftext (post content)
- permalink
- flair
- is_video

- replies: a list of reply objects, each with:
  - author
  - body
  - score
  - created_utc
  - created_date
  - permalink

## Logs

Logs are saved to `reddit_scraper.log` and also displayed in the console.  
Set `"clear_logs": true` in `config.json` to clear the log file at the start of each run.

## Note

This tool is for educational purposes. Please respect Reddit's terms of service and rate limits.
