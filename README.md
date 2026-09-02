# Binance AI Trading Workflow Agent

An enterprise-grade AI trading agent built with **Binance Agent OS** and the **Model Context Protocol (MCP)**. This agent autonomously executes trading workflows while maintaining strict security controls through isolated sub-accounts and granular permissions.

## 🚀 Features

- **Autonomous Trading**: AI-driven market analysis and trade execution
- **MCP Integration**: Standardized protocol for AI models (ChatGPT, Claude, etc.)
- **Sandboxed Execution**: Isolated sub-accounts with no withdrawal permissions
- **Risk Management**: Position sizing, stop-loss, and take-profit automation
- **Real-time Market Data**: Stream prices, balances, and order status
- **Audit Trail**: Complete logging of all trades and agent decisions
- **Permission Scopes**: Granular control over agent capabilities

## 📋 Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    AI Agent (LLM)                       │
│              (ChatGPT, Claude, etc.)                    │
└──────────────────────┬──────────────────────────────────┘
                       │
            ┌──────────▼───────────┐
            │  MCP Server/Client   │
            │  (Standardized API)  │
            └──────────┬───────────┘
                       │
        ┌──────────────┼──────────────┐
        │              │              │
   ┌────▼────┐  ┌─────▼────┐  ┌─────▼────┐
   │ Market  │  │ Trading  │  │ Account  │
   │ Data    │  │ Executor │  │ Manager  │
   │ Service │  │ Service  │  │ Service  │
   └────┬────┘  └─────┬────┘  └─────┬────┘
        │             │             │
        └─────────────┼─────────────┘
                      │
         ┌────────────▼────────────┐
         │   Binance Agent OS      │
         │  ┌──────────────────┐   │
         │  │ Isolated Sub-    │   │
         │  │ Account          │   │
         │  │ (No Withdrawal)  │   │
         │  └──────────────────┘   │
         └────────────┬─────────────┘
                      │
         ┌────────────▼────────────┐
         │   Binance APIs          │
         │  • Spot Trading         │
         │  • Futures Trading      │
         │  • Market Data          │
         │  • Account Info         │
         └─────────────────────────┘
```

## 🔐 Security Model

1. **No Withdrawal Permissions**: Agents cannot withdraw funds from Binance
2. **Isolated Sub-accounts**: All trades executed in dedicated agent accounts
3. **User Funding**: Users transfer funds from main account to agent sub-account
4. **Scoped Access**: API keys restricted to specific operations (market data, trading, transfers)
5. **Approval Workflows**: Manual confirmation required for sensitive operations
6. **Audit Logging**: Every agent action is logged and monitored

## 🛠️ Project Structure

```
.
├── README.md                          # This file
├── requirements.txt                   # Python dependencies
├── .env.example                       # Environment variables template
├── config/
│   ├── __init__.py
│   ├── settings.py                    # Configuration management
│   ├── trading_strategies.yaml        # Strategy definitions
│   └── permissions.yaml               # Permission scopes
├── src/
│   ├── __init__.py
│   ├── agent/
│   │   ├── __init__.py
│   │   ├── trading_agent.py           # Main agent logic
│   │   ├── decision_engine.py         # AI decision making
│   │   └── workflow_manager.py        # Trade workflow orchestration
│   ├── services/
│   │   ├── __init__.py
│   │   ├── market_data_service.py     # Real-time market data
│   │   ├── trading_service.py         # Trade execution
│   │   ├── account_service.py         # Account management
│   │   └── risk_manager.py            # Risk controls
│   ├── mcp/
│   │   ├── __init__.py
│   │   ├── server.py                  # MCP server implementation
│   │   ├── resources.py               # MCP resource definitions
│   │   └── tools.py                   # MCP tool implementations
│   ├── models/
│   │   ├── __init__.py
│   │   ├── trade.py                   # Trade data model
│   │   ├── order.py                   # Order model
│   │   └── market_data.py             # Market data model
│   └── utils/
│       ├── __init__.py
│       ├── logger.py                  # Logging configuration
│       ├── decorators.py              # Permission & validation decorators
│       └── validators.py              # Input validation
├── tests/
│   ├── __init__.py
│   ├── test_agent.py
│   ├── test_trading_service.py
│   ├── test_mcp_server.py
│   └── fixtures/
│       └── mock_data.py
├── examples/
│   ├── simple_trading_agent.py         # Minimal agent example
│   ├── momentum_strategy.py            # Example: momentum trading
│   └── grid_trading_strategy.py        # Example: grid trading
├── docs/
│   ├── SETUP.md                        # Setup guide
│   ├── MCP_INTEGRATION.md              # MCP protocol guide
│   ├── TRADING_STRATEGIES.md           # Strategy documentation
│   ├── API_REFERENCE.md                # API reference
│   └── SECURITY.md                     # Security best practices
├── .gitignore
├── docker-compose.yml                  # Docker setup
├── Dockerfile
└── setup.py
```

## ⚡ Quick Start

### Prerequisites
- Python 3.10+
- Binance account with Agent OS enabled
- API keys with appropriate permissions

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/binance-ai-trading-agent.git
cd binance-ai-trading-agent

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your Binance API credentials
```

