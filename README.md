# 🔭 Tata Communications — Competitive Intelligence Dashboard

A production-grade competitive intelligence platform built with Python + Streamlit.
Tracks competitors, pricing signals, product launches, and news sentiment in real time.

---

## 🗂️ Project Structure

```
INI-Internship/
├── app.py                    ← Main Streamlit dashboard (launch this)
├── competitors.py            ← Competitor config (add/edit competitors here)
├── config.py                 ← Industry RSS feeds, product categories & API key placeholders
├── data_manager.py           ← Data persistence & caching layer (MySQL + JSON fallback)
├── db.py                     ← MySQL connection, schema management & CRUD helpers
├── requirements.txt          ← All Python dependencies
├── setup_and_run.sh          ← One-click setup & launch script (Mac/Linux)
├── .env.example              ← Template for environment variables (DB credentials, API keys)
├── scrapers/
│   ├── news_scraper.py       ← Google News RSS + competitor RSS scraping
│   ├── sentiment_analyzer.py ← TextBlob NLP sentiment analysis
│   └── pricing_tracker.py    ← Pricing database + web extraction
└── data/                     ← Auto-created; stores JSON cache files
    ├── cache.json
    ├── news_data.json
    ├── pricing_data.json
    └── products_data.json
```

---

## 🚀 Quick Start

### Option A — One command (Mac/Linux)
```bash
chmod +x setup_and_run.sh
./setup_and_run.sh
```

### Option B — Manual setup
```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Download NLTK data
python3 -c "import nltk; nltk.download('punkt'); nltk.download('stopwords'); nltk.download('vader_lexicon')"

# 4. (Optional) Configure environment variables — see Database Setup below

# 5. Launch dashboard
streamlit run app.py
```

Open **http://localhost:8501** in your browser.

---

## 🗄️ Database Setup

The application supports **MySQL** as the primary data store, with an automatic fallback to JSON file storage when MySQL credentials are not configured.

### Using JSON file storage (default — no setup required)
Leave `DB_USER` and `DB_PASSWORD` unset (or blank). All data is persisted in the `data/` directory.

### Using MySQL
1. Copy `.env.example` to `.env` and fill in your MySQL credentials:
    ```bash
    cp .env.example .env
    ```
    ```ini
    DB_HOST=localhost
    DB_PORT=3306
    DB_USER=your_mysql_user
    DB_PASSWORD=your_mysql_password
    DB_NAME=competitive_intel
    ```
2. The setup script (or `db.init_schema()`) will create the required tables automatically on first run.
3. **Optional API keys** for enhanced news coverage can also be set in `.env`:
    ```ini
    GNEWS_API_KEY=your_key_here
    NEWSAPI_KEY=your_key_here
    ```

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
In `config.py`, extend `INDUSTRY_RSS_FEEDS` or add competitor-specific `news_queries` in `competitors.py`.

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
| NLP / Sentiment | TextBlob + NLTK |
| Data Storage | MySQL (primary) · JSON flat files (fallback) |
| Data Processing | pandas |
| Visualisation | Altair · Matplotlib · WordCloud |
| Styling | Custom CSS (Space Grotesk font) |

---

## 🔒 Notes

- This tool uses only **publicly available** RSS feeds and Google News
- No paid APIs are required; optional API keys (`GNEWS_API_KEY`, `NEWSAPI_KEY`) improve news coverage
- MySQL integration uses `mysql-connector-python>=9.1.0`; the app falls back to JSON storage when credentials are absent
- Enterprise pricing data should be verified with your sales/analyst team

---

*Tata Communications Internal Use Only · Built for Market Intelligence*
