"""
Data fetcher module.
Responsible for retrieving market data from external APIs.
Supports Polygon, Finnhub, and other sources with fallback to mock data.
"""

import logging
import requests
import random
from typing import Dict, List, Optional
from datetime import datetime, timedelta


# Data structures for type hints
class PriceData:
    """Stock price and volume data."""
    def __init__(self, ticker: str, price: float, volume: int, rsi: float, atr: float, pct_change: float):
        self.ticker = ticker
        self.price = price
        self.volume = volume
        self.rsi = rsi
        self.atr = atr
        self.pct_change = pct_change
    
    def to_dict(self):
        return {
            'ticker': self.ticker,
            'price': self.price,
            'volume': self.volume,
            'rsi': self.rsi,
            'atr': self.atr,
            'pct_change': self.pct_change
        }


class NewsItem:
    """News article and sentiment data."""
    def __init__(self, ticker: str, headline: str, source: str, sentiment: str, timestamp: str, summary: str = ""):
        self.ticker = ticker
        self.headline = headline
        self.source = source
        self.sentiment = sentiment  # 'Positive', 'Neutral', 'Negative'
        self.timestamp = timestamp
        self.summary = summary
    
    def to_dict(self):
        return {
            'ticker': self.ticker,
            'headline': self.headline,
            'source': self.source,
            'sentiment': self.sentiment,
            'timestamp': self.timestamp,
            'summary': self.summary
        }


class Fundamental:
    """Fundamental company data."""
    def __init__(self, ticker: str, market_cap_millions: float, float_millions: float, pe_ratio: float):
        self.ticker = ticker
        self.market_cap_millions = market_cap_millions
        self.float_millions = float_millions
        self.pe_ratio = pe_ratio
    
    def to_dict(self):
        return {
            'ticker': self.ticker,
            'market_cap_millions': self.market_cap_millions,
            'float_millions': self.float_millions,
            'pe_ratio': self.pe_ratio
        }


