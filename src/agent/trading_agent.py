"""Main trading agent"""

import asyncio
from typing import Optional, Dict, List
from datetime import datetime

from src.services.market_data_service import MarketDataService
from src.services.trading_service import TradingService
from src.services.account_service import AccountService
from src.services.risk_manager import RiskManager
from src.models.trade import Trade, TradeType
from src.models.order import OrderSide
from src.utils.logger import get_logger, setup_logging
from config.settings import Settings

logger = get_logger(__name__)


class TradingAgent:
    """Main trading agent orchestrator"""
    
    def __init__(
        self,
        api_key: str,
        api_secret: str,
        sub_account_id: Optional[str] = None,
        agent_name: str = "AI Trading Agent"
    ):
        """Initialize trading agent
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            sub_account_id: Sub-account ID for agent
            agent_name: Name of the agent
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.sub_account_id = sub_account_id or Settings.BINANCE_SUB_ACCOUNT_ID
        self.agent_name = agent_name
        self.agent_id = f"{agent_name}_{int(datetime.utcnow().timestamp())}"
        
        # Initialize services
        self.market_service = MarketDataService()
        self.trading_service = TradingService(api_key, api_secret)
        self.account_service = AccountService(api_key, api_secret)
        self.risk_manager = RiskManager()
        
        # Agent state
        self.is_running = False
        self.trading_pairs: List[str] = [Settings.DEFAULT_TRADING_PAIR]
        self.market_data_cache: Dict[str, float] = {}
        
        logger.info(f"Initialized {agent_name} (ID: {self.agent_id})")
    
    async def initialize(self):
        """Initialize agent and verify connectivity"""
        try:
            logger.info("Initializing agent...")
            
            # Verify account access
            async with self.account_service:
                account_info = await self.account_service.get_account_info()
                logger.info(f"Connected to account: {account_info.get('makerCommission')}")
            
            # Verify market data access
            async with self.market_service:
                price = await self.market_service.get_price(self.trading_pairs[0])
                logger.info(f"Market data accessible. {self.trading_pairs[0]}: ${price}")
            
            logger.info("Agent initialization complete")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize agent: {e}")
            return False
    
    async def start(self):
        """Start the trading agent"""
        try:
            if not await self.initialize():
                logger.error("Failed to initialize agent")
                return
            
            self.is_running = True
            logger.info(f"{self.agent_name} started")
            
            # Main trading loop
            while self.is_running:
                await self._trading_cycle()
                await asyncio.sleep(60)  # Wait before next cycle
        except Exception as e:
            logger.error(f"Agent error: {e}")
            self.is_running = False
    
    async def stop(self):
        """Stop the trading agent"""
        self.is_running = False
        logger.info(f"{self.agent_name} stopped")
    
    async def _trading_cycle(self):
        """Execute one trading cycle"""
        try:
            # Check risk limits
            if not self.risk_manager.check_daily_loss_limit():
                logger.warning("Daily loss limit reached, pausing trades")
                return
            
            # Update market data
            async with self.market_service:
                for pair in self.trading_pairs:
                    try:
                        market_data = await self.market_service.get_market_data(pair)
                        self.market_data_cache[pair] = market_data.last_price
                    except Exception as e:
                        logger.error(f"Failed to get market data for {pair}: {e}")
            
            # Analyze and execute trades
            async with self.trading_service:
                # Check for open orders
                open_orders = await self.trading_service.get_open_orders()
                logger.info(f"Open orders: {len(open_orders)}")
                
                # Example: Basic momentum strategy
                for pair in self.trading_pairs:
                    await self._analyze_and_trade(pair)
        except Exception as e:
            logger.error(f"Error in trading cycle: {e}")
    
    async def _analyze_and_trade(self, symbol: str):
        """Analyze market and execute trade for symbol
        
        Args:
            symbol: Trading symbol
        """
        try:
            # Get market data
            market_data = self.market_data_cache.get(symbol)
            if not market_data:
                return
            
            # Simple momentum strategy
            if market_data > 0:  # Placeholder for actual signal
                # Calculate position size
                account_balance = await self.account_service.get_balance_for_asset(
                    Settings.DEFAULT_QUOTE_ASSET
                )
                available_balance = account_balance["free"]
                position_size_usd = min(
                    available_balance * 0.1,  # 10% of balance
                    Settings.MAX_POSITION_SIZE_USD
                )
                
                # Check risk limits
                if not self.risk_manager.check_position_size_limit(position_size_usd):
                    logger.warning(f"Position size limit exceeded for {symbol}")
                    return
                
                # Calculate entry and exit prices
                current_price = market_data
                quantity = position_size_usd / current_price
                
                # Place limit order (bid 1% below market)
                limit_price = current_price * 0.99
                
                order = await self.trading_service.place_limit_order(
                    symbol=symbol,
                    side=OrderSide.BUY,
                    quantity=quantity,
                    price=limit_price
                )
                
                # Create trade record
                trade = Trade(
                    trade_id=f"{self.agent_id}_{order.order_id}",
                    symbol=symbol,
                    trade_type=TradeType.LONG,
                    entry_price=limit_price,
                    quantity=quantity,
                    entry_time=datetime.utcnow(),
                    strategy="momentum",
                    agent_decision="BUY"
                )
                
                # Set risk management levels
                trade.stop_loss = self.risk_manager.calculate_stop_loss(limit_price, is_long=True)
                trade.take_profit = self.risk_manager.calculate_take_profit(limit_price, is_long=True)
                
                self.risk_manager.add_open_trade(trade)
                logger.info(f"Trade opened: {symbol} {quantity:.4f} @ {limit_price}")
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
    
    async def execute_trade(
        self,
        symbol: str,
        side: OrderSide,
        quantity: float,
        order_type: str = "LIMIT",
        price: Optional[float] = None
    ) -> Dict:
        """Execute a manual trade
        
        Args:
            symbol: Trading symbol
            side: BUY or SELL
            quantity: Order quantity
            order_type: LIMIT or MARKET
            price: Order price (required for LIMIT)
        
        Returns:
            Order result
        """
        try:
            # Check risk limits
            if not self.risk_manager.check_daily_loss_limit():
                raise Exception("Daily loss limit reached")
            
            async with self.trading_service:
                if order_type == "LIMIT" and price is not None:
                    order = await self.trading_service.place_limit_order(
                        symbol=symbol,
                        side=side,
                        quantity=quantity,
                        price=price
                    )
                elif order_type == "MARKET":
                    order = await self.trading_service.place_market_order(
                        symbol=symbol,
                        side=side,
                        quantity=quantity
                    )
                else:
                    raise ValueError(f"Invalid order type: {order_type}")
                
                return {
                    "order_id": order.order_id,
                    "symbol": order.symbol,
                    "side": order.side.value,
                    "quantity": order.quantity,
                    "status": order.status.value
                }
        except Exception as e:
            logger.error(f"Error executing trade: {e}")
            raise
    
    def get_agent_stats(self) -> Dict:
        """Get agent statistics
        
        Returns:
            Agent performance statistics
        """
        stats = self.risk_manager.get_closed_trades_stats()
        stats.update({
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "is_running": self.is_running,
            "open_positions": self.risk_manager.get_open_positions_count(),
            "trading_pairs": self.trading_pairs
        })
        return stats
