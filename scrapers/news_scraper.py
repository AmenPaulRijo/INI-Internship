# scrapers/news_scraper.py

import feedparser
import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import random
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from competitors import NEWS_KEYWORDS

GNEWS_RSS = "https://news.google.com/rss/search?q={query}&hl=en-IN&gl=IN&ceid=IN:en"


def scrape_google_news_rss(query: str, max_items: int = 10) -> list:
    url = GNEWS_RSS.format(query=requests.utils.quote(query))
    articles = []
    try:
        feed = feedparser.parse(url)
        for entry in feed.entries[:max_items]:
            published = datetime.now().isoformat()
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                published = datetime(*entry.published_parsed[:6]).isoformat()
            articles.append({
                "title":   entry.get("title", ""),
                "link":    entry.get("link", ""),
                "published": published,
                "summary": BeautifulSoup(entry.get("summary", ""), "html.parser").get_text()[:300],
                "source":  entry.get("source", {}).get("title", "Google News"),
            })
        time.sleep(0.1)
    except Exception as e:
        print(f"[RSS] Error fetching '{query}': {e}")
    return articles


def scrape_all_news() -> dict:
    """Returns a dict: { company_name: [articles...] }"""
    all_news = {}

    for company_name, keywords in NEWS_KEYWORDS.items():
        print(f"  -> Fetching news for {company_name}...")
        company_articles = []
        for keyword in keywords[:2]:
            articles = scrape_google_news_rss(keyword, max_items=8)
            company_articles.extend(articles)
            time.sleep(random.uniform(0.5, 1.5))

        # Deduplicate by title
        seen, unique = set(), []
        for a in company_articles:
            if a["title"] not in seen:
                seen.add(a["title"])
                unique.append(a)

        all_news[company_name] = unique[:12]

    total = sum(len(v) for v in all_news.values())
    print(f"[NewsScraper] Total articles: {total}")
    return all_news  # always a dict