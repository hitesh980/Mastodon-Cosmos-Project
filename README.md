# Mastodon Cosmos Project

A Python-based data collection tool for gathering and processing posts from the Mastodon social network, specifically targeting the `#ai` hashtag. The project fetches public posts, cleans HTML content, extracts metadata, and exports structured data to CSV for analysis.

## Features

- **API Integration**: Connects to Mastodon API to fetch posts from the `#ai` hashtag timeline.
- **Incremental Collection**: Uses pagination (`max_id`) to collect older posts without duplicates, maintaining state across runs.
- **Data Processing**: Cleans HTML from post content, extracts user metadata, mentions, tags, and engagement metrics.
- **Output Formats**: Saves raw JSON and processed CSV files.
- **Automation**: Supports cron jobs for scheduled daily runs.
- **Environment Configuration**: Uses `.env` for secure API credentials.

## Installation

1. Clone or navigate to the project directory.
2. Create a virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

1. Obtain a Mastodon access token from your Mastodon instance (e.g., mastodon.social).
2. Create a `.env` file in the project root:
   ```env
   MASTODON_BASE_URL=https://mastodon.social
   MASTODON_ACCESS_TOKEN=your_access_token_here
   MASTODON_HASHTAG=ai
   MASTODON_LIMIT=20
   ```

## Usage

### Manual Run
Run the collector script:
```bash
python src/collector.py
```
This fetches the latest posts, processes them, and updates `data/raw/ai_latest.json` and `data/processed/ai_latest.csv`.

### Automated Run (Cron)
Set up a daily cron job:
```bash
crontab -e
```
Add:
```
0 0 * * * source /path/to/project/.venv/bin/activate && cd /path/to/project && python src/collector.py >> data/cron.log 2>&1
```
Replace `/path/to/project` with the absolute path.

## Project Structure

- `src/collector.py`: Main script for data collection and processing.
- `data/raw/`: Raw JSON responses.
- `data/processed/`: Cleaned CSV files.
- `data/state.json`: Tracks the last fetched post ID for incremental collection.
- `requirements.txt`: Python dependencies.
- `.env`: Environment variables (not committed).

## Challenges Faced

During development:
- Resolved missing dependencies (e.g., `python-dotenv`).
- Fixed environment variable misuse and API authentication errors.
- Addressed cron job setup issues with venv activation and permissions.
- Implemented HTML cleaning and duplicate handling for data integrity.

## Next Steps

The project is evolving to incorporate computational technology for narrative analysis of the collected #ai posts. This includes exploring natural language processing (NLP) techniques to understand trends, sentiments, and themes in the data. Work is ongoing to integrate tools like topic modeling or sentiment analysis for deeper insights.

## License

[Add license if applicable]