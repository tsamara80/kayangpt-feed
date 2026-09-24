#!/usr/bin/env python3
"""
Kayan updates feed, version 2.

Runs daily in GitHub Actions (private repo). Steps:

1. Read the upstream changelog RSS feed.
2. Classify each new entry: LIVE_NOW, COMING_SOON or DISCARD, applying the Kayan rules.
3. Rewrite kept entries for Kayan in English and Arabic, returned as JSON.
4. Guard: reject any output that names the provider, links outside Kayan, or
   mentions a feature that is unavailable in the region. Failed items are held,
   never published.
5. Save the full working file (private): data/updates_full.json
6. Write the clean public file: public/updates.json
   (LIVE_NOW and COMING_SOON only, no source links, newest first by real date,
   last FEED_DAYS days only). The workflow pushes it to the public repo.

Modes:
  python update_feed.py              normal daily run
  python update_feed.py --reclean    one time pass that rewrites every stored
                                     item under the current rules (fixes items
                                     written by version 1)

Env: ANTHROPIC_API_KEY (required), MODEL (optional), FEED_DAYS (optional, default 180)
"""

import json
import os
import re
import sys
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime

HERE = os.path.dirname(os.path.abspath(__file__))
RSS_URL = "https://ideas.gohighlevel.com/api/changelog/feed.rss"
FULL_FILE = os.path.join(HERE, "data", "updates_full.json")
LEGACY_FILE = os.path.join(HERE, "updates.json")
PUBLIC_FILE = os.path.join(HERE, "public", "updates.json")
MODEL = os.environ.get("MODEL", "claude-sonnet-4-6")
FEED_DAYS = int(os.environ.get("FEED_DAYS", "180"))

# ----------------------------------------------------------------------------
# Kayan rules shared by both prompts. Keep in sync with kayan_rules.md.
# ----------------------------------------------------------------------------
KAYAN_RULES = """Kayan rules (these override the source text):
1. Never name the underlying provider: no HighLevel, GoHighLevel, GHL, HL, LeadConnector, Lead Connector.
2. These features are NOT available to Kayan users and must never be described as available:
   SMS (any SMS sending, receiving, reminders or campaigns), Missed Call Text Back,
   WhatsApp Call Text Back, AI voice calling (the system making or receiving phone calls).
3. If an update is ONLY about an unavailable feature, it is DISCARD.
   If it mentions one alongside available channels, keep it and silently remove the unavailable part
   (for example "email, SMS and WhatsApp" becomes "email and WhatsApp"). Never replace SMS with WhatsApp
   unless the source says the feature works on WhatsApp.
4. Use the real interface labels from the source (for example "Automation > Workflows", "Settings > Domains").
   Never invent menu names such as "Kayan Automations tab". If a label itself contains the provider's name,
   describe it by its function instead.
5. No URLs, no links, no app version numbers (for example "version 4.25.0"), no prices.
6. Arabic: formal Arabic (فصحى), masculine or neutral plural address, never feminine,
   "برنامج تدريبي" never "كورس". Arabic interface terms: Workflows = مسارات العمل,
   Pipelines = مراحل المبيعات, Funnels = صفحات البيع, Settings = الإعدادات, Contacts = جهات الاتصال,
   Calendars = التقويمات, Social Planner = مخطط النشر, Client Portal = بوابة العملاء.
   After an Arabic interface term, add the English label in brackets on first use."""

FILTER_PROMPT = """You decide whether a software changelog entry should appear in the feature updates feed
of Kayan.ai, a platform for coaches, consultants, specialists and local businesses.

{rules}

Categories:
LIVE_NOW: available now, and something Kayan users (not agencies) would use directly: conversations,
workflows and automations, forms, calendars, funnels, websites, programs and memberships, email,
WhatsApp, Instagram and Facebook, payments a client sees, AI assistants, or removal of something in use.
COMING_SOON: beta, labs or announced but not generally available.
DISCARD: agency or reseller settings, rebilling, SaaS configuration, infrastructure, carrier or phone costs,
audit logs, permission plumbing, cosmetic changes, or anything only about an unavailable feature (rule 3).

Reply with ONLY this JSON, nothing else:
{{"category": "LIVE_NOW" | "COMING_SOON" | "DISCARD", "reason": "one line"}}

Entry title: {title}
Entry content: {content}
"""

