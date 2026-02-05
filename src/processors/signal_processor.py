"""
Signal processor module.
Applies filters, calculates scores, generates ranked trading signals.
"""

import logging
from typing import Dict, List, Optional
from src.core.scoring import ScoringEngine


class SignalProcessor:
    """Processes market data and generates ranked trading signals."""
    
    def __init__(self, config: dict):
        """Initialize with configuration and scoring engine."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.scoring_engine = ScoringEngine()
        self.filters = config.get('filters', {})
        self.signals_config = config.get('signals', {})
    
    def process_data(self, market_data: Dict) -> List[Dict]:
        """
        Master method: filter, score, and rank signals.
        
        Args:
            market_data: Dict with timestamp, prices, news, fundamentals, sectors
            
        Returns:
            List of signal dicts sorted by composite score (highest first)
        """
        self.logger.info("Processing market data into signals...")
        
        # Step 1: Apply filters
        filtered_symbols = self.apply_filters(
            market_data.get('prices', {}),
            market_data.get('fundamentals', {})
        )
        self.logger.info(f"After filters: {len(filtered_symbols)} symbols remain")
        
        # Step 2: Score each symbol using all 5 metrics
        signals = self.generate_signals(
            filtered_symbols,
            market_data.get('prices', {}),
            market_data.get('news', {}),
            market_data.get('fundamentals', {}),
            market_data.get('sectors', {})
        )
        self.logger.info(f"Generated {len(signals)} scoring signals")
        
        # Step 3: Rank, apply risk controls, return top signals
        ranked_signals = self.rank_signals(signals)
        
        self.logger.info(f"Final ranked signals: {len(ranked_signals)}")
        
        return ranked_signals
    
    def apply_filters(self, prices: Dict, fundamentals: Dict) -> List[str]:
        """
        Filter symbols based on price, volume, market cap, float criteria.
        
        Args:
            prices: Dict of ticker -> {price, volume, volume_20day_avg, ...}
            fundamentals: Dict of ticker -> {market_cap_millions, float_millions, ...}
            
        Returns:
            List of tickers that pass all filters
        """
        filtered = []
        
        min_price = self.filters.get('min_price', 2.0)
        max_price = self.filters.get('max_price', 500.0)
        min_volume = self.filters.get('min_avg_volume', 500000)
        min_market_cap = self.filters.get('min_market_cap_millions', 100)
        max_float = self.filters.get('max_float_millions', 250)
        
        for ticker, price_data in prices.items():
            price = price_data.get('price', 0)
            volume = price_data.get('volume', 0)
            
            # Price filter
            if price < min_price or price > max_price:
                self.logger.debug(f"  {ticker}: price {price} outside range [{min_price}, {max_price}]")
                continue
            
            # Volume filter
            if volume < min_volume:
                self.logger.debug(f"  {ticker}: volume {volume} below {min_volume}")
                continue
            
            # Fundamentals filters
            fund_data = fundamentals.get(ticker, {})
            market_cap = fund_data.get('market_cap_millions', 0)
            float_shares = fund_data.get('float_millions', 0)
            
            if market_cap < min_market_cap:
                self.logger.debug(f"  {ticker}: market cap {market_cap}M below {min_market_cap}M")
                continue
            
            if float_shares > max_float:
                self.logger.debug(f"  {ticker}: float {float_shares}M exceeds {max_float}M")
                continue
            
            # Passed all filters
            filtered.append(ticker)
        
        return filtered
    
    def generate_signals(
        self,
        symbols: List[str],
        prices: Dict,
        news: Dict,
        fundamentals: Dict,
        sectors: Dict
    ) -> List[Dict]:
        """
        Generate signals by calculating composite scores for each symbol.
        
        Args:
            symbols: Filtered list of tickers
            prices: Price/volume data
            news: News and sentiment data
            fundamentals: Fundamental data
            sectors: Sector ETF data
            
        Returns:
            List of signal dicts: {ticker, composite_score, momentum_score, volume_score, ...}
        """
        signals = []
        
        for ticker in symbols:
            price_data = prices.get(ticker, {})
            news_data = news.get(ticker, [])
            fund_data = fundamentals.get(ticker, {})
            
            # Calculate all 5 component scores
            momentum_score = self.scoring_engine.calculate_momentum_score(
                rsi=price_data.get('rsi', 50)
            )
            
            volume_score = self.scoring_engine.calculate_volume_score(
                current_volume=price_data.get('volume', 0),
                avg_volume=price_data.get('volume_20day_avg', 0)
            )
            
            # Relative strength vs sector
            sector_etf = self._find_sector_etf(ticker)
            stock_pct_change = price_data.get('pct_change', 0)
            sector_pct_change = sectors.get(sector_etf, {}).get('pct_change', 0)
            
            relative_strength_score = self.scoring_engine.calculate_relative_strength_score(
                stock_pct_change=stock_pct_change,
                sector_pct_change=sector_pct_change
            )
            
            # News sentiment score - count positive articles
            positive_count = sum(1 for item in news_data if item.get('sentiment') == 'Positive')
            news_sentiment_score = self.scoring_engine.calculate_news_sentiment_score(
                positive_articles=positive_count,
                total_articles=len(news_data) if news_data else 1
            )
            
            # Catalyst score (simple keyword matching)
            catalyst_keywords = ['beat', 'launch', 'expansion', 'partnership', 'acquisition']
            catalyst_found = False
            
            for article in news_data:
                headline = article.get('headline', '').lower()
                if any(keyword in headline for keyword in catalyst_keywords):
                    catalyst_found = True
                    break
            
            # Pass catalyst data as list of dicts (empty or with one catalyst)
            catalyst_list = [{'name': 'positive_catalyst', 'weight': 1.0}] if catalyst_found else []
            catalyst_score = self.scoring_engine.calculate_catalyst_score(catalyst_list)
            
            # Calculate composite score
            composite_score = self.scoring_engine.calculate_composite_score(
                momentum_score=momentum_score,
                volume_score=volume_score,
                rel_strength_score=relative_strength_score,
                news_sentiment_score=news_sentiment_score,
                catalyst_score=catalyst_score
            )
            
            # Calculate risk score
            risk_score = self._calculate_risk_score(price_data)
            
            signal = {
                'ticker': ticker,
                'composite_score': round(composite_score, 2),
                'momentum_score': round(momentum_score, 2),
                'volume_score': round(volume_score, 2),
                'relative_strength_score': round(relative_strength_score, 2),
                'news_sentiment_score': round(news_sentiment_score, 2),
                'catalyst_score': round(catalyst_score, 2),
                'risk_score': round(risk_score, 2),
                'current_price': round(price_data.get('price', 0), 2),
                'atr': round(price_data.get('atr', 0), 2),
                'pct_change_today': round(price_data.get('pct_change', 0), 2),
                'rsi': round(price_data.get('rsi', 50), 2)
            }
            
            signals.append(signal)
        
        return signals
    
    def rank_signals(self, signals: List[Dict]) -> List[Dict]:
        """
        Rank signals by composite score and apply risk controls.
        
        Args:
            signals: List of signal dicts
            
        Returns:
            Top ranked signals filtered by score and risk thresholds
        """
        # Sort by composite score (highest first)
        ranked = sorted(signals, key=lambda x: x['composite_score'], reverse=True)
        
        # Apply threshold filters from config
        min_score = self.signals_config.get('min_composite_score', 50)
        max_risk = self.signals_config.get('max_acceptable_risk_score', 75)
        
        filtered_ranked = []
        for signal in ranked:
            if signal['composite_score'] >= min_score and signal['risk_score'] <= max_risk:
                filtered_ranked.append(signal)
        
        # Limit to top N signals
        max_signals = self.signals_config.get('max_signals_per_run', 10)
        
        return filtered_ranked[:max_signals]
    
    def _find_sector_etf(self, ticker: str) -> str:
        """Find sector ETF for a given stock."""
        # Simplified mapping; in production, use a database
        sector_map = {
            'AAPL': 'XLK', 'MSFT': 'XLK', 'GOOGL': 'XLK',  # Tech
            'JPM': 'XLF', 'BAC': 'XLF',  # Finance
            'XOM': 'XLE', 'CVX': 'XLE',  # Energy
            'JNJ': 'XLV', 'PFE': 'XLV',  # Healthcare
        }
        return sector_map.get(ticker, 'XLK')  # Default to tech
    
    def _calculate_risk_score(self, price_data: Dict) -> float:
        """
        Calculate risk score based on volatility (ATR) and recent price movement.
        Higher ATR = higher risk.
        
        Args:
            price_data: Dict with atr and pct_change
            
        Returns:
            Risk score 0-100
        """
        atr = price_data.get('atr', 1.0)
        price = price_data.get('price', 100)
        
        # ATR as % of price
        atr_pct = (atr / price) * 100 if price > 0 else 0
        
        # Map to 0-100 scale: 0-2% ATR = low risk (20), 5%+ = high risk (80)
        if atr_pct < 1:
            risk = 20
        elif atr_pct > 5:
            risk = 80
        else:
            risk = 20 + (atr_pct / 5) * 60
        
        return min(100, max(0, risk))
