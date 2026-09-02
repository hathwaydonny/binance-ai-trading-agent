# MCP Integration Guide

## What is MCP (Model Context Protocol)?

MCP is an open protocol that allows AI models (Claude, ChatGPT, etc.) to interact with external tools and services in a standardized way.

With Binance Agent OS MCP integration, you can:
- 🤖 Ask Claude to check prices
- 💰 Let AI manage your trades
- 📊 Get real-time market analysis
- 📈 Automate trading decisions

## Architecture

```
┌─────────────────────┐
│   AI Model (LLM)    │
│  (Claude, ChatGPT)  │
└──────────┬──────────┘
           │
           │ JSON-RPC
           │ Protocol
           ▼
┌─────────────────────────────────────┐
│   MCP Server                        │
│ (binance-ai-trading-agent)          │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Binance Resources           │   │
│  │ - Market Data               │   │
│  │ - Orders                    │   │
│  │ - Account Info              │   │
│  └─────────────────────────────┘   │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ Binance Tools               │   │
│  │ - get_market_price()        │   │
│  │ - place_order()             │   │
│  │ - get_account_balance()     │   │
│  │ - analyze_market()          │   │
│  └─────────────────────────────┘   │
└──────────┬──────────────────────────┘
           │
           ▼
┌─────────────────────────────────────┐
│   Binance Agent OS                  │
│   (Isolated Sub-Account)            │
│   No Withdrawal Permissions         │
└─────────────────────────────────────┘
```

## Quick Start

### 1. Start the MCP Server

```bash
# In terminal 1
python -m src.mcp.server
```

You should see:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. Configure Claude/LLM Client

#### For Cursor IDE:

1. Create `.cursor/rules` file:

```json
{
  "mcpServers": {
    "binance-trading-agent": {
      "url": "http://localhost:8000"
    }
  }
}
```

2. Restart Cursor

#### For VS Code with Claude Extension:

1. Open settings.json
2. Add configuration:

```json
{
  "claude.mcp": {
    "servers": {
      "binance": {
        "url": "http://localhost:8000",
        "mode": "http"
      }
    }
  }
}
```

#### For Claude via API:

```python
import anthropic

client = anthropic.Anthropic()

response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    tools=[
        {
            "type": "computer_use",
            "name": "binance_agent",
            "url": "http://localhost:8000"
        }
    ],
    messages=[
        {
            "role": "user",
            "content": "What's the current price of Bitcoin?"
        }
    ]
)
```

### 3. Start Asking Questions

```
You: "What's the current price of BTCUSDT?"

Claude uses the MCP tool to:
1. Call GET /mcp/tools/call
2. Execute get_market_price
3. Return: "Bitcoin is currently trading at $42,500"
```

## Available Resources

### Market Data Resource

**Schema:**
```json
{
  "symbol": "BTCUSDT",
  "last_price": 42500.00,
  "bid_price": 42499.50,
  "ask_price": 42500.50,
  "high_24h": 43000.00,
  "low_24h": 42000.00,
  "volume_24h": 25000.50,
  "price_change_24h_percent": 2.5,
  "timestamp": "2026-09-02T15:30:00Z"
}
```

**Access:**
```
GET /mcp/resources
```

### Account Resource

**Schema:**
```json
{
  "total_balance": 5000.00,
  "free_balance": 4500.00,
  "locked_balance": 500.00,
  "maker_commission": 0.001,
  "taker_commission": 0.001,
  "open_positions": 2
}
```

### Order Resource

**Schema:**
```json
{
  "order_id": "123456789",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "type": "LIMIT",
  "quantity": 0.5,
  "price": 42000.00,
  "status": "FILLED",
  "filled_quantity": 0.5,
  "created_time": "2026-09-02T15:20:00Z"
}
```

## Available Tools

### 1. get_market_price

**Purpose:** Fetch current price for a symbol

**Parameters:**
- `symbol` (string, required): Trading symbol (e.g., "BTCUSDT")

