# data_manager.py - Handles caching and data persistence
# Supports MySQL (primary) with automatic fallback to JSON file storage.

import json
import os
from datetime import datetime, timedelta
from typing import Optional

import db

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
CACHE_FILE = os.path.join(DATA_DIR, "cache.json")
NEWS_FILE = os.path.join(DATA_DIR, "news_data.json")
PRODUCTS_FILE = os.path.join(DATA_DIR, "products_data.json")
CACHE_EXPIRY_HOURS = 6  # Re-fetch news every 6 hours


def ensure_data_dir():
    os.makedirs(DATA_DIR, exist_ok=True)


# ── JSON-backed cache helpers (used as fallback) ──────────────────────────────

def _load_json_cache() -> dict:
    ensure_data_dir()
    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as f:
            return json.load(f)
    return {}


def _save_json_cache(cache: dict):
    ensure_data_dir()
    with open(CACHE_FILE, "w") as f:
        json.dump(cache, f, indent=2)


# ── public cache API ──────────────────────────────────────────────────────────

def is_cache_fresh(key: str, hours: int = CACHE_EXPIRY_HOURS) -> bool:
    if db.mysql_available():
        entry = db.get_cache_entry(key)
        if not entry:
            return False
        cached_time = entry["cached_at"]
        if isinstance(cached_time, str):
            cached_time = datetime.fromisoformat(cached_time)
        return datetime.now() - cached_time < timedelta(hours=hours)

    cache = _load_json_cache()
    if key not in cache:
        return False
    ts = cache[key].get("timestamp")
    if not ts:
        return False
    cached_time = datetime.fromisoformat(ts)
    return datetime.now() - cached_time < timedelta(hours=hours)


def get_cached_data(key: str) -> Optional[dict]:
    if db.mysql_available():
        entry = db.get_cache_entry(key)
        return entry["data"] if entry else None

    cache = _load_json_cache()
    return cache[key].get("data") if key in cache else None


def set_cached_data(key: str, data):
    if db.mysql_available():
        db.set_cache_entry(key, data)
        return

    cache = _load_json_cache()
    cache[key] = {"timestamp": datetime.now().isoformat(), "data": data}
    _save_json_cache(cache)


# ── news data ─────────────────────────────────────────────────────────────────

def save_news_data(news_data: dict):
    if db.mysql_available():
        for company, articles in news_data.items():
            db.upsert_news_articles(company, articles)
        db.set_cache_entry("news", {"fetched_at": datetime.now().isoformat()})
        return

    ensure_data_dir()
    payload = {"fetched_at": datetime.now().isoformat(), "news": news_data}
    with open(NEWS_FILE, "w") as f:
        json.dump(payload, f, indent=2)
    set_cached_data("news", {"fetched_at": payload["fetched_at"]})


def load_news_data() -> Optional[dict]:
    if db.mysql_available():
        data = db.fetch_news_articles()
        return data if data else None

    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, "r") as f:
            payload = json.load(f)
            return payload.get("news", {})
    return None


def get_news_age() -> str:
    if db.mysql_available():
        fetched_at = db.get_news_fetched_at()
        if fetched_at:
            delta = datetime.now() - fetched_at
            if delta.seconds < 3600 and delta.days == 0:
                return f"{delta.seconds // 60} minutes ago"
            elif delta.days == 0:
                return f"{delta.seconds // 3600} hours ago"
            else:
                return f"{delta.days} days ago"
        return "Never"

    if os.path.exists(NEWS_FILE):
        with open(NEWS_FILE, "r") as f:
            payload = json.load(f)
            fetched_at = payload.get("fetched_at")
            if fetched_at:
                dt = datetime.fromisoformat(fetched_at)
                delta = datetime.now() - dt
                if delta.seconds < 3600 and delta.days == 0:
                    return f"{delta.seconds // 60} minutes ago"
                elif delta.days == 0:
                    return f"{delta.seconds // 3600} hours ago"
                else:
                    return f"{delta.days} days ago"
    return "Never"


