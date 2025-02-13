# Trading Pal Data Server

The Trading Pal data server provides real-time market data via a REST API.  This document details the API endpoints and data formats.

## API Endpoints

* `/data/{symbol}`: Returns real-time data for the specified symbol.  `symbol` should be in the format `exchange:symbol` (e.g., `NASDAQ:AAPL`).
* `/historical/{symbol}/{start}/{end}`: Returns historical data for the specified symbol between the given start and end dates.  Dates should be in YYYY-MM-DD format.

## Data Formats

All data is returned in JSON format.  The structure of the data will vary depending on the endpoint.  See the examples below.

## Examples

### Real-time Data

```json
{
  "symbol": "NASDAQ:AAPL",
  "timestamp": "2025-02-13T10:32:00Z",
  "price": 150.25,
  "volume": 10000
}
```

### Historical Data

```json
[
  {
    "symbol": "NASDAQ:AAPL",
    "timestamp": "2025-02-12T10:00:00Z",
    "price": 149.50,
    "volume": 5000
  },
  {
    "symbol": "NASDAQ:AAPL",
    "timestamp": "2025-02-12T10:01:00Z",
    "price": 149.75,
    "volume": 6000
  }
]
