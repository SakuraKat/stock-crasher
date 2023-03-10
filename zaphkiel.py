from math import floor


def round_number(number, decimal_places):
    return floor(number * (10 ** decimal_places)) / (10 ** decimal_places)