### Configuration

1. **Create Binance Agent Sub-account**
   - Log into Binance
   - Navigate to Agent OS dashboard
   - Create new agent sub-account
   - Fund with trading capital

2. **Generate API Keys**
   - Create API key for agent sub-account
   - Select permission scopes:
     - Market Data: READ
     - Account Data: READ
     - Spot Trading: READ, WRITE
     - Futures Trading: READ, WRITE (optional)

3. **Update Configuration**
   ```bash
   # .env file
   BINANCE_API_KEY=your_api_key
   BINANCE_API_SECRET=your_api_secret
   BINANCE_SUB_ACCOUNT_ID=your_sub_account_id
   AGENT_MODE=paper|live  # Start with paper trading
   ```

### Run Your First Agent

```bash
# Run simple example
python -m examples.simple_trading_agent

# Run with MCP server
python -m src.mcp.server

# Run tests
pytest tests/ -v
```

## 📚 Documentation

- **[Setup Guide](docs/SETUP.md)**: Detailed installation and configuration
- **[MCP Integration](docs/MCP_INTEGRATION.md)**: Connect AI models via Model Context Protocol
- **[Trading Strategies](docs/TRADING_STRATEGIES.md)**: Build custom trading strategies
- **[API Reference](docs/API_REFERENCE.md)**: Complete API documentation
- **[Security Guide](docs/SECURITY.md)**: Best practices and risk management

## 🤖 Example: Simple Trading Agent

```python
from src.agent.trading_agent import TradingAgent
from src.services.market_data_service import MarketDataService

# Initialize services
agent = TradingAgent(
    api_key="your_key",
    api_secret="your_secret",
    sub_account_id="your_sub_account"
)

# Define trading logic
async def trading_workflow():
    # Get market data
    btc_price = await agent.market_service.get_price("BTCUSDT")
    print(f"BTC Price: ${btc_price}")
    
    # Analyze and decide
    signal = await agent.decision_engine.analyze_market("BTCUSDT")
    
    # Execute trade
    if signal == "BUY":
        order = await agent.execute_trade(
            symbol="BTCUSDT",
            side="BUY",
            quantity=0.01,
            order_type="LIMIT",
            price=btc_price * 0.99  # Bid 1% below market
        )
        print(f"Order placed: {order}")

# Run agent
import asyncio
asyncio.run(trading_workflow())
```

## 🔗 Connecting with MCP

Connect your agent to Claude, ChatGPT, or other LLMs via MCP:

```bash
# Start MCP server
python -m src.mcp.server --port 8000

# In your LLM client configuration:
# MCP Server: http://localhost:8000
# Available Tools:
#   - get_market_data
#   - place_order
#   - get_account_balance
#   - get_open_orders
```

## 📊 Monitoring & Analytics

- **Trade History**: View all executed trades with entry/exit points
- **Performance Metrics**: P&L, win rate, Sharpe ratio
- **Risk Analytics**: Drawdown analysis, Value at Risk
- **Agent Logs**: Complete audit trail of decisions and actions

## ⚠️ Risk Management

This agent implements critical risk controls:

- **Max Position Size**: Limits per trade
- **Daily Loss Limit**: Stops trading if daily loss exceeds threshold
- **Stop-Loss Orders**: Automatic exit on adverse moves
- **Blacklist Protection**: Excludes risky assets
- **Rate Limiting**: Prevents excessive order placement

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_trading_service.py::test_place_order -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## 🤝 Contributing

Contributions welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📖 Resources

- [Binance Agent OS Documentation](https://www.binance.com/en/support/faq/how-binance-agent-os-is-changing-crypto-trading)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [Binance API Reference](https://binance-docs.github.io/apidocs/)
- [Agent OS MCP Guide](https://essamamdani.com/blog/binance-agent-os-mcp-trading-guide-2026)

## ⚖️ License

MIT License - see LICENSE file for details

## ⚡ Disclaimer

**TRADING RISK WARNING**: Cryptocurrency trading carries substantial risk. This agent is provided as-is without guarantees. Users are responsible for:
- Validating all trading logic before live deployment
- Monitoring agent behavior continuously
- Understanding and accepting financial risks
- Complying with local regulations

## 💬 Support

For issues, questions, or suggestions:
- Open an [Issue](https://github.com/yourusername/binance-ai-trading-agent/issues)
- Check [Discussions](https://github.com/yourusername/binance-ai-trading-agent/discussions)
- Review [Documentation](docs/)

---

**Built with ❤️ for the crypto trading community**
