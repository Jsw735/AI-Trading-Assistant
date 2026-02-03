"""
Signal processor module.
Processes market data to generate trading signals and scores.
"""

import logging
import pandas as pd
from typing import Dict, List
from core.scoring import ScoringEngine


class SignalProcessor:
    """Processes market data and generates ranked trading signals."""
    
    def __init__(self, config: dict, market_data: dict):
        """Initialize with configuration and market data."""
        self.config = config
        self.market_data = market_data
        self.logger = logging.getLogger(__name__)
        self.scoring_engine = ScoringEngine(config)
    
    def apply_filters(self, signals: List[Dict]) -> List[Dict]:
        """
        Apply price, volume, market cap, and float filters.
        
        Returns:
            Filtered list of signals.
        """
        self.logger.info("Applying filters...")
        
        filters = self.config['filters']
        filtered = []
        
        for signal in signals:
            # Check price range
            if not (filters['min_price'] <= signal.get('price', 0) <= filters['max_price']):
                continue
            
            # Check volume
            if signal.get('volume', 0) < filters['min_avg_volume']:
                continue
            
            # Check market cap
            if signal.get('market_cap_millions', 0) < filters['min_market_cap_millions']:
                continue
            
            # Check float
            if signal.get('float_millions', 0) > filters['max_float_millions']:
                continue
            
            filtered.append(signal)
        
        self.logger.info(f"Filtered to {len(filtered)} signals from {len(signals)}")
        return filtered
    
    def generate_signals(self) -> List[Dict]:
        """
        Generate trading signals from market data.
        
        Returns:
            List of signal dicts with scores.
        """
        self.logger.info("Generating signals...")
        
        signals = []
        
        # TODO: Iterate through market data and calculate scores
        # For now, return empty list
        
        return signals
    
    def rank_signals(self, signals: List[Dict], top_n: int = 20) -> List[Dict]:
        """
        Rank signals by score and apply risk filters.
        
        Args:
            signals: List of signal dicts
            top_n: Return top N signals
            
        Returns:
            Top ranked signals with risk assessment.
        """
        self.logger.info(f"Ranking {len(signals)} signals...")
        
        # Sort by score descending
        ranked = sorted(signals, key=lambda x: x.get('score', 0), reverse=True)
        
        # Apply risk controls
        account = self.config['account']
        max_loss_per_trade = account['max_loss_per_trade_pct']
        
        for signal in ranked:
            # Calculate position sizing and risk
            signal['position_size'] = account['position_size']
            signal['stop_loss_pct'] = max_loss_per_trade
            signal['risk_score'] = self._calculate_risk_score(signal)
        
        # Return top N
        return ranked[:top_n]
    
    def _calculate_risk_score(self, signal: Dict) -> float:
        """
        Calculate risk score for signal (0-100, lower = less risky).
        """
        # Simple implementation
        volatility = signal.get('volatility', 0)
        risk_score = min(100, volatility * 10)
        return risk_score