# Mock product launches data (would be scraped in production)
MOCK_PRODUCT_LAUNCHES = [
    {
        "company": "Tata Communications",
        "product": "IZO Internet WAN 2.0",
        "date": "2024-11-15",
        "category": "SD-WAN",
        "description": "Enhanced SD-WAN with AI-driven traffic optimization and 99.99% SLA",
        "impact": "High",
        "source": "Press Release",
    },
    {
        "company": "Tata Communications",
        "product": "DIGO Platform v3",
        "date": "2024-10-20",
        "category": "Digital Platform",
        "description": "New self-service portal with real-time analytics and automated provisioning",
        "impact": "Medium",
        "source": "Blog Post",
    },
    {
        "company": "Bharti Airtel",
        "product": "Airtel IQ Voice 2.0",
        "date": "2024-12-01",
        "category": "UCaaS",
        "description": "Cloud communication platform with AI-powered call analytics",
        "impact": "High",
        "source": "Press Release",
    },
    {
        "company": "Bharti Airtel",
        "product": "Smart Bytes Enterprise",
        "date": "2024-10-10",
        "category": "Cloud",
        "description": "New enterprise data management and analytics solution",
        "impact": "Medium",
        "source": "Announcement",
    },
    {
        "company": "Reliance Jio",
        "product": "JioAirFiber Enterprise",
        "date": "2024-11-28",
        "category": "Connectivity",
        "description": "5G Fixed Wireless Access targeting SMBs with competitive pricing",
        "impact": "High",
        "source": "Official Launch",
    },
    {
        "company": "AT&T",
        "product": "AT&T MEC Solutions",
        "date": "2024-11-05",
        "category": "Edge Computing",
        "description": "Multi-access Edge Computing for manufacturing and retail verticals",
        "impact": "Medium",
        "source": "Analyst Briefing",
    },
    {
        "company": "Verizon Business",
        "product": "BlueJeans AI Studio",
        "date": "2024-10-25",
        "category": "UCaaS",
        "description": "AI-powered video conferencing with real-time transcription",
        "impact": "Medium",
        "source": "Product Blog",
    },
    {
        "company": "BT Group",
        "product": "BT Managed SASE",
        "date": "2024-12-10",
        "category": "Cybersecurity",
        "description": "Integrated SASE platform combining SD-WAN and cloud security",
        "impact": "High",
        "source": "Press Release",
    },
    {
        "company": "NTT Ltd",
        "product": "NTT Smart World Edge",
        "date": "2024-11-18",
        "category": "Edge Computing",
        "description": "Distributed edge infrastructure for latency-sensitive applications",
        "impact": "Medium",
        "source": "Announcement",
    },
    {
        "company": "Tata Communications",
        "product": "GlobalRapide Enhanced",
        "date": "2024-09-30",
        "category": "Cloud Connectivity",
        "description": "Ultra-low latency financial market data network expansion to 15 new PoPs",
        "impact": "High",
        "source": "Press Release",
    },
    {
        "company": "Tata Communications",
        "product": "MOVE 5G IoT Module",
        "date": "2024-08-15",
        "category": "IoT",
        "description": "5G-enabled IoT connectivity solution with global eSIM management",
        "impact": "High",
        "source": "Product Launch",
    },
    {
        "company": "Bharti Airtel",
        "product": "Airtel 5G Enterprise Private Network",
        "date": "2024-09-05",
        "category": "5G",
        "description": "Private 5G network deployment for manufacturing and logistics",
        "impact": "High",
        "source": "Press Release",
    },
]


def load_product_launches() -> list:
    if db.mysql_available():
        rows = db.fetch_product_launches()
        if rows:
            return rows
        # Seed the database with defaults on first run
        db.upsert_product_launches(MOCK_PRODUCT_LAUNCHES)
        return MOCK_PRODUCT_LAUNCHES

    if os.path.exists(PRODUCTS_FILE):
        with open(PRODUCTS_FILE, "r") as f:
            return json.load(f)
    # Save defaults to JSON
    ensure_data_dir()
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(MOCK_PRODUCT_LAUNCHES, f, indent=2)
    return MOCK_PRODUCT_LAUNCHES


def save_product_launches(launches: list):
    if db.mysql_available():
        db.upsert_product_launches(launches)
        return

    ensure_data_dir()
    with open(PRODUCTS_FILE, "w") as f:
        json.dump(launches, f, indent=2)
