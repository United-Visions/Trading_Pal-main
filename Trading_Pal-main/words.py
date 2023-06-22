
# Define the phrases for each endpoint
endpoint_phrases = {
    "create_order": [
        "create an order", "place an order", "execute an order",
        "initiate an order", "start an order", "establish an order",
        "set up an order", "arrange an order", "implement an order",
        "proceed with an order", "carry out an order",
        "open a new order", "generate a trading order",
        "submit a buy/sell order", "issue a market order",
        "execute a limit order", "place a stop order",
        "create a pending order", "initiate a take profit order",
        "start a stop loss order", "establish a trailing stop order",
        "set up a market order", "arrange a limit order",
        "implement a stop order", "proceed with a pending order",
        "carry out a take profit order", "open a stop loss order",
        "generate a trailing stop order", "submit an order request",
        "issue an order execution", "execute a pending order",
        "place a take profit order", "create a stop loss order",
        "initiate a trailing stop order", "start a market order",
        "establish a limit order", "set up a stop order",
        "arrange a pending order", "implement a take profit order",
        "proceed with a stop loss order", "carry out a trailing stop order"
    ],

        "execute_backtest": ["execute a backtest", "run a backtest", "backtest trading strategy"
    ],
    
    

    "get_account_details": [
        "fetch my account details", "retrieve account information",
        "show me my account details", "can I see my account details", "display my account information",
        "provide my account details", "pull up my account details", "bring up my account information",
        "let me see my account details", "access my account details", "uncover my account details",
        "reveal my account details", "dig up my account information", "find my account details",
        "present my account information", "check my account details", "look up my account information",
        "see my account details", "unveil my account details", "expose my account information",
        "inspect my account details", "view my account information", "discover my account details",
        "outline my account information"
    ],
    "place_a_trade": [
        "place a trade", "execute a trade", "enter a trade", "initiate a trade", "start a trade",
        "establish a trade", "set a trade", "arrange a trade", "implement a trade",
        "proceed with a trade", "carry out a trade", "perform a trade", "organize a trade",
        "launch a trade", "put in a trade", "begin a trade", "kick off a trade", "activate a trade",
        "trigger a trade", "apply a trade", "commit to a trade", "finalize a trade", "authorize a trade",
        "confirm a trade", "validate a trade"
    ],
    

   
    "get_latest_price_and_liquidity": [
        "get latest price", "get latest liquidity", "fetch latest price and liquidity"
                                       ],
    
    "get_candlestick_data": [
        "fetch candlestick data", "get candlestick data", "retrieve candlestick data",
        "show me candlestick data", "can I see candlestick data", "display candlestick information",
        "provide candlestick data", "pull up candlestick data", "bring up candlestick information",
        "let me see candlestick data", "access candlestick data", "uncover candlestick data",
        "reveal candlestick data", "dig up candlestick information", "find candlestick data",
        "present candlestick information", "check candlestick data", "look up candlestick information",
        "see candlestick data", "unveil candlestick data", "expose candlestick information",
        "inspect candlestick data", "view candlestick information", "discover candlestick data",
        "outline candlestick information"
    ],
    "get_order_book": [
        "fetch order book", "get order book", "retrieve order book",
        "show me order book", "can I see order book", "display order book information",
        "provide order book", "pull up order book", "bring up order book information",
        "let me see order book", "access order book", "uncover order book",
        "reveal order book", "dig up order book information", "find order book",
        "present order book information", "check order book", "look up order book information",
        "see order book", "unveil order book", "expose order book information",
        "inspect order book", "view order book information", "discover order book",
        "outline order book information"
    ],
    "get_position_book": [
        "fetch position book", "get position book", "retrieve position book",
        "show me position book", "can I see position book", "display position book information",
        "provide position book", "pull up position book", "bring up position book information",
        "let me see position book", "access position book", "uncover position book",
        "reveal position book", "dig up position book information", "find position book",
        "present position book information", "check position book", "look up position book information",
        "see position book", "unveil position book", "expose position book information",
        "inspect position book", "view position book information", "discover position book",
        "outline position book information"
    ],
    "get_accounts": [
        "get accounts", "fetch accounts", "retrieve accounts",
        "list all accounts", "show my accounts", "get my account list",
        "view available accounts", "display account information"
        "provide account details", "pull up account information"
        "show me my account list", "access account information"
        "uncover account details", "retrieve account list"
        "list all authorized accounts", "present account information"
        "check my account list", "look up account information",
        "see my accounts", "unveil account details",
        "expose account information", "inspect account details",
        "view account information", "discover account list",
        "outline account information"
    ],
    "get_account_summary": [
        "get my account summary", "fetch my account summary",
        "retrieve account summary", "show account summary",
        "display account summary", "provide account summary",
        "pull up account summary", "show me account summary",
        "access account summary", "uncover account summary",
        "reveal account summary", "display summary of my account",
        "check my account summary", "look up account summary",
        "see my account summary", "unveil account summary",
        "expose account summary", "inspect account summary",
        "view account summary", "discover account summary",
        "outline account summary"
    ],
    "get_account_instruments": [
        "get account instruments", "fetch account instruments",
        "retrieve account instruments", "show account instruments",
        "display account instruments", "provide account instruments",
        "pull up account instruments", "show me account instruments",
        "access account instruments", "uncover account instruments",
        "reveal account instruments", "display instruments of my account",
        "check my account instruments", "look up account instruments",
        "see my account instruments", "unveil account instruments",
        "expose account instruments", "inspect account instruments",
        "view account instruments", "discover account instruments",
        "outline account instruments"
    ],
    "set_account_configuration": [
        "set account configuration", "update account configuration",
        "modify account configuration", "change account configuration",
        "configure my account", "modify my account configuration",
        "change my account configuration", "adjust account settings",
        "customize account configuration", "update my account settings",
        "configure account preferences", "change account preferences",
        "modify my account preferences", "update my account preferences",
        "adjust account parameters", "customize account options",
        "update my account configuration"
    ],
    "get_account_changes": [
        "get account changes", "fetch account changes",
        "retrieve account changes", "show account changes",
        "display account changes", "provide account changes",
        "pull up account changes", "show me account changes",
        "access account changes", "uncover account changes",
        "reveal account changes", "display changes in my account",
        "check my account changes", "look up account changes",
        "see my account changes", "unveil account changes",
        "expose account changes", "inspect account changes",
        "view account changes", "discover account changes",
        "outline account changes"
    ],
    
     "get_orders": [
        "get orders", "fetch orders", "retrieve orders",
        "list all orders", "show my orders", "get my order list",
        "view available orders", "display order information"
        "provide order details", "pull up order information"
        "show me my order list", "access order information"
        "uncover order details", "retrieve order list"
        "list all open orders", "list all pending orders",
        "present order information", "check my order list",
        "look up order information", "see my orders",
        "unveil order details", "expose order information",
        "inspect order details", "view order information",
        "discover order list", "outline order information"
    ],
    "get_pending_orders": [
        "get pending orders", "fetch pending orders",
        "retrieve pending orders", "show pending orders",
        "display pending orders", "provide pending order details",
        "pull up pending order information", "show me pending orders",
        "access pending order information", "uncover pending orders",
        "retrieve pending order list", "list all pending orders",
        "present pending order information", "check my pending order list",
        "look up pending order information", "see my pending orders",
        "unveil pending order details", "expose pending order information",
        "inspect pending order details", "view pending order information",
        "discover pending order list", "outline pending order information"
    ],
    "get_order_details": [
        "get order details", "fetch order details",
        "retrieve order details", "show order details",
        "display order details", "provide order information",
        "pull up order details", "show me order details",
        "access order details", "uncover order information",
        "reveal order information", "display details of my order",
        "check my order details", "look up order details",
        "see my order details", "unveil order information",
        "expose order information", "inspect order details",
        "view order information", "discover order details",
        "outline order information",
        "get details of an order", "fetch information about an order",
        "retrieve order specifics", "show me the details of an order",
        "display order information", "provide order specifics",
        "pull up order specifics", "access order information",
        "uncover order specifics", "reveal order details",
        "check details of my order", "look up order specifics",
        "see the specifics of my order", "unveil order details",
        "expose order specifics", "inspect order specifics",
        "view order details", "discover order specifics",
        "outline order details"
    ],
   "replace_order": [
        "replace an order", "modify an order",
        "update an order", "amend an order",
        "change an order", "revise an order",
        "edit an order", "adjust an order",
        "substitute an order", "alter an order",
        "replace my existing order", "modify my current order",
        "update my order details", "amend my open order",
        "change the order specifics", "revise the order parameters",
        "edit the existing order", "adjust the order details",
        "substitute my current order", "alter my open order",
        "replace the order", "modify the existing order",
        "update the order attributes", "amend the open order",
        "change the order specifics", "revise the order parameters",
        "edit the existing order", "adjust the order details",
        "substitute the current order", "alter the open order",
        "replace an order in my account", "modify an existing order",
        "update the order in my account", "amend an open order in my account",
        "change the order specifics in my account", "revise the order parameters in my account",
        "edit the existing order in my account", "adjust the order details in my account",
        "substitute my current order in my account", "alter my open order in my account"
    ],
    "cancel_order": [
        "cancel an order", "remove an order",
        "delete an order", "terminate an order",
        "cancel my existing order", "remove my current order",
        "delete my order", "terminate my open order",
        "cancel the order", "remove the order",
        "delete the order", "terminate the order",
        "cancel an open order", "remove an open order",
        "delete an open order", "terminate an open order",
        "cancel my open order", "remove my open order",
        "delete my open order", "terminate my open order",
        "cancel a pending order", "remove a pending order",
        "delete a pending order", "terminate a pending order",
        "cancel my pending order", "remove my pending order",
        "delete my pending order", "terminate my pending order",
        "cancel the pending order", "remove the pending order",
        "delete the pending order", "terminate the pending order",
        "cancel an order in my account", "remove an order in my account",
        "delete an order in my account", "terminate an order in my account",
        "cancel my order in my account", "remove my order in my account",
        "delete my order in my account", "terminate my order in my account",
        "cancel the order in my account", "remove the order in my account",
        "delete the order in my account", "terminate the order in my account"
    ],
    "update_order_extensions": [
        "update order extensions", "modify order extensions",
        "update my order extensions", "modify my order extensions",
        "update extensions for my order", "modify extensions for my order",
        "update extensions for an order", "modify extensions for an order",
        "update order extensions in my account", "modify order extensions in my account",
        "update extensions for my order in my account", "modify extensions for my order in my account"
    ],
    "get_trades": [
        "get trades", "fetch trades", "retrieve trades",
        "get my trades", "fetch my trades", "retrieve my trades",
        "get trades in my account", "fetch trades in my account",
        "retrieve trades in my account", "get trades for my account",
        "fetch trades for my account", "retrieve trades for my account"
    ],
     "get_open_trades": [
        "get open trades", "fetch open trades",
        "get my open trades", "fetch my open trades",
        "get open trades in my account", "fetch open trades in my account",
        "get open trades for my account", "fetch open trades for my account"
    ],
    "get_trade_details": [
        "get trade details", "fetch trade details",
        "get details of a trade", "fetch details of a trade",
        "get details of my trade", "fetch details of my trade",
        "get details of a trade in my account", "fetch details of a trade in my account"
    ],
    "close_trade": [
        "close a trade", "terminate a trade",
        "close my trade", "terminate my trade",
        "close a trade in my account", "terminate a trade in my account"
    ],
    "update_trade_extensions": [
        "update trade extensions", "modify trade extensions",
        "update my trade extensions", "modify my trade extensions",
        "update extensions for my trade", "modify extensions for my trade",
        "update extensions for a trade", "modify extensions for a trade",
        "update trade extensions in my account", "modify trade extensions in my account",
        "update extensions for my trade in my account", "modify extensions for my trade in my account"
    ],
    "update_trade_orders": [
        "update trade orders", "modify trade orders",
        "update my trade orders", "modify my trade orders",
        "update orders for my trade", "modify orders for my trade",
        "update orders for a trade", "modify orders for a trade",
        "update trade orders in my account", "modify trade orders in my account",
        "update orders for my trade in my account", "modify orders for my trade in my account"
    ],
    "get_positions": [
        "get positions", "fetch positions", "retrieve positions",
        "get my positions", "fetch my positions", "retrieve my positions",
        "get positions in my account", "fetch positions in my account",
        "retrieve positions in my account", "get positions for my account",
        "fetch positions for my account", "retrieve positions for my account"
    ],
    "get_open_positions": [
        "get open positions", "fetch open positions",
        "get my open positions", "fetch my open positions",
        "get open positions in my account", "fetch open positions in my account",
        "get open positions for my account", "fetch open positions for my account"
    ],
    "get_position_details": [
        "get position details", "fetch position details",
        "get details of a position", "fetch details of a position",
        "get details of my position", "fetch details of my position",
        "get details of a position in my account", "fetch details of a position in my account"
    ],
    "close_position": [
        "close a position", "terminate a position",
        "close my position", "terminate my position",
        "close a position in my account", "terminate a position in my account"
    ],
    "get_transactions": [
        "get transactions", "fetch transactions",
        "get my transactions", "fetch my transactions",
        "get transactions in my account", "fetch transactions in my account",
        "get transactions for my account", "fetch transactions for my account"
    ],
    "get_transaction_details": [
        "get transaction details", "fetch transaction details",
        "get details of a transaction", "fetch details of a transaction",
        "get details of my transaction", "fetch details of my transaction",
        "get details of a transaction in my account", "fetch details of a transaction in my account"
    ],
    "get_transactions_id_range": [
        "get transactions in range", "fetch transactions in range",
        "get transactions within a range", "fetch transactions within a range",
        "get transactions in a specific range", "fetch transactions in a specific range",
        "get transactions in a given range", "fetch transactions in a given range"
    ],
    "get_transactions_since_id": [
        "get transactions since ID", "fetch transactions since ID",
        "get transactions starting from ID", "fetch transactions starting from ID",
        "get transactions after ID", "fetch transactions after ID",
        "get transactions since a specific ID", "fetch transactions since a specific ID"
    ],
    "get_transaction_stream": [
        "get transaction stream", "fetch transaction stream",
        "get stream of transactions", "fetch stream of transactions",
        "get transactions in a streaming format", "fetch transactions in a streaming format"
    ],
    "get_latest_candles": [
        "get latest candles", "fetch latest candles",
        "get the most recent candles", "fetch the most recent candles",
        "get candles for the latest timeframe", "fetch candles for the latest timeframe"
    ],
    "get_pricing": [
        "get pricing", "fetch pricing", "retrieve pricing",
        "get pricing information", "fetch pricing information", "retrieve pricing information"
    ],
    "get_pricing_stream": [
        "get pricing stream", "fetch pricing stream",
        "get stream of pricing", "fetch stream of pricing",
        "get pricing in a streaming format", "fetch pricing in a streaming format"
    ],
    "get_instrument_candles": [
        "get instrument candles", "fetch instrument candles",
        "get candles for an instrument", "fetch candles for an instrument",
        "get candlestick data for an instrument", "fetch candlestick data for an instrument"
    ]
}   
intents = {
    "get_account_details": 0,
    "get_account_details": 1,
    "get_candlestick_data": 2,
    "get_order_book": 3,
    "get_position_book": 4, 
    "get_accounts": 5,
    "get_account_summary": 6,
    "get_account_instruments": 7,
    "set_account_configuration": 8,
    "get_account_changes": 9,
    "create_order": 10,
    "get_orders": 11,
    "get_pending_orders": 12,
    "get_order_details": 13,
    "replace_order": 14,
    "cancel_order": 15,
    "update_order_extensions": 16,
    "get_trades": 17,
    "get_open_trades": 18,
    "get_trade_details": 19,
    "close_trade": 20,
    "update_trade_extensions": 21,
    "update_trade_orders": 22,
    "get_positions": 23,
    "get_open_positions": 24,
    "get_position_details": 25,
    "close_position": 26,
    "get_transactions": 27,
    "get_transaction_details": 28,
    "get_transactions_id_range": 29,
    "get_transactions_since_id": 30,
    "get_transaction_stream": 31,
    "get_latest_candles": 32,
    "get_pricing": 33,
    "get_pricing_stream": 34,
    "get_instrument_candles": 35
}


