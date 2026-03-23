# app.py - Tata Communications Competitive Intelligence Dashboard

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import json
import os
import sys
import threading

# ── page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(
    page_title="Tata Comms | Competitive Intel",
    page_icon="🔭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── local imports ─────────────────────────────────────────────────────────────
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from competitors import COMPETITORS, TATA_PROFILE, MARKET_SEGMENTS
from data_manager import (
    load_news_data,
    save_news_data,
    get_news_age,
    load_product_launches,
    is_cache_fresh,
)
from scrapers.pricing_tracker import load_pricing_data, get_pricing_dataframe
from scrapers.sentiment_analyzer import (
    enrich_articles_with_sentiment,
    compute_company_sentiment_summary,
)

# ── custom CSS ────────────────────────────────────────────────────────────────
st.markdown(
    """
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── root ── */
:root {
    --tata-blue:   #0033A0;
    --tata-light:  #0057D9;
    --accent:      #00C6FF;
    --positive:    #22C55E;
    --negative:    #EF4444;
    --neutral:     #F59E0B;
    --bg-dark:     #0A0F1E;
    --bg-card:     #111827;
    --border:      rgba(255,255,255,0.08);
    --text-muted:  rgba(255,255,255,0.45);
}

html, body, [class*="css"] {
    font-family: 'Space Grotesk', sans-serif !important;
    background-color: var(--bg-dark) !important;
    color: #E8EDF5 !important;
}

/* sidebar */
[data-testid="stSidebar"] {
    background: #0D1424 !important;
    border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] * { color: #C9D4E8 !important; }

/* cards */
.intel-card {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 20px 24px;
    margin-bottom: 12px;
    transition: border-color .2s;
}
.intel-card:hover { border-color: rgba(0,198,255,0.3); }

/* KPI metric */
.kpi-block {
    background: linear-gradient(135deg, #111827 0%, #0D1424 100%);
    border: 1px solid var(--border);
    border-radius: 10px;
    padding: 18px 20px;
    text-align: center;
}
.kpi-number {
    font-size: 2.2rem;
    font-weight: 700;
    background: linear-gradient(90deg, #00C6FF, #0057D9);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    line-height: 1.1;
}
.kpi-label { font-size: .78rem; color: var(--text-muted); margin-top: 4px; letter-spacing: .06em; text-transform: uppercase; }

/* sentiment badges */
.badge-positive { background:#052e16; color:#4ade80; border:1px solid #166534; padding:2px 10px; border-radius:99px; font-size:.75rem; font-weight:600; }
.badge-negative { background:#2d0707; color:#f87171; border:1px solid #991b1b; padding:2px 10px; border-radius:99px; font-size:.75rem; font-weight:600; }
.badge-neutral  { background:#1c1003; color:#fbbf24; border:1px solid #92400e; padding:2px 10px; border-radius:99px; font-size:.75rem; font-weight:600; }

/* trend icons */
.trend-up   { color: #ef4444; }
.trend-down { color: #22c55e; }
.trend-flat { color: #94a3b8; }

/* header */
.dash-header {
    background: linear-gradient(135deg, #0033A0 0%, #001F60 60%, #0A0F1E 100%);
    border-radius: 16px;
    padding: 28px 32px;
    margin-bottom: 24px;
    border: 1px solid rgba(0,198,255,0.2);
    position: relative;
    overflow: hidden;
}
.dash-header::after {
    content: '';
    position: absolute;
    top: -40px; right: -40px;
    width: 220px; height: 220px;
    border-radius: 50%;
    background: radial-gradient(circle, rgba(0,198,255,.15), transparent 70%);
    pointer-events: none;
}
.dash-title { font-size: 1.9rem; font-weight: 700; letter-spacing: -.02em; }
.dash-sub   { color: rgba(255,255,255,.55); font-size: .9rem; margin-top: 4px; }

/* section title */
.section-title {
    font-size: 1.05rem;
    font-weight: 600;
    color: #CBD5E1;
    border-left: 3px solid var(--accent);
    padding-left: 10px;
    margin: 20px 0 14px 0;
    letter-spacing: .01em;
}

/* news card */
.news-item {
    border-left: 3px solid var(--tata-light);
    padding: 10px 14px;
    margin-bottom: 10px;
    background: rgba(255,255,255,.025);
    border-radius: 0 8px 8px 0;
}
.news-title { font-weight: 600; font-size: .9rem; margin-bottom: 4px; }
.news-meta  { font-size: .75rem; color: var(--text-muted); }
.news-summary { font-size: .82rem; color: #94a3b8; margin-top: 5px; line-height: 1.45; }

/* product launch row */
.launch-row {
    display: flex;
    align-items: flex-start;
    gap: 14px;
    padding: 12px 0;
    border-bottom: 1px solid var(--border);
}
.launch-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    margin-top: 5px;
    flex-shrink: 0;
}
.impact-high   { background: #22c55e; box-shadow: 0 0 8px #22c55e88; }
.impact-medium { background: #f59e0b; }
.impact-low    { background: #94a3b8; }

/* streamlit overrides */
.stButton > button {
    background: linear-gradient(90deg, var(--tata-blue), var(--tata-light)) !important;
    color: white !important;
    border: none !important;
    border-radius: 8px !important;
    font-weight: 600 !important;
    font-family: 'Space Grotesk', sans-serif !important;
    letter-spacing: .03em !important;
}
.stButton > button:hover { opacity: .88 !important; }
[data-testid="stMetricValue"] { font-family: 'JetBrains Mono', monospace !important; }
.stTabs [data-baseweb="tab"] { font-family: 'Space Grotesk', sans-serif !important; }
div[data-testid="stDataFrame"] { border-radius: 10px; overflow: hidden; }
</style>
""",
    unsafe_allow_html=True,
)

