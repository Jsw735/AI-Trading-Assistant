"""Integration tests for signal generation."""

import unittest
from src.fetchers.data_fetcher import DataFetcher
from src.processors.signal_processor import SignalProcessor


class TestSignalGeneration(unittest.TestCase):
    """Test end-to-end signal generation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.config = {
            'account': {'total_capital': 1000, 'position_size': 50},
            'filters': {'min_price': 5, 'max_price': 200, 'min_avg_volume': 1000000},
            'signals': {'momentum_period': 14}
        }
    
    def test_fetch_data(self):
        """Test data fetching."""
        fetcher = DataFetcher(self.config)
        data = fetcher.fetch_all_data()
        self.assertIsNotNone(data)
    
    def test_signal_processing(self):
        """Test signal processing."""
        # Mock data
        mock_data = {'prices': {}, 'news': {}}
        processor = SignalProcessor(self.config, mock_data)
        signals = processor.generate_signals()
        self.assertIsInstance(signals, list)


if __name__ == '__main__':
    unittest.main()
