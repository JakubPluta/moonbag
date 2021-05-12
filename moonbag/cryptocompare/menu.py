from moonbag.cryptocompare.cryptocomp import CryptoCompare, API_KEY
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
import difflib
import pandas as pd
import textwrap
from argparse import ArgumentError
from moonbag.cryptocompare.utils import get_closes_matches_by_name, get_closes_matches_by_symbol
logger = logging.getLogger("compare-menu")

compare = CryptoCompare(API_KEY)


class Controller:

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="coin", add_help=False)
        self.parser.add_argument("cmd")
        self.base_commands = ["help", "exit", "quit", "r", "q"]
        self.mapper = {
        }

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("CryptoCompare        You need API_KEY to use this menu.")
        print("   news              show latest crypto news [CryptoCompare]")
        print("   coins             show available coins: Symbol and Names [CryptoCompare]")
        print("   similar           try to find coin symbol [CryptoCompare]")
        print("   topmc             try to find coin symbol [CryptoCompare]")

        print("   topex             show top  exchanges for given pair: Default BTC/USD [CryptoCompare]")
        print("   lex               show names of all exchanges  [CryptoCompare]")
        print("   topexsym          show top coins on given exchange [CryptoCompare]")
        print("   orders            show  order book for given pair and exchange. Default LUNA/BTC, Binance [CryptoCompare]")

        print("   price             show latest price info for given pair like BTC/USD [CryptoCompare]")
        print("   priced            show historical prices with 1 day interval [CryptoCompare]")
        print("   priceh            show historical prices with 1 hour interval [CryptoCompare]")
        print("   pricem            show historical prices with 1 min interval [CryptoCompare]")

        print("   volumed           show daily volume for given pair. Default: BTC/USD [CryptoCompare]")
        print("   volumeh           show hourly volume for given pair. Default: BTC/USD [CryptoCompare]")

        print("   tsignals          show latest trading signals for given coin. Default ETH [CryptoCompare]")
        print("   pairvolume        show latest volume for given pair of coins [CryptoCompare]")
        print("   toptrading        show top trading pairs for given coin [CryptoCompare]")
        print("   onchain           show list of coins with on-chain data available [CryptoCompare]")
        print("   chaincoin         show on chain data for given coin [CryptoCompare]")
        print("   hchaincoin        show historical on chain data for given coin [CryptoCompare]")

        print(" ")
        return

    @staticmethod
    def show_prices(args):
        parser = argparse.ArgumentParser(
            prog="prices",
            add_help=True,
            description="get prices",
        )
        parser.add_argument(
            '-c', "-fsym", help="symbol of the coin",
            dest="symbol", required=True, type=str,
        )
        parser.add_argument(
            '-t',"-tsym", help="symbol of second coin in pair. Default: USD", dest="tosymbol", required=False, type=str,
            default='USD'
        )

        if not args:
            print("You didn't pass coin symbol. Please use price -c symbol")
            return

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        try:
            prices = compare.get_price(parsy.symbol, parsy.tosymbol)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coins ")
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
                            help="symbol or name of coin", dest="symbol", required=True, type=str,
                            )

        parser.add_argument('-k', '--key',
                            help="search by symbol or name", dest="key", required=False, type=str,
                            default='symbol', choices=['symbol', 'name']
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
            res = get_closes_matches_by_name(parsy.symbol, coins)
        else:
            res = get_closes_matches_by_symbol(parsy.symbol, coins)
        if res:
            df = pd.Series(res).to_frame().reset_index()
            df.columns = ['Symbol', 'Name']
            print_table(df)
        else:
            print(pd.DataFrame())

    @staticmethod
    def show_top_list_by_market_cap(args):
        parser = argparse.ArgumentParser(
            prog="topmc",
            add_help=True,
            description="get top market cap coins",
        )
        parser.add_argument(
            "-t", "--tsym", help="Denomination coin in which you want to see market cap",
            dest="tosymbol", required=False, type=str,
            default='USD'
        )
        parser.add_argument(
            "-n", "--num", '--limit', help="top n of coins", dest="limit", required=False, type=int,
            default=50
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = compare.get_top_list_by_market_cap(
                currency=parsy.tosymbol, limit=parsy.limit)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coins ")
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
            "-t", "--tsym", help="tosymbol", dest="tosymbol", required=False, type=str,
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
            prices = compare.get_top_exchanges(parsy.symbol, parsy.tosymbol)
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
            df = compare.get_latest_news(sort_order=parsy.sort)
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
            "-t", "--tsym", help="to symbol [default USD]", dest="tosymbol", required=False, type=str,
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
            prices = compare.get_historical_day_prices(parsy.symbol, parsy.tosymbol, parsy.limit)
        except ValueError as e:
            print(f"{e}, ")
            return
        print_table(prices)

    def get_hour_prices(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = compare.get_historical_hour_prices(parsy.symbol, parsy.tosymbol)
        except ValueError as e:
            print(f"{e}, ")
            return
        print_table(prices)

    def get_minute_prices(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = compare.get_historical_minutes_prices(parsy.symbol, parsy.tosymbol)
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
            "-t", '--tsym', help="to symbol, second pair", dest="tsym", required=False, type=str,
            default='BTC'
        )
        parser.add_argument(
            "-e", "--exchange", help="exchange", dest="exchange", required=False, type=str,
            default='Binance'
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

    @staticmethod
    def show_all_exchanges():
        df = compare.get_all_exchanges_names()
        print_table(df)

    @staticmethod
    def show_exchanges_by_top_symbol(args):
        parser = argparse.ArgumentParser(
            prog="exchange symbols",
            add_help=True,
            description="get order book for pair of coins",
        )

        parser.add_argument(
            "-e", "--exchange", help="exchange", dest="exchange", required=False, type=str,
            default='binance'
        )

        parser.add_argument(
            "-n", "--num", '--limit', help="last n quotes", dest="limit", required=False, type=int,
            default=100
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = compare.get_exchanges_top_symbols_by_volume(
                exchange=parsy.exchange, limit=parsy.limit)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(df)

    @staticmethod
    def get_top_list_pair_volume(args):
        parser = argparse.ArgumentParser(
            prog="pairvolume",
            add_help=True,
            description="get top list by pair volume",
        )
        parser.add_argument(
            "-t", "--tsym", help="tosymbol", dest="tosymbol", required=False, type=str,
            default='USD'
        )
        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = compare.get_top_list_by_pair_volume(parsy.tosymbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(df)

    def show_daily_coin_volume(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = compare.get_daily_symbol_volume(parsy.symbol, parsy.tosymbol, parsy.limit)
        except ValueError as e:
            print(f"{e}, ")
            return
        print_table(prices)

    def show_hourly_coin_volume(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = compare.get_hourly_symbol_volume(parsy.symbol, parsy.tosymbol, parsy.limit)
        except ValueError as e:
            print(f"{e}, ")
            return
        print_table(prices)

    @staticmethod
    def show_available_blockchain_lists():
        print_table(compare.get_blockchain_available_coins_list())


    @staticmethod
    def show_latest_blockchain_data(args):
        parser = argparse.ArgumentParser(
            prog="blockchain data",
            add_help=True,
            description="get top list by pari folvume",
        )
        parser.add_argument(
            "-c", "--coin", help="Coin to get", dest="symbol", required=True, type=str,
            default='ETH'
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        if parsy.symbol.upper() not in compare.blockchain_coins_list:
            print(f"{parsy.symbol} not found in blockchain data list. User onchaincoins "
                  f"to see available coins for onchain data")
            return
        try:
            df = compare.get_latest_blockchain_data(parsy.symbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(df)


    @staticmethod
    def show_histo_blockchain_data(args):
        parser = argparse.ArgumentParser(
            prog="blockchain data",
            add_help=True,
            description="get top list by pari folvume",
        )
        parser.add_argument(
            "-c", "--coin", help="Coin to get", dest="symbol", required=True, type=str,
            default='ETH'
        )
        parser.add_argument(
            "-n", "--num", '--limit', help="last n quotes", dest="limit", required=False, type=int,
            default=100
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = compare.get_historical_blockchain_data(symbol=parsy.symbol, limit=parsy.limit)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(df)

    @staticmethod
    def show_top_trading_pairs(args):
        parser = argparse.ArgumentParser(
            prog="trading pairs",
            add_help=True,
            description="get top list by",
        )
        parser.add_argument(
            "-c", "--coin", help="Coin to get", dest="symbol", required=True, type=str,
            default='ETH'
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = compare.get_top_of_trading_pairs(symbol=parsy.symbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(df)

def main():
    c = Controller()
    choices = c.base_commands + [
        'price','coins','similar','topex','news', 'lex',
        'priced','priceh','pricem','tsignals','orders','extopsym','pairvolume','volumeh','volumed',
        'onchain', 'chaincoin', 'hchaincoin', 'toptrading', 'topmc', 'topexsym'

    ]

    parser = argparse.ArgumentParser(prog="cmc", add_help=False)
    parser.add_argument("cmd", choices=choices)
    print(LOGO)
    c.help()
    while True:
        an_input = input(f"> {MOON} ")
        try:
            parsy, others = parser.parse_known_args(an_input.split())
            cmd = parsy.cmd

            if cmd == "help":
                c.help()
            elif cmd in ["exit", "quit", "q"]:
                return False
            elif cmd == "r":
                return True
            if cmd == 'price':
                c.show_prices(others)
            elif cmd == 'coins':
                c.show_coins()
            elif cmd == 'similar':
                c.find_similar_coins(others)
            elif cmd == 'topmc':
                c.show_top_list_by_market_cap(others)
            elif cmd == 'exchanges':
                c.show_top_exchanges(others)
            elif cmd == 'news':
                c.show_news(others)
            elif cmd == 'priceh':
                c._get_prices(others)
            elif cmd == 'priced':
                c.get_day_prices(others)
            elif cmd == 'pricem':
                c.get_minute_prices(others)
            elif cmd == 'tsignals':
                c.get_trading_signals(others)
            elif cmd == 'orders':
                c.get_top_orders(others)
            elif cmd == 'lex':
                c.show_all_exchanges()
            elif cmd == 'topexsym':
                c.show_exchanges_by_top_symbol(others)
            elif cmd == 'pairvolume':
                c.get_top_list_pair_volume(others)
            elif cmd == 'volumed':
                c.show_daily_coin_volume(others)
            elif cmd == 'volumeh':
                c.show_hourly_coin_volume(others)
            elif cmd == 'onchain':
                c.show_available_blockchain_lists()
            elif cmd == 'chaincoin':
                c.show_latest_blockchain_data(others)
            elif cmd == 'hchaincoin':
                c.show_histo_blockchain_data(others)
            elif cmd == 'toptrading':
                c.show_top_trading_pairs(others)

        except ArgumentError:
            print("The command selected doesn't exist")
            print("\n")
            continue

        except SystemExit:
            print("\n")
            continue


if __name__ == "__main__":
    main()
