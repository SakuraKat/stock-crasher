from math import floor

from pythonosc import udp_client


def send_message(client: udp_client.SimpleUDPClient, message: str) -> None:
    client.send_message("/chatbox/input", [message, True])


def round_number(number: float, decimal_places: int) -> float:
    return floor(number * (10 ** decimal_places)) / (10 ** decimal_places)
