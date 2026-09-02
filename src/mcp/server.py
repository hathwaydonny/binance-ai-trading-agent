"""MCP Server implementation"""

import asyncio
import json
from typing import Optional, Dict, Any
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import uvicorn

from src.mcp.resources import BinanceResources
from src.mcp.tools import BinanceTools
from src.agent.trading_agent import TradingAgent
from src.utils.logger import get_logger, setup_logging
from config.settings import Settings

logger = get_logger(__name__)


class MCPServer:
    """MCP (Model Context Protocol) Server for Binance Agent OS"""
    
    def __init__(
        self,
        trading_agent: Optional[TradingAgent] = None,
        host: str = Settings.MCP_SERVER_HOST,
        port: int = Settings.MCP_SERVER_PORT
    ):
        """Initialize MCP server
        
        Args:
            trading_agent: Trading agent instance
            host: Server host
            port: Server port
        """
        self.trading_agent = trading_agent
        self.host = host
        self.port = port
        
        # Initialize FastAPI app
        self.app = FastAPI(
            title="Binance Agent OS MCP Server",
            description="MCP Protocol Server for AI Trading Agent",
            version="1.0.0"
        )
        
        # Register routes
        self._register_routes()
        
        logger.info(f"MCP Server initialized on {host}:{port}")
    
    def _register_routes(self):
        """Register API routes"""
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "timestamp": str(datetime.utcnow())}
        
        @self.app.get("/mcp/resources")
        async def list_resources():
            """List available resources"""
            return {
                "resources": [
                    {
                        "name": "market_data",
                        "schema": BinanceResources.get_market_data_schema()
                    },
                    {
                        "name": "order",
                        "schema": BinanceResources.get_order_schema()
                    },
                    {
                        "name": "account",
                        "schema": BinanceResources.get_account_schema()
                    }
                ]
            }
        
        @self.app.get("/mcp/tools")
        async def list_tools():
            """List available tools"""
            return {"tools": BinanceTools.get_all_tools()}
        
        @self.app.post("/mcp/tools/call")
        async def call_tool(request: Dict[str, Any]):
            """Call a tool
            
            Request format:
            {
                "tool_name": "get_market_price",
                "parameters": {"symbol": "BTCUSDT"}
            }
            """
            try:
                tool_name = request.get("tool_name")
                parameters = request.get("parameters", {})
                
                logger.info(f"Tool call: {tool_name} with params: {parameters}")
                
                if not self.trading_agent:
                    raise HTTPException(status_code=400, detail="Trading agent not initialized")
                
                # Route to appropriate tool handler
                if tool_name == "get_market_price":
                    return await self._handle_get_market_price(parameters)
                elif tool_name == "place_order":
                    return await self._handle_place_order(parameters)
                elif tool_name == "get_account_balance":
                    return await self._handle_get_account_balance(parameters)
                elif tool_name == "get_open_orders":
                    return await self._handle_get_open_orders(parameters)
                elif tool_name == "analyze_market":
                    return await self._handle_analyze_market(parameters)
                else:
                    raise HTTPException(status_code=400, detail=f"Unknown tool: {tool_name}")
            except Exception as e:
                logger.error(f"Tool call error: {e}")
                raise HTTPException(status_code=500, detail=str(e))
        
        @self.app.get("/agent/status")
        async def get_agent_status():
            """Get agent status"""
            if not self.trading_agent:
                return {"error": "Agent not initialized"}
            
            return self.trading_agent.get_agent_stats()
    
    async def _handle_get_market_price(self, params: Dict[str, Any]) -> Dict:
        """Handle get_market_price tool call"""
        symbol = params.get("symbol")
        if not symbol:
            raise ValueError("symbol parameter required")
        
        async with self.trading_agent.market_service:
            price = await self.trading_agent.market_service.get_price(symbol)
            return {"symbol": symbol, "price": price}
    
    async def _handle_place_order(self, params: Dict[str, Any]) -> Dict:
        """Handle place_order tool call"""
        required_params = ["symbol", "side", "quantity", "order_type"]
        for param in required_params:
            if param not in params:
                raise ValueError(f"{param} parameter required")
        
        return await self.trading_agent.execute_trade(
            symbol=params["symbol"],
            side=params["side"],
            quantity=float(params["quantity"]),
            order_type=params["order_type"],
            price=params.get("price")
        )
    
    async def _handle_get_account_balance(self, params: Dict[str, Any]) -> Dict:
        """Handle get_account_balance tool call"""
        async with self.trading_agent.account_service:
            balances = await self.trading_agent.account_service.get_account_balance()
            return {"balances": balances}
    
    async def _handle_get_open_orders(self, params: Dict[str, Any]) -> Dict:
        """Handle get_open_orders tool call"""
        symbol = params.get("symbol")
        
        async with self.trading_agent.trading_service:
            orders = await self.trading_agent.trading_service.get_open_orders(symbol)
            return {
                "orders": [
                    {
                        "order_id": o.order_id,
                        "symbol": o.symbol,
                        "side": o.side.value,
                        "quantity": o.quantity,
                        "price": o.price,
                        "status": o.status.value
                    }
                    for o in orders
                ]
            }
    
    async def _handle_analyze_market(self, params: Dict[str, Any]) -> Dict:
        """Handle analyze_market tool call"""
        symbol = params.get("symbol")
        interval = params.get("interval", "1h")
        
        if not symbol:
            raise ValueError("symbol parameter required")
        
        async with self.trading_agent.market_service:
            market_data = await self.trading_agent.market_service.get_market_data(symbol)
            candles = await self.trading_agent.market_service.get_historical_klines(
                symbol,
                interval=interval,
                limit=100
            )
        
        # Get technical analysis
        analysis = await self.trading_agent.decision_engine.analyze_technical_indicators(
            symbol,
            candles
        )
        
        return {
            "symbol": symbol,
            "price": market_data.last_price,
            "24h_change": market_data.price_change_24h_percent,
            "technical_analysis": analysis
        }
    
    def run(self):
        """Start the MCP server"""
        logger.info(f"Starting MCP server on {self.host}:{self.port}")
        uvicorn.run(self.app, host=self.host, port=self.port)


if __name__ == "__main__":
    from datetime import datetime
    
    # Setup logging
    setup_logging()
    
    # Initialize agent
    agent = TradingAgent(
        api_key=Settings.BINANCE_API_KEY,
        api_secret=Settings.BINANCE_API_SECRET
    )
    
    # Start MCP server
    server = MCPServer(trading_agent=agent)
    server.run()