# ── helpers ───────────────────────────────────────────────────────────────────
ALL_COMPANIES = list(COMPETITORS.keys())
COMPANY_COLORS = {"Tata Communications": TATA_PROFILE["color"]}
COMPANY_COLORS.update({k: v["color"] for k, v in COMPETITORS.items()})

TATA_COLOR = TATA_PROFILE["color"]
DARK_TEMPLATE = dict(
    template="plotly_dark",
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
)


def sentiment_badge(label: str) -> str:
    cls = {"Positive": "badge-positive", "Negative": "badge-negative"}.get(label, "badge-neutral")
    return f'<span class="{cls}">{label}</span>'


def trend_icon(trend: str) -> str:
    return {"increasing": "↑", "decreasing": "↓"}.get(trend, "→")


def trend_css(trend: str) -> str:
    return {"increasing": "trend-up", "decreasing": "trend-down"}.get(trend, "trend-flat")


def format_date(iso_str: str) -> str:
    try:
        return datetime.fromisoformat(iso_str).strftime("%d %b %Y")
    except Exception:
        return iso_str[:10]


@st.cache_data(ttl=300)
def get_pricing_df():
    return get_pricing_dataframe()


# ── sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        """
        <div style="text-align:center;padding:16px 0 8px">
            <div style="font-size:1.6rem;font-weight:700;background:linear-gradient(90deg,#00C6FF,#0057D9);
                        -webkit-background-clip:text;-webkit-text-fill-color:transparent;">TATA COMMS</div>
            <div style="font-size:.72rem;color:#64748b;letter-spacing:.12em;margin-top:2px;">COMPETITIVE INTELLIGENCE</div>
        </div>
        <hr style="border-color:rgba(255,255,255,.06);margin:8px 0 16px">
        """,
        unsafe_allow_html=True,
    )

    st.markdown("**📡 Data Controls**")
    data_age = get_news_age()
    st.caption(f"Last fetched: **{data_age}**")

    if st.button("🔄 Refresh All Data", use_container_width=True):
        with st.spinner("Scraping news & sentiment…"):
            from scrapers.news_scraper import scrape_all_news
            news = scrape_all_news()
            # Handle if scraper returns a list instead of dict
            if isinstance(news, list):
                news_dict = {}
                for item in news:
                    company = item.get("company", "Unknown")
                    if company not in news_dict:
                        news_dict[company] = []
                    news_dict[company].append(item)
                news = news_dict
            enriched = enrich_articles_with_sentiment(news)
            save_news_data(enriched)
            st.cache_data.clear()
        st.success("✅ Data refreshed!")
        st.rerun()

    st.markdown("---")
    st.markdown("**🏢 Competitors**")
    selected_companies = st.multiselect(
        "Show competitors",
        options=ALL_COMPANIES,
        default=ALL_COMPANIES,
        label_visibility="collapsed",
    )

    st.markdown("---")
    st.markdown("**🗂️ Filters**")
    sentiment_filter = st.selectbox("Sentiment", ["All", "Positive", "Neutral", "Negative"])
    date_range = st.selectbox("Time range", ["Last 7 days", "Last 30 days", "Last 90 days", "All time"])

    st.markdown("---")
    st.caption("© 2025 Tata Communications Ltd\nInternal Use Only")

# ── load data ─────────────────────────────────────────────────────────────────
news_data = load_news_data() or {}
product_launches = load_product_launches()
pricing_df = get_pricing_df()

# Ensure Tata is included
display_companies = ["Tata Communications"] + selected_companies

# Compute sentiment summaries
sentiment_summaries = {}
for company in display_companies:
    articles = news_data.get(company, [])
    sentiment_summaries[company] = compute_company_sentiment_summary(articles)

# ── header ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
    <div class="dash-header">
        <div class="dash-title">🔭 Competitive Intelligence Dashboard</div>
        <div class="dash-sub">
            Tata Communications · Market Intel Platform ·
            <span style="color:#00C6FF;">Updated {datetime.now().strftime("%d %b %Y, %H:%M")}</span>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# ── KPI row ───────────────────────────────────────────────────────────────────
total_articles = sum(len(news_data.get(c, [])) for c in display_companies)
total_launches = len(product_launches)
tata_sentiment = sentiment_summaries.get("Tata Communications", {})
tata_score = tata_sentiment.get("avg_score", 50)
avg_competitor_score = (
    sum(
        sentiment_summaries.get(c, {}).get("avg_score", 50)
        for c in selected_companies
    )
    / max(len(selected_companies), 1)
)

k1, k2, k3, k4, k5 = st.columns(5)
kpis = [
    (k1, str(len(selected_companies)), "Competitors Tracked"),
    (k2, str(total_articles), "News Articles"),
    (k3, str(total_launches), "Product Launches"),
    (k4, f"{tata_score:.0f}/100", "Tata Sentiment Score"),
    (
        k5,
        f"+{tata_score - avg_competitor_score:.1f}",
        "vs Competitor Avg",
    ),
]
for col, val, lbl in kpis:
    with col:
        st.markdown(
            f'<div class="kpi-block"><div class="kpi-number">{val}</div>'
            f'<div class="kpi-label">{lbl}</div></div>',
            unsafe_allow_html=True,
        )

st.markdown("<br>", unsafe_allow_html=True)

# ── tabs ──────────────────────────────────────────────────────────────────────
tab_overview, tab_news, tab_sentiment, tab_pricing, tab_products, tab_radar = st.tabs(
    ["📊 Overview", "📰 News Feed", "💬 Sentiment", "💰 Pricing Intel", "🚀 Product Launches", "🕸️ Radar"]
)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 1 — OVERVIEW
# ══════════════════════════════════════════════════════════════════════════════
with tab_overview:
    col_left, col_right = st.columns([3, 2], gap="large")

    with col_left:
        st.markdown('<div class="section-title">Sentiment Score Comparison</div>', unsafe_allow_html=True)

        companies_for_chart = [c for c in display_companies if c in sentiment_summaries]
        scores_for_chart = [sentiment_summaries[c]["avg_score"] for c in companies_for_chart]
        colors_for_chart = [COMPANY_COLORS.get(c, "#64748b") for c in companies_for_chart]

        fig_bar = go.Figure(
            go.Bar(
                x=companies_for_chart,
                y=scores_for_chart,
                marker_color=colors_for_chart,
                marker_line_width=0,
                text=[f"{s:.0f}" for s in scores_for_chart],
                textposition="outside",
                textfont=dict(size=12, color="#CBD5E1"),
            )
        )
        fig_bar.add_hline(y=50, line_dash="dot", line_color="rgba(255,255,255,.2)", annotation_text="Neutral")
        fig_bar.update_layout(
            **DARK_TEMPLATE,
            height=320,
            margin=dict(l=0, r=0, t=10, b=40),
            yaxis=dict(range=[0, 105], showgrid=True, gridcolor="rgba(255,255,255,.05)"),
            xaxis=dict(showgrid=False, tickangle=-20),
            showlegend=False,
        )
        st.plotly_chart(fig_bar, use_container_width=True)

        st.markdown('<div class="section-title">News Volume by Company</div>', unsafe_allow_html=True)
        vol_companies = [c for c in display_companies if news_data.get(c)]
        vol_counts = [len(news_data.get(c, [])) for c in vol_companies]
        fig_vol = px.bar(
            x=vol_counts,
            y=vol_companies,
            orientation="h",
            color=vol_counts,
            color_continuous_scale=[[0, "#1e3a5f"], [0.5, "#0057D9"], [1, "#00C6FF"]],
            labels={"x": "Articles", "y": ""},
        )
        fig_vol.update_layout(
            **DARK_TEMPLATE,
            height=270,
            margin=dict(l=0, r=0, t=10, b=10),
            coloraxis_showscale=False,
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)"),
            yaxis=dict(showgrid=False),
        )
        st.plotly_chart(fig_vol, use_container_width=True)

    with col_right:
        st.markdown('<div class="section-title">Sentiment Breakdown</div>', unsafe_allow_html=True)
        # Stacked bar for pos/neg/neutral
        pos_vals = [sentiment_summaries.get(c, {}).get("positive_pct", 0) for c in display_companies]
        neu_vals = [sentiment_summaries.get(c, {}).get("neutral_pct", 100) for c in display_companies]
        neg_vals = [sentiment_summaries.get(c, {}).get("negative_pct", 0) for c in display_companies]

        fig_stack = go.Figure()
        fig_stack.add_trace(go.Bar(name="Positive", x=display_companies, y=pos_vals, marker_color="#22c55e"))
        fig_stack.add_trace(go.Bar(name="Neutral", x=display_companies, y=neu_vals, marker_color="#f59e0b"))
        fig_stack.add_trace(go.Bar(name="Negative", x=display_companies, y=neg_vals, marker_color="#ef4444"))
        fig_stack.update_layout(
            **DARK_TEMPLATE,
            barmode="stack",
            height=280,
            margin=dict(l=0, r=0, t=10, b=50),
            legend=dict(orientation="h", y=-0.25, x=0, font=dict(size=11)),
            xaxis=dict(tickangle=-20, showgrid=False),
            yaxis=dict(title="%", showgrid=True, gridcolor="rgba(255,255,255,.05)"),
        )
        st.plotly_chart(fig_stack, use_container_width=True)

        st.markdown('<div class="section-title">Competitor Summary</div>', unsafe_allow_html=True)
        for company in selected_companies[:5]:
            s = sentiment_summaries.get(company, {})
            color = COMPANY_COLORS.get(company, "#64748b")
            badge = sentiment_badge(s.get("label", "Neutral"))
            st.markdown(
                f"""
                <div class="intel-card" style="padding:12px 16px;margin-bottom:8px;border-left:3px solid {color}">
                    <div style="display:flex;justify-content:space-between;align-items:center;">
                        <span style="font-weight:600;font-size:.9rem">{company}</span>
                        {badge}
                    </div>
                    <div style="color:#64748b;font-size:.75rem;margin-top:5px;">
                        Score: <b style="color:#CBD5E1">{s.get('avg_score',50):.0f}/100</b> &nbsp;·&nbsp;
                        Articles: <b style="color:#CBD5E1">{s.get('article_count',0)}</b> &nbsp;·&nbsp;
                        Segment: <b style="color:#CBD5E1">{COMPETITORS.get(company,{}).get('segment','—')}</b>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 2 — NEWS FEED
