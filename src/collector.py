import os
import re
import json
import html
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("MASTODON_BASE_URL", "https://mastodon.social")
ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")
HASHTAG = os.getenv("MASTODON_HASHTAG", "ai")
LIMIT = int(os.getenv("MASTODON_LIMIT", "20"))

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"
RAW_DIR = DATA_DIR / "raw"
PROCESSED_DIR = DATA_DIR / "processed"
STATE_FILE = DATA_DIR / "state.json"

RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
DATA_DIR.mkdir(parents=True, exist_ok=True)

def clean_html_text(text):
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text(encoding="utf-8"))
    return {"max_id": None}

def save_state(max_id):
    STATE_FILE.write_text(json.dumps({"max_id": max_id}, indent=2), encoding="utf-8")

def fetch_page(session, max_id=None):
    url = f"{BASE_URL}/api/v1/timelines/tag/{HASHTAG}"
    params = {"limit": LIMIT}
    if max_id:
        params["max_id"] = max_id

    headers = {}
    if ACCESS_TOKEN:
        headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"

    response = session.get(url, headers=headers, params=params, timeout=30)
    print("REQUEST URL:", response.url)
    print("STATUS:", response.status_code)
    response.raise_for_status()
    return response.json(), response.headers

def main():
    state = load_state()
    session = requests.Session()

    posts, headers = fetch_page(session, state.get("max_id"))

    if not posts:
        print("No new posts found.")
        return

    latest_id = posts[0]["id"]
    oldest_id = posts[-1]["id"]

    raw_file = RAW_DIR / f"{HASHTAG}_latest.json"
    raw_file.write_text(json.dumps(posts, ensure_ascii=False, indent=2), encoding="utf-8")

    rows = []
    for post in posts:
        account = post.get("account", {})
        mentions = post.get("mentions", [])
        tags = post.get("tags", [])

        rows.append({
            "post_id": post.get("id"),
            "created_at": post.get("created_at"),
            "account_id": account.get("id"),
            "username": account.get("username"),
            "acct": account.get("acct"),
            "display_name": account.get("display_name"),
            "followers_count": account.get("followers_count"),
            "following_count": account.get("following_count"),
            "statuses_count": account.get("statuses_count"),
            "bot": account.get("bot"),
            "visibility": post.get("visibility"),
            "language": post.get("language"),
            "in_reply_to_id": post.get("in_reply_to_id"),
            "in_reply_to_account_id": post.get("in_reply_to_account_id"),
            "replies_count": post.get("replies_count"),
            "reblogs_count": post.get("reblogs_count"),
            "favourites_count": post.get("favourites_count"),
            "quotes_count": post.get("quotes_count"),
            "content_html": post.get("content"),
            "content_text": clean_html_text(post.get("content")),
            "mentions_count": len(mentions),
            "mentions_accts": ",".join(m.get("acct", "") for m in mentions),
            "tags_count": len(tags),
            "tags": ",".join(t.get("name", "") for t in tags),
            "post_url": post.get("url"),
            "uri": post.get("uri")
        })

    df = pd.DataFrame(rows).drop_duplicates(subset=["post_id"])
    csv_file = PROCESSED_DIR / f"{HASHTAG}_latest.csv"
    df.to_csv(csv_file, index=False)

    save_state(latest_id)

    print(f"Saved {len(posts)} raw posts to {raw_file}")
    print(f"Saved {len(df)} cleaned rows to {csv_file}")
    print(f"Checkpoint updated to max_id={latest_id}")
    print(f"Oldest post on this run: {oldest_id}")

if __name__ == "__main__":
    main()