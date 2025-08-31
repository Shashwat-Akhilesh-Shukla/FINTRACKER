# app/services/sentiment_service.py
from textblob import TextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import Tuple

class SentimentService:
    def __init__(self):
        self.vader_analyzer = SentimentIntensityAnalyzer()

    async def analyze_sentiment(self, text: str) -> Tuple[str, float]:
        """Analyze sentiment of text using multiple methods"""
        if not text:
            return "neutral", 0.0

        # VADER sentiment analysis (better for financial text)
        vader_scores = self.vader_analyzer.polarity_scores(text)
        vader_compound = vader_scores['compound']

        # TextBlob sentiment analysis
        blob = TextBlob(text)
        textblob_polarity = blob.sentiment.polarity

        # Combine scores (weighted average)
        combined_score = (vader_compound * 0.7) + (textblob_polarity * 0.3)

        # Determine sentiment category
        if combined_score >= 0.1:
            sentiment = "positive"
        elif combined_score <= -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"

        return sentiment, round(combined_score, 3)
