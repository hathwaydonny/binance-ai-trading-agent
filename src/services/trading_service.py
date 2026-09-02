"""Trading service for executing orders"""

import asyncio
import hashlib
import hmac
import time
from datetime import datetime
from typing import Dict, List, Optional
from enum import Enum
import aiohttp

from src.models.order import Order, OrderSide, OrderType, OrderStatus
from src.utils.logger import get_logger
from src.utils.validators import validate_symbol, validate_quantity, validate_price
from config.settings import Settings

logger = get_logger(__name__)


class TradingService:
    """Service for executing trades on Binance"""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize trading service
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com" if not Settings.USE_TESTNET else "https://testnet.binance.vision"
        self.session: Optional[aiohttp.ClientSession] = None
        self.orders: Dict[str, Order] = {}  # Cache of orders
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_request_kwargs(self, endpoint: str, method: str = "GET", params: Dict = None) -> Dict:
        """Generate request kwargs with authentication
        
        Args:
            endpoint: API endpoint
            method: HTTP method
            params: Query parameters
        
        Returns:
            Request kwargs
        """
        if params is None:
            params = {}
        
        params["timestamp"] = int(time.time() * 1000)
        
        # Create query string
        query_string = "&".join([f"{k}={v}" for k, v in sorted(params.items())])
        
        # Sign request
        signature = hmac.new(
            self.api_secret.encode(),
            query_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        params["signature"] = signature
        
        kwargs = {
            "params": params,
            "headers": {
                "X-MBX-APIKEY": self.api_key
            }
        }
        
        return kwargs
    
    async def place_limit_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        price: float,
        time_in_force: str = "GTC"
    ) -> Order:
        """Place a limit order
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            price: Order price
            time_in_force: GTC, IOC, FOK
        
        Returns:
            Order object
        """
        try:
            # Validate inputs
            validate_symbol(symbol)
            validate_quantity(quantity)
            validate_price(price)
            
            # Prepare request
            endpoint = "/api/v3/order"
            params = {
                "symbol": symbol,
                "side": side.value,
                "type": "LIMIT",
                "timeInForce": time_in_force,
                "quantity": quantity,
                "price": price
            }
            
            kwargs = self._get_request_kwargs(endpoint, "POST", params)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.post(url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    order = Order(
                        order_id=str(data["orderId"]),
                        symbol=symbol,
                        side=side,
                        order_type=OrderType.LIMIT,
                        quantity=quantity,
                        price=price,
                        status=OrderStatus(data["status"]),
                        created_time=datetime.fromtimestamp(data["transactTime"] / 1000)
                    )
                    
                    self.orders[order.order_id] = order
                    logger.info(f"Order placed: {symbol} {side.value} {quantity} @ {price}")
                    return order
                else:
                    error = await response.text()
                    logger.error(f"Failed to place order: {error}")
                    raise Exception(f"Order placement failed: {error}")
        except Exception as e:
            logger.error(f"Error placing limit order: {e}")
            raise
    
    async def place_market_order(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float
    ) -> Order:
        """Place a market order
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
        
        Returns:
            Order object
        """
        try:
            # Validate inputs
            validate_symbol(symbol)
            validate_quantity(quantity)
            
            # Prepare request
            endpoint = "/api/v3/order"
            params = {
                "symbol": symbol,
                "side": side.value,
                "type": "MARKET",
                "quantity": quantity
            }
            
            kwargs = self._get_request_kwargs(endpoint, "POST", params)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.post(url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    # Market orders are immediately filled
                    filled_price = float(data["fills"][0]["price"]) if data["fills"] else 0
                    
                    order = Order(
                        order_id=str(data["orderId"]),
                        symbol=symbol,
                        side=side,
                        order_type=OrderType.MARKET,
                        quantity=quantity,
                        price=None,
                        status=OrderStatus.FILLED,
                        created_time=datetime.fromtimestamp(data["transactTime"] / 1000),
                        filled_quantity=quantity,
                        filled_price=filled_price
                    )
                    
                    self.orders[order.order_id] = order
                    logger.info(f"Market order executed: {symbol} {side.value} {quantity}")
                    return order
                else:
                    error = await response.text()
                    logger.error(f"Failed to place market order: {error}")
                    raise Exception(f"Market order failed: {error}")
        except Exception as e:
            logger.error(f"Error placing market order: {e}")
            raise
    
    async def cancel_order(self, symbol: str, order_id: str) -> bool:
        """Cancel an order
        
        Args:
            symbol: Trading symbol
            order_id: Order ID to cancel
        
        Returns:
            True if successful
        """
        try:
            validate_symbol(symbol)
            
            endpoint = "/api/v3/order"
            params = {
                "symbol": symbol,
                "orderId": order_id
            }
            
            kwargs = self._get_request_kwargs(endpoint, "DELETE", params)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.delete(url, **kwargs) as response:
                if response.status == 200:
                    logger.info(f"Order cancelled: {symbol} {order_id}")
                    return True
                else:
                    error = await response.text()
                    logger.error(f"Failed to cancel order: {error}")
                    return False
        except Exception as e:
            logger.error(f"Error cancelling order: {e}")
            raise
    
    async def get_order_status(self, symbol: str, order_id: str) -> OrderStatus:
        """Get order status
        
        Args:
            symbol: Trading symbol
            order_id: Order ID
        
        Returns:
            Order status
        """
        try:
            validate_symbol(symbol)
            
            endpoint = "/api/v3/order"
            params = {
                "symbol": symbol,
                "orderId": order_id
            }
            
            kwargs = self._get_request_kwargs(endpoint, "GET", params)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    return OrderStatus(data["status"])
                else:
                    logger.error(f"Failed to get order status: {response.status}")
                    raise Exception(f"Failed to get order status")
        except Exception as e:
            logger.error(f"Error fetching order status: {e}")
            raise
    
    async def get_open_orders(self, symbol: Optional[str] = None) -> List[Order]:
        """Get open orders
        
        Args:
            symbol: Trading symbol (optional, None for all symbols)
        
        Returns:
            List of open orders
        """
        try:
            endpoint = "/api/v3/openOrders"
            params = {}
            if symbol:
                validate_symbol(symbol)
                params["symbol"] = symbol
            
            kwargs = self._get_request_kwargs(endpoint, "GET", params)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    orders = []
                    for order_data in data:
                        order = Order(
                            order_id=str(order_data["orderId"]),
                            symbol=order_data["symbol"],
                            side=OrderSide(order_data["side"]),
                            order_type=OrderType(order_data["type"]),
                            quantity=float(order_data["origQty"]),
                            price=float(order_data.get("price", 0)),
                            status=OrderStatus(order_data["status"]),
                            created_time=datetime.fromtimestamp(order_data["time"] / 1000),
                            filled_quantity=float(order_data["executedQty"])
                        )
                        orders.append(order)
                    
                    logger.info(f"Fetched {len(orders)} open orders")
                    return orders
                else:
                    logger.error(f"Failed to get open orders: {response.status}")
                    raise Exception(f"Failed to get open orders")
        except Exception as e:
            logger.error(f"Error fetching open orders: {e}")
            raise
