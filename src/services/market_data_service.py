"""Market data service for real-time price information"""

import asyncio
from datetime import datetime
from typing import Dict, List, Optional
import aiohttp
from src.models.market_data import MarketData, Candle
from src.utils.logger import get_logger
from config.settings import Settings

logger = get_logger(__name__)


class MarketDataService:
    """Service for fetching and managing market data from Binance"""
    
    def __init__(self):
        """Initialize market data service"""
        self.base_url = "https://api.binance.com" if not Settings.USE_TESTNET else "https://testnet.binance.vision"
        self.ws_url = "wss://stream.binance.com:9443" if not Settings.USE_TESTNET else "wss://stream.testnet.binance.vision:9443"
        self.cache: Dict[str, MarketData] = {}
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    async def get_price(self, symbol: str) -> float:
        """Get current price for a symbol
        
        Args:
            symbol: Trading symbol (e.g., BTCUSDT)
        
        Returns:
            Current price
        """
        try:
            url = f"{self.base_url}/api/v3/ticker/price"
            params = {"symbol": symbol}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    return float(data["price"])
                else:
                    logger.error(f"Failed to get price for {symbol}: {response.status}")
                    raise Exception(f"API error: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
            raise
    
    async def get_market_data(self, symbol: str) -> MarketData:
        """Get comprehensive market data for a symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            MarketData object
        """
        try:
            url = f"{self.base_url}/api/v3/ticker/24hr"
            params = {"symbol": symbol}
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    market_data = MarketData(
                        symbol=symbol,
                        timestamp=datetime.utcnow(),
                        last_price=float(data["lastPrice"]),
                        bid_price=float(data.get("bidPrice", data["lastPrice"])),
                        ask_price=float(data.get("askPrice", data["lastPrice"])),
                        high_24h=float(data["highPrice"]),
                        low_24h=float(data["lowPrice"]),
                        volume_24h=float(data["volume"]),
                        price_change_24h_percent=float(data["priceChangePercent"]),
                        volume_usd=float(data.get("quoteAssetVolume", 0))
                    )
                    
                    self.cache[symbol] = market_data
                    logger.info(f"Updated market data for {symbol}")
                    return market_data
                else:
                    logger.error(f"Failed to get market data for {symbol}: {response.status}")
                    raise Exception(f"API error: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching market data for {symbol}: {e}")
            raise
    
    async def get_historical_klines(self, symbol: str, interval: str = "1h", limit: int = 100) -> List[Candle]:
        """Get historical klines (candlestick data)
        
        Args:
            symbol: Trading symbol
            interval: Kline interval (1m, 5m, 1h, 1d, etc.)
            limit: Number of klines to fetch
        
        Returns:
            List of Candle objects
        """
        try:
            url = f"{self.base_url}/api/v3/klines"
            params = {
                "symbol": symbol,
                "interval": interval,
                "limit": min(limit, 1000)  # Binance limit is 1000
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    candles = []
                    for kline in data:
                        candle = Candle(
                            timestamp=datetime.fromtimestamp(kline[0] / 1000),
                            open=float(kline[1]),
                            high=float(kline[2]),
                            low=float(kline[3]),
                            close=float(kline[4]),
                            volume=float(kline[7])
                        )
                        candles.append(candle)
                    
                    logger.info(f"Fetched {len(candles)} klines for {symbol}")
                    return candles
                else:
                    logger.error(f"Failed to get klines for {symbol}: {response.status}")
                    raise Exception(f"API error: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching klines for {symbol}: {e}")
            raise
    
    def get_cached_price(self, symbol: str) -> Optional[float]:
        """Get cached price for a symbol
        
        Args:
            symbol: Trading symbol
        
        Returns:
            Cached price or None
        """
        if symbol in self.cache:
            return self.cache[symbol].last_price
        return None
    
    async def get_order_book(self, symbol: str, limit: int = 5) -> Dict:
        """Get order book for a symbol
        
        Args:
            symbol: Trading symbol
            limit: Depth limit (5, 10, 20, 50, 100, 500, 1000)
        
        Returns:
            Order book with bids and asks
        """
        try:
            url = f"{self.base_url}/api/v3/depth"
            params = {
                "symbol": symbol,
                "limit": limit
            }
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    return await response.json()
                else:
                    logger.error(f"Failed to get order book for {symbol}: {response.status}")
                    raise Exception(f"API error: {response.status}")
        except Exception as e:
            logger.error(f"Error fetching order book for {symbol}: {e}")
            raise
