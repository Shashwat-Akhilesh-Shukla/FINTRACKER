# app/utils/text_processing.py
import re
from typing import List, Dict, Set
from datetime import datetime
import string
from collections import Counter

class TextProcessor:
    """Utility class for text processing and analysis"""
    
    def __init__(self):
        # Financial keywords for relevance scoring
        self.financial_keywords = {
            'high_value': [
                'earnings', 'revenue', 'profit', 'loss', 'dividend', 'ipo', 'merger',
                'acquisition', 'buyout', 'stock', 'shares', 'market cap', 'valuation'
            ],
            'medium_value': [
                'quarterly', 'annual', 'guidance', 'forecast', 'outlook', 'estimate',
                'target', 'rating', 'upgrade', 'downgrade', 'bull', 'bear'
            ],
            'low_value': [
                'financial', 'business', 'company', 'corporate', 'investment',
                'trading', 'market', 'economic', 'industry', 'sector'
            ]
        }
        
        # Stock symbol pattern
        self.stock_pattern = re.compile(r'\b[A-Z]{1,5}\b')
        
        # Common words to exclude from symbol extraction
        self.excluded_words = {
            'THE', 'AND', 'FOR', 'ARE', 'BUT', 'NOT', 'YOU', 'ALL', 'CAN', 'HER', 
            'WAS', 'ONE', 'OUR', 'HAD', 'HAS', 'HIS', 'NEW', 'NOW', 'OLD', 'SEE', 
            'TWO', 'WAY', 'WHO', 'BOY', 'DID', 'ITS', 'LET', 'PUT', 'SAY', 'SHE', 
            'TOO', 'USE', 'CEO', 'CFO', 'CTO', 'USA', 'USD', 'API', 'GDP', 'IPO', 
            'SEC', 'ETF', 'ESG', 'NYSE', 'NASDAQ', 'DOW', 'SPX', 'QQQ', 'IWM'
        }

    def clean_text(self, text: str) -> str:
        """Clean and normalize text"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', ' ', text)
        
        # Remove URLs
        text = re.sub(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', text)
        
        # Remove email addresses
        text = re.sub(r'\S+@\S+', '', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove leading/trailing whitespace
        text = text.strip()
        
        return text

    def extract_stock_symbols(self, text: str) -> List[str]:
        """Extract potential stock symbols from text"""
        if not text:
            return []
        
        # Find all potential symbols
        potential_symbols = self.stock_pattern.findall(text.upper())
        
        # Filter out common words and invalid symbols
        symbols = []
        for symbol in potential_symbols:
            if (len(symbol) >= 2 and 
                symbol not in self.excluded_words and
                not symbol.isdigit() and
                not all(c in string.digits + '.' for c in symbol)):
                symbols.append(symbol)
        
        # Remove duplicates and limit to reasonable number
        return list(set(symbols))[:15]

    def categorize_content(self, title: str, content: str) -> str:
        """Categorize news content based on keywords"""
        text = f"{title} {content}".lower()
        
        category_keywords = {
            'earnings': [
                'earnings', 'quarterly results', 'q1', 'q2', 'q3', 'q4', 
                'revenue', 'profit', 'loss', 'eps', 'earnings per share'
            ],
            'mergers': [
                'merger', 'acquisition', 'buyout', 'takeover', 'deal',
                'acquire', 'purchase', 'combine', 'consolidation'
            ],
            'markets': [
                'market', 'trading', 'dow jones', 'nasdaq', 's&p 500', 
                'index', 'futures', 'commodities', 'volatility'
            ],
            'crypto': [
                'bitcoin', 'cryptocurrency', 'crypto', 'blockchain', 
                'ethereum', 'dogecoin', 'digital currency', 'mining'
            ],
            'fed': [
                'federal reserve', 'fed', 'interest rate', 'monetary policy',
                'jerome powell', 'fomc', 'quantitative easing'
            ],
            'economic': [
                'inflation', 'unemployment', 'gdp', 'economy', 'economic',
                'recession', 'growth', 'consumer spending', 'retail sales'
            ],
            'tech': [
                'technology', 'artificial intelligence', 'ai', 'software',
                'cloud computing', 'cybersecurity', 'semiconductor'
            ],
            'energy': [
                'oil', 'energy', 'renewable', 'solar', 'wind', 'gas',
                'petroleum', 'crude', 'natural gas', 'drilling'
            ],
            'healthcare': [
                'healthcare', 'pharmaceutical', 'biotech', 'medical',
                'drug approval', 'clinical trial', 'fda approval'
            ],
            'real_estate': [
                'real estate', 'housing', 'mortgage', 'reit',
                'property', 'construction', 'homebuilding'
            ]
        }
        
        # Score each category
        category_scores = {}
        for category, keywords in category_keywords.items():
            score = sum(1 for keyword in keywords if keyword in text)
            if score > 0:
                category_scores[category] = score
        
        # Return category with highest score
        if category_scores:
            return max(category_scores, key=category_scores.get)
        
        return 'general'

    def extract_financial_entities(self, text: str) -> Dict[str, List[str]]:
        """Extract financial entities like companies, metrics, etc."""
        if not text:
            return {}
        
        text_lower = text.lower()
        entities = {
            'companies': [],
            'metrics': [],
            'currencies': [],
            'exchanges': []
        }
        
        # Company indicators
        company_patterns = [
            r'([A-Z][a-z]+ (?:Inc|Corp|Corporation|Company|Ltd|Limited)\.?)',
            r'([A-Z][a-z]+ (?:& [A-Z][a-z]+)+ (?:Inc|Corp|Corporation)\.?)'
        ]
        
        for pattern in company_patterns:
            matches = re.findall(pattern, text)
            entities['companies'].extend(matches)
        
        # Financial metrics
        metric_patterns = [
            r'(\$[\d,]+(?:\.\d+)?[MBK]?)',  # Dollar amounts
            r'([\d,]+(?:\.\d+)?%)',  # Percentages
            r'([\d,]+(?:\.\d+)? (?:billion|million|thousand))'  # Large numbers
        ]
        
        for pattern in metric_patterns:
            matches = re.findall(pattern, text)
            entities['metrics'].extend(matches)
        
        # Currencies
        currency_symbols = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF']
        for currency in currency_symbols:
            if currency.lower() in text_lower:
                entities['currencies'].append(currency)
        
        # Exchanges
        exchanges = ['NYSE', 'NASDAQ', 'LSE', 'TSE', 'HKSE']
        for exchange in exchanges:
            if exchange.lower() in text_lower:
                entities['exchanges'].append(exchange)
        
        # Clean up and deduplicate
        for key in entities:
            entities[key] = list(set(entities[key]))
        
        return entities

    def calculate_readability_score(self, text: str) -> float:
        """Calculate a simple readability score"""
        if not text:
            return 0.0
        
        # Basic metrics
        sentences = len(re.findall(r'[.!?]+', text))
        words = len(text.split())
        
        if sentences == 0 or words == 0:
            return 0.0
        
        # Simple readability approximation
        avg_sentence_length = words / sentences
        
        # Prefer moderate sentence lengths (10-20 words)
        if 10 <= avg_sentence_length <= 20:
            readability = 1.0
        elif avg_sentence_length < 10:
            readability = avg_sentence_length / 10
        else:
            readability = max(0.1, 1.0 - (avg_sentence_length - 20) / 50)
        
        return min(1.0, max(0.0, readability))

    def extract_keywords(self, text: str, max_keywords: int = 10) -> List[str]:
        """Extract important keywords from text"""
        if not text:
            return []
        
        # Clean and normalize
        text = self.clean_text(text.lower())
        
        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'is', 'are', 'was', 'were', 'been', 'be', 'have',
            'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should',
            'may', 'might', 'must', 'can', 'this', 'that', 'these', 'those'
        }
        
        # Extract words (2+ characters, alphanumeric)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text)
        
        # Filter stop words and count frequency
        word_freq = Counter(
            word for word in words 
            if word not in stop_words and len(word) > 2
        )
        
        # Get most common keywords
        keywords = [word for word, _ in word_freq.most_common(max_keywords)]
        
        return keywords

    def calculate_financial_relevance(self, title: str, content: str) -> float:
        """Calculate how relevant the content is to finance"""
        text = f"{title} {content}".lower()
        
        relevance_score = 0.0
        
        # Score based on financial keywords
        for category, keywords in self.financial_keywords.items():
            category_score = sum(1 for keyword in keywords if keyword in text)
            
            if category == 'high_value':
                relevance_score += category_score * 0.3
            elif category == 'medium_value':
                relevance_score += category_score * 0.2
            else:  # low_value
                relevance_score += category_score * 0.1
        
        # Bonus for stock symbols
        symbols = self.extract_stock_symbols(text)
        relevance_score += len(symbols) * 0.1
        
        # Bonus for financial entities
        entities = self.extract_financial_entities(text)
        relevance_score += len(entities['metrics']) * 0.05
        relevance_score += len(entities['companies']) * 0.1
        
        # Normalize to 0-1 range
        return min(1.0, relevance_score)

# Global instance
text_processor = TextProcessor()
