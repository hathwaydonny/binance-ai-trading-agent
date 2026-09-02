"""Market data models"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional


@dataclass
class Candle:
    """OHLCV candle (price bar)"""
    
    timestamp: datetime
    open: float
    high: float
    low: float
    close: float
    volume: float
    
    def mid_price(self) -> float:
        """Calculate mid price"""
        return (self.high + self.low) / 2
    
    def range(self) -> float:
        """Calculate price range (high - low)"""
        return self.high - self.low
    
    def body(self) -> float:
        """Calculate candle body (close - open)"""
        return abs(self.close - self.open)


@dataclass
class MarketData:
    """Real-time market data for a symbol"""
    
    symbol: str
    timestamp: datetime
    
    # Current price information
    last_price: float
    bid_price: float
    ask_price: float
    
    # Price statistics
    high_24h: float
    low_24h: float
    volume_24h: float
    
    # Technical indicators
    price_change_24h_percent: float
    
    # Additional data
    volume_usd: Optional[float] = None
    makers_buy_total: Optional[float] = None
    makers_sell_total: Optional[float] = None
    
    def spread(self) -> float:
        """Calculate bid-ask spread in percentage"""
        if self.bid_price == 0:
            return 0.0
        return ((self.ask_price - self.bid_price) / self.bid_price) * 100
    
    def mid_price(self) -> float:
        """Calculate mid price"""
        return (self.bid_price + self.ask_price) / 2
    
    def is_bullish_24h(self) -> bool:
        """Check if price is up in last 24h"""
        return self.price_change_24h_percent > 0
    
    def volatility_24h(self) -> float:
        """Estimate 24h volatility"""
        if self.low_24h == 0:
            return 0.0
        return ((self.high_24h - self.low_24h) / self.low_24h) * 100
