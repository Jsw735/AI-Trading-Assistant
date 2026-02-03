"""Unit tests for scoring engine."""

import unittest
from src.core.scoring import ScoringEngine


class TestScoringEngine(unittest.TestCase):
    """Test ScoringEngine methods."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'signals': {
                'rsi_period': 14,
                'rsi_overbought': 70,
                'rsi_oversold': 30
            }
        }
        self.engine = ScoringEngine(self.config)
    
    def test_momentum_score_oversold(self):
        """Test momentum score for RSI < 30 (oversold)."""
        score = self.engine.calculate_momentum_score(rsi=20, atr_val=1.0)
        self.assertGreater(score, 40)
    
    def test_momentum_score_overbought(self):
        """Test momentum score for RSI > 70 (overbought)."""
        score = self.engine.calculate_momentum_score(rsi=80, atr_val=1.0)
        self.assertGreater(score, 50)
    
    def test_volume_score_no_surge(self):
        """Test volume score when no surge."""
        score = self.engine.calculate_volume_score(current_volume=1000000, avg_volume=1000000)
        self.assertEqual(score, 0.0)
    
    def test_volume_score_with_surge(self):
        """Test volume score with significant surge."""
        score = self.engine.calculate_volume_score(current_volume=3000000, avg_volume=1000000, threshold=150)
        self.assertGreater(score, 0)
    
    def test_relative_strength_score(self):
        """Test relative strength calculation."""
        score = self.engine.calculate_relative_strength_score(
            stock_pct_change=5.0,
            sector_pct_change=-1.0,
            min_threshold=5.0
        )
        self.assertGreater(score, 25)


if __name__ == '__main__':
    unittest.main()