class DataFetcher:
    """Fetches price, volume, news, and fundamental data from APIs."""
    
    def __init__(self, config: dict):
        """Initialize with configuration."""
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.polygon_api_key = config.get('data_sources', {}).get('polygon_api_key')
        self.finnhub_api_key = config.get('data_sources', {}).get('finnhub_api_key')
        self.session = requests.Session()
    
    def fetch_price_volume_data(self, symbols: List[str]) -> Dict[str, dict]:
        """
        Fetch price and volume data from Polygon or mock data.
        
        Args:
            symbols: List of stock tickers
            
        Returns:
            Dict with ticker: {price, volume, rsi, atr, pct_change, 20day_avg_volume}
        """
        self.logger.info(f"Fetching price/volume data for {len(symbols)} symbols...")
        
        data = {}
        
        for ticker in symbols:
            try:
                # Attempt real API call if key is set
                if self.polygon_api_key and self.polygon_api_key != "YOUR_POLYGON_API_KEY":
                    # TODO: Implement Polygon API call
                    # https://polygon.io/docs/stocks/get-previous-close
                    pass
                
                # Fallback: Mock data for testing
                data[ticker] = self._mock_price_data(ticker)
            
            except Exception as e:
                self.logger.warning(f"Failed to fetch price data for {ticker}: {e}")
                data[ticker] = self._mock_price_data(ticker)
        
        return data
    
    def fetch_news_data(self, symbols: List[str]) -> Dict[str, List[dict]]:
        """
        Fetch news and catalysts from Finnhub or mock data.
        
        Args:
            symbols: List of stock tickers
            
        Returns:
            Dict with ticker: [list of news articles as dicts]
        """
        self.logger.info(f"Fetching news data for {len(symbols)} symbols...")
        
        data = {}
        
        for ticker in symbols:
            try:
                # Attempt real API call if key is set
                if self.finnhub_api_key and self.finnhub_api_key != "YOUR_FINNHUB_API_KEY":
                    # TODO: Implement Finnhub API call
                    # https://finnhub.io/docs/api/company-news
                    pass
                
                # Fallback: Mock news for testing
                data[ticker] = self._mock_news_data(ticker)
            
            except Exception as e:
                self.logger.warning(f"Failed to fetch news data for {ticker}: {e}")
                data[ticker] = self._mock_news_data(ticker)
        
        return data
    
    def fetch_fundamentals(self, symbols: List[str]) -> Dict[str, dict]:
        """
        Fetch fundamental data from Financial Modeling Prep or mock data.
        
        Args:
            symbols: List of stock tickers
            
        Returns:
            Dict with ticker: {market_cap_millions, float_millions, pe_ratio}
        """
        self.logger.info(f"Fetching fundamentals for {len(symbols)} symbols...")
        
        data = {}
        
        for ticker in symbols:
            try:
                # Attempt real API call if key is set
                if self.finnhub_api_key and self.finnhub_api_key != "YOUR_FINNHUB_API_KEY":
                    # TODO: Implement Finnhub company profile API call
                    # https://finnhub.io/docs/api/company-profile
                    pass
                
                # Fallback: Mock data for testing
                data[ticker] = self._mock_fundamental_data(ticker)
            
            except Exception as e:
                self.logger.warning(f"Failed to fetch fundamentals for {ticker}: {e}")
                data[ticker] = self._mock_fundamental_data(ticker)
        
        return data
    
    def fetch_sector_data(self, sector_etfs: List[str]) -> Dict[str, dict]:
        """
        Fetch sector ETF data for relative strength calculation.
        
        Args:
            sector_etfs: List of ETF tickers (XLK, XLF, etc.)
            
        Returns:
            Dict with etf: {price, pct_change}
        """
        self.logger.info(f"Fetching sector ETF data for {len(sector_etfs)} ETFs...")
        
        data = {}
        
        for etf in sector_etfs:
            try:
                # Attempt real API call if key is set
                if self.polygon_api_key and self.polygon_api_key != "YOUR_POLYGON_API_KEY":
                    # TODO: Implement Polygon API call for ETF data
                    pass
                
                # Fallback: Mock sector data
                data[etf] = self._mock_sector_data(etf)
            
            except Exception as e:
                self.logger.warning(f"Failed to fetch sector data for {etf}: {e}")
                data[etf] = self._mock_sector_data(etf)
        
        return data
    
    def fetch_all_data(self) -> Dict:
        """
        Master method to fetch all required data.
        
        Returns:
            Dict with all market data: {timestamp, prices, news, fundamentals, sectors}
        """
        self.logger.info("Starting data fetch cycle...")
        
        # TODO: Read from watchlist file or database
        default_symbols = ['AAPL', 'MSFT', 'TSLA', 'NVDA', 'GOOGL']
        sector_etfs = ['XLK', 'XLF', 'XLE', 'XLI', 'XLV']
        
        all_data = {
            'timestamp': datetime.now().isoformat(),
            'prices': self.fetch_price_volume_data(default_symbols),
            'news': self.fetch_news_data(default_symbols),
            'fundamentals': self.fetch_fundamentals(default_symbols),
            'sectors': self.fetch_sector_data(sector_etfs)
        }
        
        return all_data
    
    # ===== MOCK DATA GENERATORS (for testing without API keys) =====
    
    def _mock_price_data(self, ticker: str) -> dict:
        """Generate realistic mock price data."""
        base_prices = {
            'AAPL': 150.0, 'MSFT': 370.0, 'TSLA': 92.0,
            'NVDA': 145.0, 'GOOGL': 155.0, 'XLK': 450.0
        }
        
        base_price = base_prices.get(ticker, 100.0)
        price = base_price + random.uniform(-5, 5)
        volume = random.randint(50000000, 150000000)
        rsi = random.uniform(30, 70)
        atr = random.uniform(1.0, 3.0)
        pct_change = random.uniform(-3.0, 5.0)
        
        return {
            'ticker': ticker,
            'price': round(price, 2),
            'volume': volume,
            'rsi': round(rsi, 2),
            'atr': round(atr, 2),
            'pct_change': round(pct_change, 2),
            'volume_20day_avg': volume - random.randint(10000000, 50000000)
        }
    
    def _mock_news_data(self, ticker: str) -> List[dict]:
        """Generate realistic mock news data."""
        news_templates = [
            {'headline': f'{ticker} reports Q4 earnings beat', 'sentiment': 'Positive'},
            {'headline': f'{ticker} launches new product line', 'sentiment': 'Positive'},
            {'headline': f'{ticker} CEO discusses expansion plans', 'sentiment': 'Neutral'},
            {'headline': f'{ticker} faces supply chain challenges', 'sentiment': 'Negative'},
        ]
        
        selected = news_templates[:random.randint(1, 3)]
        for item in selected:
            item['ticker'] = ticker
            item['source'] = random.choice(['Reuters', 'Bloomberg', 'CNBC', 'MarketWatch'])
            item['timestamp'] = (datetime.now() - timedelta(hours=random.randint(0, 24))).isoformat()
            item['summary'] = f"AI-generated summary of {item['headline']}"
        
        return [news_dict for news_dict in selected]
    
    def _mock_fundamental_data(self, ticker: str) -> dict:
        """Generate realistic mock fundamental data."""
        fundamentals = {
            'AAPL': {'market_cap_millions': 3000000, 'float_millions': 15, 'pe_ratio': 28.5},
            'MSFT': {'market_cap_millions': 2800000, 'float_millions': 7, 'pe_ratio': 32.1},
            'TSLA': {'market_cap_millions': 1200000, 'float_millions': 3, 'pe_ratio': 65.3},
        }
        
        base = fundamentals.get(ticker, {
            'market_cap_millions': 500000,
            'float_millions': 5,
            'pe_ratio': 25.0
        })
        
        return {
            'ticker': ticker,
            'market_cap_millions': base['market_cap_millions'],
            'float_millions': base['float_millions'],
            'pe_ratio': base['pe_ratio']
        }
    
    def _mock_sector_data(self, etf: str) -> dict:
        """Generate realistic mock sector ETF data."""
        etf_prices = {
            'XLK': 450.0, 'XLF': 35.0, 'XLE': 75.0, 'XLI': 90.0, 'XLV': 140.0
        }
        
        base_price = etf_prices.get(etf, 100.0)
        price = base_price + random.uniform(-2, 2)
        pct_change = random.uniform(-2.0, 2.0)
        
        return {
            'etf': etf,
            'price': round(price, 2),
            'pct_change': round(pct_change, 2)
        }
