---
title: Backtesting
permalink: /docs/backtesting/
---

# Trading Pal Backtesting Engine

Trading Pal's advanced backtesting engine combines natural language processing with sophisticated market analysis to test trading strategies across multiple asset classes. Our AI-powered system enables traders to define strategies in plain English while providing comprehensive performance metrics and risk analysis.

## Natural Language Strategy Definition

### Example Strategy Commands
```text
"Buy when the 20-day moving average crosses above the 50-day moving average and RSI is below 70"

"Sell if price drops below the lower Bollinger Band and volume is above the 20-day average"

"Long entry when MACD histogram turns positive and price is above 200-day MA"

"Place a buy order for 100 shares when RSI drops below 30"

"Execute short position if price breaks below support with increased volume"
```

## Multi-Market Testing

### Stocks (via Alpaca)
- US Equities
- Real-time data
- Historical prices
- Volume analysis

### Forex (via OANDA)
- Major pairs
- Minor pairs
- Tick data
- Spread analysis

### Crypto (via Alpaca)
- Major cryptocurrencies
- 24/7 trading
- Order book data
- Market depth

## AI-Powered Analysis

### Strategy Validation
Our AI agents validate trading strategies by analyzing:
- Historical performance
- Risk metrics
- Market conditions
- Correlation analysis

### Performance Metrics
```json
{
  "totalReturn": "25.8%",
  "sharpeRatio": 1.85,
  "maxDrawdown": "12.3%",
  "winRate": "62.5%",
  "profitFactor": 1.75,
  "averageTrade": "$245.50",
  "tradeCount": 156
}
```

## Advanced Features

### Multi-Broker Testing
Test strategies across different brokers and markets simultaneously, with unified reporting and analysis.

### AI Strategy Optimization
Machine learning algorithms optimize strategy parameters based on historical performance.

### Risk Analysis
Comprehensive risk assessment including VaR, correlation analysis, and stress testing.

## Natural Language Commands

| Command Type | Example | Description |
|--------------|---------|-------------|
| Strategy Definition | "Buy when RSI is oversold and MACD crosses up" | Define trading rules in plain English |
| Performance Analysis | "Show me the strategy performance for last month" | Request specific performance metrics |
| Risk Management | "Set stop loss at 2% per trade" | Configure risk parameters |
| Portfolio Management | "Optimize position sizes for maximum Sharpe ratio" | Portfolio optimization commands |

## Integration with Trading Pal Agent

### AI Agent Capabilities
The Trading Pal AI agent enhances backtesting by:

- Validating strategy logic and parameters
- Suggesting optimizations based on historical performance
- Monitoring for potential risks and correlations
- Providing natural language insights and recommendations
- Automating strategy deployment across multiple brokers

[Back to Documentation](/docs/home)
