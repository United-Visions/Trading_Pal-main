---
title: Charts Display
permalink: /docs/charts_display/
---

# Trading Pal Charts Display

Trading Pal's charting system provides a powerful visualization platform that integrates with our AI trading agent and multiple data sources. The system supports real-time data from both Alpaca and OANDA, enabling comprehensive market analysis across stocks, forex, and cryptocurrencies.

## Chart Types

### Candlestick
Japanese candlestick charts with customizable colors and styles for price action analysis.

### Line
Clean line charts ideal for trend analysis and price movement tracking.

### Bar
Traditional OHLC bar charts with optional volume indicators.

### Area
Filled area charts for visualizing cumulative data and volume analysis.

## Market Coverage

### Stocks (Alpaca)
- US Equities
- Real-time Level 2 Data
- Pre/Post Market Data
- Historical OHLCV

### Forex (OANDA)
- Major/Minor Pairs
- Tick-by-Tick Data
- Spread Information
- Position Book Data

### Crypto (Alpaca)
- Major Cryptocurrencies
- 24/7 Market Data
- Order Book Depth
- Trade History

## Technical Indicators

| Category | Indicators | Customization |
|----------|------------|---------------|
| Trend | Moving Averages (SMA, EMA, WMA), MACD, ADX, Parabolic SAR | Periods, Colors, Styles |
| Momentum | RSI, Stochastic, CCI, Williams %R | Overbought/Oversold Levels |
| Volatility | Bollinger Bands, ATR, Standard Deviation | Deviation Multiplier, Period |
| Volume | OBV, Volume Profile, Money Flow Index | Time Periods, Display Style |

## AI Integration

### Natural Language Chart Control
Control charts using natural language commands:

```text
"Show me a 1-hour candlestick chart for EUR/USD"
"Add Bollinger Bands with 20-period and 2 standard deviations"
"Display RSI in a separate panel below"
"Zoom to the last 5 trading days"
"Save this chart layout as 'Forex Analysis'"
```

## Interactive Features

### Chart Controls
- 🖱️ Mouse wheel zoom
- 👆 Click and drag to pan
- 📏 Drawing tools
- 📊 Multi-timeframe analysis
- 🎯 Price alerts

### Trading Integration
- 💼 One-click trading
- 📈 Position visualization
- ⚡ Real-time order updates
- 💰 P&L tracking
- 🎚️ Risk management overlays

## Chart Configurations

```javascript
// Example chart configuration
const chart = new Chart({
  type: 'candlestick',
  data: {
    symbol: 'NASDAQ:AAPL',
    timeframe: '1H',
    indicators: [{
      type: 'ema',
      period: 20,
      color: '#2196f3'
    }, {
      type: 'bollinger',
      period: 20,
      stdDev: 2,
      fill: 'rgba(33, 150, 243, 0.1)'
    }]
  },
  options: {
    theme: 'dark',
    autoScale: true,
    volume: true,
    crosshair: true
  }
});
```

## Advanced Features

### Trading Pal Integration
The charting system integrates with Trading Pal's core features:

- AI-powered pattern recognition and alerts
- Automated strategy visualization
- Multi-broker order management
- Real-time position tracking
- Custom indicator development
- Chart-based backtesting
