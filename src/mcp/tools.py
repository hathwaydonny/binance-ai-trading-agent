"""MCP Tools - expose trading operations as tools"""

from typing import Dict, List, Any, Optional
from src.utils.logger import get_logger

logger = get_logger(__name__)


class BinanceTools:
    """MCP Tools for Binance trading operations"""
    
    @staticmethod
    def get_get_market_price_tool() -> Dict:
        """Get tool definition for fetching market price
        
        Returns:
            Tool definition
        """
        return {
            "name": "get_market_price",
            "description": "Get current market price for a trading symbol",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading symbol (e.g., BTCUSDT)"
                    }
                },
                "required": ["symbol"]
            }
        }
    
    @staticmethod
    def get_place_order_tool() -> Dict:
        """Get tool definition for placing orders
        
        Returns:
            Tool definition
        """
        return {
            "name": "place_order",
            "description": "Place a buy or sell order",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading symbol"
                    },
                    "side": {
                        "type": "string",
                        "enum": ["BUY", "SELL"],
                        "description": "Order side"
                    },
                    "quantity": {
                        "type": "number",
                        "description": "Order quantity"
                    },
                    "order_type": {
                        "type": "string",
                        "enum": ["LIMIT", "MARKET"],
                        "description": "Order type"
                    },
                    "price": {
                        "type": "number",
                        "description": "Order price (required for LIMIT orders)"
                    }
                },
                "required": ["symbol", "side", "quantity", "order_type"]
            }
        }
    
    @staticmethod
    def get_get_account_balance_tool() -> Dict:
        """Get tool definition for fetching account balance
        
        Returns:
            Tool definition
        """
        return {
            "name": "get_account_balance",
            "description": "Get account balance and asset information",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "asset": {
                        "type": "string",
                        "description": "Asset symbol (optional, leave empty for all assets)"
                    }
                },
                "required": []
            }
        }
    
    @staticmethod
    def get_get_open_orders_tool() -> Dict:
        """Get tool definition for fetching open orders
        
        Returns:
            Tool definition
        """
        return {
            "name": "get_open_orders",
            "description": "Get list of open orders",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Filter by trading symbol (optional)"
                    }
                },
                "required": []
            }
        }
    
    @staticmethod
    def get_analyze_market_tool() -> Dict:
        """Get tool definition for market analysis
        
        Returns:
            Tool definition
        """
        return {
            "name": "analyze_market",
            "description": "Analyze market data and generate trading signals",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "Trading symbol to analyze"
                    },
                    "interval": {
                        "type": "string",
                        "enum": ["1m", "5m", "1h", "4h", "1d"],
                        "description": "Candle interval"
                    }
                },
                "required": ["symbol"]
            }
        }
    
    @staticmethod
    def get_all_tools() -> List[Dict]:
        """Get all available tools
        
        Returns:
            List of all tool definitions
        """
        return [
            BinanceTools.get_get_market_price_tool(),
            BinanceTools.get_place_order_tool(),
            BinanceTools.get_get_account_balance_tool(),
            BinanceTools.get_get_open_orders_tool(),
            BinanceTools.get_analyze_market_tool()
        ]
