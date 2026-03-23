# scrapers/sentiment_analyzer.py - News sentiment analysis

from textblob import TextBlob
import re


def clean_text(text: str) -> str:
    text = re.sub(r"http\S+|www\S+", "", text)
    text = re.sub(r"[^a-zA-Z0-9\s.,!?'-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def analyze_sentiment(text: str) -> dict:
    cleaned = clean_text(text)
    if not cleaned:
        return {"polarity": 0.0, "subjectivity": 0.5, "label": "Neutral", "score": 50}
    blob = TextBlob(cleaned)
    polarity = blob.sentiment.polarity
    subjectivity = blob.sentiment.subjectivity
    if polarity > 0.15:
        label = "Positive"
    elif polarity < -0.15:
        label = "Negative"
    else:
        label = "Neutral"
    score = int((polarity + 1) / 2 * 100)
    return {
        "polarity": round(polarity, 4),
        "subjectivity": round(subjectivity, 4),
        "label": label,
        "score": score,
    }


def enrich_articles_with_sentiment(news_data: dict) -> dict:
    enriched = {}
    for company, articles in news_data.items():
        enriched_articles = []
        for article in articles:
            text = f"{article.get('title', '')} {article.get('summary', '')}"
            sentiment = analyze_sentiment(text)
            enriched_articles.append({**article, "sentiment": sentiment})
        enriched[company] = enriched_articles
    return enriched


def compute_company_sentiment_summary(articles: list) -> dict:
    if not articles:
        return {
            "avg_polarity": 0.0, "avg_score": 50,
            "positive_pct": 0, "negative_pct": 0, "neutral_pct": 100,
            "label": "Neutral", "article_count": 0,
        }
    polarities = [a["sentiment"]["polarity"] for a in articles if "sentiment" in a]
    scores    = [a["sentiment"]["score"]    for a in articles if "sentiment" in a]
    labels    = [a["sentiment"]["label"]    for a in articles if "sentiment" in a]
    if not polarities:
        return {
            "avg_polarity": 0.0, "avg_score": 50,
            "positive_pct": 0, "negative_pct": 0, "neutral_pct": 100,
            "label": "Neutral", "article_count": len(articles),
        }
    avg_polarity = sum(polarities) / len(polarities)
    avg_score    = sum(scores) / len(scores)
    total = len(labels) or 1
    pos = labels.count("Positive")
    neg = labels.count("Negative")
    neu = labels.count("Neutral")
    overall_label = "Positive" if avg_polarity > 0.1 else "Negative" if avg_polarity < -0.1 else "Neutral"
    return {
        "avg_polarity":  round(avg_polarity, 4),
        "avg_score":     round(avg_score, 1),
        "positive_pct":  round(pos / total * 100, 1),
        "negative_pct":  round(neg / total * 100, 1),
        "neutral_pct":   round(neu / total * 100, 1),
        "label":         overall_label,
        "article_count": len(articles),
    }