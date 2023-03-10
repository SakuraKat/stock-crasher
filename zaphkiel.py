from abc import ABC
from math import floor

from pythonosc import udp_client
from requests import Session
from requests_cache import CacheMixin, SQLiteCache
from requests_ratelimiter import LimiterMixin, MemoryQueueBucket
from yfinance import Ticker


class CachedLimiterSession(CacheMixin, LimiterMixin, Session, ABC):
    """ """


def _get_session() -> CachedLimiterSession:
    session: CachedLimiterSession = CachedLimiterSession(
        per_second=0.9,
        bucket_class=MemoryQueueBucket,
        backend=SQLiteCache("yfinance.cache"),
    )
    session.headers['User-agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) ' \
                                    'AppleWebKit/537.36 (KHTML, like Gecko) ' \
                                    'Chrome/111.0.0.0 Safari/537.36'
    return session


_CACHED_SESSION: CachedLimiterSession = _get_session()


def get_session() -> CachedLimiterSession:
    global _CACHED_SESSION
    if not _CACHED_SESSION:
        _CACHED_SESSION = _get_session()

    return _CACHED_SESSION


def send_message(client: udp_client.SimpleUDPClient, message: str) -> None:
    client.send_message("/chatbox/input", [message, True])


def round_number(number: float, decimal_places: int) -> float:
    return floor(number * (10 ** decimal_places)) / (10 ** decimal_places)


def get_ticker_obj(ticker_symbol: str) -> Ticker:
    return Ticker(ticker_symbol, session=get_session())
