# Initialize position and trailing stop loss
position = 0  # 0 means no position, 1 means long, -1 means short
trailing_stop_loss = None
take_profit = None

# Initial balance and peak balance
starting_balance = balance = 100000
peak_balance = balance

# Drawdown
max_drawdown = 0

# Trading statistics
total_trades = 0
winning_trades = 0
losing_trades = 0
take_profit_hits = 0
trailing_stop_loss_hits = 0

# Backtesting
for i in range(1, len(df) - 1):  # We should stop at len(df) - 2
    # Current and previous close prices
    curr_close = df['close'].iloc[i]
    prev_close = df['close'].iloc[i-1]

    # Check if we are not in a position
    if position == 0:
        # Check for potential upward trend reversal (buy condition)
        if curr_close > prev_close:
            position = 1  # Enter a long position
            buy_price = curr_close
            trailing_stop_loss = df['low'].iloc[i-1]  # Initial trailing stop loss
            take_profit = curr_close * 1.02  # Take profit at 2% above the current close
            total_trades += 1

        # Check for potential downward trend reversal (sell condition)
        elif curr_close < prev_close:
            position = -1  # Enter a short position
            sell_price = curr_close
            trailing_stop_loss = df['high'].iloc[i-1]  # Initial trailing stop loss
            take_profit = curr_close * 0.98  # Take profit at 2% below the current close
            total_trades += 1

    # Check if we are in a long position
    elif position == 1:
        # Update trailing stop loss and take profit
        trailing_stop_loss = max(trailing_stop_loss, df['low'].iloc[i-1])
        take_profit = max(take_profit, df['close'].iloc[i+1])

        # Check for take profit condition
        if curr_close >= take_profit:
            position = 0  # Close the long position
            sell_price = curr_close
            old_balance = balance
            balance *= sell_price / buy_price  # Adjust the balance
            take_profit = None
            winning_trades += 1
            take_profit_hits += 1

        # Check for trailing stop loss hit
        elif curr_close < trailing_stop_loss:
            position = 0  # Close the long position
            sell_price = trailing_stop_loss
            old_balance = balance
            balance *= sell_price / buy_price  # Adjust the balance
            trailing_stop_loss = None
            losing_trades += 1
            trailing_stop_loss_hits += 1

    # Check if we are in a short position
    elif position == -1:
        # Update trailing stop loss and take profit
        trailing_stop_loss = min(trailing_stop_loss, df['high'].iloc[i-1])
        take_profit = min(take_profit, df['close'].iloc[i+1])

        # Check for take profit condition
        if curr_close <= take_profit:
            position = 0  # Close the short position
            buy_price = curr_close
            old_balance = balance
            balance *= sell_price / buy_price  # Adjust the balance
            take_profit = None
            winning_trades += 1
            take_profit_hits += 1

        # Check for trailing stop loss hit
        elif curr_close > trailing_stop_loss:
            position = 0  # Close the short position
            buy_price = trailing_stop_loss
            old_balance = balance
            balance *= sell_price / buy_price  # Adjust the balance
            trailing_stop_loss = None
            losing_trades += 1
            trailing_stop_loss_hits += 1

# Compute final trading statistics
total_profits = balance - starting_balance
win_rate = winning_trades / total_trades if total_trades else 0
loss_rate = losing_trades / total_trades if total_trades else 0

print(f"Starting balance: {starting_balance}")
print(f"Ending balance: {balance}")
print(f"Total profits: {total_profits}")
print(f"Max drawdown: {max_drawdown}")
print(f"Total trades: {total_trades}")
print(f"Winning trades: {winning_trades}")
print(f"Losing trades: {losing_trades}")
print(f"Win rate: {win_rate}")
print(f"Loss rate: {loss_rate}")
print(f"Take profit hits: {take_profit_hits}")
print(f"Trailing stop loss hits: {trailing_stop_loss_hits}")
