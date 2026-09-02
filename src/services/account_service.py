"""Account service for managing account information"""

import hashlib
import hmac
import time
from typing import Dict, Optional, List
from decimal import Decimal
import aiohttp

from src.utils.logger import get_logger
from config.settings import Settings

logger = get_logger(__name__)


class AccountService:
    """Service for account management and information"""
    
    def __init__(self, api_key: str, api_secret: str):
        """Initialize account service
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
        """
        self.api_key = api_key
        self.api_secret = api_secret
        self.base_url = "https://api.binance.com" if not Settings.USE_TESTNET else "https://testnet.binance.vision"
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def _get_request_kwargs(self, endpoint: str, params: Dict = None) -> Dict:
        """Generate request kwargs with authentication
        
        Args:
            endpoint: API endpoint
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
    
    async def get_account_balance(self) -> Dict[str, float]:
        """Get account balances for all assets
        
        Returns:
            Dictionary of asset symbols to balances
        """
        try:
            endpoint = "/api/v3/account"
            params = {}
            
            kwargs = self._get_request_kwargs(endpoint, params)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    balances = {}
                    for balance in data["balances"]:
                        asset = balance["asset"]
                        free = float(balance["free"])
                        locked = float(balance["locked"])
                        total = free + locked
                        
                        if total > 0:  # Only include non-zero balances
                            balances[asset] = {
                                "total": total,
                                "free": free,
                                "locked": locked
                            }
                    
                    logger.info(f"Fetched account balance for {len(balances)} assets")
                    return balances
                else:
                    logger.error(f"Failed to get account balance: {response.status}")
                    raise Exception(f"Failed to get account balance")
        except Exception as e:
            logger.error(f"Error fetching account balance: {e}")
            raise
    
    async def get_balance_for_asset(self, asset: str) -> Dict[str, float]:
        """Get balance for a specific asset
        
        Args:
            asset: Asset symbol (e.g., BTC, USDT)
        
        Returns:
            Balance information (total, free, locked)
        """
        try:
            balances = await self.get_account_balance()
            
            if asset in balances:
                return balances[asset]
            else:
                logger.warning(f"Asset {asset} not found in account")
                return {"total": 0, "free": 0, "locked": 0}
        except Exception as e:
            logger.error(f"Error fetching balance for {asset}: {e}")
            raise
    
    async def get_account_info(self) -> Dict:
        """Get detailed account information
        
        Returns:
            Account info including maker/taker commissions, balances, etc.
        """
        try:
            endpoint = "/api/v3/account"
            params = {}
            
            kwargs = self._get_request_kwargs(endpoint, params)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    logger.info("Fetched detailed account information")
                    return data
                else:
                    logger.error(f"Failed to get account info: {response.status}")
                    raise Exception(f"Failed to get account info")
        except Exception as e:
            logger.error(f"Error fetching account info: {e}")
            raise
    
    async def get_trading_fees(self) -> Dict:
        """Get trading fees (VIP level dependent)
        
        Returns:
            Trading fees information
        """
        try:
            endpoint = "/api/v3/tradeFee"
            params = {}
            
            kwargs = self._get_request_kwargs(endpoint, params)
            
            if not self.session:
                self.session = aiohttp.ClientSession()
            
            url = f"{self.base_url}{endpoint}"
            async with self.session.get(url, **kwargs) as response:
                if response.status == 200:
                    data = await response.json()
                    logger.info("Fetched trading fees")
                    return data
                else:
                    logger.error(f"Failed to get trading fees: {response.status}")
                    raise Exception(f"Failed to get trading fees")
        except Exception as e:
            logger.error(f"Error fetching trading fees: {e}")
            raise
    
    async def calculate_portfolio_value(self, quote_asset: str = "USDT") -> float:
        """Calculate total portfolio value in quote asset
        
        Args:
            quote_asset: Quote asset to value portfolio in (e.g., USDT)
        
        Returns:
            Total portfolio value
        """
        try:
            balances = await self.get_account_balance()
            
            # For now, return USDT balance as portfolio value
            # In production, would need to fetch prices for other assets
            if quote_asset in balances:
                return balances[quote_asset]["total"]
            else:
                logger.warning(f"Quote asset {quote_asset} not found")
                return 0.0
        except Exception as e:
            logger.error(f"Error calculating portfolio value: {e}")
            raise
