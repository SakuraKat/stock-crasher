from string import Template
from time import sleep

import yfinance as yf
from pythonosc import udp_client

import config
import zaphkiel

_PREVIOUS_DATA: dict = dict()
_CURRENT_DATA: dict = dict()
_SEND_QUEUE: list = []
_SUMMARY_SEND_QUEUE: list = []


def get_stocks_data(tickers_list):
    return yf.download(tickers=tickers_list, period='5m', interval='1m', progress=False)


def initialize_previous_data(tickers_list):
    for idx, ticker in enumerate(tickers_list):
        data_open = 0
        data_high = 0

        _PREVIOUS_DATA[ticker] = {
            'open': data_open,
            'high': data_high,
        }


def update_tickers_data(tickers_list):
    if not _PREVIOUS_DATA:
        return

    _UPDATES_ONLY_MODE: bool = config.updates_only_mode
    _PRECISION: int = config.precision

    for idx, ticker in enumerate(tickers_list):
        data = get_stocks_data(ticker)
        data_open: float = data['Open'][1]
        data_high: float = data['High'][1]

        _CURRENT_DATA[ticker] = {
            'open': data_open,
            'high': data_high,
        }

        unit = '$'
        price: str = str(zaphkiel.round_number(_CURRENT_DATA[ticker]['open'], _PRECISION))
        change: float = _CURRENT_DATA[ticker]['open'] - _PREVIOUS_DATA[ticker]['open']
        change: str = str(zaphkiel.round_number(change, _PRECISION))

        if _CURRENT_DATA[ticker]['open'] > _PREVIOUS_DATA[ticker]['open']:
            _SEND_QUEUE.append(
                Template(config.up_msg)
                .substitute(
                    ticker=ticker,
                    unit=unit,
                    change=change,
                    price=price,
                )
            )
            _SUMMARY_SEND_QUEUE.append(f"⬆️{ticker}⬆️")
            continue
        elif _CURRENT_DATA[ticker]['open'] < _PREVIOUS_DATA[ticker]['open']:
            _SEND_QUEUE.append(
                Template(config.down_msg)
                .substitute(
                    ticker=ticker,
                    unit=unit,
                    change=change,
                    price=price,
                )
            )
            _SUMMARY_SEND_QUEUE.append(f"⬇️{ticker}⬇️")
            continue
        if not _UPDATES_ONLY_MODE:
            _SEND_QUEUE.append(
                Template(config.same_msg)
                .substitute(
                    ticker=ticker,
                    unit=unit,
                    price=price,
                )
            )


if __name__ == '__main__':
    client = udp_client.SimpleUDPClient("127.0.0.1", 9000)

    while True:
        tickers: list[str] = config.tickers
        time_between_messages = config.time_between_messages
        time_between_updates = config.time_between_updates

        if _PREVIOUS_DATA:
            _PREVIOUS_DATA = _CURRENT_DATA
        else:
            initialize_previous_data(tickers)
        _CURRENT_DATA = dict()

        update_tickers_data(tickers)

        while _SEND_QUEUE:
            zaphkiel.send_message(client, _SEND_QUEUE.pop(0))
            sleep(time_between_messages)
        summary_message = ' '.join(_SUMMARY_SEND_QUEUE)
        _SUMMARY_SEND_QUEUE = []
        zaphkiel.send_message(client, summary_message)
        sleep(time_between_updates)
