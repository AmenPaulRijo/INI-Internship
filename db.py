# db.py - MySQL database connection and schema management

import os
import json
import logging
from datetime import datetime
from typing import Optional

from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

# ── connection config (from environment variables) ────────────────────────────
DB_CONFIG = {
    "host":     os.getenv("DB_HOST", "localhost"),
    "port":     int(os.getenv("DB_PORT", "3306")),
    "user":     os.getenv("DB_USER", ""),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "competitive_intel"),
}

_mysql_available: Optional[bool] = None  # lazy-evaluated


def is_mysql_configured() -> bool:
    """Return True only when MySQL credentials are present in the environment."""
    return bool(DB_CONFIG["user"] and DB_CONFIG["password"])


def get_connection():
    """
    Return an open mysql.connector connection.
    Raises ImportError if the driver is not installed,
    or mysql.connector.Error on connection failure.
    """
    import mysql.connector  # noqa: PLC0415
    return mysql.connector.connect(**DB_CONFIG)


def mysql_available() -> bool:
    """
    Return True if MySQL is reachable.  Result is cached for the process lifetime
    to avoid repeated connection attempts when MySQL is not configured.
    """
    global _mysql_available
    if _mysql_available is not None:
        return _mysql_available
    if not is_mysql_configured():
        _mysql_available = False
        return False
    try:
        conn = get_connection()
        conn.close()
        _mysql_available = True
    except Exception as exc:
        logger.warning("MySQL not available (%s). Falling back to JSON storage.", exc)
        _mysql_available = False
    return _mysql_available


