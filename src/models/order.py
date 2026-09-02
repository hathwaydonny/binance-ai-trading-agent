"""Order data model"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class OrderSide(str, Enum):
    """Order side"""
    BUY = "BUY"
    SELL = "SELL"


class OrderType(str, Enum):
    """Order type"""
    LIMIT = "LIMIT"
    MARKET = "MARKET"
    STOP_LOSS = "STOP_LOSS"
    TAKE_PROFIT = "TAKE_PROFIT"
    STOP_LOSS_LIMIT = "STOP_LOSS_LIMIT"
    TRAILING_STOP = "TRAILING_STOP"


class OrderStatus(str, Enum):
    """Order status"""
    NEW = "NEW"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    FILLED = "FILLED"
    CANCELLED = "CANCELLED"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass
class Order:
    """Represents a single order"""
    
    order_id: str
    symbol: str
    side: OrderSide
    order_type: OrderType
    quantity: float
    price: Optional[float] = None  # None for market orders
    
    # Order status
    status: OrderStatus = OrderStatus.NEW
    created_time: datetime = None
    update_time: Optional[datetime] = None
    
    # Fill information
    filled_quantity: float = 0.0
    filled_price: Optional[float] = None
    
    # Additional parameters
    stop_price: Optional[float] = None  # For stop orders
    time_in_force: str = "GTC"  # Good-Til-Cancel
    
    # Metadata
    trade_id: Optional[str] = None
    agent_id: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate order data"""
        if self.created_time is None:
            self.created_time = datetime.utcnow()
        
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
    
    def is_open(self) -> bool:
        """Check if order is still open"""
        return self.status in [OrderStatus.NEW, OrderStatus.PARTIALLY_FILLED]
    
    def is_closed(self) -> bool:
        """Check if order is closed"""
        return self.status in [OrderStatus.FILLED, OrderStatus.CANCELLED, OrderStatus.REJECTED]
    
    def fill_percentage(self) -> float:
        """Get fill percentage"""
        if self.quantity == 0:
            return 0.0
        return (self.filled_quantity / self.quantity) * 100
