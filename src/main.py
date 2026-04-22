import os
import re
import json
import html
import time
from pathlib import Path

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

BASE_URL = os.getenv("MASTODON_BASE_URL", "https://mastodon.social")
ACCESS_TOKEN = os.getenv("MASTODON_ACCESS_TOKEN")
HASHTAG = "ai"
LIMIT = 20
MAX_PAGES = 5
SLEEP_SECONDS = 1

RAW_DIR = Path("data/raw")
PROCESSED_DIR = Path("data/processed")
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def clean_html_text(text):
    if not text:
        return ""
    text = re.sub(r"<br\s*/?>", " ", text)
    text = re.sub(r"<[^>]+>", "", text)
    text = html.unescape(text)
    text = re.sub(r"\s+", " ", text).strip()
    return text

session = requests.Session()
headers = {}
if ACCESS_TOKEN:
    headers["Authorization"] = f"Bearer {ACCESS_TOKEN}"

all_posts = []
max_id = None

for page in range(MAX_PAGES):
    url = f"{BASE_URL}/api/v1/timelines/tag/{HASHTAG}"
    params = {"limit": LIMIT}
    if max_id:
        params["max_id"] = max_id

    response = session.get(url, headers=headers, params=params, timeout=30)
    print(f"Page {page + 1} URL:", response.url)
    print(f"Page {page + 1} STATUS:", response.status_code)
    response.raise_for_status()

    posts = response.json()
    if not posts:
        print("No more posts returned.")
        break

    all_posts.extend(posts)
    max_id = posts[-1]["id"]

    print(f"Collected {len(posts)} posts on page {page + 1}")
    time.sleep(SLEEP_SECONDS)

raw_file = RAW_DIR / f"{HASHTAG}_timeline_pages.json"
with open(raw_file, "w", encoding="utf-8") as f:
    json.dump(all_posts, f, ensure_ascii=False, indent=2)

rows = []
for post in all_posts:
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
csv_file = PROCESSED_DIR / f"{HASHTAG}_timeline.csv"
df.to_csv(csv_file, index=False)

print(f"Saved {len(all_posts)} raw posts to {raw_file}")
print(f"Saved {len(df)} cleaned rows to {csv_file}")