**Example:**
```json
{
  "tool_name": "get_market_price",
  "parameters": {"symbol": "BTCUSDT"}
}
```

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "price": 42500.00
}
```

### 2. place_order

**Purpose:** Place buy or sell orders

**Parameters:**
- `symbol` (string, required): Trading symbol
- `side` (string, required): "BUY" or "SELL"
- `quantity` (number, required): Order quantity
- `order_type` (string, required): "LIMIT" or "MARKET"
- `price` (number, optional): Order price (required for LIMIT)

**Example:**
```json
{
  "tool_name": "place_order",
  "parameters": {
    "symbol": "BTCUSDT",
    "side": "BUY",
    "quantity": 0.01,
    "order_type": "LIMIT",
    "price": 42000.00
  }
}
```

**Response:**
```json
{
  "order_id": "123456789",
  "symbol": "BTCUSDT",
  "side": "BUY",
  "quantity": 0.01,
  "status": "NEW"
}
```

### 3. get_account_balance

**Purpose:** Fetch account balance for all assets

**Parameters:**
- `asset` (string, optional): Specific asset filter

**Example:**
```json
{
  "tool_name": "get_account_balance",
  "parameters": {"asset": "USDT"}
}
```

**Response:**
```json
{
  "balances": {
    "USDT": {"total": 5000.00, "free": 4500.00, "locked": 500.00},
    "BTC": {"total": 0.5, "free": 0.45, "locked": 0.05}
  }
}
```

### 4. get_open_orders

**Purpose:** Get list of open orders

**Parameters:**
- `symbol` (string, optional): Filter by symbol

**Example:**
```json
{
  "tool_name": "get_open_orders",
  "parameters": {"symbol": "BTCUSDT"}
}
```

**Response:**
```json
{
  "orders": [
    {
      "order_id": "123456789",
      "symbol": "BTCUSDT",
      "side": "BUY",
      "quantity": 0.01,
      "price": 42000.00,
      "status": "NEW"
    }
  ]
}
```

### 5. analyze_market

**Purpose:** Analyze market and generate trading signals

**Parameters:**
- `symbol` (string, required): Trading symbol
- `interval` (string, optional): "1m", "5m", "1h", "4h", "1d" (default: "1h")

**Example:**
```json
{
  "tool_name": "analyze_market",
  "parameters": {
    "symbol": "BTCUSDT",
    "interval": "1h"
  }
}
```

**Response:**
```json
{
  "symbol": "BTCUSDT",
  "price": 42500.00,
  "24h_change": 2.5,
  "technical_analysis": {
    "sma_20": 42200.00,
    "sma_50": 41800.00,
    "rsi": 65.5,
    "macd": {
      "macd": 150.00,
      "signal": 140.00,
      "histogram": 10.00
    },
    "signals": ["uptrend", "bullish_macd"]
  }
}
```

## Example Workflows

### Workflow 1: Check Price and Place Order

```python
async def workflow_1():
    # Claude asks: "Is BTC above $42k? If yes, buy 0.01 BTC"
    
    # MCP Tool 1: Get price
    response = await mcp.call_tool("get_market_price", {"symbol": "BTCUSDT"})
    price = response["price"]  # 42500.00
    
    if price > 42000:
        # MCP Tool 2: Place order
        order = await mcp.call_tool("place_order", {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "quantity": 0.01,
            "order_type": "LIMIT",
            "price": price * 0.99  # 1% below market
        })
        return f"Order placed: {order['order_id']}"
```

### Workflow 2: Analyze and Trade

```python
async def workflow_2():
    # Claude asks: "Analyze BTC and trade if strong buy signal"
    
    # MCP Tool: Analyze market
    analysis = await mcp.call_tool("analyze_market", {
        "symbol": "BTCUSDT",
        "interval": "1h"
    })
    
    # Extract signals
    signals = analysis["technical_analysis"]["signals"]
    
    if "uptrend" in signals and "bullish_macd" in signals:
        # Get balance
        balance = await mcp.call_tool("get_account_balance", {})
        usdt = balance["balances"]["USDT"]["free"]
        
        # Place trade
        order = await mcp.call_tool("place_order", {
            "symbol": "BTCUSDT",
            "side": "BUY",
            "quantity": (usdt * 0.1) / analysis["price"],
            "order_type": "MARKET"
        })
        return f"Bullish signal detected. Order: {order['order_id']}"
```

## Error Handling

### Common Errors

**401 Unauthorized:**
```json
{
  "detail": "Invalid API credentials"
}
```

Fix: Check `.env` file for correct API keys

**400 Bad Request:**
```json
{
  "detail": "symbol parameter required"
}
```

Fix: Check tool parameters match schema

**429 Too Many Requests:**
```json
{
  "detail": "Rate limit exceeded"
}
```

Fix: Reduce request frequency

**500 Internal Server Error:**
```json
{
  "detail": "Order placement failed: Insufficient balance"
}
```

Fix: Ensure sufficient balance in account

## Best Practices

✅ **DO:**
- Test on paper trading first
- Use small positions initially
- Implement stop-losses
- Monitor activity logs
- Validate LLM responses before execution
- Use explicit confirmation for large orders

❌ **DON'T:**
- Deploy without testing
- Use leverage without understanding risks
- Let LLM make all decisions
- Ignore rate limits
- Leave agent unattended
- Enable auto-execution for large trades

## Debugging

### Check MCP Server Status

```bash
curl http://localhost:8000/health
```

### View Available Tools

```bash
curl http://localhost:8000/mcp/tools | jq
```

### Test Tool Call

```bash
curl -X POST http://localhost:8000/mcp/tools/call \
  -H "Content-Type: application/json" \
  -d '{
    "tool_name": "get_market_price",
    "parameters": {"symbol": "BTCUSDT"}
  }'
```

### View Agent Status

```bash
curl http://localhost:8000/agent/status | jq
```

## Troubleshooting

### MCP Server Won't Start

```bash
# Check port 8000 is available
lsof -i :8000

# Use different port
MCP_SERVER_PORT=8001 python -m src.mcp.server
```

### Claude Can't Connect

1. Ensure server is running: `curl http://localhost:8000/health`
2. Check firewall allows connections to port 8000
3. Verify MCP client configuration
4. Check logs: `tail -f logs/trading_agent.log`

### Tool Execution Fails

1. Check `.env` configuration
2. Verify API credentials
3. Ensure account has sufficient balance
4. Check rate limits haven't been exceeded

---

**Ready to use MCP?** Start the server and connect your LLM! 🚀
