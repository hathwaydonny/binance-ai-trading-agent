# Setup Guide - Binance AI Trading Agent

## Prerequisites

- Python 3.10 or higher
- Binance account (testnet or live)
- Git
- pip (Python package manager)

## Step 1: Clone the Repository

```bash
git clone https://github.com/hathwaydonny/binance-ai-trading-agent.git
cd binance-ai-trading-agent
```

## Step 2: Create Python Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

## Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

## Step 4: Binance Agent OS Setup

### 4.1 Create Agent Sub-Account

1. Log into [Binance](https://www.binance.com)
2. Navigate to **Wallet** → **Sub-Account**
3. Click **Create Sub-Account**
4. Select **Standard Sub-Account**
5. Set sub-account email (e.g., `agent_subaccount@yourmail.com`)
6. Create the sub-account

### 4.2 Fund the Sub-Account

1. Go to **Wallet** → **Overview**
2. Find your agent sub-account
3. Click **Transfer**
4. Transfer trading capital (recommend starting with small amount like $100-$500 for testing)
5. Select USDT or your preferred asset
6. Confirm transfer

### 4.3 Generate API Keys

1. Log into the sub-account (or use **Sub-Account Management** if in main account)
2. Go to **Account** → **API Management**
3. Click **Create API**
4. Choose **Trading** API Type
5. Set the following permissions:
   - ✅ Read User Data
   - ✅ Spot & Margin Trading  
   - ❌ DO NOT enable Withdrawals (security best practice)
6. Click **Confirm Create**
7. Save both:
   - **API Key**
   - **Secret Key**

⚠️ **IMPORTANT**: Never share your API keys. Store them securely.

## Step 5: Configure Environment

```bash
# Copy example environment file
cp .env.example .env

# Edit .env with your credentials
nano .env  # or use your preferred editor
```

### Configuration Template

```env
# Binance API Configuration
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
BINANCE_SUB_ACCOUNT_ID=your_sub_account_id

# Trading Mode (paper or live)
AGENT_MODE=paper
USE_TESTNET=true  # Start with testnet for testing

# Trading Configuration
DEFAULT_TRADING_PAIR=BTCUSDT
MAX_POSITION_SIZE_USD=1000
MAX_DAILY_LOSS_PERCENT=5

# Risk Management
STOP_LOSS_PERCENT=2.0
TAKE_PROFIT_PERCENT=5.0
```

## Step 6: Test Connection

```bash
# Run quick connectivity test
python -c "from config.settings import Settings; Settings.validate(); print('Configuration valid!')"
```

## Step 7: Run Examples

### 7.1 Simple Trading Agent

```bash
python -m examples.simple_trading_agent
```

This will:
- Connect to Binance API
- Fetch market data
- Display current price
- Verify account access

### 7.2 Start MCP Server

```bash
python -m src.mcp.server
```

The server will start on `http://localhost:8000`

**Available endpoints:**
- `GET /health` - Health check
- `GET /mcp/resources` - List available resources
- `GET /mcp/tools` - List available tools
- `POST /mcp/tools/call` - Execute a tool
- `GET /agent/status` - Agent status

### 7.3 Run Tests

```bash
# Run all tests
pytest tests/ -v

# Run specific test
pytest tests/test_trading_service.py -v

# Run with coverage
pytest tests/ --cov=src --cov-report=html
```

## Step 8: Use with LLM (Claude, ChatGPT, etc.)

### Connect Claude to MCP Server

1. Start the MCP server:
   ```bash
   python -m src.mcp.server
   ```

2. In your Claude client/IDE (e.g., Cursor, VS Code), configure MCP:
   ```json
   {
     "mcpServers": {
       "binance-agent": {
         "command": "python",
         "args": ["-m", "src.mcp.server"]
       }
     }
   }
   ```

3. Claude can now:
   - Query market prices
   - Check account balance
   - Place orders
   - Analyze markets
   - View open orders

### Example Claude Prompt

```
Hey Claude, can you:
1. Check the current price of BTCUSDT
2. Get my account balance
3. Analyze if BTC looks bullish or bearish
4. If bullish and confidence > 70%, place a small buy order
```

Claude will use the MCP tools to execute these steps autonomously!

## Deployment Options

### Option 1: Local Machine

Perfect for development and testing:

```bash
python -m src.mcp.server
```

### Option 2: Docker

```bash
# Build Docker image
docker build -t binance-agent .

# Run container
docker run -e BINANCE_API_KEY=your_key \
  -e BINANCE_API_SECRET=your_secret \
  -p 8000:8000 \
  binance-agent
```

### Option 3: Cloud Deployment (AWS/Google Cloud)

See `Dockerfile` for containerization. Deploy to:
- AWS EC2
- Google Cloud Run
- Azure Container Instances
- DigitalOcean App Platform

## Troubleshooting

### API Connection Issues

```bash
# Test API connectivity
python -c "
import asyncio
from src.services.market_data_service import MarketDataService

async def test():
    async with MarketDataService() as service:
        price = await service.get_price('BTCUSDT')
        print(f'BTC Price: ${price}')

asyncio.run(test())
"
```

### Authentication Errors

1. **Check API key/secret** are correct
2. **Verify permissions** in Binance API settings
3. **Check IP whitelist** (if enabled)
4. **Ensure timestamp sync** between your machine and Binance servers

### Import Errors

```bash
# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Check Python version
python --version  # Should be 3.10+
```

### Rate Limiting

If you get "429 Too Many Requests":
- Reduce request frequency
- Increase delays between operations
- Check `MAX_ORDERS_PER_MINUTE` in `.env`

## Security Best Practices

✅ **DO:**
- Use API keys with minimal required permissions
- Never enable withdrawals for agent API keys
- Use sub-accounts to isolate agent trading
- Store credentials in `.env` (never in code)
- Use HTTPS/TLS for server connections
- Regularly rotate API keys
- Monitor agent activity logs

❌ **DON'T:**
- Share API keys with anyone
- Commit `.env` file to version control
- Enable all permissions unnecessarily
- Use main account API keys for agents
- Deploy with `debug=True` in production
- Log sensitive information

## Next Steps

1. **Learn the architecture** - Read `docs/ARCHITECTURE.md`
2. **Explore trading strategies** - Check `examples/` directory
3. **Understand risk management** - Review `docs/RISK_MANAGEMENT.md`
4. **Build custom strategy** - See `docs/CUSTOM_STRATEGIES.md`
5. **Monitor performance** - Use dashboard in `docs/MONITORING.md`

## Support & Resources

- 📚 [Binance Agent OS Documentation](https://www.binance.com/en/support/faq/how-binance-agent-os-is-changing-crypto-trading)
- 🤖 [Model Context Protocol](https://modelcontextprotocol.io/)
- 📡 [Binance API Reference](https://binance-docs.github.io/apidocs/)
- 💬 [GitHub Issues](https://github.com/hathwaydonny/binance-ai-trading-agent/issues)
- 📖 [Documentation](docs/)

## Frequently Asked Questions

**Q: Is it safe to connect my Binance account?**
A: Yes, if you follow security best practices:
- Use sub-accounts only
- Disable withdrawals
- Use testnet for testing
- Monitor activity regularly

**Q: Can I lose all my money?**
A: Yes, trading always carries risk. Start small, use stop-losses, and test thoroughly on paper trading first.

**Q: What's the minimum starting capital?**
A: $100-$500 for testing. Scale up as you gain confidence.

**Q: Can I run multiple agents?**
A: Yes! Create multiple sub-accounts and run separate agents for each.

**Q: How do I stop the agent?**
A: Press `Ctrl+C` in the terminal or call the `.stop()` method.

---

**Ready to start trading?** Follow the steps above and run your first agent! 🚀