# ══════════════════════════════════════════════════════════════════════════════
with tab_news:
    st.markdown('<div class="section-title">Latest Market News</div>', unsafe_allow_html=True)

    news_col1, news_col2 = st.columns([1, 3])
    with news_col1:
        news_company_filter = st.selectbox(
            "Company", ["All"] + display_companies, key="news_company"
        )
    with news_col2:
        news_search = st.text_input("🔍 Search headlines", placeholder="Enter keyword…", key="news_search")

    # Flatten all articles
    all_articles = []
    for company in display_companies:
        for article in news_data.get(company, []):
            all_articles.append({**article, "company": company})

    # Apply filters
    if news_company_filter != "All":
        all_articles = [a for a in all_articles if a["company"] == news_company_filter]
    if news_search:
        kw = news_search.lower()
        all_articles = [
            a for a in all_articles
            if kw in a.get("title", "").lower() or kw in a.get("summary", "").lower()
        ]
    if sentiment_filter != "All":
        all_articles = [
            a for a in all_articles
            if a.get("sentiment", {}).get("label") == sentiment_filter
        ]

    # Sort by date
    all_articles.sort(key=lambda x: x.get("published", ""), reverse=True)

    st.caption(f"Showing **{len(all_articles)}** articles")

    if not all_articles:
        st.info("No news articles found. Click **Refresh All Data** in the sidebar to fetch live news.")
    else:
        for art in all_articles[:40]:
            company = art.get("company", "")
            color = COMPANY_COLORS.get(company, "#64748b")
            sentiment = art.get("sentiment", {})
            badge = sentiment_badge(sentiment.get("label", "Neutral")) if sentiment else ""
            pub_date = format_date(art.get("published", ""))

            st.markdown(
                f"""
                <div class="news-item" style="border-left-color:{color}">
                    <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                        <div class="news-title">
                            <a href="{art.get('link','#')}" target="_blank"
                               style="color:#E2E8F0;text-decoration:none;">
                               {art.get('title','(No title)')}
                            </a>
                        </div>
                        <div style="flex-shrink:0;margin-left:12px;">{badge}</div>
                    </div>
                    <div class="news-meta">
                        <span style="color:{color};font-weight:600">{company}</span> &nbsp;·&nbsp;
                        {pub_date} &nbsp;·&nbsp;
                        {art.get('source','')}
                    </div>
                    <div class="news-summary">{art.get('summary','')[:200]}…</div>
                </div>
                """,
                unsafe_allow_html=True,
            )

