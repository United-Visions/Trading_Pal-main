# Trading Pal Charts Display Logic

Trading Pal uses a client-side charting library to display market data.  This document details the features and customization options of the charting library.

## Features

* **Multiple chart types:**  Candlestick, line, bar, area.
* **Technical indicators:**  Moving averages, RSI, MACD, Bollinger Bands.
* **Customizable appearance:**  Colors, styles, fonts.
* **Interactive features:**  Zooming, panning, crosshairs.

## Customization

The charting library can be customized through various configuration options.  See the examples below.

## Examples

### Basic Candlestick Chart

```javascript
const chart = new Chart({
  type: 'candlestick',
  data: {
    labels: ['2025-02-12', '2025-02-13'],
    datasets: [{
      data: [
        { open: 149.50, high: 150.00, low: 149.00, close: 149.75 },
        { open: 149.75, high: 150.50, low: 149.50, close: 150.25 }
      ]
    }]
  }
});
