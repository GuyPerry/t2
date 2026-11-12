"""
Breaking Science & Tech News Agent
-----------------------------------
Runs every hour, fetches RSS feeds, uses AI to pick the top 3 highest-impact
worldwide science & technology stories, then posts them to the CAP news service.
"""

import os
import json
import time
import logging
import schedule
import feedparser
import requests
from datetime import datetime, timezone
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# ── Configuration ──────────────────────────────────────────────────────────────
NEWS_SERVICE_URL = os.getenv("NEWS_SERVICE_URL", "http://localhost:4004/api")
OPENAI_API_KEY   = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL     = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
TOP_N            = int(os.getenv("TOP_N", "3"))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)
log = logging.getLogger(__name__)

# ── RSS Feed Sources (Science & Technology) ────────────────────────────────────
RSS_FEEDS = [
    # Science
    {"url": "https://feeds.nature.com/nature/rss/current",        "source": "Nature"},
    {"url": "https://www.sciencedaily.com/rss/top/science.xml",   "source": "ScienceDaily"},
    {"url": "https://rss.sciencemag.org/rss/news_current.xml",    "source": "Science Magazine"},
    # Technology
    {"url": "https://feeds.arstechnica.com/arstechnica/index",    "source": "Ars Technica"},
    {"url": "https://www.wired.com/feed/rss",                     "source": "WIRED"},
    {"url": "https://techcrunch.com/feed/",                       "source": "TechCrunch"},
    # Space & General Science
    {"url": "https://www.nasa.gov/rss/dyn/breaking_news.rss",     "source": "NASA"},
    {"url": "https://phys.org/rss-feed/breaking/",                "source": "Phys.org"},
    {"url": "https://www.newscientist.com/feed/home/",            "source": "New Scientist"},
]


def fetch_articles() -> list[dict]:
    """Fetch raw articles from all RSS feeds."""
    articles = []
    for feed_cfg in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_cfg["url"])
            for entry in feed.entries[:8]:  # take up to 8 per feed
                published = entry.get("published", "") or entry.get("updated", "")
                articles.append({
                    "headline":    entry.get("title", "").strip(),
                    "url":         entry.get("link", ""),
                    "summary_raw": entry.get("summary", entry.get("description", ""))[:800],
                    "published":   published,
                    "source":      feed_cfg["source"],
                })
        except Exception as exc:
            log.warning("Failed to fetch %s: %s", feed_cfg["source"], exc)

    log.info("Fetched %d raw articles from %d feeds", len(articles), len(RSS_FEEDS))
    return articles


def select_top_stories(articles: list[dict]) -> list[dict]:
    """
    Use AI to pick the top 3 highest-impact worldwide science & tech stories
    and return structured data with impact scores and cleaned summaries.
    """
    if not articles:
        log.warning("No articles to process")
        return []

    if not OPENAI_API_KEY:
        log.warning("OPENAI_API_KEY not set — returning first %d articles without AI ranking", TOP_N)
        return _fallback_selection(articles)

    client = OpenAI(api_key=OPENAI_API_KEY)

    # Build a compact list for the prompt
    articles_text = "\n".join(
        f"[{i}] SOURCE: {a['source']} | HEADLINE: {a['headline']} | SUMMARY: {a['summary_raw'][:300]}"
        for i, a in enumerate(articles)
    )

    prompt = f"""You are a science and technology news editor for a global audience.

From the list below, select exactly {TOP_N} stories that represent the BIGGEST, most impactful,
worldwide-relevant breaking science or technology events. Prioritise:
- Major scientific discoveries or breakthroughs with global significance
- Critical technology events affecting millions of people worldwide
- Space exploration milestones
- AI/computing advances with significant societal impact

For each selected story return a JSON array with exactly {TOP_N} objects.
Each object MUST have these fields:
  "index"       : (int) the [index] from the list
  "headline"    : (string) clean, concise headline (max 120 chars)
  "summary"     : (string) 2–3 sentence factual summary written for a general audience (max 300 chars)
  "impactScore" : (int) 1–10 global importance score (8–10 = critical/breakthrough)

Return ONLY the raw JSON array, no markdown, no explanation.

ARTICLES:
{articles_text}
"""

    try:
        response = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=1200
        )
        raw = response.choices[0].message.content.strip()
        # Strip markdown code fences if present
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        selected = json.loads(raw)
    except Exception as exc:
        log.error("AI selection failed: %s", exc)
        return _fallback_selection(articles)

    result = []
    for item in selected[:TOP_N]:
        idx = item.get("index", 0)
        original = articles[idx] if idx < len(articles) else articles[0]
        result.append({
            "headline":    item.get("headline", original["headline"]),
            "summary":     item.get("summary", original["summary_raw"][:300]),
            "source":      original["source"],
            "url":         original["url"],
            "publishedAt": _parse_date(original["published"]),
            "category":    "Science & Technology",
            "impactScore": int(item.get("impactScore", 7))
        })

    log.info("AI selected %d top stories", len(result))
    return result


def _fallback_selection(articles: list[dict]) -> list[dict]:
    """Simple fallback when AI is unavailable: return first TOP_N articles."""
    return [
        {
            "headline":    a["headline"],
            "summary":     a["summary_raw"][:300],
            "source":      a["source"],
            "url":         a["url"],
            "publishedAt": _parse_date(a["published"]),
            "category":    "Science & Technology",
            "impactScore": 7
        }
        for a in articles[:TOP_N]
    ]


def _parse_date(raw: str) -> str:
    """Return an ISO-8601 datetime string, defaulting to now."""
    if not raw:
        return datetime.now(timezone.utc).isoformat()
    try:
        import email.utils
        t = email.utils.parsedate_to_datetime(raw)
        return t.isoformat()
    except Exception:
        return datetime.now(timezone.utc).isoformat()


def post_to_service(items: list[dict]) -> bool:
    """POST the selected news items to the CAP service via the ingestNews action."""
    if not items:
        log.info("Nothing to post")
        return True

    url = f"{NEWS_SERVICE_URL}/ingestNews"
    payload = {"items": items}
    headers = {"Content-Type": "application/json"}

    try:
        resp = requests.post(url, json=payload, headers=headers, timeout=15)
        resp.raise_for_status()
        log.info("Successfully ingested %d items. Response: %s", len(items), resp.text[:200])
        return True
    except requests.RequestException as exc:
        log.error("Failed to post to news service: %s", exc)
        return False


def run_cycle():
    """One full agent cycle: fetch → rank → post."""
    log.info("═" * 60)
    log.info("Starting news fetch cycle at %s", datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    articles = fetch_articles()
    top_stories = select_top_stories(articles)
    success = post_to_service(top_stories)

    if success:
        log.info("Cycle complete — posted %d stories", len(top_stories))
        for i, s in enumerate(top_stories, 1):
            log.info("  [%d] (%d/10) %s", i, s.get("impactScore", 0), s.get("headline", ""))
    else:
        log.error("Cycle failed — stories were not saved")
    log.info("═" * 60)


if __name__ == "__main__":
    log.info("🔬 Breaking Science & Tech News Agent starting…")
    log.info("Target service : %s", NEWS_SERVICE_URL)
    log.info("Top N stories  : %d", TOP_N)
    log.info("AI model       : %s", OPENAI_MODEL if OPENAI_API_KEY else "DISABLED (no API key)")

    # Run once immediately on startup
    run_cycle()

    # Then schedule every hour
    schedule.every().hour.do(run_cycle)
    log.info("Scheduled: running every hour. Press Ctrl+C to stop.")

    while True:
        schedule.run_pending()
        time.sleep(30)
