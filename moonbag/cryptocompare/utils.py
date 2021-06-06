import pandas as pd
import difflib
import logging
import argparse


logger = logging.getLogger("cryptocompare-utils")

# TODO Make those algorithms better for name
def get_closes_matches_by_name(name: str, coins: dict):  # pragma: no cover
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


def get_closes_matches_by_symbol(symbol: str, coins: dict):  # pragma: no cover
    sim = difflib.get_close_matches(symbol.upper(), list(coins.keys()), 10, cutoff=0.5)
    try:
        res = {s: coins.get(s) for s in sim}
    except TypeError as e:
        logger.log(2, e)
        res = {}
    return res


def create_dct_mapping_from_df(df, col1, col2):
    return dict(zip(df[col1], df[col2]))


def print_no_api_key_msg():  # pragma: no cover
    print(
        "\n\nYou didn't pass API key for CryptoComapre. You can't use that section.\n"
        "To do that please visit https://min-api.cryptocompare.com/ and get your free key\n"
        "Then go to moonbag.common.keys and add your key to variable CC_API_KEY\n"
        "CC_API_KEY = <your_key> and restart program\n"
    )
