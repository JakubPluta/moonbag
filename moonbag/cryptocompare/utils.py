import pandas as pd
import difflib
import logging

logger = logging.getLogger('cryptocompare-utils')

# TODO Make those algorithms better for name
def get_closes_matches_by_name(name: str, coins: dict):
    sim = difflib.get_close_matches(name, list(coins.values()), 10, cutoff=0.3)
    res = {}
    try:
        for s in sim:
            for k, v in coins.items():
                if s == v:
                    res[k] = v
                else:
                    continue
    except TypeError as e:
        logger.log(2, e)
    return res


def get_closes_matches_by_symbol(symbol: str, coins: dict):
    sim = difflib.get_close_matches(symbol.upper(), list(coins.keys()), 10, cutoff=0.5)
    try:
        res = {s: coins.get(s) for s in sim}
    except TypeError as e:
        logger.log(2, e)
        res = {}
    return res

