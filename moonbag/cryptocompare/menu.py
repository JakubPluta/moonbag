#!/usr/bin/env python
import sys
import os
from moonbag.cryptocompare.cryptocomp import CryptoCompare, API_KEY
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
import pandas as pd
from argparse import ArgumentError
from moonbag.cryptocompare.utils import (
    get_closes_matches_by_name,
    get_closes_matches_by_symbol,
    print_no_api_key_msg,
)
from inspect import signature


logger = logging.getLogger("compare-menu")


class Controller:
    def __init__(self):
        self.client = CryptoCompare(API_KEY)
        self.parser = argparse.ArgumentParser(prog="coin", add_help=False)
        self.parser.add_argument("cmd")
        self.base_commands = ["help", "exit", "quit", "r", "q"]
        self.mapper = {
            "price": self.show_prices,
            "coins": self.show_coins,
            "similar": self.find_similar_coins,
            "top_exchanges": self.show_top_exchanges,
            "news": self.show_news,
            "list_exchanges": self.show_all_exchanges,
            "price_day": self.show_day_prices,
            "price_hour": self.show_hour_prices,
            "price_minute": self.show_minute_prices,
            "orders": self.show_top_orders,
            "top_symbols_ex": self.show_exchanges_by_top_symbol,
            "pair_volume": self.show_top_list_pair_volume,
            "volume_hour": self.show_hourly_coin_volume,
            "volume_day": self.show_daily_coin_volume,
            "list_bc_coins": self.show_available_blockchain_lists,
            "coin_bc": self.show_latest_blockchain_data,
            "coin_bc_hist": self.show_histo_blockchain_data,
            "trade_signals": self.show_trading_signals,
            "top_trading": self.show_top_trading_pairs,
            "top_mcap": self.show_top_list_by_market_cap,
            "orders_snap": self.show_order_book_snapshot,
            "wallets": self.show_all_wallets,
            "gambling": self.show_all_gambling,
            "recommended": self.show_recommended,
            "social": self.show_latest_socials,
            "social_hist": self.show_histo_socials,
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
        print(
            "   coins             show available coins: Symbol and Names [CryptoCompare]"
        )
        print("   similar           try to find coin symbol [CryptoCompare]")
        print("   top_mcap          top market cap coins [CryptoCompare]")

        print(
            "   top_exchanges     show top  exchanges for given pair: Default BTC/USD [CryptoCompare]"
        )
        print("   list_exchanges    show names of all exchanges  [CryptoCompare]")
        print("   top_symbols_ex    show top coins on given exchange [CryptoCompare]")
        print(
            "   orders            show  order book for given pair and exchange. LUNA/BTC,Binance [CryptoCompare]"
        )
        print(
            "   orders_snap       show  order book for given pair and exchange. LUNA/BTC,Binance [CryptoCompare]"
        )
        print(
            "   price             show latest price info for given pair like BTC/USD [CryptoCompare]"
        )
        print(
            "   price_day         show historical prices with 1 day interval [CryptoCompare]"
        )
        print(
            "   price_hour        show historical prices with 1 hour interval [CryptoCompare]"
        )
        print(
            "   price_minute      show historical prices with 1 min interval [CryptoCompare]"
        )

        print(
            "   volume_day        show daily volume for given pair. Default: BTC/USD [CryptoCompare]"
        )
        print(
            "   volume_hour       show hourly volume for given pair. Default: BTC/USD [CryptoCompare]"
        )

        print(
            "   trade_signals     show latest trading signals for given coin. Default ETH [CryptoCompare]"
        )
        print(
            "   pair_volume       show latest volume for given pair of coins [CryptoCompare]"
        )
        print(
            "   top_trading       show top trading pairs for given coin [CryptoCompare]"
        )
        print(
            "   list_bc_coins     show list of coins with on-chain data available [CryptoCompare]"
        )
        print("   coin_bc           show on chain data for given coin [CryptoCompare]")
        print(
            "   coin_bc_hist      show historical on chain data for given coin [CryptoCompare]"
        )

        print("   wallets           show all available wallets [CryptoCompare]")
        print("   gambling          show all available gambling [CryptoCompare]")
        print(
            "   recommended       show all recommendation fro wallets and exchanges [CryptoCompare]"
        )

        print(
            "   social            show latest social stats for given coins symbol   [CryptoCompare]"
        )
        print(
            "   social_hist       show historical social stats for given coins symbol "
            "(weekly aggregated) [CryptoCompare]"
        )
        print(" ")
        return

    def show_prices(self, args):
        parser = argparse.ArgumentParser(
            prog="prices",
            add_help=True,
            description="get prices",
        )
        parser.add_argument(
            "-c",
            "-fsym",
            help="symbol of the coin",
            dest="symbol",
            required=True,
            type=str,
        )
        parser.add_argument(
            "-t",
            "-tsym",
            help="Second coin in pair. Default USD",
            dest="tosymbol",
            required=False,
            type=str,
            default="USD",
        )

        if not args:
            print("You didn't pass coin symbol. Please use price -c symbol")
            return

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        try:
            prices = self.client.get_price(parsy.symbol, parsy.tosymbol)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coins ")
            return
        print_table(prices)

    def show_coins(
        self,
    ):
        print_table(self.client.coin_list.reset_index())

    def find_similar_coins(self, args):
        parser = argparse.ArgumentParser(
            prog="similar",
            add_help=True,
            description="Find similar coins",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="symbol or name of coin",
            dest="symbol",
            required=True,
            type=str,
        )

        parser.add_argument(
            "-k",
            "--key",
            help="search by symbol or name",
            dest="key",
            required=False,
            type=str,
            default="symbol",
            choices=["symbol", "name"],
        )

        if not args:
            print("You didn't pass coin symbol. Please use similar -c symbol")
            return

        parsy, others = parser.parse_known_args(args)
        if not parsy or parsy.symbol is None:
            return

        coin_df = self.client.coin_list
        coins = dict(zip(coin_df["Symbol"], coin_df["FullName"]))

        if parsy.key == "name":
            res = get_closes_matches_by_name(parsy.symbol, coins)
        else:
            res = get_closes_matches_by_symbol(parsy.symbol, coins)
        if res:
            df = pd.Series(res).to_frame().reset_index()
            df.columns = ["Symbol", "Name"]
            print_table(df)
        else:
            print(pd.DataFrame())

    def show_top_list_by_market_cap(self, args):
        parser = argparse.ArgumentParser(
            prog="topmc",
            add_help=True,
            description="get top market cap coins",
        )
        parser.add_argument(
            "-t",
            "--tsym",
            help="To symbol - coin in which you want to see market cap data",
            dest="tosymbol",
            required=False,
            type=str,
            default="USD",
        )
        parser.add_argument(
            "-n",
            "--num",
            "--limit",
            help="top n of coins",
            dest="limit",
            required=False,
            type=int,
            default=50,
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = self.client.get_top_list_by_market_cap(
                currency=parsy.tosymbol, limit=parsy.limit
            )
        except (ValueError, Exception) as e:
            print(f"{e}, To check list of coins use command: coins ")
            return

        if df.empty:
            print(f"Empty dataframe returned for {parsy.tosymbol} ")
            return

        print_table(df, floatfmt=".2f")

    def show_top_exchanges(self, args):
        parser = argparse.ArgumentParser(
            prog="exchanges",
            add_help=True,
            description="get top exchanges",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="symbol or name of coin",
            dest="symbol",
            required=False,
            type=str,
            default="BTC",
        )
        parser.add_argument(
            "-t",
            "--tsym",
            help="To symbol - coin in which you want to see data",
            dest="tosymbol",
            required=False,
            type=str,
            default="USD",
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        try:
            prices = self.client.get_top_exchanges(parsy.symbol, parsy.tosymbol)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coinlist ")
            return
        print_table(prices)

    def show_news(self, args):
        parser = argparse.ArgumentParser(
            prog="news",
            add_help=True,
            description="latest news",
        )
        parser.add_argument(
            "-s",
            "--sort",
            help="Sorting [latest, popular]",
            dest="sort",
            required=False,
            type=str,
            default="latest",
            choices=["latest", "popular"],
        )
        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        try:
            df = self.client.get_latest_news(sort_order=parsy.sort)
        except ValueError as e:
            print(f"{e} ")
            return
        print_table(df)

    def _get_prices(self, args):
        parser = argparse.ArgumentParser(
            prog="histoprices",
            add_help=True,
            description="get historical prices",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin symbol",
            dest="symbol",
            required=False,
            type=str,
            default="BTC",
        )
        parser.add_argument(
            "-t",
            "--tsym",
            help="to symbol [default USD]",
            dest="tosymbol",
            required=False,
            type=str,
            default="USD",
        )

        parser.add_argument(
            "-n",
            "--num",
            "--limit",
            help="last n quotes",
            dest="limit",
            required=False,
            type=int,
            default=100,
        )

        if not args:
            print("You didn't pass coin symbol. Please use -c symbol")
            return

        parsy, _ = parser.parse_known_args(args)
        return parsy

    def show_day_prices(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            parsy = self._get_prices(args)
            prices = self.client.get_historical_day_prices(
                parsy.symbol, parsy.tosymbol, parsy.limit
            )
        except ValueError as e:
            print(f"{e}, ")
            return
        print(f"Day prices for {parsy.symbol}/{parsy.tosymbol}")
        print_table(prices)

    def show_hour_prices(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = self.client.get_historical_hour_prices(
                parsy.symbol, parsy.tosymbol
            )
        except ValueError as e:
            print(f"{e}, ")
            return
        print(f"Hour prices for {parsy.symbol}/{parsy.tosymbol}")
        print_table(prices)

    def show_minute_prices(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = self.client.get_historical_minutes_prices(
                parsy.symbol, parsy.tosymbol
            )
        except ValueError as e:
            print(f"{e}, ")
            return
        print(f"Minute prices for {parsy.symbol}/{parsy.tosymbol}")
        print_table(prices)

    def show_trading_signals(self, args):
        parser = argparse.ArgumentParser(
            prog="topmcap",
            add_help=True,
            description="get top market cap",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin symbol",
            dest="symbol",
            required=True,
            type=str,
            default="ETH",
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        try:
            df = self.client.get_latest_trading_signals(parsy.symbol)
        except ValueError as e:
            print(f"{e} ")
            return
        if df.empty:
            print(f"No tradings signals found for coin {parsy.symbol}")
        else:
            print_table(df)

    def show_orderbooks(
        self,
    ):
        df = self.client.get_order_books_exchanges()
        print_table(df)

    def show_top_orders(self, args):
        parser = argparse.ArgumentParser(
            prog="orders",
            add_help=True,
            description="get order book for pair of coins",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin smybol",
            dest="symbol",
            required=True,
            type=str,
            default="ETH",
        )
        parser.add_argument(
            "-t",
            "--tsym",
            help="to symbol, second pair",
            dest="tsym",
            required=False,
            type=str,
            default="BTC",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            help="exchange",
            dest="exchange",
            required=False,
            type=str,
            default="Binance",
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = self.client.get_order_book_top(
                symbol=parsy.symbol, to_symbol=parsy.tsym, exchange=parsy.exchange
            )
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coins ")
            return
        print_table(df)

    def show_all_exchanges(
        self,
    ):
        df = self.client.get_all_exchanges_names()
        print_table(df)

    def show_exchanges_by_top_symbol(self, args):
        parser = argparse.ArgumentParser(
            prog="exchange symbols",
            add_help=True,
            description="get order book for pair of coins",
        )

        parser.add_argument(
            "-e",
            "--exchange",
            help="exchange",
            dest="exchange",
            required=False,
            type=str,
            default="binance",
        )

        parser.add_argument(
            "-n",
            "--num",
            "--limit",
            help="last n quotes",
            dest="limit",
            required=False,
            type=int,
            default=100,
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = self.client.get_exchanges_top_symbols_by_volume(
                exchange=parsy.exchange, limit=parsy.limit
            )
        except ValueError as e:
            print(f"{e}")
            return
        if df.empty:
            print(f"Could'nt find data for Exchange: {parsy.exchange}")
        print_table(df)

    def show_top_list_pair_volume(self, args):
        parser = argparse.ArgumentParser(
            prog="pairvolume",
            add_help=True,
            description="get top list by pair volume",
        )
        parser.add_argument(
            "-t",
            "--tsym",
            help="To symbol - coin in which you want to see data",
            dest="tosymbol",
            required=False,
            type=str,
            default="USD",
        )
        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = self.client.get_top_list_by_pair_volume(parsy.tosymbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(df)

    def show_daily_coin_volume(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = self.client.get_daily_symbol_volume(
                parsy.symbol, parsy.tosymbol, parsy.limit
            )
        except ValueError as e:
            print(f"{e}, ")
            return
        print(f"Daily volume for {parsy.symbol}/{parsy.tosymbol}")
        print_table(prices)

    def show_hourly_coin_volume(self, args):
        parsy = self._get_prices(args)
        if not parsy:
            return
        try:
            prices = self.client.get_hourly_symbol_volume(
                parsy.symbol, parsy.tosymbol, parsy.limit
            )
        except ValueError as e:
            print(f"{e}, ")
            return
        print(f"Hourly volume for {parsy.symbol}/{parsy.tosymbol}")
        print_table(prices)

    def show_available_blockchain_lists(
        self,
    ):
        print_table(self.client.get_blockchain_available_coins_list())

    def show_latest_blockchain_data(self, args):
        parser = argparse.ArgumentParser(
            prog="blockchain data",
            add_help=True,
            description="get latest block chain data for given coin [To see supported coins use onchain command ",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin symbol",
            dest="symbol",
            required=True,
            type=str,
            default="ETH",
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        if parsy.symbol.upper() not in self.client.blockchain_coins_list:
            print(
                f"{parsy.symbol} not found in blockchain data list. Use onchain "
                f"to see available coins for onchain data"
            )
            return
        try:
            df = self.client.get_latest_blockchain_data(parsy.symbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(df)

    def show_histo_blockchain_data(self, args):
        parser = argparse.ArgumentParser(
            prog="blockchain data",
            add_help=True,
            description="get historical block chain data for given coin [To see supported coins use onchain command",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin symbol",
            dest="symbol",
            required=True,
            type=str,
            default="ETH",
        )
        parser.add_argument(
            "-n",
            "--num",
            "--limit",
            help="number of results",
            dest="limit",
            required=False,
            type=int,
            default=100,
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = self.client.get_historical_blockchain_data(
                symbol=parsy.symbol, limit=parsy.limit
            )
        except ValueError as e:
            print(f"{e}")
            return
        if df.empty:
            print(f"No data found for {parsy.symbol}")
        print_table(df, floatfmt=".0f")

    def show_top_trading_pairs(self, args):
        parser = argparse.ArgumentParser(
            prog="trading pairs",
            add_help=True,
            description="get top trading pairs",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin symbol",
            dest="symbol",
            required=True,
            type=str,
            default="ETH",
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = self.client.get_top_of_trading_pairs(symbol=parsy.symbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(df, floatfmt=".6f")

    def show_order_book_snapshot(self, args):
        parser = argparse.ArgumentParser(
            prog="orders snapshot",
            add_help=True,
            description="get order book snapshot for pair of coins",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin symbol",
            dest="symbol",
            required=True,
            type=str,
            default="ETH",
        )
        parser.add_argument(
            "-t",
            "--tsym",
            help="to symbol, second pair",
            dest="tsym",
            required=False,
            type=str,
            default="BTC",
        )
        parser.add_argument(
            "-e",
            "--exchange",
            help="exchange",
            dest="exchange",
            required=False,
            type=str,
            default="Binance",
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return
        try:
            df = self.client.get_order_book_snapshot(
                symbol=parsy.symbol, to_symbol=parsy.tsym, exchange=parsy.exchange
            )
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coins ")
            return
        print_table(df)

    def show_all_wallets(
        self,
    ):
        print_table(self.client.get_all_wallet_info(), floatfmt=".2f")

    def show_all_gambling(
        self,
    ):
        print_table(self.client.get_all_gambling_info(), floatfmt=".2f")

    def show_recommended(self, args):
        parser = argparse.ArgumentParser(
            prog="recommendations",
            add_help=True,
            description="get recommended exchanges and wallets",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin symbol",
            dest="symbol",
            required=True,
            type=str,
            default="ETH",
        )
        parser.add_argument(
            "-k",
            "--key",
            help="What you need recommendations for ? choose from [wallet, exchange]",
            dest="key",
            required=True,
            type=str,
            choices=["wallet", "exchange"],
            default="wallet",
        )
        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        if parsy.key == "exchange":
            func = self.client.get_recommended_exchanges
        else:
            func = self.client.get_recommended_wallets

        try:
            df = func(symbol=parsy.symbol)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coins ")
            return

        if df.empty:
            print(f"Not found recommended {parsy.key} for {parsy.symbol}")
        print_table(df, floatfmt=".2f")

    def show_latest_socials(self, args):
        parser = argparse.ArgumentParser(
            prog="socials",
            add_help=True,
            description="get latest social stats",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="symbol or id of coin. Default 7605 - > ETH",
            dest="symbol",
            required=False,
            default=7605,
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        if isinstance(parsy.symbol, str) and parsy.symbol.isalpha():
            coin_id = self.client.coin_mapping.get(parsy.symbol.upper())
            if coin_id:
                df = self.client.get_latest_social_coin_stats(coin_id=coin_id)
            else:
                print(
                    f"Could'nt find coin {parsy.symbol}. To see list of coins use coins command"
                )
                return
        elif isinstance(parsy.symbol, int) or parsy.symbol.isdigit():
            df = self.client.get_latest_social_coin_stats(coin_id=int(parsy.symbol))
        else:
            df = pd.DataFrame()
        print_table(df)

    def show_histo_socials(self, args):
        parser = argparse.ArgumentParser(
            prog="socials historical",
            add_help=True,
            description="get social historical stats - weekly aggregated",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="symbol or id of coin. Default 7605 - > ETH",
            dest="symbol",
            required=False,
            default=7605,
        )

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        if isinstance(parsy.symbol, str) and parsy.symbol.isalpha():
            coin_id = self.client.coin_mapping.get(parsy.symbol.upper())
            if coin_id:
                df = self.client.get_historical_social_stats(coin_id=coin_id)
            else:
                print(
                    f"Could'nt find coin {parsy.symbol}. To see list of coins use coins command"
                )
                return
        elif isinstance(parsy.symbol, int) or parsy.symbol.isdigit():
            df = self.client.get_historical_social_stats(coin_id=int(parsy.symbol))
        else:
            df = pd.DataFrame()
        print_table(df, floatfmt=".0f")


def main():
    c = Controller()
    choices = c.base_commands + list(c.mapper.keys())
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(prog="cmc", add_help=False)
    parser.add_argument("cmd", choices=choices)

    print(LOGO)
    c.help()
    while True:

        if c.client.api_key is None:
            print_no_api_key_msg()
            break

        an_input = input(f"{MOON}> ")
        try:
            parsy, others = parser.parse_known_args(an_input.split())
            cmd = parsy.cmd

            if cmd == "help":
                c.help()
            elif cmd in ["exit", "quit", "q"]:
                return False
            elif cmd == "r":
                return True

            view = c.mapper.get(cmd)
            if view is None:
                continue
            elif callable(
                view
            ):  # If function takes params return func(args), else func()
                if len(signature(view).parameters) > 0:
                    view(others)
                else:
                    view()

        except ArgumentError:
            print("The command selected doesn't exist")
            print("\n")
            continue

        except SystemExit:
            print("\n")
            continue


if __name__ == "__main__":
    main()
