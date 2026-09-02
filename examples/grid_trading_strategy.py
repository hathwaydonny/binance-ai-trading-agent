"""Grid trading strategy example

Grid trading places multiple buy and sell orders at different price levels.
This captures profits as the price moves within a range.
"""

import asyncio
from typing import List
from src.agent.trading_agent import TradingAgent
from src.models.order import OrderSide
from src.utils.logger import setup_logging, get_logger
from config.settings import Settings

setup_logging()
logger = get_logger(__name__)


class GridTradingStrategy:
    """Grid trading strategy implementation"""
    
    def __init__(self, agent: TradingAgent, symbol: str = "BTCUSDT"):
        """Initialize grid trading strategy
        
        Args:
            agent: Trading agent
            symbol: Trading symbol
        """
        self.agent = agent
        self.symbol = symbol
        self.grid_levels = 10  # Number of price levels
        self.grid_step_percent = 0.5  # 0.5% between levels
        self.position_size_per_level = 0.001  # BTC per level
    
    def calculate_grid_levels(self, base_price: float) -> dict:
        """Calculate grid buy and sell levels
        
        Args:
            base_price: Current price
        
        Returns:
            Dict with buy and sell levels
        """
        price_step = base_price * (self.grid_step_percent / 100)
        
        buy_levels = []
        sell_levels = []
        
        # Create buy levels below base price
        for i in range(1, self.grid_levels + 1):
            buy_price = base_price - (price_step * i)
            buy_levels.append(buy_price)
        
        # Create sell levels above base price
        for i in range(1, self.grid_levels + 1):
            sell_price = base_price + (price_step * i)
            sell_levels.append(sell_price)
        
        return {
            "buy_levels": sorted(buy_levels, reverse=True),
            "sell_levels": sorted(sell_levels)
        }
    
    async def place_grid_orders(self, base_price: float) -> List[dict]:
        """Place grid buy and sell orders
        
        Args:
            base_price: Current price
        
        Returns:
            List of placed orders
        """
        levels = self.calculate_grid_levels(base_price)
        orders = []
        
        try:
            # Place buy orders
            logger.info(f"Placing {len(levels['buy_levels'])} buy orders...")
            for buy_price in levels["buy_levels"]:
                try:
                    order = await self.agent.execute_trade(
                        symbol=self.symbol,
                        side=OrderSide.BUY,
                        quantity=self.position_size_per_level,
                        order_type="LIMIT",
                        price=buy_price
                    )
                    orders.append(order)
                    logger.info(f"  Buy order: {buy_price} x {self.position_size_per_level}")
                except Exception as e:
                    logger.error(f"Failed to place buy order: {e}")
            
            # Place sell orders
            logger.info(f"Placing {len(levels['sell_levels'])} sell orders...")
            for sell_price in levels["sell_levels"]:
                try:
                    order = await self.agent.execute_trade(
                        symbol=self.symbol,
                        side=OrderSide.SELL,
                        quantity=self.position_size_per_level,
                        order_type="LIMIT",
                        price=sell_price
                    )
                    orders.append(order)
                    logger.info(f"  Sell order: {sell_price} x {self.position_size_per_level}")
                except Exception as e:
                    logger.error(f"Failed to place sell order: {e}")
            
            logger.info(f"Grid trading strategy deployed: {len(orders)} orders placed")
            return orders
        
        except Exception as e:
            logger.error(f"Error placing grid orders: {e}")
            raise


async def main():
    """Run grid trading strategy example"""
    
    try:
        # Initialize agent
        agent = TradingAgent(
            api_key=Settings.BINANCE_API_KEY,
            api_secret=Settings.BINANCE_API_SECRET,
            agent_name="Grid Trading Bot"
        )
        
        if not await agent.initialize():
            logger.error("Failed to initialize agent")
            return
        
        # Get current price
        async with agent.market_service:
            current_price = await agent.market_service.get_price("BTCUSDT")
            logger.info(f"Current BTC price: ${current_price}")
        
        # Initialize strategy
        strategy = GridTradingStrategy(agent, symbol="BTCUSDT")
        
        # Place grid orders
        orders = await strategy.place_grid_orders(current_price)
        
        logger.info(f"\nGrid trading strategy active with {len(orders)} orders")
        logger.info("Strategy will capture profits as price moves within the grid")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
