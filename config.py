# List of stocks to track
# Default: ['UBER', 'AAPL', 'MSFT', 'TSLA']
tickers = [
    'UBER',
    'AAPL',
    'MSFT',
    'TSLA',
]

# Messages to send when a stock is up, down, or the same
# ${ticker} is the ticker symbol
# ${unit} is the currency unit
# ${change} is the change in price
# Default:
# up_msg = '${ticker} is 📈up📈 by 📈${unit}${change} (~${unit}${price}) BUY BUY BUY'
# down_msg = '${ticker} is 📉down📉 by 📉${unit}${change} (~${unit}${price}) SELL SELL SELL'
# same_msg = '${ticker} is the same (~${unit}${price}) 🛑HOLD🛑 🛑HOLD🛑 🛑HOLD🛑'

up_msg = '${ticker} is 📈up📈 by 📈${unit}${change} (~${unit}${price}) BUY BUY BUY'
down_msg = '${ticker} is 📉down📉 by 📉${unit}${change} (~${unit}${price}) SELL SELL SELL'
same_msg = '${ticker} is the same (~${unit}${price}) 🛑HOLD🛑 🛑HOLD🛑 🛑HOLD🛑'

# If True, only send updates when a stock changes
# If False, send updates every time the script runs
# Default: True
updates_only_mode = True

# Time between messages in seconds
# Default: 10
time_between_messages = 10

# Time between updates in seconds
# Default: 60
time_between_updates = 60

# Precision of the stock price
# 0 is show the full price
# Default: 4
precision = 4
