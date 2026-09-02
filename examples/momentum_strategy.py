"""Momentum trading strategy example

Momentum trading buys assets with strong upward momentum
and sells when momentum weakens.
"""

import asyncio
from src.agent.trading_agent import TradingAgent
from src.agent.decision_engine import DecisionEngine, TradeSignal
from src.models.order import OrderSide
from src.utils.logger import setup_logging, get_logger
from config.settings import Settings

setup_logging()
logger = get_logger(__name__)


class MomentumStrategy:
    """Momentum trading strategy"""
    
    def __init__(self, agent: TradingAgent):
        """Initialize momentum strategy
        
        Args:
            agent: Trading agent
        """
        self.agent = agent
        self.decision_engine = DecisionEngine()
        self.min_confidence = 0.65
    
    async def analyze_and_trade(self, symbol: str):
        """Analyze momentum and execute trade
        
        Args:
            symbol: Trading symbol
        """
        try:
            # Get market data
            async with self.agent.market_service:
                market_data = await self.agent.market_service.get_market_data(symbol)
                candles = await self.agent.market_service.get_historical_klines(
                    symbol,
                    interval="1h",
                    limit=100
                )
            
            logger.info(f"Analyzing {symbol}...")
            logger.info(f"  Current Price: ${market_data.last_price}")
            logger.info(f"  24h Change: {market_data.price_change_24h_percent:.2f}%")
            
            # Analyze technical indicators
            analysis = await self.decision_engine.analyze_technical_indicators(
                symbol,
                candles
            )
            
            logger.info(f"  SMA(20): ${analysis['sma_20']:.2f}")
            logger.info(f"  SMA(50): ${analysis['sma_50']:.2f}")
            logger.info(f"  RSI(14): {analysis['rsi']:.2f}")
            logger.info(f"  Signals: {analysis['signals']}")
            
            # Generate trading decision
            decision = await self.decision_engine.analyze_market(symbol, market_data)
            
            logger.info(f"\n  Signal: {decision['signal']}")
            logger.info(f"  Confidence: {decision['confidence']:.2%}")
            logger.info(f"  Recommended Action: {decision['recommended_action']}")
            
            # Execute trade if signal is strong
            if decision["confidence"] >= self.min_confidence:
                if decision["signal"] == TradeSignal.STRONG_BUY:
                    await self._execute_buy(symbol, market_data.last_price)
                elif decision["signal"] == TradeSignal.BUY:
                    await self._execute_buy(symbol, market_data.last_price, size_factor=0.5)
                elif decision["signal"] == TradeSignal.STRONG_SELL:
                    await self._execute_sell(symbol, market_data.last_price)
            else:
                logger.info("  ⏭️ Skipping trade (low confidence)")
        
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
    
    async def _execute_buy(self, symbol: str, price: float, size_factor: float = 1.0):
        """Execute buy trade
        
        Args:
            symbol: Trading symbol
            price: Current price
            size_factor: Position size multiplier (0-1)
        """
        try:
            # Calculate position size (10% of balance)
            async with self.agent.account_service:
                balance = await self.agent.account_service.get_balance_for_asset(
                    Settings.DEFAULT_QUOTE_ASSET
                )
                available = balance["free"]
            
            position_usd = available * 0.1 * size_factor  # 10% of balance
            quantity = position_usd / price
            
            # Place limit order (1% below market)
            limit_price = price * 0.99
            
            logger.info(f"\n🔵 BUY Signal - Executing...")
            logger.info(f"  Symbol: {symbol}")
            logger.info(f"  Quantity: {quantity:.6f}")
            logger.info(f"  Price: ${limit_price:.2f}")
            
            order = await self.agent.execute_trade(
                symbol=symbol,
                side=OrderSide.BUY,
                quantity=quantity,
                order_type="LIMIT",
                price=limit_price
            )
            
            logger.info(f"  Order ID: {order['order_id']}")
            logger.info(f"  Status: {order['status']}")
        
        except Exception as e:
            logger.error(f"Error executing buy trade: {e}")
    
    async def _execute_sell(self, symbol: str, price: float):
        """Execute sell trade
        
        Args:
            symbol: Trading symbol
            price: Current price
        """
        try:
            # Get current position
            async with self.agent.trading_service:
                open_orders = await self.agent.trading_service.get_open_orders(symbol)
            
            if not open_orders:
                logger.info("No open positions to sell")
                return
            
            logger.info(f"\n🔴 SELL Signal - Executing...")
            logger.info(f"  Symbol: {symbol}")
            logger.info(f"  Price: ${price:.2f}")
            
            # Sell all positions (market order)
            for order in open_orders:
                await self.agent.execute_trade(
                    symbol=symbol,
                    side=OrderSide.SELL,
                    quantity=order.filled_quantity,
                    order_type="MARKET"
                )
        
        except Exception as e:
            logger.error(f"Error executing sell trade: {e}")


async def main():
    """Run momentum trading strategy"""
    
    try:
        # Initialize agent
        agent = TradingAgent(
            api_key=Settings.BINANCE_API_KEY,
            api_secret=Settings.BINANCE_API_SECRET,
            agent_name="Momentum Trading Bot"
        )
        
        if not await agent.initialize():
            logger.error("Failed to initialize agent")
            return
        
        # Initialize strategy
        strategy = MomentumStrategy(agent)
        
        # Analyze and trade
        logger.info("="*60)
        logger.info("Momentum Trading Strategy")
        logger.info("="*60)
        
        await strategy.analyze_and_trade("BTCUSDT")
        await strategy.analyze_and_trade("ETHUSDT")
        
        logger.info("\n" + "="*60)
        logger.info("Analysis Complete")
        logger.info("="*60)
    
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