# ── DDL ───────────────────────────────────────────────────────────────────────
_SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS news_articles (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    company       VARCHAR(120) NOT NULL,
    title         TEXT         NOT NULL,
    link          TEXT,
    published     DATETIME,
    summary       TEXT,
    source        VARCHAR(200),
    sentiment_label VARCHAR(20),
    sentiment_score FLOAT,
    fetched_at    DATETIME     DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_company (company),
    INDEX idx_published (published)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS product_launches (
    id          INT          AUTO_INCREMENT PRIMARY KEY,
    company     VARCHAR(120) NOT NULL,
    product     VARCHAR(255) NOT NULL,
    launch_date DATE,
    category    VARCHAR(100),
    description TEXT,
    impact      VARCHAR(20),
    source      VARCHAR(200),
    INDEX idx_company (company)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS pricing_data (
    id            INT          AUTO_INCREMENT PRIMARY KEY,
    company       VARCHAR(120) NOT NULL,
    product       VARCHAR(255) NOT NULL,
    pricing_model VARCHAR(200),
    entry_price   VARCHAR(100),
    price_range   VARCHAR(100),
    notes         TEXT,
    source        VARCHAR(200),
    last_updated  VARCHAR(20),
    trend         VARCHAR(20),
    updated_at    DATETIME     DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    UNIQUE KEY uq_company_product (company, product),
    INDEX idx_company (company)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS cache_entries (
    cache_key   VARCHAR(255) NOT NULL PRIMARY KEY,
    cached_at   DATETIME     NOT NULL,
    data_json   LONGTEXT
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
"""


def init_schema():
    """Create all tables if they do not exist yet."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        for statement in _SCHEMA_SQL.strip().split(";"):
            stmt = statement.strip()
            if stmt:
                cursor.execute(stmt)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


# ── news articles ─────────────────────────────────────────────────────────────

def upsert_news_articles(company: str, articles: list):
    """
    Insert news articles for *company* into the database.
    Duplicate titles for the same company are skipped (INSERT IGNORE).
    """
    if not articles:
        return
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT IGNORE INTO news_articles
                (company, title, link, published, summary, source,
                 sentiment_label, sentiment_score, fetched_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
        """
        rows = []
        for art in articles:
            sentiment = art.get("sentiment") or {}
            published = None
            raw_pub = art.get("published", "")
            if raw_pub:
                try:
                    published = datetime.fromisoformat(raw_pub)
                except ValueError:
                    pass
            rows.append((
                company,
                art.get("title", "")[:500],
                art.get("link", "")[:2000],
                published,
                (art.get("summary") or "")[:1000],
                (art.get("source") or "")[:200],
                sentiment.get("label", "Neutral"),
                float(sentiment.get("score", 0.0)),
                datetime.now(),
            ))
        cursor.executemany(sql, rows)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def fetch_news_articles(company: Optional[str] = None) -> dict:
    """
    Return news articles as ``{company: [article_dict, …]}``.
    Pass *company* to restrict to a single company.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        if company:
            cursor.execute(
                "SELECT * FROM news_articles WHERE company = %s ORDER BY published DESC",
                (company,),
            )
        else:
            cursor.execute("SELECT * FROM news_articles ORDER BY published DESC")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    result: dict = {}
    for row in rows:
        company_name = row["company"]
        article = {
            "title":     row["title"],
            "link":      row["link"],
            "published": row["published"].isoformat() if row["published"] else "",
            "summary":   row["summary"],
            "source":    row["source"],
            "sentiment": {
                "label": row["sentiment_label"],
                "score": row["sentiment_score"],
            },
        }
        result.setdefault(company_name, []).append(article)
    return result


def get_news_fetched_at() -> Optional[datetime]:
    """Return the most recent ``fetched_at`` timestamp across all articles."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(fetched_at) FROM news_articles")
        row = cursor.fetchone()
        return row[0] if row and row[0] else None
    finally:
        cursor.close()
        conn.close()


# ── product launches ──────────────────────────────────────────────────────────

def upsert_product_launches(launches: list):
    """Insert product launch records, ignoring exact duplicates."""
    if not launches:
        return
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT IGNORE INTO product_launches
                (company, product, launch_date, category, description, impact, source)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        """
        rows = []
        for launch in launches:
            date_val = None
            raw_date = launch.get("date", "")
            if raw_date:
                try:
                    date_val = datetime.strptime(raw_date, "%Y-%m-%d").date()
                except ValueError:
                    pass
            rows.append((
                launch.get("company", "")[:120],
                launch.get("product", "")[:255],
                date_val,
                (launch.get("category") or "")[:100],
                (launch.get("description") or "")[:1000],
                (launch.get("impact") or "")[:20],
                (launch.get("source") or "")[:200],
            ))
        cursor.executemany(sql, rows)
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def fetch_product_launches() -> list:
    """Return all product launches as a list of dicts."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM product_launches ORDER BY launch_date DESC")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    launches = []
    for row in rows:
        launches.append({
            "company":     row["company"],
            "product":     row["product"],
            "date":        row["launch_date"].isoformat() if row["launch_date"] else "",
            "category":    row["category"],
            "description": row["description"],
            "impact":      row["impact"],
            "source":      row["source"],
        })
    return launches


# ── pricing data ──────────────────────────────────────────────────────────────

def upsert_pricing_data(pricing: dict):
    """
    Upsert pricing records from the nested ``{company: {product: details}}`` dict
    used throughout the application.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO pricing_data
                (company, product, pricing_model, entry_price, price_range,
                 notes, source, last_updated, trend)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE
                pricing_model = VALUES(pricing_model),
                entry_price   = VALUES(entry_price),
                price_range   = VALUES(price_range),
                notes         = VALUES(notes),
                source        = VALUES(source),
                last_updated  = VALUES(last_updated),
                trend         = VALUES(trend),
                updated_at    = CURRENT_TIMESTAMP
        """
        rows = []
        for company, products in pricing.items():
            if company == "last_updated" or not isinstance(products, dict):
                continue
            for product, details in products.items():
                if not isinstance(details, dict):
                    continue
                rows.append((
                    company[:120],
                    product[:255],
                    (details.get("model") or "")[:200],
                    (details.get("entry_price") or "")[:100],
                    (details.get("price_range") or "")[:100],
                    (details.get("notes") or "")[:1000],
                    (details.get("source") or "")[:200],
                    (details.get("last_updated") or "")[:20],
                    (details.get("trend") or "stable")[:20],
                ))
        if rows:
            cursor.executemany(sql, rows)
            conn.commit()
    finally:
        cursor.close()
        conn.close()


def fetch_pricing_data() -> dict:
    """
    Return pricing data in the nested ``{company: {product: details}}`` format
    expected by the rest of the application.
    """
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM pricing_data ORDER BY company, product")
        rows = cursor.fetchall()
    finally:
        cursor.close()
        conn.close()

    result: dict = {"last_updated": datetime.now().isoformat()}
    for row in rows:
        company = row["company"]
        product = row["product"]
        result.setdefault(company, {})[product] = {
            "model":        row["pricing_model"],
            "entry_price":  row["entry_price"],
            "price_range":  row["price_range"],
            "notes":        row["notes"],
            "source":       row["source"],
            "last_updated": row["last_updated"],
            "trend":        row["trend"],
        }
    return result


# ── cache entries ─────────────────────────────────────────────────────────────

def set_cache_entry(key: str, data):
    """Persist an arbitrary JSON-serialisable value under *key*."""
    conn = get_connection()
    try:
        cursor = conn.cursor()
        sql = """
            INSERT INTO cache_entries (cache_key, cached_at, data_json)
            VALUES (%s, %s, %s)
            ON DUPLICATE KEY UPDATE
                cached_at = VALUES(cached_at),
                data_json = VALUES(data_json)
        """
        cursor.execute(sql, (key, datetime.now(), json.dumps(data)))
        conn.commit()
    finally:
        cursor.close()
        conn.close()


def get_cache_entry(key: str) -> Optional[dict]:
    """Return ``{"cached_at": datetime, "data": …}`` or *None* if missing."""
    conn = get_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT cached_at, data_json FROM cache_entries WHERE cache_key = %s",
            (key,),
        )
        row = cursor.fetchone()
    finally:
        cursor.close()
        conn.close()

    if not row:
        return None
    return {
        "cached_at": row["cached_at"],
        "data":      json.loads(row["data_json"]) if row["data_json"] else None,
    }
