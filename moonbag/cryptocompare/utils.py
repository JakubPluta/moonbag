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


BASE_PARSER_CONFIG =  {
    "coin" : False,
    "tosymbol": False,
    "exchange":False,
    "limit" : False,
    'sort' : False,
    'key' : False,
}

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
            default=100,
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
            required=True,
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

METHODS_MAPPER = {
    'coin': 'add_coin_argument',
    'tosymbol': 'add_to_symbol_argument',
    'limit': 'add_limit_argument',
    'exchange': 'add_exchange_argument',
    'sort': 'add_sort_argument',
    'key': 'add_key_argument',
}


class CustomParser:

    @staticmethod
    def _modify_default_dict_of_arguments(dct: dict, **kwargs):
        if kwargs:
            list_of_arguments = [
                'help', 'dest', 'required',
                'type', 'choices', 'default'
            ]

            for argument in list_of_arguments:
                if argument in kwargs:
                    dct[argument] = kwargs.get(argument)
        return dct

    @classmethod
    def add_coin_argument(cls, parser, **kwargs):
        dct = cls._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['coin'], **kwargs)
        parser.add_argument("-c","--coin",'--fsym', **dct)

    @classmethod
    def add_to_symbol_argument(cls,parser, **kwargs):
        dct = cls._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['tosymbol'], **kwargs)
        parser.add_argument("-t", "--tsym",'--to', **dct)

    @classmethod
    def add_limit_argument(cls, parser, **kwargs):
        dct = cls._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['limit'], **kwargs)
        parser.add_argument("-n","--limit", **dct)

    @classmethod
    def add_exchange_argument(cls, parser,  **kwargs):
        dct = cls._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['exchange'], **kwargs)
        parser.add_argument("-e", "--exchange", **dct)

    @classmethod
    def add_key_argument(cls, parser, **kwargs):
        dct = cls._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['key'], **kwargs)
        parser.add_argument("-k", "--key", **dct)

    @classmethod
    def add_sort_argument(cls, parser ,**kwargs):
        dct = cls._modify_default_dict_of_arguments(BASE_PARSER_ARGUMENTS['sort'], **kwargs)
        parser.add_argument("-s", "--sort", **dct)

    @classmethod
    def add_custom_argument(cls,  parser , *args, **kwargs):
        parser.add_argument(*args, **kwargs)

    @staticmethod
    def build_parser(parser, config=None):
        if not config:
            return parser
        for method_name, method in METHODS_MAPPER.items():
            if method_name in config and config[method_name] is True:
                getattr(customparser, method)(parser)
            elif method_name in config and isinstance(config[method_name], dict):
                getattr(customparser, method)(parser, **config[method_name])
        return parser


customparser = CustomParser()
build_parser = customparser.build_parser

# p = argparse.ArgumentParser(prog="kupa")
#
# pp = build_parser(p, config={"coin" : True, "tosymbol":True,}
#
# })
#
# #pp = build_parser(p)
# print(pp._actions)