# ══════════════════════════════════════════════════════════════════════════════
# TAB 3 — SENTIMENT
# ══════════════════════════════════════════════════════════════════════════════
with tab_sentiment:
    st.markdown('<div class="section-title">Sentiment Analysis Deep-Dive</div>', unsafe_allow_html=True)

    sc1, sc2 = st.columns([3, 2], gap="large")

    with sc1:
        # Polarity scatter
        scatter_data = []
        for company in display_companies:
            for art in news_data.get(company, []):
                if "sentiment" in art:
                    scatter_data.append(
                        {
                            "Company": company,
                            "Polarity": art["sentiment"]["polarity"],
                            "Subjectivity": art["sentiment"]["subjectivity"],
                            "Title": art.get("title", "")[:60],
                            "Label": art["sentiment"]["label"],
                        }
                    )

        if scatter_data:
            df_scatter = pd.DataFrame(scatter_data)
            fig_scatter = px.scatter(
                df_scatter,
                x="Polarity",
                y="Subjectivity",
                color="Company",
                symbol="Label",
                hover_data=["Title"],
                color_discrete_map=COMPANY_COLORS,
                title="Polarity vs Subjectivity",
            )
            fig_scatter.add_vline(x=0, line_dash="dot", line_color="rgba(255,255,255,.2)")
            fig_scatter.add_hline(y=0.5, line_dash="dot", line_color="rgba(255,255,255,.2)")
            fig_scatter.update_layout(
                **DARK_TEMPLATE,
                height=380,
                margin=dict(l=0, r=0, t=40, b=10),
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig_scatter, use_container_width=True)
        else:
            st.info("No sentiment data. Refresh data to compute sentiment.")

        # Timeline of sentiment
        st.markdown('<div class="section-title">Sentiment Timeline</div>', unsafe_allow_html=True)
        timeline_data = []
        for company in display_companies:
            for art in news_data.get(company, []):
                if "sentiment" in art and art.get("published"):
                    try:
                        dt = datetime.fromisoformat(art["published"]).date()
                        timeline_data.append(
                            {
                                "Date": str(dt),
                                "Company": company,
                                "Score": art["sentiment"]["score"],
                            }
                        )
                    except Exception:
                        pass

        if timeline_data:
            df_timeline = pd.DataFrame(timeline_data)
            df_timeline = df_timeline.groupby(["Date", "Company"])["Score"].mean().reset_index()
            fig_timeline = px.line(
                df_timeline,
                x="Date",
                y="Score",
                color="Company",
                color_discrete_map=COMPANY_COLORS,
                markers=True,
            )
            fig_timeline.add_hline(y=50, line_dash="dot", line_color="rgba(255,255,255,.2)", annotation_text="Neutral")
            fig_timeline.update_layout(
                **DARK_TEMPLATE,
                height=280,
                margin=dict(l=0, r=0, t=10, b=10),
                yaxis=dict(range=[0, 100], showgrid=True, gridcolor="rgba(255,255,255,.05)"),
                legend=dict(font=dict(size=10)),
            )
            st.plotly_chart(fig_timeline, use_container_width=True)

    with sc2:
        st.markdown('<div class="section-title">Company Scores</div>', unsafe_allow_html=True)
        for company in display_companies:
            s = sentiment_summaries.get(company, {})
            score = s.get("avg_score", 50)
            color = COMPANY_COLORS.get(company, "#64748b")
            bar_color = "#22c55e" if score > 60 else "#ef4444" if score < 40 else "#f59e0b"

            st.markdown(
                f"""
                <div style="margin-bottom:14px">
                    <div style="display:flex;justify-content:space-between;margin-bottom:4px">
                        <span style="font-size:.85rem;font-weight:600;color:{color}">{company}</span>
                        <span style="font-size:.85rem;font-weight:700;color:{bar_color}">{score:.0f}/100</span>
                    </div>
                    <div style="background:rgba(255,255,255,.07);border-radius:99px;height:7px;overflow:hidden">
                        <div style="width:{score}%;background:{bar_color};height:100%;border-radius:99px;
                                    transition:width .5s"></div>
                    </div>
                    <div style="font-size:.72rem;color:#64748b;margin-top:3px">
                        📰 {s.get('article_count',0)} articles &nbsp;
                        ✅ {s.get('positive_pct',0):.0f}% pos &nbsp;
                        ❌ {s.get('negative_pct',0):.0f}% neg
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

        st.markdown('<div class="section-title">Sentiment Distribution</div>', unsafe_allow_html=True)
        total_pos = sum(
            int(sentiment_summaries.get(c, {}).get("positive_pct", 0) * sentiment_summaries.get(c, {}).get("article_count", 0) / 100)
            for c in display_companies
        )
        total_neg = sum(
            int(sentiment_summaries.get(c, {}).get("negative_pct", 0) * sentiment_summaries.get(c, {}).get("article_count", 0) / 100)
            for c in display_companies
        )
        total_neu = max(1, total_articles - total_pos - total_neg)

        fig_pie = go.Figure(
            go.Pie(
                labels=["Positive", "Neutral", "Negative"],
                values=[total_pos or 1, total_neu, total_neg or 1],
                hole=0.55,
                marker_colors=["#22c55e", "#f59e0b", "#ef4444"],
                textfont_size=12,
            )
        )
        fig_pie.update_layout(
            **DARK_TEMPLATE,
            height=220,
            margin=dict(l=0, r=0, t=10, b=10),
            showlegend=True,
            legend=dict(font=dict(size=11), orientation="h", y=-0.1),
        )
        st.plotly_chart(fig_pie, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 4 — PRICING
# ══════════════════════════════════════════════════════════════════════════════
with tab_pricing:
    st.markdown('<div class="section-title">Pricing Intelligence Database</div>', unsafe_allow_html=True)
    st.caption("ℹ️ Enterprise telecom pricing is quote-based. Data sourced from public reports, RFPs, and industry analysis.")

    pc1, pc2 = st.columns([1, 3])
    with pc1:
        price_company = st.selectbox("Filter company", ["All"] + list(COMPANY_COLORS.keys()), key="price_co")
    with pc2:
        price_search = st.text_input("Search products", placeholder="e.g. SD-WAN, Cloud, IoT…", key="price_s")

    df_show = pricing_df.copy()
    if price_company != "All":
        df_show = df_show[df_show["Company"] == price_company]
    if price_search:
        kw = price_search.lower()
        df_show = df_show[
            df_show["Product/Service"].str.lower().str.contains(kw) |
            df_show["Notes"].str.lower().str.contains(kw)
        ]

    # Colour-code trend
    def style_trend(val):
        if val == "increasing":
            return "color:#ef4444;font-weight:700"
        elif val == "decreasing":
            return "color:#22c55e;font-weight:700"
        return "color:#94a3b8"

    st.dataframe(
        df_show.drop(columns=["Source"], errors="ignore"),
        use_container_width=True,
        height=380,
        column_config={
            "Trend": st.column_config.TextColumn("Trend"),
            "Price Range": st.column_config.TextColumn("Price Range", width="medium"),
            "Notes": st.column_config.TextColumn("Notes", width="large"),
        },
    )

    st.markdown("---")
    pc3, pc4 = st.columns(2)

    with pc3:
        st.markdown('<div class="section-title">Pricing Model Distribution</div>', unsafe_allow_html=True)
        model_counts = pricing_df["Pricing Model"].value_counts().reset_index()
        model_counts.columns = ["Model", "Count"]
        fig_models = px.pie(
            model_counts,
            names="Model",
            values="Count",
            hole=0.5,
            color_discrete_sequence=["#0033A0", "#0057D9", "#00C6FF", "#38BDF8", "#7DD3FC", "#BAE6FD"],
        )
        fig_models.update_layout(**DARK_TEMPLATE, height=280, margin=dict(l=0, r=0, t=10, b=0))
        st.plotly_chart(fig_models, use_container_width=True)

    with pc4:
        st.markdown('<div class="section-title">Pricing Trend by Company</div>', unsafe_allow_html=True)
        trend_map = {"increasing": 1, "stable": 0, "decreasing": -1}
        trend_df = pricing_df.copy()
        trend_df["trend_val"] = trend_df["Trend"].map(trend_map)
        trend_agg = trend_df.groupby("Company")["trend_val"].mean().reset_index()
        trend_agg.columns = ["Company", "Avg Trend"]
        trend_agg["Direction"] = trend_agg["Avg Trend"].apply(
            lambda x: "Increasing" if x > 0.1 else "Decreasing" if x < -0.1 else "Stable"
        )
        fig_trend = px.bar(
            trend_agg.sort_values("Avg Trend"),
            x="Avg Trend",
            y="Company",
            orientation="h",
            color="Direction",
            color_discrete_map={"Increasing": "#ef4444", "Stable": "#94a3b8", "Decreasing": "#22c55e"},
        )
        fig_trend.update_layout(
            **DARK_TEMPLATE,
            height=280,
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis=dict(range=[-1.2, 1.2], zeroline=True, zerolinecolor="rgba(255,255,255,.2)"),
        )
        st.plotly_chart(fig_trend, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 5 — PRODUCT LAUNCHES
# ══════════════════════════════════════════════════════════════════════════════
with tab_products:
    st.markdown('<div class="section-title">Recent Product & Service Launches</div>', unsafe_allow_html=True)

    pl1, pl2, pl3 = st.columns(3)
    with pl1:
        pl_company = st.selectbox("Company", ["All"] + display_companies, key="pl_co")
    with pl2:
        categories = sorted(set(p["category"] for p in product_launches))
        pl_category = st.selectbox("Category", ["All"] + categories, key="pl_cat")
    with pl3:
        pl_impact = st.selectbox("Impact", ["All", "High", "Medium", "Low"], key="pl_imp")

    filtered_launches = product_launches
    if pl_company != "All":
        filtered_launches = [p for p in filtered_launches if p["company"] == pl_company]
    if pl_category != "All":
        filtered_launches = [p for p in filtered_launches if p["category"] == pl_category]
    if pl_impact != "All":
        filtered_launches = [p for p in filtered_launches if p["impact"] == pl_impact]

    filtered_launches.sort(key=lambda x: x.get("date", ""), reverse=True)

    pll, plr = st.columns([2, 3], gap="large")

    with pll:
        st.caption(f"**{len(filtered_launches)}** launches found")
        for launch in filtered_launches:
            color = COMPANY_COLORS.get(launch["company"], "#64748b")
            impact_cls = f"impact-{launch['impact'].lower()}"
            st.markdown(
                f"""
                <div class="launch-row">
                    <div class="launch-dot {impact_cls}"></div>
                    <div>
                        <div style="font-weight:600;font-size:.88rem;color:#E2E8F0">{launch['product']}</div>
                        <div style="font-size:.75rem;margin-top:2px">
                            <span style="color:{color};font-weight:600">{launch['company']}</span> &nbsp;·&nbsp;
                            <span style="color:#64748b">{launch['date']}</span> &nbsp;·&nbsp;
                            <span style="background:rgba(255,255,255,.07);padding:1px 7px;border-radius:4px;
                                         font-size:.7rem;color:#94a3b8">{launch['category']}</span>
                        </div>
                        <div style="font-size:.78rem;color:#64748b;margin-top:3px;line-height:1.4">
                            {launch['description'][:100]}…
                        </div>
                    </div>
                </div>
                """,
                unsafe_allow_html=True,
            )

    with plr:
        st.markdown('<div class="section-title">Launches by Company</div>', unsafe_allow_html=True)
        launch_df = pd.DataFrame(product_launches)
        company_launch_counts = launch_df.groupby("company").size().reset_index(name="count")
        company_launch_counts["color"] = company_launch_counts["company"].map(COMPANY_COLORS)
        fig_launches = px.bar(
            company_launch_counts.sort_values("count"),
            x="count",
            y="company",
            orientation="h",
            color="company",
            color_discrete_map=COMPANY_COLORS,
            text="count",
        )
        fig_launches.update_traces(textposition="outside", textfont_color="#CBD5E1")
        fig_launches.update_layout(
            **DARK_TEMPLATE,
            height=320,
            margin=dict(l=0, r=0, t=10, b=10),
            showlegend=False,
            xaxis=dict(showgrid=True, gridcolor="rgba(255,255,255,.05)"),
        )
        st.plotly_chart(fig_launches, use_container_width=True)

        st.markdown('<div class="section-title">Category Heatmap</div>', unsafe_allow_html=True)
        pivot = launch_df.pivot_table(
            index="company", columns="category", aggfunc="size", fill_value=0
        )
        fig_heat = px.imshow(
            pivot,
            color_continuous_scale=[[0, "#0A0F1E"], [0.3, "#0033A0"], [1, "#00C6FF"]],
            aspect="auto",
            text_auto=True,
        )
        fig_heat.update_layout(
            **DARK_TEMPLATE,
            height=280,
            margin=dict(l=0, r=0, t=10, b=10),
            xaxis=dict(tickangle=-30),
        )
        st.plotly_chart(fig_heat, use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# TAB 6 — RADAR (Competitive Positioning)
# ══════════════════════════════════════════════════════════════════════════════
with tab_radar:
    st.markdown('<div class="section-title">Competitive Positioning Radar</div>', unsafe_allow_html=True)
    st.caption("Scores are based on analyst reports, Gartner Magic Quadrant, and public capability disclosures. Scale: 0–10.")

    # Radar data (analyst-grade scoring)
    radar_scores = {
        "Tata Communications": [8, 9, 8, 6, 7, 8, 8],
        "Bharti Airtel":       [7, 6, 5, 7, 6, 6, 6],
        "Reliance Jio":        [9, 4, 3, 8, 5, 4, 5],
        "AT&T":                [7, 8, 6, 6, 8, 7, 8],
        "Verizon Business":    [7, 8, 6, 7, 9, 7, 8],
        "BT Group":            [6, 7, 5, 5, 7, 7, 6],
        "NTT Ltd":             [7, 7, 6, 5, 7, 8, 7],
    }
    radar_categories = MARKET_SEGMENTS + [MARKET_SEGMENTS[0]]  # close loop

    ra1, ra2 = st.columns([3, 2])

    with ra1:
        companies_to_radar = st.multiselect(
            "Select companies to compare",
            options=list(radar_scores.keys()),
            default=["Tata Communications", "Bharti Airtel", "AT&T"],
            key="radar_sel",
        )

        fig_radar = go.Figure()
        for company in companies_to_radar:
            scores = radar_scores.get(company, [5] * 7)
            scores_loop = scores + [scores[0]]
            fig_radar.add_trace(
                go.Scatterpolar(
                    r=scores_loop,
                    theta=radar_categories,
                    fill="toself",
                    name=company,
                    line_color=COMPANY_COLORS.get(company, "#64748b"),
                    fillcolor=COMPANY_COLORS.get(company, "#64748b"),
                    opacity=0.25,
                )
            )
        fig_radar.update_layout(
            **DARK_TEMPLATE,
            polar=dict(
                radialaxis=dict(visible=True, range=[0, 10], gridcolor="rgba(255,255,255,.1)", color="#64748b"),
                angularaxis=dict(gridcolor="rgba(255,255,255,.1)", linecolor="rgba(255,255,255,.15)"),
                bgcolor="rgba(0,0,0,0)",
            ),
            height=480,
            margin=dict(l=40, r=40, t=40, b=40),
            legend=dict(font=dict(size=11), bgcolor="rgba(0,0,0,0)"),
        )
        st.plotly_chart(fig_radar, use_container_width=True)

    with ra2:
        st.markdown('<div class="section-title">Capability Scores</div>', unsafe_allow_html=True)
        score_df = pd.DataFrame(radar_scores, index=MARKET_SEGMENTS).T
        score_df["Overall"] = score_df.mean(axis=1).round(1)
        score_df = score_df.sort_values("Overall", ascending=False)

        st.dataframe(
            score_df.style.background_gradient(cmap="Blues", vmin=0, vmax=10),
            use_container_width=True,
            height=320,
        )

        st.markdown('<div class="section-title">Tata vs Market Average</div>', unsafe_allow_html=True)
        tata_r = radar_scores["Tata Communications"]
        all_avg = [
            sum(radar_scores[c][i] for c in radar_scores) / len(radar_scores)
            for i in range(len(MARKET_SEGMENTS))
        ]

        fig_gap = go.Figure()
        fig_gap.add_trace(go.Bar(name="Tata Comms", x=MARKET_SEGMENTS, y=tata_r, marker_color=TATA_COLOR))
        fig_gap.add_trace(go.Bar(name="Market Avg", x=MARKET_SEGMENTS, y=all_avg, marker_color="#334155"))
        fig_gap.update_layout(
            **DARK_TEMPLATE,
            barmode="group",
            height=260,
            margin=dict(l=0, r=0, t=10, b=60),
            xaxis=dict(tickangle=-30, showgrid=False),
            yaxis=dict(range=[0, 10.5], showgrid=True, gridcolor="rgba(255,255,255,.05)"),
            legend=dict(font=dict(size=10), orientation="h", y=-0.35),
        )
        st.plotly_chart(fig_gap, use_container_width=True)

# ── footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
    <hr style="border-color:rgba(255,255,255,.06);margin:32px 0 16px">
    <div style="text-align:center;color:#334155;font-size:.75rem">
        Tata Communications Competitive Intelligence Platform &nbsp;·&nbsp;
        Internal Use Only &nbsp;·&nbsp;
        Data sourced from public news, RSS feeds &amp; analyst reports
    </div>
    """,
    unsafe_allow_html=True,
)
