"""
Main entry point for AI Trading Assistant.
Orchestrates data fetching, signal generation, and Excel output.
"""

import json
import logging
import sys
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from fetchers.data_fetcher import DataFetcher
from processors.signal_processor import SignalProcessor
from utils.excel_writer import ExcelWriter
from utils.logger import setup_logger


def load_config(config_path: str = "config/default_config.json") -> dict:
    """Load configuration from JSON file."""
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        print(f"✓ Config loaded from {config_path}")
        return config
    except FileNotFoundError:
        raise FileNotFoundError(f"Config file not found: {config_path}")
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in config file: {e}")


def run_trading_analysis():
    """
    Main workflow:
    1. Load configuration
    2. Fetch market data (prices, volume, news, fundamentals)
    3. Calculate signals and scores
    4. Filter and rank signals
    5. Generate Excel output
    6. Send alerts (if applicable)
    """
    
    logger = setup_logger("trading_assistant")
    
    print("\n" + "="*60)
    print("AI TRADING ASSISTANT - SIGNAL GENERATION")
    print("="*60)
    
    try:
        # 1. Load config
        logger.info("Loading configuration...")
        config = load_config()
        
        # 2. Fetch data
        logger.info("Fetching market data...")
        fetcher = DataFetcher(config)
        market_data = fetcher.fetch_all_data()
        
        logger.info(f"  - Fetched {len(market_data.get('prices', {}))} price quotes")
        logger.info(f"  - Fetched {sum(len(v) for v in market_data.get('news', {}).values())} news items")
        logger.info(f"  - Fetched {len(market_data.get('fundamentals', {}))} fundamentals")
        logger.info(f"  - Fetched {len(market_data.get('sectors', {}))} sector ETFs")
        
        # 3. Process signals
        logger.info("Processing signals...")
        processor = SignalProcessor(config)
        signals_ranked = processor.process_data(market_data)
        
        logger.info(f"  - Generated {len(signals_ranked)} ranked signals")
        
        # 4. Generate Excel
        logger.info("Generating Excel output...")
        excel_writer = ExcelWriter(config)
        output_file = excel_writer.write_workbook(signals_ranked, market_data)
        
        logger.info(f"Output written to: {output_file}")
        print(f"\n✓ Analysis complete! Output: {output_file}")
        print(f"\nTop signals generated:")
        for i, signal in enumerate(signals_ranked[:5], 1):
            print(f"  {i}. {signal['ticker']}: Score {signal['composite_score']}/100")
        
        # 5. Send alerts (if configured)
        # TODO: Implement alert logic
        
        return output_file
        
    except Exception as e:
        logger.error(f"Error during analysis: {e}", exc_info=True)
        print(f"\n✗ Error: {e}")
        return None


if __name__ == "__main__":
    output = run_trading_analysis()
    sys.exit(0 if output else 1)
