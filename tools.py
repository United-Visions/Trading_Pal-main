from typing import Dict, Any, List
import json

class Tool:
    def __init__(self, name: str, description: str, function: callable, required_params: List[str] = None):
        self.name = name
        self.description = description
        self.function = function
        self.required_params = required_params or []

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Tool] = {}

    def register(self, name: str, description: str, function: callable, required_params: List[str] = None):
        self.tools[name] = Tool(name, description, function, required_params)

    def get_tool(self, name: str) -> Tool:
        return self.tools.get(name)

    def get_tool_descriptions(self) -> str:
        descriptions = []
        for tool in self.tools.values():
            params = ", ".join(tool.required_params) if tool.required_params else "none"
            descriptions.append(f"Tool: {tool.name}\nDescription: {tool.description}\nRequired Parameters: {params}\n")
        return "\n".join(descriptions)

    def create_trading_strategy(self, strategy_type: str, timeframe: str, currency_pair: str) -> dict:
        """Create a trading strategy template based on type"""
        templates = {
            "trend_following": {
                "name": f"Trend Following Strategy - {currency_pair} {timeframe}",
                "description": "A trend following strategy using moving averages and RSI",
                "code": """
import pandas as pd
import numpy as np

def initialize(context):
    context.sma_short = 20
    context.sma_long = 50
    context.rsi_period = 14
    context.rsi_upper = 70
    context.rsi_lower = 30

def calculate_signals(df):
    # Calculate SMAs
    df['SMA_short'] = df['close'].rolling(window=context.sma_short).mean()
    df['SMA_long'] = df['close'].rolling(window=context.sma_long).mean()
    
    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=context.rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=context.rsi_period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Generate signals
    df['signal'] = 0
    df.loc[(df['SMA_short'] > df['SMA_long']) & (df['RSI'] < context.rsi_upper), 'signal'] = 1
    df.loc[(df['SMA_short'] < df['SMA_long']) & (df['RSI'] > context.rsi_lower), 'signal'] = -1
    
    return df

def backtest(df):
    context = type('Context', (), {})()
    initialize(context)
    
    df = calculate_signals(df)
    df['position'] = df['signal'].shift(1)
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['position'] * df['returns']
    
    backtestResults = {
        'total_returns': float(df['strategy_returns'].sum()),
        'sharpe_ratio': float(df['strategy_returns'].mean() / df['strategy_returns'].std() * np.sqrt(252)),
        'max_drawdown': float(df['strategy_returns'].cumsum().diff().min()),
        'win_rate': float(len(df[df['strategy_returns'] > 0]) / len(df[df['strategy_returns'] != 0]))
    }
    
    return backtestResults
"""
            },
            "breakout": {
                "name": f"Breakout Strategy - {currency_pair} {timeframe}",
                "description": "A breakout strategy using Bollinger Bands",
                # Add breakout strategy template code here
            },
            "mean_reversion": {
                "name": f"Mean Reversion Strategy - {currency_pair} {timeframe}",
                "description": "A mean reversion strategy using RSI and Bollinger Bands",
                # Add mean reversion strategy template code here
            }
        }
        
        return templates.get(strategy_type, templates["trend_following"])

# Register the new tool
tool_registry = ToolRegistry()
tool_registry.register(
    "create_trading_strategy",
    "Create a trading strategy template for backtesting",
    tool_registry.create_trading_strategy,
    ["strategy_type", "timeframe", "currency_pair"]
)

def create_strategy_template(strategy_type: str, timeframe: str, currency_pair: str) -> dict:
    """Create a strategy template based on type"""
    
    templates = {
        "trend_following": {
            "name": f"Trend Following Strategy - {currency_pair} {timeframe}",
            "description": "A trend following strategy using moving averages and RSI",
            "code": """
import pandas as pd
import numpy as np

def initialize(context):
    context.sma_short = 20
    context.sma_long = 50
    context.rsi_period = 14
    context.rsi_upper = 70
    context.rsi_lower = 30

def calculate_signals(df):
    # Calculate SMAs
    df['SMA_short'] = df['close'].rolling(window=context.sma_short).mean()
    df['SMA_long'] = df['close'].rolling(window=context.sma_long).mean()
    
    # Calculate RSI
    delta = df['close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=context.rsi_period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=context.rsi_period).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))
    
    # Generate signals
    df['signal'] = 0
    df.loc[(df['SMA_short'] > df['SMA_long']) & (df['RSI'] < context.rsi_upper), 'signal'] = 1
    df.loc[(df['SMA_short'] < df['SMA_long']) & (df['RSI'] > context.rsi_lower), 'signal'] = -1
    
    return df

def backtest(df):
    context = type('Context', (), {})()
    initialize(context)
    
    df = calculate_signals(df)
    df['position'] = df['signal'].shift(1)
    df['returns'] = df['close'].pct_change()
    df['strategy_returns'] = df['position'] * df['returns']
    
    backtestResults = {
        'total_returns': float(df['strategy_returns'].sum()),
        'sharpe_ratio': float(df['strategy_returns'].mean() / df['strategy_returns'].std() * np.sqrt(252)),
        'max_drawdown': float(df['strategy_returns'].cumsum().diff().min()),
        'win_rate': float(len(df[df['strategy_returns'] > 0]) / len(df[df['strategy_returns'] != 0]))
    }
    
    return backtestResults
"""
        },
        "breakout": {
            "name": f"Breakout Strategy - {currency_pair} {timeframe}",
            "description": "A breakout strategy using Bollinger Bands",
            # Add breakout strategy template code here
        },
        "mean_reversion": {
            "name": f"Mean Reversion Strategy - {currency_pair} {timeframe}",
            "description": "A mean reversion strategy using RSI and Bollinger Bands",
            # Add mean reversion strategy template code here
        }
    }
    
    return templates.get(strategy_type, templates["trend_following"])

def create_blank_strategy(params: dict) -> dict:
    """Create a new blank strategy with basic template"""
    try:
        strategy_type = params.get('type', 'trend_following')
        timeframe = params.get('timeframe', 'H1')
        currency_pair = params.get('currency_pair', 'USD_CAD')
        
        template = create_strategy_template(strategy_type, timeframe, currency_pair)
        
        return {
            "status": "success",
            "strategy": {
                "name": template["name"],
                "description": template["description"],
                "code": template["code"],
                "currency_pair": currency_pair,
                "timeframe": timeframe,
                "type": strategy_type
            }
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e)
        }
