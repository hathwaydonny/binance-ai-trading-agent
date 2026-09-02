"""MCP Resources - expose trading agent capabilities as resources"""

from typing import Dict, List, Optional
from dataclasses import asdict
from src.models.market_data import MarketData
from src.models.order import Order
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BinanceResources:
    """MCP Resources for Binance trading"""
    
    @staticmethod
    def get_market_data_schema() -> Dict:
        """Get market data resource schema
        
        Returns:
            JSON schema for market data
        """
        return {
            "type": "object",
            "title": "MarketData",
            "description": "Real-time market data for a trading symbol",
            "properties": {
                "symbol": {"type": "string", "description": "Trading symbol"},
                "last_price": {"type": "number", "description": "Last traded price"},
                "bid_price": {"type": "number", "description": "Current bid price"},
                "ask_price": {"type": "number", "description": "Current ask price"},
                "high_24h": {"type": "number", "description": "24h high price"},
                "low_24h": {"type": "number", "description": "24h low price"},
                "volume_24h": {"type": "number", "description": "24h trading volume"},
                "price_change_24h_percent": {"type": "number", "description": "24h price change %"},
                "timestamp": {"type": "string", "format": "date-time", "description": "Data timestamp"}
            },
            "required": ["symbol", "last_price", "bid_price", "ask_price"]
        }
    
    @staticmethod
    def get_order_schema() -> Dict:
        """Get order resource schema
        
        Returns:
            JSON schema for orders
        """
        return {
            "type": "object",
            "title": "Order",
            "description": "Trading order information",
            "properties": {
                "order_id": {"type": "string", "description": "Order ID"},
                "symbol": {"type": "string", "description": "Trading symbol"},
                "side": {"type": "string", "enum": ["BUY", "SELL"]},
                "type": {"type": "string", "enum": ["LIMIT", "MARKET"]},
                "quantity": {"type": "number", "description": "Order quantity"},
                "price": {"type": "number", "description": "Order price (for LIMIT orders)"},
                "status": {"type": "string", "description": "Order status"},
                "filled_quantity": {"type": "number", "description": "Filled quantity"},
                "created_time": {"type": "string", "format": "date-time"}
            },
            "required": ["order_id", "symbol", "side", "type", "quantity", "status"]
        }
    
    @staticmethod
    def get_account_schema() -> Dict:
        """Get account info resource schema
        
        Returns:
            JSON schema for account info
        """
        return {
            "type": "object",
            "title": "Account",
            "description": "Trading account information",
            "properties": {
                "total_balance": {"type": "number", "description": "Total account balance in USDT"},
                "free_balance": {"type": "number", "description": "Free/available balance"},
                "locked_balance": {"type": "number", "description": "Balance locked in open orders"},
                "maker_commission": {"type": "number", "description": "Maker commission rate"},
                "taker_commission": {"type": "number", "description": "Taker commission rate"},
                "open_positions": {"type": "integer", "description": "Number of open positions"}
            },
            "required": ["total_balance", "free_balance"]
        }
