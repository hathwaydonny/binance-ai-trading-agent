"""Simple trading agent example"""

import asyncio
import os
from dotenv import load_dotenv

from src.agent.trading_agent import TradingAgent
from src.utils.logger import setup_logging, get_logger
from config.settings import Settings

# Setup logging
setup_logging()
logger = get_logger(__name__)


async def main():
    """Run simple trading agent example"""
    
    try:
        # Validate configuration
        Settings.validate()
        logger.info("Configuration validated")
        
        # Initialize agent
        agent = TradingAgent(
            api_key=Settings.BINANCE_API_KEY,
            api_secret=Settings.BINANCE_API_SECRET,
            agent_name="Simple Trading Agent"
        )
        
        # Initialize connection
        if not await agent.initialize():
            logger.error("Failed to initialize agent")
            return
        
        logger.info("✅ Agent initialized successfully")
        logger.info(f"Agent ID: {agent.agent_id}")
        logger.info(f"Trading Pairs: {agent.trading_pairs}")
        
        # Get account info
        async with agent.account_service:
            balance = await agent.account_service.get_account_balance()
            logger.info(f"Account Balance: {balance}")
        
        # Get market price
        async with agent.market_service:
            for pair in agent.trading_pairs:
                try:
                    price = await agent.market_service.get_price(pair)
                    market_data = await agent.market_service.get_market_data(pair)
                    logger.info(f"{pair}: ${price}")
                    logger.info(f"  24h Change: {market_data.price_change_24h_percent:.2f}%")
                    logger.info(f"  24h High: ${market_data.high_24h}")
                    logger.info(f"  24h Low: ${market_data.low_24h}")
                except Exception as e:
                    logger.error(f"Error fetching data for {pair}: {e}")
        
        # Get agent statistics
        stats = agent.get_agent_stats()
        logger.info(f"Agent Stats: {stats}")
        
        logger.info("\n" + "="*50)
        logger.info("Simple Trading Agent Example Completed!")
        logger.info("="*50)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        raise


if __name__ == "__main__":
    asyncio.run(main())
