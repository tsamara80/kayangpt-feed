#!/usr/bin/env python3
"""
KayanGPT Live Feed Updater
--------------------------
Runs daily (via GitHub Actions). Does the following:

1. Fetches the GoHighLevel changelog RSS feed.
2. For each NEW entry (not already in updates.json), asks Claude to
   classify it as LIVE_NOW / COMING_SOON / DISCARD.
3. For anything kept, asks Claude to rewrite it in Kayan's voice,
   stripping every mention of GoHighLevel/GHL/HighLevel.
4. Merges the result into updates.json, sorted newest first.

updates.json is the file KayanGPT's Action reads from (via the raw
GitHub URL — see README.md for the exact setup).

Requires env var: ANTHROPIC_API_KEY
"""

import json
import os
import re
import sys
from datetime import datetime, timezone

import feedparser
import anthropic

RSS_URL = "https://ideas.gohighlevel.com/api/changelog/feed.rss"
DATA_FILE = os.path.join(os.path.dirname(__file__), "updates.json")
MODEL = "claude-sonnet-4-6"

FILTER_PROMPT = """You are filtering a GoHighLevel changelog entry to decide if it should
appear in KayanGPT, a white-label product. Never mention GoHighLevel,
GHL, or HighLevel in your output — Kayan is a fully separate brand.

Given the raw changelog entry below, classify it into exactly one
category:

LIVE_NOW — a feature or capability currently available that Kayan
end-users (coaches, consultants, service providers) would directly
interact with. Includes: Conversation AI, workflows/automations,
forms, calendars, funnels, websites, courses, WhatsApp/SMS, payments
UI visible to a client, or any deprecation/removal of something
currently in use.

COMING_SOON — a beta/labs feature not yet generally available.
Only relevant if a user specifically asks about upcoming features
or the roadmap. Do not include how-to steps since it isn't usable yet.

DISCARD — agency/backend-only settings, SaaS/rebilling/reseller
config, infrastructure or carrier cost changes, internal audit logs,
permission plumbing, or purely cosmetic/UI polish with no functional
change.

Respond with ONLY a JSON object, no other text:
{"category": "LIVE_NOW" | "COMING_SOON" | "DISCARD", "reason": "one line justification"}

Raw entry title: {title}
Raw entry content: {content}
"""

REWRITE_PROMPT = """Rewrite this GoHighLevel changelog entry as a Kayan.ai feature update.

Hard rules:
- Never mention GoHighLevel, GHL, HighLevel, or LeadConnector anywhere.
- Reframe it as a native Kayan.ai feature, in Kayan's voice: direct, clear, professional.
- If category is COMING_SOON, do NOT include step-by-step instructions
  (nothing is usable yet) — just describe what's coming.
- If category is LIVE_NOW, include a short "How to set it up" section
  with concrete steps, adapted to sound like Kayan's own dashboard
  (e.g. "Kayan dashboard", "Kayan Automations tab") rather than copying
  GHL's literal menu names if they'd expose the underlying platform.
- Keep it tight: a title, 1-2 sentence summary, bullet list of what's
  new, and (for LIVE_NOW) a short how-to. No fluff, no marketing tone.

Category: {category}
Raw title: {title}
Raw content: {content}

Output ONLY the rewritten update text, no preamble.
"""


def load_existing():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"last_updated": None, "updates": []}


def save(data):
    data["last_updated"] = datetime.now(timezone.utc).isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def clean_html(raw):
    return re.sub("<[^<]+?>", "", raw or "").strip()


def classify(client, title, content):
    prompt = FILTER_PROMPT.format(title=title, content=content)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=200,
        messages=[{"role": "user", "content": prompt}],
    )
    text = resp.content[0].text.strip()
    text = re.sub(r"^```json|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {"category": "DISCARD", "reason": "unparseable classifier output"}


def rewrite(client, category, title, content):
    prompt = REWRITE_PROMPT.format(category=category, title=title, content=content)
    resp = client.messages.create(
        model=MODEL,
        max_tokens=800,
        messages=[{"role": "user", "content": prompt}],
    )
    return resp.content[0].text.strip()


def main():
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)
    data = load_existing()
    existing_links = {u["source_link"] for u in data["updates"]}

    feed = feedparser.parse(RSS_URL)
    new_count = 0

    for entry in feed.entries:
        link = entry.get("link", entry.get("id", ""))
        if link in existing_links:
            continue  # already processed

        title = clean_html(entry.get("title", ""))
        content = clean_html(entry.get("summary", entry.get("description", "")))
        published = entry.get("published", entry.get("updated", ""))

        result = classify(client, title, content)
        category = result.get("category", "DISCARD")

        if category == "DISCARD":
            # Mark as seen so we don't reprocess it, but don't store content
            data["updates"].append({
                "source_link": link,
                "category": "DISCARD",
                "published": published,
            })
            continue

        rewritten = rewrite(client, category, title, content)

        data["updates"].append({
            "source_link": link,
            "category": category,
            "published": published,
            "title": title,
            "content": rewritten,
            "processed_at": datetime.now(timezone.utc).isoformat(),
        })
        new_count += 1
        print(f"Processed [{category}]: {title}")

    # Keep newest first (by published date string fallback to processed order)
    data["updates"].sort(key=lambda u: u.get("published", ""), reverse=True)

    save(data)
    print(f"Done. {new_count} new update(s) added.")


if __name__ == "__main__":
    main()
