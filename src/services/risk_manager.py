"""Risk management service"""

from typing import Optional, Dict, List
from datetime import datetime, timedelta
from src.models.trade import Trade, TradeStatus
from src.utils.logger import get_logger
from config.settings import Settings

logger = get_logger(__name__)


class RiskManager:
    """Service for managing trading risks and position limits"""
    
    def __init__(self):
        """Initialize risk manager"""
        self.max_position_size_usd = Settings.MAX_POSITION_SIZE_USD
        self.max_daily_loss_percent = Settings.MAX_DAILY_LOSS_PERCENT
        self.stop_loss_percent = Settings.STOP_LOSS_PERCENT
        self.take_profit_percent = Settings.TAKE_PROFIT_PERCENT
        self.open_trades: Dict[str, Trade] = {}
        self.closed_trades: List[Trade] = []
    
    def check_position_size_limit(self, position_size_usd: float) -> bool:
        """Check if position size is within limits
        
        Args:
            position_size_usd: Position size in USD
        
        Returns:
            True if within limits
        """
        if position_size_usd > self.max_position_size_usd:
            logger.warning(
                f"Position size {position_size_usd} exceeds limit {self.max_position_size_usd}"
            )
            return False
        return True
    
    def calculate_stop_loss(self, entry_price: float, is_long: bool = True) -> float:
        """Calculate stop loss price
        
        Args:
            entry_price: Entry price
            is_long: True for long positions, False for short
        
        Returns:
            Stop loss price
        """
        if is_long:
            return entry_price * (1 - self.stop_loss_percent / 100)
        else:
            return entry_price * (1 + self.stop_loss_percent / 100)
    
    def calculate_take_profit(self, entry_price: float, is_long: bool = True) -> float:
        """Calculate take profit price
        
        Args:
            entry_price: Entry price
            is_long: True for long positions, False for short
        
        Returns:
            Take profit price
        """
        if is_long:
            return entry_price * (1 + self.take_profit_percent / 100)
        else:
            return entry_price * (1 - self.take_profit_percent / 100)
    
    def add_open_trade(self, trade: Trade) -> None:
        """Add an open trade to tracking
        
        Args:
            trade: Trade object
        """
        self.open_trades[trade.trade_id] = trade
        logger.info(f"Added open trade: {trade.trade_id}")
    
    def close_trade(self, trade_id: str, exit_price: float, exit_reason: str = None) -> Optional[Trade]:
        """Close an open trade
        
        Args:
            trade_id: Trade ID
            exit_price: Exit price
            exit_reason: Reason for exit
        
        Returns:
            Closed Trade object
        """
        if trade_id not in self.open_trades:
            logger.warning(f"Trade {trade_id} not found in open trades")
            return None
        
        trade = self.open_trades.pop(trade_id)
        trade.close(exit_price, exit_reason)
        self.closed_trades.append(trade)
        logger.info(f"Closed trade {trade_id}: P&L={trade.pnl:.2f} ({trade.pnl_percent:.2f}%)")
        return trade
    
    def check_daily_loss_limit(self) -> bool:
        """Check if daily loss exceeds limit
        
        Returns:
            True if within daily loss limit
        """
        # Calculate today's P&L
        today = datetime.utcnow().date()
        today_pnl = 0.0
        
        for trade in self.closed_trades:
            if trade.exit_time and trade.exit_time.date() == today and trade.pnl is not None:
                today_pnl += trade.pnl
        
        # For demo purposes, assuming $1000 starting capital
        starting_capital = 1000.0
        loss_percent = abs(today_pnl) / starting_capital * 100 if today_pnl < 0 else 0
        
        if loss_percent > self.max_daily_loss_percent:
            logger.warning(
                f"Daily loss {loss_percent:.2f}% exceeds limit {self.max_daily_loss_percent}%"
            )
            return False
        
        return True
    
    def get_open_positions_count(self) -> int:
        """Get number of open positions
        
        Returns:
            Count of open trades
        """
        return len(self.open_trades)
    
    def get_total_open_pnl(self, current_prices: Dict[str, float]) -> float:
        """Calculate total P&L of open positions
        
        Args:
            current_prices: Dict of symbol to current price
        
        Returns:
            Total unrealized P&L
        """
        total_pnl = 0.0
        
        for trade in self.open_trades.values():
            if trade.symbol in current_prices:
                current_price = current_prices[trade.symbol]
                if trade.trade_type.value == "long":
                    pnl = (current_price - trade.entry_price) * trade.quantity
                else:
                    pnl = (trade.entry_price - current_price) * trade.quantity
                total_pnl += pnl
        
        return total_pnl
    
    def get_closed_trades_stats(self) -> Dict:
        """Get statistics of closed trades
        
        Returns:
            Trade statistics
        """
        if not self.closed_trades:
            return {
                "total_trades": 0,
                "winning_trades": 0,
                "losing_trades": 0,
                "win_rate": 0.0,
                "total_pnl": 0.0,
                "average_pnl": 0.0
            }
        
        winning_trades = [t for t in self.closed_trades if t.is_profitable()]
        losing_trades = [t for t in self.closed_trades if not t.is_profitable()]
        total_pnl = sum(t.pnl for t in self.closed_trades if t.pnl is not None)
        
        return {
            "total_trades": len(self.closed_trades),
            "winning_trades": len(winning_trades),
            "losing_trades": len(losing_trades),
            "win_rate": len(winning_trades) / len(self.closed_trades) * 100,
            "total_pnl": total_pnl,
            "average_pnl": total_pnl / len(self.closed_trades)
        }
