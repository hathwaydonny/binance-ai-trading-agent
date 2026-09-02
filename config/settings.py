"""Application settings and configuration"""

import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings"""
    
    # Binance API
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    BINANCE_SUB_ACCOUNT_ID: str = os.getenv("BINANCE_SUB_ACCOUNT_ID", "")
    
    # Trading Mode
    AGENT_MODE: str = os.getenv("AGENT_MODE", "paper")  # paper or live
    USE_TESTNET: bool = os.getenv("USE_TESTNET", "true").lower() == "true"
    
    # Trading Configuration
    DEFAULT_TRADING_PAIR: str = os.getenv("DEFAULT_TRADING_PAIR", "BTCUSDT")
    DEFAULT_QUOTE_ASSET: str = os.getenv("DEFAULT_QUOTE_ASSET", "USDT")
    MAX_POSITION_SIZE_USD: float = float(os.getenv("MAX_POSITION_SIZE_USD", "1000"))
    MAX_DAILY_LOSS_PERCENT: float = float(os.getenv("MAX_DAILY_LOSS_PERCENT", "5"))
    
    # Risk Management
    STOP_LOSS_PERCENT: float = float(os.getenv("STOP_LOSS_PERCENT", "2.0"))
    TAKE_PROFIT_PERCENT: float = float(os.getenv("TAKE_PROFIT_PERCENT", "5.0"))
    TRAILING_STOP_PERCENT: float = float(os.getenv("TRAILING_STOP_PERCENT", "1.5"))
    MAX_LEVERAGE: int = int(os.getenv("MAX_LEVERAGE", "1"))
    
    # MCP Server
    MCP_SERVER_HOST: str = os.getenv("MCP_SERVER_HOST", "0.0.0.0")
    MCP_SERVER_PORT: int = int(os.getenv("MCP_SERVER_PORT", "8000"))
    MCP_LOG_LEVEL: str = os.getenv("MCP_LOG_LEVEL", "INFO")
    
    # LLM Configuration
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    ANTHROPIC_API_KEY: str = os.getenv("ANTHROPIC_API_KEY", "")
    
    # Logging
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FILE: str = os.getenv("LOG_FILE", "logs/trading_agent.log")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///trading_agent.db")
    
    # Monitoring
    PROMETHEUS_ENABLED: bool = os.getenv("PROMETHEUS_ENABLED", "true").lower() == "true"
    PROMETHEUS_PORT: int = int(os.getenv("PROMETHEUS_PORT", "9090"))
    
    # Feature Flags
    ENABLE_BACKTESTING: bool = os.getenv("ENABLE_BACKTESTING", "true").lower() == "true"
    ENABLE_PAPER_TRADING: bool = os.getenv("ENABLE_PAPER_TRADING", "true").lower() == "true"
    ENABLE_LIVE_TRADING: bool = os.getenv("ENABLE_LIVE_TRADING", "false").lower() == "true"
    
    # Notifications
    SLACK_WEBHOOK_URL: Optional[str] = os.getenv("SLACK_WEBHOOK_URL")
    EMAIL_ALERTS_ENABLED: bool = os.getenv("EMAIL_ALERTS_ENABLED", "false").lower() == "true"
    EMAIL_RECIPIENT: Optional[str] = os.getenv("EMAIL_RECIPIENT")
    
    # Rate Limiting
    API_RATE_LIMIT_REQUESTS: int = int(os.getenv("API_RATE_LIMIT_REQUESTS", "1000"))
    API_RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("API_RATE_LIMIT_WINDOW_SECONDS", "60"))
    MAX_ORDERS_PER_MINUTE: int = int(os.getenv("MAX_ORDERS_PER_MINUTE", "10"))
    
    # Approval Workflow
    REQUIRE_APPROVAL_FOR_TRADES: bool = os.getenv("REQUIRE_APPROVAL_FOR_TRADES", "true").lower() == "true"
    APPROVAL_TIMEOUT_SECONDS: int = int(os.getenv("APPROVAL_TIMEOUT_SECONDS", "300"))
    
    @classmethod
    def validate(cls):
        """Validate required configuration"""
        if not cls.BINANCE_API_KEY:
            raise ValueError("BINANCE_API_KEY is required")
        if not cls.BINANCE_API_SECRET:
            raise ValueError("BINANCE_API_SECRET is required")
        
        if cls.AGENT_MODE not in ["paper", "live"]:
            raise ValueError(f"Invalid AGENT_MODE: {cls.AGENT_MODE}")
        
        if cls.ENABLE_LIVE_TRADING and cls.AGENT_MODE == "paper":
            raise ValueError("Cannot enable live trading in paper mode")
    
    @classmethod
    def is_live_trading(cls) -> bool:
        """Check if live trading is enabled"""
        return cls.ENABLE_LIVE_TRADING and cls.AGENT_MODE == "live"
    
    @classmethod
    def is_paper_trading(cls) -> bool:
        """Check if paper trading is enabled"""
        return cls.ENABLE_PAPER_TRADING and cls.AGENT_MODE == "paper"
