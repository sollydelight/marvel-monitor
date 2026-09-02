"""
Marvel news RSS digest.

Checks a list of entertainment trade RSS feeds for new articles mentioning
Marvel-related keywords, and emails you a digest of anything new.

State (which article links have already been sent) is stored in
seen_articles.json so re-runs only alert on genuinely new items.
"""

import json
import os
import re
import sys
from pathlib import Path

import feedparser
import requests

STATE_FILE = Path(__file__).parent / "seen_articles.json"

# Real, confirmed RSS feeds
FEEDS = [
    "https://variety.com/feed/",
    "https://www.hollywoodreporter.com/feed/",
    "https://deadline.com/feed/",
]

# Only alert on articles matching these keywords (case-insensitive)
KEYWORDS = ["marvel", "mcu", "x-men", "spider-man", "avengers", "disney"]

RESEND_API_KEY = os.environ.get("RESEND_API_KEY")
ALERT_EMAIL_TO = os.environ.get("ALERT_EMAIL_TO")
ALERT_EMAIL_FROM = os.environ.get("ALERT_EMAIL_FROM", "alerts@resend.dev")


def load_seen():
    if STATE_FILE.exists():
        return set(json.loads(STATE_FILE.read_text()))
    return set()


def save_seen(seen):
    STATE_FILE.write_text(json.dumps(sorted(seen)))


def matches_keywords(text):
    text = text.lower()
    return any(kw in text for kw in KEYWORDS)


def fetch_new_articles(seen):
    new_items = []
    for feed_url in FEEDS:
        try:
            parsed = feedparser.parse(feed_url)
        except Exception as e:
            print(f"[RSS] Error parsing {feed_url}: {e}", file=sys.stderr)
            continue

        source_name = parsed.feed.get("title", feed_url)

        for entry in parsed.entries:
            link = entry.get("link")
            title = entry.get("title", "")
            summary = entry.get("summary", "")

            if not link or link in seen:
                continue

            if matches_keywords(title) or matches_keywords(summary):
                new_items.append(
                    {
                        "source": source_name,
                        "title": title,
                        "link": link,
                    }
                )
                seen.add(link)

    return new_items, seen


def send_email(new_items):
    subject = f"Marvel news digest: {len(new_items)} new article(s)"
    body = "<p>New Marvel-related articles:</p><ul>"
    for item in new_items:
        body += (
            f'<li><b>{item["source"]}</b>: '
            f'<a href="{item["link"]}">{item["title"]}</a></li>'
        )
    body += "</ul>"

    if not RESEND_API_KEY or not ALERT_EMAIL_TO:
        print("[Email] Missing RESEND_API_KEY or ALERT_EMAIL_TO - printing instead.")
        print(subject)
        print(body)
        return

    resp = requests.post(
        "https://api.resend.com/emails",
        headers={
            "Authorization": f"Bearer {RESEND_API_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "from": ALERT_EMAIL_FROM,
            "to": [ALERT_EMAIL_TO],
            "subject": subject,
            "html": body,
        },
        timeout=20,
    )
    if resp.status_code >= 300:
        print(f"[Email] Failed to send: {resp.status_code} {resp.text}", file=sys.stderr)
    else:
        print("[Email] Digest sent.")


def main():
    seen = load_seen()
    new_items, seen = fetch_new_articles(seen)

    if new_items:
        send_email(new_items)
    else:
        print("No new matching articles found.")

    save_seen(seen)


if __name__ == "__main__":
    main()