REWRITE_PROMPT = """Rewrite this changelog entry as a Kayan.ai feature update, in English and in Arabic.

{rules}

Style: direct, clear, professional, no marketing tone, no fluff.
Structure for each language: a short title, a 1 to 2 sentence summary, then a short list of what is new.
If category is LIVE_NOW, add a short "How to use it" list with concrete steps using the real interface labels.
If category is COMING_SOON, describe what is planned, give no steps and no dates.

Category: {category}
Title: {title}
Content: {content}

Reply with ONLY this JSON, nothing else:
{{"title": "...", "content": "...", "title_ar": "...", "content_ar": "..."}}
Use plain text with line breaks inside content and content_ar. No markdown headings, no links.
"""

# Anything matching this must never reach the public file.
BANNED = re.compile(
    r"high\s?level|\bghl\b|\bhl\b|lead\s?connector|gohighlevel|msgsndr|"
    r"https?://|www\.|\bSMS\b|missed call text|call text back|"
    r"v(?:ersion)?\s?\d+\.\d+\.\d+|كورس|رسائل\s?نصية|الرسائل\s?النصية",
    re.IGNORECASE,
)


def now_iso():
    return datetime.now(timezone.utc).isoformat()


def to_dt(value):
    """Parse RSS or ISO dates. Returns an aware datetime, or epoch when unknown."""
    if not value:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    try:
        dt = parsedate_to_datetime(value)
    except (TypeError, ValueError):
        try:
            dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
        except ValueError:
            return datetime(1970, 1, 1, tzinfo=timezone.utc)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt


def clean_html(raw):
    return re.sub(r"<[^<]+?>", "", raw or "").strip()


def extract_json(text):
    text = re.sub(r"^```(?:json)?|```$", "", text.strip(), flags=re.MULTILINE).strip()
    start, end = text.find("{"), text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return json.loads(text[start : end + 1])


def ask(client, prompt, max_tokens):
    resp = client.messages.create(
        model=MODEL, max_tokens=max_tokens, messages=[{"role": "user", "content": prompt}]
    )
    return resp.content[0].text


def classify(client, title, content):
    """Returns (category, reason) or (None, reason) when the model output is unusable."""
    prompt = FILTER_PROMPT.format(rules=KAYAN_RULES, title=title, content=content)
    try:
        result = extract_json(ask(client, prompt, 200))
    except Exception as exc:  # retried on the next daily run
        return None, f"classifier error: {exc}"
    category = result.get("category")
    if category not in ("LIVE_NOW", "COMING_SOON", "DISCARD"):
        return None, f"classifier returned {category!r}"
    return category, result.get("reason", "")


def guard_failures(item):
    """Names every banned match in the public fields. Empty list means safe."""
    hits = []
    for field in ("title", "content", "title_ar", "content_ar"):
        for match in BANNED.finditer(item.get(field) or ""):
            hits.append(f"{field}: {match.group(0)!r}")
    return hits


def rewrite(client, category, title, content):
    """Two attempts. Returns (fields, problems). Fields is None when both attempts fail."""
    prompt = REWRITE_PROMPT.format(rules=KAYAN_RULES, category=category, title=title, content=content)
    problems = []
    for _ in range(2):
        try:
            out = extract_json(ask(client, prompt, 2500))
        except Exception as exc:
            problems = [f"rewrite error: {exc}"]
            continue
        fields = {k: (out.get(k) or "").strip() for k in ("title", "content", "title_ar", "content_ar")}
        if not all(fields.values()):
            problems = ["rewrite missing a field"]
            continue
        problems = guard_failures(fields)
        if not problems:
            return fields, []
        prompt += "\n\nYour previous answer broke the rules here: " + "; ".join(problems) + ". Fix these and reply again."
    return None, problems


def load_full():
    if os.path.exists(FULL_FILE):
        with open(FULL_FILE, encoding="utf-8") as f:
            return json.load(f)
    # First run of version 2: migrate the version 1 file.
    if os.path.exists(LEGACY_FILE):
        with open(LEGACY_FILE, encoding="utf-8") as f:
            legacy = json.load(f)
        items = []
        for u in legacy.get("updates", []):
            item = {
                "source_link": u.get("source_link", ""),
                "category": u.get("category", "DISCARD"),
                "published": to_dt(u.get("published")).isoformat(),
                "raw_title": u.get("title", ""),
                "raw_content": "",
                "status": "legacy" if u.get("category") != "DISCARD" else "discarded",
            }
            if item["status"] == "legacy":
                item.update({"title": u.get("title", ""), "content": u.get("content", ""), "title_ar": "", "content_ar": ""})
            items.append(item)
        print(f"Migrated {len(items)} items from version 1.")
        return {"last_updated": None, "updates": items}
    return {"last_updated": None, "updates": []}


