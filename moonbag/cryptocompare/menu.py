from moonbag.cryptocompare.cryptocomp import CryptoCompare, API_KEY
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
import difflib
import pandas as pd
import textwrap
from argparse import ArgumentError

logger = logging.getLogger("compare-menu")

compare = CryptoCompare(API_KEY)


class Controller:

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="coin", add_help=False)
        self.parser.add_argument("cmd")
        self.base_commands = ["help", "exit", "quit", "r", "q"]

    @staticmethod
    def show_prices(args):
        parser = argparse.ArgumentParser(
            prog="prices",
            add_help=True,
            description="get prices",
        )
        parser.add_argument(
            "-c", "--coin", help="Coin to get", dest="symbol", required=True, type=str,
        )
        parser.add_argument(
            "-f", "--fiat",'--currency', help="Coin to get", dest="currency", required=False, type=str,
            default='USD'
        )

        if not args:
            print("You didn't pass coin symbol. Please use price -c symbol")
            return

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        if not parsy.currency:
            parsy.currency = 'USD'

        try:
            prices = compare.get_price(parsy.symbol, parsy.currency)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coinlist ")
            return
        print_table(prices)

    @staticmethod
    def show_coins():
        print_table(compare.coin_list)

    @staticmethod
    def find_similar_coins(args):
        parser = argparse.ArgumentParser(
            prog="similar",
            add_help=True,
            description="Find similar coins",
        )
        parser.add_argument('-c', '--coin',
                            help="Symbol/Name of Coin", dest="symbol", required=True, type=str,
                            )

        parser.add_argument('-k', '--key',
                            help="search by symbol or name", dest="key", required=False, type=str,
                            default='symbol', choices=['symbol','name']
                            )

        if not args:
            print("You didn't pass coin symbol. Please use similar -c symbol")
            return

        parsy, others = parser.parse_known_args(args)
        if not parsy or parsy.symbol is None:
            return

        coin_df = compare.coin_list
        coins = dict(zip(coin_df['Symbol'],coin_df['FullName']))

        if parsy.key == 'name':
            sim = difflib.get_close_matches(parsy.symbol.upper(), list(coins.values()), 10,cutoff=0.3)
            if sim:
                res = {}
                for s in sim:
                    for k, v in coins.items():
                        if s == v:
                            res[k] = v
                        else:
                            continue
                df = pd.Series(res).to_frame().reset_index()
                df.columns = ['Symbol', 'Name']
                print_table(df)
        else:
            sim = difflib.get_close_matches(parsy.symbol.upper(), list(coins.keys()), 10,cutoff=0.5)
            if sim:
                res = {s : coins.get(s) for s in sim}
                df = pd.Series(res).to_frame().reset_index()
                df.columns = ['Symbol', 'Name']
                print_table(df)
            else:
                print_table(pd.DataFrame())

    @staticmethod
    def show_top_list_by_market_cap(args):
        parser = argparse.ArgumentParser(
            prog="topmcap",
            add_help=True,
            description="get top market cap",
        )
        parser.add_argument(
            "-f", "--fiat", '--currency', help="Coin to get", dest="currency", required=False, type=str,
            default='USD'
        )
        parser.add_argument(
            "-n", "--num", '--limit', help="top n of coins", dest="limit", required=False, type=int,
            default=50
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        if not parsy.currency:
            parsy.currency = 'USD'

        if not parsy.limit:
            parsy.limit = 50

        try:
            df = compare.get_top_list_by_market_cap(
                currency=parsy.currency, limit=parsy.limit)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coinlist ")
            return
        print_table(df)

    @staticmethod
    def show_top_exchanges(args):
        parser = argparse.ArgumentParser(
            prog="exchanges",
            add_help=True,
            description="get top exchanges",
        )
        parser.add_argument(
            "-c", "--coin", help="Coin to get", dest="symbol", required=False, type=str, default='BTC'
        )
        parser.add_argument(
            "-f", "--fiat", '--currency', help="currency", dest="currency", required=False, type=str,
            default='USD'
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        if not parsy.symbol:
            parsy.currency = 'BTC'

        if not parsy.currency:
            parsy.currency = 'USD'

        try:
            prices = compare.get_top_exchanges(parsy.symbol, parsy.currency)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coinlist ")
            return
        print_table(prices)

    @staticmethod
    def show_news(args):
        parser = argparse.ArgumentParser(
            prog="news",
            add_help=True,
            description="latest news",
        )
        parser.add_argument('-s', '--sort',
                            help="Sorting [latest, popular]",
                            dest="sort", required=False, type=str, default='latest',
                            choices=["latest" , "popular"]
                            )
        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        try:
            df = compare.get_latest_news()
            df = df.applymap(
                lambda x: "\n".join(textwrap.wrap(x, width=200))
                if isinstance(x, str)
                else x
            )
        except ValueError as e:
            print(f"{e} ")
            return
        print_table(df)

    @staticmethod
    def _get_prices(args):
        parser = argparse.ArgumentParser(
            prog="histoprices",
            add_help=True,
            description="get historical prices",
        )
        parser.add_argument(
            "-c", "--coin", help="Coin symbol", dest="symbol", required=False, type=str, default='BTC'
        )
        parser.add_argument(
            "-f", "--fiat", '--currency', help="currency [default USD]", dest="currency", required=False, type=str,
            default='USD'
        )

        parser.add_argument(
            "-n", "--num", '--limit', help="last n quotes", dest="limit", required=False, type=int,
            default=100
        )

        if not args:
            print("You didn't pass coin symbol. Please use price -c symbol")
            return

        parsy, _ = parser.parse_known_args(args)
        return parsy

    def get_day_prices(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            parsy = self._get_prices(args)
            prices = compare.get_historical_day_prices(parsy.symbol, parsy.currency, parsy.limit)
        except ValueError as e:
            print(f"{e}, ")
            return
        print_table(prices)

    def get_hour_prices(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = compare.get_historical_hour_prices(parsy.symbol, parsy.currency)
        except ValueError as e:
            print(f"{e}, ")
            return
        print_table(prices)

    def get_minute_prices(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = compare.get_historical_minutes_prices(parsy.symbol, parsy.currency)
        except ValueError as e:
            print(f"{e}, ")
            return
        print_table(prices)

    @staticmethod
    def get_trading_signals(args):
        parser = argparse.ArgumentParser(
            prog="topmcap",
            add_help=True,
            description="get top market cap",
        )
        parser.add_argument(
            "-c", "--coin", help="Coin to get", dest="symbol", required=True, type=str,
            default='ETH'
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        try:
            df = compare.get_latest_trading_signals(parsy.symbol)
        except ValueError as e:
            print(f"{e} ")
            return
        if df.empty:
            print(f"No tradings signals found for coin {parsy.symbol}")
        else:
            print_table(df)

    @staticmethod
    def show_orderbooks():
        df = compare.get_order_books_exchanges()
        print_table(df)

    @staticmethod
    def get_top_orders(args):
        parser = argparse.ArgumentParser(
            prog="orders",
            add_help=True,
            description="get order book for pair of coins",
        )
        parser.add_argument(
            "-c", "--coin", help="Coin to get", dest="symbol", required=True, type=str,
            default='ETH'
        )
        parser.add_argument(
            "-o", "--other", '--tsym', help="to symbol, second pair", dest="tsym", required=False, type=str,
            default='BTC'
        )
        parser.add_argument(
            "-e", "--exchange", help="exchange", dest="exchange", required=False, type=str,
            default='binance'
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = compare.get_order_book_top(
                symbol=parsy.symbol, to_symbol=parsy.tsym, exchange=parsy.exchange)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coinlist ")
            return
        print_table(df)

    def show_all_exchanges(self):
        df = compare.get_all_exchanges_names()
        print_table(df)



def main():
    c = Controller()
    choices = c.base_commands + ['price','coinlist','similar','topmcap','exchanges','news', 'listexchanges',
                                 'dprice','hprice','mprice','tsignals','orders']

    parser = argparse.ArgumentParser(prog="cmc", add_help=False)
    parser.add_argument("cmd", choices=choices)
    print(LOGO)
    while True:
        an_input = input(f"> {MOON} ")
        try:
            parsy, others = parser.parse_known_args(an_input.split())
            cmd = parsy.cmd

            if cmd == "help":
                print('help')
            elif cmd in ["exit", "quit", "q"]:
                return False
            elif cmd == "r":
                return True

            if cmd == 'price':
                c.show_prices(others)
            elif cmd == 'coinlist':
                c.show_coins()
            elif cmd == 'similar':
                c.find_similar_coins(others)
            elif cmd == 'topmcap':
                c.show_top_list_by_market_cap(others)

            elif cmd == 'exchanges':
                c.show_top_exchanges(others)

            elif cmd == 'news':
                c.show_news(others)
            elif cmd == 'hprice':
                c._get_prices(others)
            elif cmd == 'dprice':
                c.get_day_prices(others)
            elif cmd == 'mprice':
                c.get_minute_prices(others)

            elif cmd == 'tsignals':
                c.get_trading_signals(others)

            elif cmd == 'orders':
                c.get_top_orders(others)
            elif cmd == 'listexchanges':
                c.show_all_exchanges()


        except ArgumentError:
            print("The command selected doesn't exist")
            print("\n")
            continue

        except SystemExit:
            print("\n")
            continue


if __name__ == "__main__":
    main()
