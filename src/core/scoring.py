"""
Scoring engine for trading signals.
Combines momentum, volume, relative strength, news sentiment, and catalysts.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple


class ScoringEngine:
    """Calculates composite scores for trading signals."""
    
    def __init__(self, config: dict):
        """Initialize with configuration."""
        self.config = config
        self.weights = {
            'momentum': 0.25,
            'volume': 0.20,
            'relative_strength': 0.20,
            'news_sentiment': 0.20,
            'catalysts': 0.15
        }
    
    def calculate_momentum_score(self, rsi: float, atr_val: float) -> float:
        """
        Calculate momentum score based on RSI.
        RSI 0-100 normalized to 0-100 score.
        """
        if pd.isna(rsi):
            return 0.0
        
        # Simple RSI to score mapping
        # RSI 30-70 is neutral, extremes are interesting
        if rsi < 30:
            score = (30 - rsi) / 30 * 50  # Oversold bonus
        elif rsi > 70:
            score = (rsi - 70) / 30 * 50 + 50  # Overbought potential
        else:
            score = 25 + (rsi - 30) / 40 * 25  # Neutral zone
        
        return min(100, max(0, score))
    
    def calculate_volume_score(self, current_volume: float, avg_volume: float, threshold: float = 150) -> float:
        """
        Calculate volume surge score.
        threshold: minimum % above average to qualify (default 150%)
        """
        if avg_volume == 0:
            return 0.0
        
        volume_ratio = (current_volume / avg_volume) * 100
        
        if volume_ratio < threshold:
            return 0.0
        
        # Scale from threshold up
        score = (volume_ratio - threshold) / (threshold * 2) * 100
        return min(100, max(0, score))
    
    def calculate_relative_strength_score(self, stock_pct_change: float, sector_pct_change: float, min_threshold: float = 5.0) -> float:
        """
        Calculate relative strength vs sector.
        Positive diff = stock outperforming sector.
        """
        diff = stock_pct_change - sector_pct_change
        
        if diff < -min_threshold:
            return 0.0
        elif diff < min_threshold:
            return 25.0
        else:
            # Bonus for strong outperformance
            score = 25.0 + (diff - min_threshold) / min_threshold * 75
            return min(100, score)
    
    def calculate_news_sentiment_score(self, positive_articles: int, total_articles: int) -> float:
        """
        Calculate news sentiment score.
        Ratio of positive to total articles.
        """
        if total_articles == 0:
            return 50.0  # Neutral if no news
        
        positive_ratio = positive_articles / total_articles
        return positive_ratio * 100
    
    def calculate_catalyst_score(self, catalysts: List[Dict]) -> float:
        """
        Calculate catalyst score based on recency and keyword match.
        """
        if not catalysts:
            return 0.0
        
        # Simple implementation: catalysts within 7 days = full score
        total_score = 0
        for catalyst in catalysts:
            days_ago = catalyst.get('days_ago', 999)
            if days_ago <= 7:
                total_score += 100
            elif days_ago <= 30:
                total_score += 50
        
        avg_score = total_score / len(catalysts) if catalysts else 0
        return min(100, avg_score)
    
    def calculate_composite_score(self,
                                  momentum_score: float,
                                  volume_score: float,
                                  rel_strength_score: float,
                                  news_sentiment_score: float,
                                  catalyst_score: float) -> float:
        """
        Combine all scores using weighted average.
        
        Final Score = (Momentum×0.25) + (Volume×0.20) + (RelStrength×0.20) 
                    + (NewsSentiment×0.20) + (Catalysts×0.15)
        """
        composite = (
            momentum_score * self.weights['momentum'] +
            volume_score * self.weights['volume'] +
            rel_strength_score * self.weights['relative_strength'] +
            news_sentiment_score * self.weights['news_sentiment'] +
            catalyst_score * self.weights['catalysts']
        )
        
        return min(100, max(0, composite))
