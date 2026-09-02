"""Trade data model"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional
from enum import Enum


class TradeStatus(str, Enum):
    """Trade execution status"""
    PENDING = "pending"
    OPENED = "opened"
    CLOSED = "closed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class TradeType(str, Enum):
    """Type of trade"""
    LONG = "long"
    SHORT = "short"


@dataclass
class Trade:
    """Represents a single trade"""
    
    trade_id: str
    symbol: str
    trade_type: TradeType
    entry_price: float
    quantity: float
    entry_time: datetime
    status: TradeStatus = TradeStatus.PENDING
    
    # Exit information
    exit_price: Optional[float] = None
    exit_time: Optional[datetime] = None
    exit_reason: Optional[str] = None
    
    # Risk management
    stop_loss: Optional[float] = None
    take_profit: Optional[float] = None
    
    # Performance metrics
    pnl: Optional[float] = None
    pnl_percent: Optional[float] = None
    
    # Metadata
    strategy: str = "unknown"
    agent_decision: Optional[str] = None
    notes: Optional[str] = None
    
    def __post_init__(self):
        """Validate trade data"""
        if self.quantity <= 0:
            raise ValueError("Quantity must be positive")
        if self.entry_price <= 0:
            raise ValueError("Entry price must be positive")
    
    def close(self, exit_price: float, exit_reason: str = None):
        """Close the trade and calculate P&L"""
        self.exit_price = exit_price
        self.exit_time = datetime.utcnow()
        self.exit_reason = exit_reason
        self.status = TradeStatus.CLOSED
        
        # Calculate P&L
        if self.trade_type == TradeType.LONG:
            self.pnl = (exit_price - self.entry_price) * self.quantity
        else:  # SHORT
            self.pnl = (self.entry_price - exit_price) * self.quantity
        
        self.pnl_percent = (self.pnl / (self.entry_price * self.quantity)) * 100
    
    def is_profitable(self) -> bool:
        """Check if trade is profitable"""
        return self.pnl is not None and self.pnl > 0
    
    def duration_minutes(self) -> Optional[int]:
        """Get trade duration in minutes"""
        if self.exit_time:
            return int((self.exit_time - self.entry_time).total_seconds() / 60)
        return None
