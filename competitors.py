# competitors.py - Competitor configuration for Tata Communications

TATA_PROFILE = {
    "name": "Tata Communications",
    "ticker": "TATACOMM.NS",
    "website": "https://www.tatacommunications.com",
    "description": "Global digital infrastructure provider",
    "rss_feeds": [
        "https://www.tatacommunications.com/feed/",
    ],
    "color": "#0033A0",
    "products": [
        "IZO Multi Cloud Connect",
        "MOVE Platform",
        "GlobalRapide",
        "IZO Internet WAN",
        "Tata Communications DIGO",
        "Cyber Security Services",
    ],
}

COMPETITORS = {
    "Bharti Airtel": {
        "ticker": "BHARTIARTL.NS",
        "website": "https://www.airtel.in",
        "rss_feeds": [
            "https://www.airtel.in/press-release/rss",
        ],
        "color": "#ED1C24",
        "segment": "Telecom / Enterprise",
        "hq": "India",
        "products": ["Airtel IQ", "Smart Bytes", "SD-WAN", "Airtel Cloud"],
    },
    "Reliance Jio": {
        "ticker": "RELIANCE.NS",
        "website": "https://www.jio.com",
        "rss_feeds": [],
        "color": "#0F4C81",
        "segment": "Telecom / Consumer & Enterprise",
        "hq": "India",
        "products": ["JioFiber", "JioBusiness", "Jio Cloud", "JioMeet"],
    },
    "AT&T": {
        "ticker": "T",
        "website": "https://www.att.com",
        "rss_feeds": [
            "https://about.att.com/newsroom/rss",
        ],
        "color": "#00A8E0",
        "segment": "Global Telecom",
        "hq": "USA",
        "products": ["AT&T Business Fiber", "AT&T SD-WAN", "AT&T Cybersecurity"],
    },
    "Verizon Business": {
        "ticker": "VZ",
        "website": "https://www.verizon.com/business/",
        "rss_feeds": [
            "https://www.verizon.com/about/news/rss.xml",
        ],
        "color": "#CD040B",
        "segment": "Global Telecom",
        "hq": "USA",
        "products": ["Verizon SD-WAN", "ThingSpace", "BlueJeans", "MEC"],
    },
    "BT Group": {
        "ticker": "BT-A.L",
        "website": "https://www.bt.com",
        "rss_feeds": [
            "https://newsroom.bt.com/feed/",
        ],
        "color": "#5514B4",
        "segment": "Global Telecom",
        "hq": "UK",
        "products": ["BT Cloud", "BT Managed SD-WAN", "BT Security"],
    },
    "NTT Ltd": {
        "ticker": "9432.T",
        "website": "https://www.ntt.com",
        "rss_feeds": [
            "https://www.ntt.com/en/news/rss.xml",
        ],
        "color": "#009FE3",
        "segment": "Global Telecom / IT Services",
        "hq": "Japan",
        "products": ["NTT Smart World", "Nexcenter", "Managed SD-WAN"],
    },
}

# News search keywords for each competitor
NEWS_KEYWORDS = {
    "Tata Communications": ["Tata Communications", "TATACOMM", "IZO cloud", "MOVE platform"],
    "Bharti Airtel": ["Airtel enterprise", "Bharti Airtel business"],
    "Reliance Jio": ["Jio enterprise", "JioBusiness", "Reliance Jio B2B"],
    "AT&T": ["AT&T business", "AT&T enterprise network"],
    "Verizon Business": ["Verizon Business", "Verizon enterprise"],
    "BT Group": ["BT enterprise", "BT global services"],
    "NTT Ltd": ["NTT enterprise", "NTT global network"],
}

# Market segments for competitive mapping
MARKET_SEGMENTS = [
    "SD-WAN",
    "Cloud Connectivity",
    "IoT / MOVE",
    "Cybersecurity",
    "UCaaS / Collaboration",
    "Data Center / Colocation",
    "Managed Services",
]
