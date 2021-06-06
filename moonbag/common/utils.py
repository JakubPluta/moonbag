import textwrap
import pandas as pd
import datetime
import logging
import argparse
import os

logger = logging.getLogger("utils")


def formatter(x):
    if isinstance(x, int):
        return "{0:.2f}".format(x)
    elif isinstance(x, float):
        if x > 10:
            return "{0:.2f}".format(x)
        else:
            return "{0:.6f}".format(x)
    return x


def table_formatter(func):  # pragma: no cover
    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)
        df = df.applymap(lambda x: formatter(x))
        return df

    return wrapper


# FIXME Make this func more general
def wrap_text_in_df(df: pd.DataFrame, w=55):  # pragma: no cover
    return df.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=w)) if isinstance(x, str) else x
    )


def underscores_to_newline_replace(cols: list, line: int = 13):
    return [
        textwrap.fill(c.replace("_", " "), line, break_long_words=False)
        for c in list(cols)
    ]


def wrap_headers_in_dataframe(df: pd.DataFrame, n=15, replace=None):
    if replace:
        return [
            textwrap.fill(c.replace(replace, " "), n, break_long_words=False)
            for c in list(df.columns)
        ]
    return [textwrap.fill(c, n, break_long_words=False) for c in list(df.columns)]


def created_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


BASE_PARSER_ARGUMENTS = {
    "coin": dict(
        help="Coin symbol",
        dest="symbol",
        required=True,
        default="ETH",
    ),
    "limit": dict(
        help="Number of results",
        dest="limit",
        required=False,
        type=int,
        default=50,
    ),
    "exchange": dict(
        help="Name of exchange",
        dest="exchange",
        required=False,
        type=str,
        default="Binance",
    ),
    "tosymbol": dict(
        help="To symbol - coin in which you want to see data",
        dest="tosymbol",
        required=False,
        type=str,
        default="USD",
    ),
    "key": dict(
        help="What you need recommendations for ? choose from [wallet, exchange]",
        dest="key",
        required=False,
        type=str,
        choices=["wallet", "exchange"],
        default="wallet",
    ),
    "sort": dict(
        help="Sorting [latest, popular]",
        dest="sort",
        required=False,
        type=str,
        default="latest",
        choices=["latest", "popular"],
    ),
    "address": dict(
        help="Token on-chain address",
        dest="address",
        required=True,
        type=str,
    ),
}


class MoonParser(argparse.ArgumentParser):
    list_of_arguments = ["help", "dest", "required", "type", "choices", "default"]

    def _modify_default_dict_of_arguments(self, dct: dict, **kwargs):
        if kwargs:
            for argument in self.list_of_arguments:
                if argument in kwargs:
                    dct[argument] = kwargs.get(argument)
        return dct

    def add_coin_argument(self, **kwargs):  # pragma: no cover
        dct = self._modify_default_dict_of_arguments(
            BASE_PARSER_ARGUMENTS["coin"], **kwargs
        )
        self.add_argument("-c", "--coin", "--fsym", **dct)

    def add_to_symbol_argument(self, **kwargs):  # pragma: no cover
        dct = self._modify_default_dict_of_arguments(
            BASE_PARSER_ARGUMENTS["tosymbol"], **kwargs
        )
        self.add_argument("-t", "--tsym", "--to", **dct)

    def add_limit_argument(self, **kwargs):  # pragma: no cover
        dct = self._modify_default_dict_of_arguments(
            BASE_PARSER_ARGUMENTS["limit"], **kwargs
        )
        self.add_argument("-n", "--limit", **dct)

    def add_exchange_argument(self, **kwargs):  # pragma: no cover
        dct = self._modify_default_dict_of_arguments(
            BASE_PARSER_ARGUMENTS["exchange"], **kwargs
        )
        self.add_argument("-e", "--exchange", **dct)

    def add_key_argument(self, **kwargs):  # pragma: no cover
        dct = self._modify_default_dict_of_arguments(
            BASE_PARSER_ARGUMENTS["key"], **kwargs
        )
        self.add_argument("-k", "--key", **dct)

    def add_sort_argument(self, **kwargs):  # pragma: no cover
        dct = self._modify_default_dict_of_arguments(
            BASE_PARSER_ARGUMENTS["sort"], **kwargs
        )
        self.add_argument("-s", "--sort", **dct)

    def add_address_argument(self, **kwargs):  # pragma: no cover
        dct = self._modify_default_dict_of_arguments(
            BASE_PARSER_ARGUMENTS["address"], **kwargs
        )
        self.add_argument("-a", "--address", **dct)


def clear():
    from sys import platform as _platform

    if _platform == "linux" or _platform == "linux2":
        os.system("clear")
    elif _platform == "darwin":
        os.system("clear")
    elif _platform == "win32" or _platform == "win64":
        os.system("cls")
