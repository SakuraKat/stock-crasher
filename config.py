# List of stocks to track
# Default: ['UBER', 'AAPL', 'MSFT', 'TSLA', 'GME', 'AMC', 'BBY', 'APE', 'DKNG']
tickers: list[str] = [
    'UBER',
    'AAPL',
    'MSFT',
    'TSLA',
    'GME',
    'AMC',
    'BBY',
    'APE',
    'DKNG',
]

# Messages to send when a stock is up, down, or the same
# ${ticker} is the ticker symbol
# ${unit} is the currency unit
# ${change} is the change in price
# Default:
# up_msg = '${ticker} is ⬆️up⬆️ by ${unit}${change} (~${unit}${price}) BUY BUY BUY'
# down_msg = '${ticker} is ⬇️down⬇️ by ${unit}${change} (~${unit}${price}) SELL SELL SELL'
# same_msg = '${ticker} is the same (~${unit}${price}) 🛑HOLD🛑 🛑HOLD🛑 🛑HOLD🛑'
up_msg: str = '${ticker} is ⬆️up⬆️ by ${unit}${change} (~${unit}${price}) BUY BUY BUY'
down_msg: str = '${ticker} is ⬇️down⬇️ by ${unit}${change} (~${unit}${price}) SELL SELL SELL'
same_msg: str = '${ticker} is the same (~${unit}${price}) 🛑HOLD🛑 🛑HOLD🛑 🛑HOLD🛑'

# Updates only mode
# If True, only send updates when a stock changes
# If False, send updates every time the script runs
# Default: True
updates_only_mode: bool = True

# Time between messages in seconds
# Default: 10
time_between_messages: int = 10

# Time between updates in seconds
# Default: 60
time_between_updates: int = 60

# Precision of the stock price
# Set it to 0 to show the full price
# Default: 4
precision: int = 4

# Timeout for requests in seconds
# Default: 3
timeout: int = 3

# Debug mode
# If True, print debug messages
# If False, don't print debug messages
# Default: False
debug_mode: bool = False
