# scrapers/pricing_tracker.py
# Tracks & stores competitor pricing signals from public web sources.
# Since telecom enterprise pricing is mostly quote-based, this module:
#   1. Scrapes publicly listed pricing pages where available
#   2. Maintains a manually-editable pricing database (JSON)
#   3. Tracks pricing mentions in news articles
#   4. Generates pricing intelligence reports

import json
import os
import re
import sys
import requests
from bs4 import BeautifulSoup
from datetime import datetime

# Ensure the project root is on the path so `db` is importable when this
# module is loaded from a subdirectory (e.g. scrapers/).
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import db  # noqa: E402

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
PRICING_FILE = os.path.join(DATA_DIR, "pricing_data.json")

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
    )
}

# Default pricing intelligence database
DEFAULT_PRICING = {
    "last_updated": datetime.now().isoformat(),
    "Tata Communications": {
        "SD-WAN (IZO)": {
            "model": "Subscription + PoP-based",
            "entry_price": "Custom quote",
            "price_range": "₹15K–₹2L/mo",
            "notes": "Tiered by bandwidth & PoP count. Global coverage premium.",
            "source": "Sales materials",
            "last_updated": "2024-Q4",
            "trend": "stable",
        },
        "IZO Multi Cloud Connect": {
            "model": "Pay-per-use + committed",
            "entry_price": "Custom quote",
            "price_range": "₹20K–₹5L/mo",
            "notes": "Connects to AWS, Azure, GCP. Port speeds 100M–10G.",
            "source": "Partner portal",
            "last_updated": "2024-Q4",
            "trend": "decreasing",
        },
        "MOVE IoT Platform": {
            "model": "Per-device SIM subscription",
            "entry_price": "$0.50/device/mo",
            "price_range": "$0.50–$5/device/mo",
            "notes": "Volume discounts at 10K+ devices. 600+ network roaming.",
            "source": "Public datasheet",
            "last_updated": "2024-Q3",
            "trend": "decreasing",
        },
        "Cyber Security (MDR)": {
            "model": "Annual subscription",
            "entry_price": "₹25L/yr",
            "price_range": "₹25L–₹2Cr/yr",
            "notes": "Includes SOC monitoring, incident response.",
            "source": "RFP documents",
            "last_updated": "2024-Q4",
            "trend": "increasing",
        },
    },
    "Bharti Airtel": {
        "SD-WAN": {
            "model": "Managed service subscription",
            "entry_price": "Custom quote",
            "price_range": "₹12K–₹1.5L/mo",
            "notes": "Strong India coverage. CPE included.",
            "source": "Industry reports",
            "last_updated": "2024-Q4",
            "trend": "stable",
        },
        "Airtel Cloud": {
            "model": "IaaS pay-as-you-go",
            "entry_price": "₹5/vCPU/hr",
            "price_range": "₹5–₹50/vCPU/hr",
            "notes": "India-specific DCs, competitive to AWS/Azure for local.",
            "source": "Public pricing",
            "last_updated": "2024-Q4",
            "trend": "decreasing",
        },
    },
    "Reliance Jio": {
        "JioFiber Enterprise": {
            "model": "Fixed monthly",
            "entry_price": "₹8,000/mo",
            "price_range": "₹8K–₹80K/mo",
            "notes": "Aggressive pricing. Disrupting SMB segment.",
            "source": "Public website",
            "last_updated": "2024-Q4",
            "trend": "decreasing",
        },
        "JioBusiness Cloud": {
            "model": "Subscription",
            "entry_price": "Custom",
            "price_range": "Custom",
            "notes": "Bundled with connectivity offerings.",
            "source": "Sales channels",
            "last_updated": "2024-Q3",
            "trend": "stable",
        },
    },
    "AT&T": {
        "AT&T SD-WAN": {
            "model": "Managed service",
            "entry_price": "$800/site/mo",
            "price_range": "$800–$5,000/site/mo",
            "notes": "US-centric. Strong in Fortune 500.",
            "source": "Gartner reports",
            "last_updated": "2024-Q4",
            "trend": "stable",
        },
        "AT&T Business Fiber": {
            "model": "Monthly subscription",
            "entry_price": "$75/mo",
            "price_range": "$75–$500/mo",
            "notes": "Up to 5Gbps for enterprise.",
            "source": "Public pricing",
            "last_updated": "2024-Q4",
            "trend": "stable",
        },
    },
    "Verizon Business": {
        "Verizon SD-WAN": {
            "model": "Managed service",
            "entry_price": "$1,000/site/mo",
            "price_range": "$1K–$6K/site/mo",
            "notes": "Premium pricing. Best-in-class SLA.",
            "source": "IDC reports",
            "last_updated": "2024-Q4",
            "trend": "stable",
        },
        "ThingSpace IoT": {
            "model": "Per-device",
            "entry_price": "$1/device/mo",
            "price_range": "$0.80–$8/device/mo",
            "notes": "Strong US coverage. Limited global footprint.",
            "source": "Public pricing",
            "last_updated": "2024-Q4",
            "trend": "decreasing",
        },
    },
    "BT Group": {
        "BT SD-WAN": {
            "model": "Managed service",
            "entry_price": "£900/site/mo",
            "price_range": "£900–£4,500/site/mo",
            "notes": "EMEA strength. Cisco/VMware partnerships.",
            "source": "Partner disclosures",
            "last_updated": "2024-Q4",
            "trend": "stable",
        },
    },
    "NTT Ltd": {
        "Managed SD-WAN": {
            "model": "Managed service",
            "entry_price": "$900/site/mo",
            "price_range": "$900–$4,000/site/mo",
            "notes": "Strong APAC presence. Global reach.",
            "source": "NTT annual report",
            "last_updated": "2024-Q4",
            "trend": "stable",
        },
    },
}


