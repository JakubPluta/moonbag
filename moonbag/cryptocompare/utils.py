import pandas as pd
import difflib
import logging
import argparse


logger = logging.getLogger("cryptocompare-utils")

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


def create_dct_mapping_from_df(df, col1, col2):
    return dict(zip(df[col1], df[col2]))


def print_no_api_key_msg():
    print(
        "You didn't pass API key for CryptoComapre. You can't use that section.\n"
        "To do that please visit https://min-api.cryptocompare.com/ and get your free key\n"
        "Then go to moonbag.common.keys and add your key to variable CC_API_KEY"
        "CC_API_KEY = <your_key> and restart program"
    )


BASE_PARSER_ARGUMENTS = {
        'coin': dict(
            help='Coin symbol',
            dest='symbol',
            required=True,
            default='ETH',
        ),
        'limit': dict(
            help='Number of results',
            dest='limit',
            required=False,
            type=int,
            default=50,
        ),
        'exchange': dict(
            help='Name of exchange',
            dest="exchange",
            required=False,
            type=str,
            default="Binance",
        ),
        'tosymbol': dict(
            help="To symbol - coin in which you want to see data",
            dest="tosymbol",
            required=False,
            type=str,
            default="USD",
        ),
        'key': dict(
            help="What you need recommendations for ? choose from [wallet, exchange]",
            dest="key",
            required=False,
            type=str,
            choices=["wallet", "exchange"],
            default="wallet",
        ),
        'sort': dict(
            help="Sorting [latest, popular]",
            dest="sort",
            required=False,
            type=str,
            default="latest",
            choices=["latest", "popular"],
        )
}


class MoonParser(argparse.ArgumentParser):
    list_of_arguments = [
        'help', 'dest', 'required',
        'type', 'choices', 'default'
    ]

    def _modify_default_dict_of_arguments(self, dct: dict, **kwargs):
        if kwargs:
            for argument in self.list_of_arguments:
                if argument in kwargs:
                    dct[argument] = kwargs.get(argument)
        return dct

    def add_coin_argument(self, **kwargs):
        dct = self._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['coin'], **kwargs)
        self.add_argument("-c", "--coin", '--fsym', **dct)

    def add_to_symbol_argument(self, **kwargs):
        dct = self._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['tosymbol'], **kwargs)
        self.add_argument("-t", "--tsym", '--to', **dct)

    def add_limit_argument(self, **kwargs):
        dct = self._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['limit'], **kwargs)
        self.add_argument("-n", "--limit", **dct)

    def add_exchange_argument(self, **kwargs):
        dct = self._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['exchange'], **kwargs)
        self.add_argument("-e", "--exchange", **dct)

    def add_key_argument(self, **kwargs):
        dct = self._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['key'], **kwargs)
        self.add_argument("-k", "--key", **dct)

    def add_sort_argument(self, **kwargs):
        dct = self._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['sort'], **kwargs)
        self.add_argument("-s", "--sort", **dct)
