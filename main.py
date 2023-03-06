from time import sleep

import yfinance as yf
from pythonosc import udp_client

import config

_PREVIOUS_DATA: dict = dict()
_CURRENT_DATA: dict = dict()
_SEND_QUEUE: list = []


def get_stocks_data(tickers):
    return yf.download(tickers=tickers, period='5m', interval='1m')


def initialize_previous_data(tickers):
    for idx, ticker in enumerate(tickers):
        data_open = 0

        _PREVIOUS_DATA[ticker] = {
            'open': data_open,
        }


def update_tickers_data(tickers_list):
    for idx, ticker in enumerate(tickers_list):
        data = get_stocks_data(ticker)
        data_open = data['Open'][1]

        _CURRENT_DATA[ticker] = {
            'open': data_open,
        }

        if _PREVIOUS_DATA:
            if _CURRENT_DATA[ticker]['open'] > _PREVIOUS_DATA[ticker]['open']:
                _SEND_QUEUE.append(
                    f'{ticker} is up '
                    f'by {_CURRENT_DATA[ticker]["open"] - _PREVIOUS_DATA[ticker]["open"]}'
                    f' ({_CURRENT_DATA[ticker]["open"]})')
            elif _CURRENT_DATA[ticker]['open'] < _PREVIOUS_DATA[ticker]['open']:
                _SEND_QUEUE.append(
                    f'{ticker} is down by '
                    f'{_PREVIOUS_DATA[ticker]["open"] - _CURRENT_DATA[ticker]["open"]}'
                    f' ({_CURRENT_DATA[ticker]["open"]})')
            else:
                _SEND_QUEUE.append(f'{ticker} is the same ({_CURRENT_DATA[ticker]["open"]})')


if __name__ == '__main__':
    tickers_list = config.tickers

    client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

    while True:
        if _PREVIOUS_DATA:
            _PREVIOUS_DATA = _CURRENT_DATA
        else:
            initialize_previous_data(tickers_list)
        _CURRENT_DATA = dict()
        update_tickers_data(tickers_list)
        while _SEND_QUEUE:
            client.send_message("/chatbox/input", [_SEND_QUEUE.pop(), True])
            sleep(10)
