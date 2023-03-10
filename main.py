import importlib
from string import Template
from time import sleep

import yfinance as yf
from pandas import DataFrame
from pythonosc import udp_client
from pythonosc.udp_client import SimpleUDPClient
from yfinance import Ticker

import config
import zaphkiel

yf.set_tz_cache_location("tz-cache")

_TICKERS: dict = dict()
_PREVIOUS_DATA: dict = dict()
_CURRENT_DATA: dict = dict()
_SEND_QUEUE: list[str] = []
_SUMMARY_SEND_QUEUE: list[str] = []


def get_stocks_data(ticker: Ticker) -> DataFrame:
    timeout: int = config.timeout
    return ticker.history(period='1d', interval='1m', timeout=timeout)


def initialize_previous_data(tickers_list: list[str]) -> None:
    for idx, ticker_symbol in enumerate(tickers_list):
        if debug_mode:
            print(f'initializing previous data for {ticker_symbol}')
        data: DataFrame = get_stocks_data(_TICKERS[ticker_symbol])
        try:
            data_open: float = data['Open'][1]
        except IndexError:
            if debug_mode:
                print(f'no data for {ticker_symbol}')
            continue

        _PREVIOUS_DATA[ticker_symbol] = {
            'open': data_open,
        }
        if debug_mode:
            print(f'previous data for {ticker_symbol}: {_PREVIOUS_DATA[ticker_symbol]}')


def update_tickers_data(tickers_list: list[str]) -> None:
    if not _PREVIOUS_DATA:
        if debug_mode:
            print('idfk what happened but previous data is empty')
        return

    updates_only_mode: bool = config.updates_only_mode
    precision: int = config.precision
    if debug_mode:
        print(f'updates only mode: {updates_only_mode}')
        print(f'precision: {precision}')

    for idx, ticker_symbol in enumerate(tickers_list):
        data: DataFrame = get_stocks_data(_TICKERS[ticker_symbol])
        try:
            data_open: float = data['Open'][1]
        except IndexError:
            if debug_mode:
                print(f'no data for {ticker_symbol}')
            continue

        _CURRENT_DATA[ticker_symbol] = {
            'open': data_open,
        }
        if debug_mode:
            print(f'current data for {ticker_symbol}: {_CURRENT_DATA[ticker_symbol]}')

        unit: str = '$'
        price: str = str(zaphkiel.round_number(_CURRENT_DATA[ticker_symbol]['open'], precision))
        change: float = _CURRENT_DATA[ticker_symbol]['open'] - _PREVIOUS_DATA[ticker_symbol]['open']
        change: str = str(zaphkiel.round_number(change, precision))

        if _CURRENT_DATA[ticker_symbol]['open'] > _PREVIOUS_DATA[ticker_symbol]['open']:
            if debug_mode:
                print(f'{ticker_symbol} is up')
            _SEND_QUEUE.append(
                Template(config.up_msg)
                .substitute(
                    ticker=ticker_symbol,
                    unit=unit,
                    change=change,
                    price=price,
                )
            )
            _SUMMARY_SEND_QUEUE.append(f"⬆️{ticker_symbol}⬆️")
            continue
        elif _CURRENT_DATA[ticker_symbol]['open'] < _PREVIOUS_DATA[ticker_symbol]['open']:
            if debug_mode:
                print(f'{ticker_symbol} is down')
            _SEND_QUEUE.append(
                Template(config.down_msg)
                .substitute(
                    ticker=ticker_symbol,
                    unit=unit,
                    change=change,
                    price=price,
                )
            )
            _SUMMARY_SEND_QUEUE.append(f"⬇️{ticker_symbol}⬇️")
            continue
        if debug_mode:
            print(f'{ticker_symbol} is the same')
        if not updates_only_mode:
            _SEND_QUEUE.append(
                Template(config.same_msg)
                .substitute(
                    ticker=ticker_symbol,
                    unit=unit,
                    price=price,
                )
            )
            _SUMMARY_SEND_QUEUE.append(f"➡️{ticker_symbol}➡️")


if __name__ == '__main__':
    if config.debug_mode:
        print('Debug mode enabled.')
        print("Connecting to VRChat's OSC")

    client: SimpleUDPClient = udp_client.SimpleUDPClient("127.0.0.1", 9000)

    while True:
        tickers: list[str] = config.tickers
        for t in tickers:
            _TICKERS[t] = zaphkiel.get_ticker_obj(t)
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
