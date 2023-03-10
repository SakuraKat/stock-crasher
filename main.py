import importlib
from string import Template
from time import sleep

import yfinance as yf
from pandas import DataFrame
from pythonosc import udp_client
from pythonosc.udp_client import SimpleUDPClient

import config
import zaphkiel

_PREVIOUS_DATA: dict = dict()
_CURRENT_DATA: dict = dict()
_SEND_QUEUE: list[str] = []
_SUMMARY_SEND_QUEUE: list[str] = []


def get_stocks_data(tickers_list: str):
    timeout: int = config.timeout
    return yf.download(tickers=tickers_list, period='5m', interval='1m', progress=False, timeout=timeout)


def initialize_previous_data(tickers_list: list[str]):
    for idx, ticker in enumerate(tickers_list):
        data: DataFrame = get_stocks_data(ticker)
        data_open: float = data['Open'][1]

        _PREVIOUS_DATA[ticker] = {
            'open': data_open,
        }


def update_tickers_data(tickers_list: list[str]):
    if not _PREVIOUS_DATA:
        if debug_mode:
            print('idfk what happened but previous data is empty')
        return

    updates_only_mode: bool = config.updates_only_mode
    precision: int = config.precision
    if debug_mode:
        print(f'updates only mode: {updates_only_mode}')
        print(f'precision: {precision}')

    for idx, ticker in enumerate(tickers_list):
        data: DataFrame = get_stocks_data(ticker)
        data_open: float = data['Open'][1]

        _CURRENT_DATA[ticker] = {
            'open': data_open,
        }
        if debug_mode:
            print(f'current data for {ticker}: {_CURRENT_DATA[ticker]}')

        unit: str = '$'
        price: str = str(zaphkiel.round_number(_CURRENT_DATA[ticker]['open'], precision))
        change: float = _CURRENT_DATA[ticker]['open'] - _PREVIOUS_DATA[ticker]['open']
        change: str = str(zaphkiel.round_number(change, precision))

        if _CURRENT_DATA[ticker]['open'] > _PREVIOUS_DATA[ticker]['open']:
            if debug_mode:
                print(f'{ticker} is up')
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
            if debug_mode:
                print(f'{ticker} is down')
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
        if debug_mode:
            print(f'{ticker} is the same')
        if not updates_only_mode:
            _SEND_QUEUE.append(
                Template(config.same_msg)
                .substitute(
                    ticker=ticker,
                    unit=unit,
                    price=price,
                )
            )


if __name__ == '__main__':
    if config.debug_mode:
        print('Debug mode enabled.')
        print("Connecting to VRChat's OSC")
    client: SimpleUDPClient = udp_client.SimpleUDPClient("127.0.0.1", 9000)

    while True:
        tickers: list[str] = config.tickers
        time_between_messages: int = config.time_between_messages
        time_between_updates: int = config.time_between_updates
        debug_mode: bool = config.debug_mode
        if debug_mode:
            print(f"Tickers: {tickers}")
            print(f"Time between messages: {time_between_messages}")
            print(f"Time between updates: {time_between_updates}")
            print(f"Debug mode: {debug_mode}")

        if _PREVIOUS_DATA:
            _PREVIOUS_DATA.update(_CURRENT_DATA)
            if debug_mode:
                print("Previous data updated.")
        else:
            initialize_previous_data(tickers)
            if debug_mode:
                print("Previous data initialized.")
        _CURRENT_DATA: dict = dict()
        _SUMMARY_SEND_QUEUE: list[str] = []
        if debug_mode:
            print("Current data cleared.")

        update_tickers_data(tickers)
        if debug_mode:
            print("Tickers data updated.")

        while _SEND_QUEUE:
            if debug_mode:
                print(f"Sending message: {_SEND_QUEUE[0]}")
            zaphkiel.send_message(client, _SEND_QUEUE.pop(0))
            if debug_mode:
                print(f"Sleeping for {time_between_messages} seconds...")
            sleep(time_between_messages)
        summary_message: str = ' '.join(_SUMMARY_SEND_QUEUE)
        if debug_mode:
            print(f"Sending summary message: {summary_message}")
        zaphkiel.send_message(client, summary_message)

        if debug_mode:
            print(f"Sleeping for {time_between_updates} seconds...")
        sleep(time_between_updates)

        importlib.reload(config)
