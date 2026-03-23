# 🔭 Tata Communications — Competitive Intelligence Dashboard

A production-grade competitive intelligence platform built with Python + Streamlit.
Tracks competitors, pricing signals, product launches, and news sentiment in real time.

---

## 🗂️ Project Structure

```
tata_competitive_intel/
├── app.py                    ← Main Streamlit dashboard (launch this)
├── competitors.py            ← Competitor config (add/edit competitors here)
├── data_manager.py           ← Data persistence & caching layer
├── requirements.txt          ← All Python dependencies
├── setup_and_run.sh          ← One-click setup & launch script (Mac/Linux)
├── scrapers/
│   ├── news_scraper.py       ← Google News RSS + competitor RSS scraping
│   ├── sentiment_analyzer.py ← TextBlob NLP sentiment analysis
│   └── pricing_tracker.py    ← Pricing database + web extraction
└── data/                     ← Auto-created; stores JSON cache files
    ├── news_data.json
    ├── pricing_data.json
    └── products_data.json
```

---

## 🚀 Quick Start

### Option A — One command (Mac/Linux)
```bash
cd tata_competitive_intel
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Option B — Manual setup
```bash
cd tata_competitive_intel

# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK data
python3 -c "import nltk; nltk.download('punkt'); nltk.download('vader_lexicon')"

# 4. Launch dashboard
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 📊 Dashboard Tabs

| Tab | What it shows |
|-----|--------------|
| **📊 Overview** | KPI summary, sentiment bar chart, news volume |
| **📰 News Feed** | Live news from Google News RSS, searchable & filterable |
| **💬 Sentiment** | Polarity/subjectivity scatter, timeline, score breakdown |
| **💰 Pricing Intel** | Pricing database, model distribution, trend analysis |
| **🚀 Product Launches** | Timeline of competitor launches, category heatmap |
| **🕸️ Radar** | Multi-dimensional competitive positioning spider chart |

---

## ⚙️ Configuration

### Adding/removing competitors
Edit `competitors.py`:
```python
COMPETITORS["New Company"] = {
    "ticker": "TICKER",
    "website": "https://...",
    "rss_feeds": ["https://.../feed"],
    "color": "#FF0000",
    "segment": "Cloud / SaaS",
    "hq": "Country",
    "products": ["Product A", "Product B"],
}
```

### Adding news search keywords
In `competitors.py`:
```python
NEWS_KEYWORDS["New Company"] = ["keyword 1", "keyword 2"]
```

### Updating pricing data
Edit `data/pricing_data.json` directly, or reset by deleting it (defaults reload from `scrapers/pricing_tracker.py`).

### Adding product launches
Edit `data/products_data.json` or update `MOCK_PRODUCT_LAUNCHES` in `data_manager.py`.

---

## 🔄 Data Refresh

- Click **"🔄 Refresh All Data"** in the sidebar to fetch live news
- Data is cached for **6 hours** automatically
- News is sourced from **Google News RSS** (no API key required)
- Sentiment analysis runs locally via **TextBlob** (no API calls)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| UI Framework | Streamlit 1.32 |
| Charts | Plotly 5 |
| Scraping | feedparser + BeautifulSoup4 |
| NLP / Sentiment | TextBlob |
| Data | pandas + JSON flat files |
| Styling | Custom CSS (Space Grotesk font) |

---

## 🔒 Notes

- This tool uses only **publicly available** RSS feeds and Google News
- No authentication or paid APIs required
- For production use, consider adding a PostgreSQL backend and Redis cache
- Enterprise pricing data should be verified with your sales/analyst team

---

*Tata Communications Internal Use Only · Built for Market Intelligence*
