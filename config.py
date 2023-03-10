# List of stocks to track
# Default: ['UBER', 'AAPL', 'MSFT', 'TSLA']
tickers = [
    'UBER',
    'AAPL',
    'MSFT',
    'TSLA',
]

up_msg = '${ticker} is up by ${unit}${change} (~${unit}${price}) BUY BUY BUY'
down_msg = '${ticker} is down by ${unit}${change} (~${unit}${price}) SELL SELL SELL'
same_msg = '${ticker} is the same (~${unit}${price}) HOLD HOLD HOLD'

# If True, only send updates when a stock changes
# If False, send updates every time the script runs
# Default: True
updates_only_mode = False

# Time between messages in seconds
# Default: 10
time_between_messages = 3

# Time between updates in seconds
# Default: 60
time_between_updates = 10

# Precision of the stock price
# 0 is show the full price
# Default: 4
precision = 4
