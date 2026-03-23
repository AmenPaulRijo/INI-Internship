"""
Configuration for Tata Communications Competitive Intelligence Dashboard
"""

TATA_COMMS = {
    "name": "Tata Communications",
    "ticker": "TATACOMM.NS",
    "website": "https://www.tatacommunications.com",
    "rss_feeds": [
        "https://www.tatacommunications.com/rss/news/",
    ],
    "news_queries": ["Tata Communications", "TATACOMM"],
    "color": "#003087",  # Tata blue
}

COMPETITORS = {
    "Bharti Airtel": {
        "name": "Bharti Airtel",
        "ticker": "BHARTIARTL.NS",
        "website": "https://www.airtel.in",
        "rss_feeds": [
            "https://www.airtel.in/press-release/rss",
        ],
        "news_queries": ["Bharti Airtel enterprise", "Airtel Business"],
        "color": "#E40000",
        "segment": "Telecom / Enterprise",
        "hq": "New Delhi, India",
        "focus": ["Mobile, Broadband, Enterprise, DTH"],
    },
    "Reliance Jio": {
        "name": "Reliance Jio",
        "ticker": "RELIANCE.NS",
        "website": "https://www.jio.com",
        "rss_feeds": [],
        "news_queries": ["Jio enterprise connectivity", "Reliance Jio B2B"],
        "color": "#0A2463",
        "segment": "Telecom / Cloud",
        "hq": "Mumbai, India",
        "focus": ["Connectivity, Cloud, IoT, 5G"],
    },
    "BSNL": {
        "name": "BSNL",
        "ticker": "N/A",
        "website": "https://www.bsnl.co.in",
        "rss_feeds": [],
        "news_queries": ["BSNL enterprise", "BSNL broadband"],
        "color": "#F97316",
        "segment": "Government Telecom",
        "hq": "New Delhi, India",
        "focus": ["Fixed line, Broadband, Mobile"],
    },
    "AT&T": {
        "name": "AT&T",
        "ticker": "T",
        "website": "https://www.att.com",
        "rss_feeds": [
            "https://about.att.com/rss/newsroom.xml",
        ],
        "news_queries": ["AT&T enterprise", "AT&T global connectivity"],
        "color": "#00A8E0",
        "segment": "Global Telecom",
        "hq": "Dallas, USA",
        "focus": ["Connectivity, SD-WAN, Cloud, Security"],
    },
    "Verizon Business": {
        "name": "Verizon Business",
        "ticker": "VZ",
        "website": "https://www.verizon.com/business/",
        "rss_feeds": [
            "https://www.verizon.com/about/news/rss.xml",
        ],
        "news_queries": ["Verizon Business enterprise", "Verizon enterprise connectivity"],
        "color": "#CD040B",
        "segment": "Global Telecom",
        "hq": "New York, USA",
        "focus": ["Networking, Security, Cloud, IoT"],
    },
    "NTT Ltd": {
        "name": "NTT Ltd",
        "ticker": "9432.T",
        "website": "https://hello.global.ntt",
        "rss_feeds": [],
        "news_queries": ["NTT Ltd enterprise", "NTT global network"],
        "color": "#009FE3",
        "segment": "Global IT Services",
        "hq": "Tokyo, Japan",
        "focus": ["Managed Services, Cloud, Security, Network"],
    },
    "Orange Business": {
        "name": "Orange Business",
        "ticker": "ORA.PA",
        "website": "https://www.orange-business.com",
        "rss_feeds": [],
        "news_queries": ["Orange Business Services", "Orange Business enterprise"],
        "color": "#FF6600",
        "segment": "Global Telecom",
        "hq": "Paris, France",
        "focus": ["SD-WAN, Cloud, IoT, Cybersecurity"],
    },
}

# Pricing tiers for key enterprise products (indicative/scraped)
PRODUCT_CATEGORIES = [
    "MPLS / Private WAN",
    "SD-WAN",
    "Global SIP Trunking",
    "Cloud Connectivity",
    "Managed Security",
    "IoT Connectivity",
    "Collaboration / UCaaS",
    "CDN / Edge",
]

# News RSS sources (tech/telecom industry)
INDUSTRY_RSS_FEEDS = [
    {"name": "TelecomTV", "url": "https://www.telecomtv.com/content/rss/"},
    {"name": "Light Reading", "url": "https://www.lightreading.com/rss.asp"},
    {"name": "FierceNetwork", "url": "https://www.fiercenetworks.com/rss/xml"},
    {"name": "Total Telecom", "url": "https://www.totaltele.com/rss.aspx"},
    {"name": "TechCrunch Telecom", "url": "https://techcrunch.com/tag/telecom/feed/"},
]

GNEWS_API_KEY = ""  # Optional: add GNews API key for better news coverage
NEWSAPI_KEY = ""    # Optional: add NewsAPI key