def save_full(data):
    os.makedirs(os.path.dirname(FULL_FILE), exist_ok=True)
    data["updates"].sort(key=lambda u: to_dt(u.get("published")), reverse=True)
    data["last_updated"] = now_iso()
    with open(FULL_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def write_public(data):
    """Only published items, only public fields, newest first, last FEED_DAYS days."""
    cutoff = datetime.now(timezone.utc) - timedelta(days=FEED_DAYS)
    public = []
    for u in data["updates"]:
        if u.get("status") != "published" or u.get("category") not in ("LIVE_NOW", "COMING_SOON"):
            continue
        if to_dt(u.get("published")) < cutoff:
            continue
        entry = {k: u[k] for k in ("category", "title", "content", "title_ar", "content_ar")}
        entry["published"] = to_dt(u["published"]).date().isoformat()
        if guard_failures(entry):  # belt and braces: never publish a failing item
            continue
        public.append(entry)
    public.sort(key=lambda e: e["published"], reverse=True)
    os.makedirs(os.path.dirname(PUBLIC_FILE), exist_ok=True)
    with open(PUBLIC_FILE, "w", encoding="utf-8") as f:
        json.dump({"last_updated": now_iso(), "updates": public}, f, ensure_ascii=False, indent=2)
    return len(public)


def process(client, item, title, content):
    """Rewrites one kept item in place and sets its status."""
    fields, problems = rewrite(client, item["category"], title, content)
    item["processed_at"] = now_iso()
    if fields:
        item.update(fields)
        item["status"] = "published"
        item.pop("problems", None)
    else:
        item["status"] = "held"
        item["problems"] = problems
    print(f"[{item['status']}] {item['category']}: {title[:80]}")


def run_daily(client, data):
    import feedparser

    by_link = {u["source_link"]: u for u in data["updates"]}
    feed = feedparser.parse(RSS_URL)
    added = 0
    for entry in feed.entries:
        link = entry.get("link", entry.get("id", ""))
        known = by_link.get(link)
        if known and known.get("status") in ("published", "discarded", "legacy"):
            continue
        title = clean_html(entry.get("title", ""))
        content = clean_html(entry.get("summary", entry.get("description", "")))
        published = to_dt(entry.get("published", entry.get("updated", ""))).isoformat()

        category, reason = classify(client, title, content)
        if category is None:
            print(f"[retry tomorrow] {title[:80]}: {reason}")
            continue  # not stored, so it is tried again next run

        item = known or {"source_link": link}
        item.update({"category": category, "reason": reason, "published": published,
                     "raw_title": title, "raw_content": content})
        if not known:
            data["updates"].append(item)
            by_link[link] = item
        if category == "DISCARD":
            item["status"] = "discarded"
            continue
        process(client, item, title, content)
        added += 1
    return added


def run_reclean(client, data):
    """Rewrites every kept item under the current rules. Uses the stored raw text when
    available, otherwise the version 1 text (which is already free of the provider name)."""
    count = 0
    for item in data["updates"]:
        if item.get("category") not in ("LIVE_NOW", "COMING_SOON"):
            continue
        if item.get("status") == "published" and "--force" not in sys.argv:
            continue  # already done under version 2; resumes an interrupted clean up without paying twice
        title = item.get("raw_title") or item.get("title", "")
        content = item.get("raw_content") or item.get("content", "")
        # Re check the category under the new rules (catches SMS only updates).
        category, reason = classify(client, title, content)
        if category is None:
            print(f"[skipped] {title[:80]}: {reason}")
            continue
        item["category"], item["reason"] = category, reason
        if category == "DISCARD":
            item["status"] = "discarded"
            continue
        process(client, item, title, content)
        count += 1
    return count


def main():
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("ERROR: ANTHROPIC_API_KEY not set", file=sys.stderr)
        sys.exit(1)
    import anthropic

    client = anthropic.Anthropic()
    data = load_full()
    if "--reclean" in sys.argv:
        n = run_reclean(client, data)
        print(f"Recleaned {n} item(s).")
    else:
        n = run_daily(client, data)
        print(f"Added {n} new item(s).")
    save_full(data)
    held = sum(1 for u in data["updates"] if u.get("status") == "held")
    published = write_public(data)
    print(f"Public feed: {published} item(s). Held for review: {held}.")


if __name__ == "__main__":
    main()