def load_pricing_data() -> dict:
    if db.mysql_available():
        data = db.fetch_pricing_data()
        if len(data) > 1:  # has at least one company besides "last_updated"
            return data
        # Seed the database with defaults on first run
        db.upsert_pricing_data(DEFAULT_PRICING)
        return DEFAULT_PRICING

    os.makedirs(DATA_DIR, exist_ok=True)
    if os.path.exists(PRICING_FILE):
        with open(PRICING_FILE, "r") as f:
            return json.load(f)
    else:
        save_pricing_data(DEFAULT_PRICING)
        return DEFAULT_PRICING


def save_pricing_data(data: dict):
    if db.mysql_available():
        db.upsert_pricing_data(data)
        return

    os.makedirs(DATA_DIR, exist_ok=True)
    data["last_updated"] = datetime.now().isoformat()
    with open(PRICING_FILE, "w") as f:
        json.dump(data, f, indent=2)


def get_pricing_dataframe():
    """Return pricing data as flat records for display."""
    import pandas as pd
    pricing = load_pricing_data()
    rows = []
    for company, products in pricing.items():
        if company == "last_updated":
            continue
        if isinstance(products, dict):
            for product, details in products.items():
                if isinstance(details, dict):
                    rows.append(
                        {
                            "Company": company,
                            "Product/Service": product,
                            "Pricing Model": details.get("model", ""),
                            "Entry Price": details.get("entry_price", ""),
                            "Price Range": details.get("price_range", ""),
                            "Notes": details.get("notes", ""),
                            "Source": details.get("source", ""),
                            "Last Updated": details.get("last_updated", ""),
                            "Trend": details.get("trend", "stable"),
                        }
                    )
    return pd.DataFrame(rows)


def extract_pricing_mentions(articles: list) -> list:
    """Extract pricing-related keywords from news articles."""
    price_patterns = [
        r"\$[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B|K))?",
        r"₹[\d,]+(?:\.\d+)?(?:\s*(?:crore|lakh|K|L|Cr))?",
        r"£[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B))?",
        r"€[\d,]+(?:\.\d+)?(?:\s*(?:million|billion|M|B))?",
        r"\b\d+(?:\.\d+)?%\s+(?:discount|reduction|increase|growth|off)\b",
        r"\bfree\s+(?:trial|tier|plan)\b",
        r"\bpricing\b",
        r"\bsubscription\b",
    ]

    results = []
    for article in articles:
        text = f"{article.get('title', '')} {article.get('summary', '')}"
        mentions = []
        for pattern in price_patterns:
            found = re.findall(pattern, text, re.IGNORECASE)
            mentions.extend(found)
        if mentions:
            results.append(
                {
                    "title": article.get("title", ""),
                    "link": article.get("link", ""),
                    "published": article.get("published", ""),
                    "price_mentions": mentions[:5],
                }
            )
    return results