# Define a list of keywords related to trading
trading_keywords = ["get account details", "fetch my account details", "retrieve account information","place a trade", "execute a trade", "enter a trade","buy order", "whats your name", "Trading Pal", "price to earnings", "PEG ratio", 
"price to earnings growth", "placing a trade", "market cap", "capitalization", "market order", 
"short interest", "dividend yield", "ROE", "return on equity", "ROA", "return on assets", 
"ROI", "return on investment", "current ratio", "quick ratio", "debt to equity", 
"profit margin", "gross margin", "operating margin", "net margin", "cash flow", 
"free cash flow", "EBITDA", "earnings before interest, taxes, depreciation, and amortization", 
"amortization", "depreciation", "capital expenditure", "capex", "inventory", 
"accounts receivable", "accounts payable", "liquidity ratio", "coverage ratio", 
"turnover ratio", "efficiency ratio", "leverage ratio", "solvency ratio", 
"FAANG", "Facebook", "Apple", "Amazon", "Netflix", "Google", "Alphabet", 
"Tesla", "Microsoft", "Nvidia", "AMD", "Intel", "Qualcomm", "Cisco", "Oracle", 
"IBM", "S&P 500", "Dow Jones", "Nasdaq", "FTSE 100", "Nikkei 225", "Hang Seng", 
"DAX", "CAC 40", "ASX 200", "BSE Sensex", "Nifty 50", "MSCI", "Russell 2000", 
"Wilshire 5000", "VIX", "volatility index", "gold", "silver", "platinum", "palladium", 
"oil", "crude oil", "natural gas", "gasoline", "heating oil", "coal", "corn", 
"wheat", "soybeans", "cotton", "sugar", "coffee", "cocoa", "rice", "oats", "barley", 
"livestock", "cattle", "hogs", "pork bellies", "lumber", "copper", "aluminum", 
"nickel", "zinc", "lead", "tin", "iron ore", "steel", "uranium", "lithium", "cobalt", 
"rare earths", "potash", "fertilizers", "agriculture", "metals", "mining", 
"energy", "utilities", "technology", "healthcare", "pharmaceuticals", "biotech", 
"consumer goods", "consumer services", "retail", "wholesale", "e-commerce", 
"industrials", "manufacturing", "construction", "real estate", "transportation", 
"logistics", "telecom", "media", "entertainment", "education", "travel", 
"hospitality", "food and beverages", "banking", "insurance", "finance", 
"investment", "private equity", "venture capital", "hedge funds", "ETFs", 
"exchange-traded funds", "mutual funds", "index funds", "managed funds", "passive investing", 
"active investing", "robo-advisors", "financial planning", "retirement planning", 
"estate planning""trade", "account", "transaction", "buy", "sell", "units", "position", "open", 
"close", "EUR/USD", "USD/JPY", "GBP/USD", "AUD/USD", "USD/CAD", "USD/CHF", "NZD/USD", 
"bitcoin", "ethereum", "ripple", "litecoin", "stop loss", "take profit", "limit order", 
"market order", "leverage", "margin", "long", "short", "bid", "ask", "spread", 
"volume", "liquidity", "pips", "lot", "bullish", "bearish", "breakout", "pullback", 
"reversal", "consolidation", "divergence", "overbought", "oversold", "resistance", 
"support", "trendline", "channel", "range", "volatility", "indicator", "RSI", "MACD", 
"Bollinger Bands", "moving average", "Fibonacci", "Ichimoku Cloud", "Stochastic", 
"ADX", "ATR", "CCI", "Pivot Points", "Parabolic SAR", "broker", "platform", 
"chart", "candlestick", "bar chart", "line chart", "order book", "fundamental analysis", 
"technical analysis", "sentiment analysis", "quantitative analysis", "qualitative analysis", 
"day trading", "swing trading", "scalping", "position trading", "carry trade", "hedging", 
"arbitrage", "martingale", "grid trading", "cost averaging", "pairs trading", 
"momentum trading", "mean reversion", "trend following", "breakout trading", 
"news trading", "value investing", "growth investing", "income investing", 
"dollar cost averaging", "lump sum investing", "dividend reinvestment", "asset allocation", 
"diversification", "risk management", "money management", "risk/reward ratio", "drawdown", 
"equity curve", "ROI", "return on investment", "profit factor", "Sharpe ratio", 
"Sortino ratio", "beta", "alpha", "standard deviation", "variance", "volatility index", 
"VIX", "futures", "options", "CFDs", "ETFs", "mutual funds", "bonds", "commodities", 
"real estate", "REITs", "indices", "index funds", "stocks", "shares", "securities", 
"derivatives", "swaps", "forwards", "interest rate", "yield", "dividend", "IPO", 
"initial public offering", "private equity", "venture capital", "leverage buyout", 
"mergers and acquisitions", "M&A", "bankruptcy", "debt", "credit", "rating", 
"inflation", "deflation", "stagflation", "recession", "depression", "economic growth", 
"GDP","forex", "crypto", "stock", "market", "trading", "currency", "bitcoin", "equity", "shares",  "forex",
"currency", "exchange rate", "pip", "lot", "spread", "margin", "leverage", "technical analysis",
"fundamental analysis", "indicator", "trend", "chart", "candlestick", "support", "resistance",
"crypto", "cryptocurrency", "bitcoin", "ethereum", "altcoin", "wallet", "blockchain", "mining",
"trading", "stock", "equity", "share", "market", "stock exchange", "index", "commodity", "futures",
"options", "bond", "yield", "dividend", "earnings", "valuation", "portfolio", "risk management",
"order", "stop loss", "take profit", "trailing stop", "position sizing", "risk-reward ratio",
"position management", "scalping", "day trading", "swing trading", "position trading", "long",
"short", "buy", "sell", "bid", "ask", "liquidity", "volume", "price action", "moving average",
"momentum", "oscillator", "RSI", "MACD", "Bollinger Bands", "Fibonacci retracement", "Elliott wave",
"crossover", "divergence", "support and resistance levels", "whipsaw", "gap", "pullback", "breakout",
"reversal", "continuation", "trend line", "candlestick pattern", "doji", "hammer", "engulfing", "harami",
"morning star", "evening star", "bullish", "bearish", "uptrend", "downtrend", "sideways market",
"volatility", "correlation", "diversification", "risk appetite", "fundamental news", "economic calendar",
"central bank", "interest rate", "inflation", "unemployment", "GDP", "earnings report", "SEC filings",
"insider trading", "market sentiment", "technical analysis software", "fundamental analysis software",
"trading platform", "broker", "spread betting", "CFD", "liquidity provider", "market maker", "order book",
"depth chart", "trade history", "position book", "risk management tool", "backtesting", "EUR/USD",
"live trading", "place", "trade", "instrument", "units","place a trade", "execute a trade", "enter a trade", "initiate a trade", "start a trade",
"establish a trade", "set a trade", "arrange a trade", "implement a trade",
"proceed with a trade", "carry out a trade", "perform a trade", "organize a trade",
"launch a trade", "put in a trade", "begin a trade", "kick off a trade", "activate a trade",
"trigger a trade", "apply a trade", "commit to a trade", "finalize a trade", "authorize a trade",
"confirm a trade", "validate a trade", "get my account details", "fetch my account details", "retrieve account information",
"show me my account details", "can I see my account details", "display my account information",
"provide my account details", "pull up my account details", "bring up my account information",
"let me see my account details", "access my account details", "uncover my account details",
"reveal my account details", "dig up my account information", "find my account details",
"present my account information", "check my account details", "look up my account information",
"see my account details", "unveil my account details", "expose my account information",
"inspect my account details", "view my account information", "discover my account details",
"outline my account information"]
