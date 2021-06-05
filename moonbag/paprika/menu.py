#!/usr/bin/env python
import sys
import os
import time
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
from argparse import ArgumentError
from inspect import signature
from moonbag.cryptocompare.utils import MoonParser
from moonbag.paprika.coinpaprika import CoinPaprika

logger = logging.getLogger("paprika-menu")


class Controller:
    def __init__(self):
        self.client = CoinPaprika()
        self.parser = argparse.ArgumentParser(prog="coin", add_help=False)
        self.parser.add_argument("cmd")
        self.base_commands = ["help", "exit", "quit", "r", "q"]
        self.mapper = {
            "coins_list": self.show_coins_list,
            "coins_info": self.show_coins_info,
            "coins_market": self.show_coins_market,
            "exchanges_info": self.show_exchanges_info,
            "exchanges_market": self.show_exchanges_market,
            "coin_exchanges": self.show_coin_exchanges,
            "coin_twitter": self.show_coin_twitter,
            "coin_events": self.show_coin_events,
            "platforms": self.show_platforms,
            "contracts": self.show_contracts,
            "global_info": self.show_global_market,
            "coin_ohlc": self.show_ohlc,
            "search": self.search,
        }

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("Coinpaprika        ")
        print("   global_info       show global info about crypto market [Coinpaprika]")
        print("   search            try to find coin, exchange [Coinpaprika]")
        print("   coins_list        show all coins available  [Coinpaprika]")
        print("   coins_info        show coins base information [Coinpaprika]")
        print("   coins_market      show coins market information [Coinpaprika]")

        print(
            "   exchanges_info    show base information about exchanges [Coinpaprika]"
        )
        print(
            "   exchanges_market  show base information about exchanges [Coinpaprika]"
        )

        print(
            "   platforms         show all platforms with smart contracts  [Coinpaprika]"
        )
        print(
            "   contracts         show all contracts for given platform platforms. Defautlt eth-ethereum  [Coinpaprika]"
        )

        print(
            "   coin_exchanges    show all exchanges for given coin. Use coin_id as input [Coinpaprika]"
        )
        print(
            "   coin_events       show all event for given coin Use coin_id as input [Coinpaprika]"
        )
        print(
            "   coin_twitter      show twitter timeline for given coin. Use coin_id as input [Coinpaprika]"
        )

        print(
            "   coin_ohlc         show coin open-high-low-close prices data for last year. Use coin_id as input [Coinpaprika]"
        )
        print(" ")
        return

    def show_coins_info(self, args):
        parser = MoonParser(
            prog="coins info",
            add_help=True,
            description="get coin information",
        )
        parser.add_limit_argument(default=500, help="Number of coins", dest="limit")
        parsy, _ = parser.parse_known_args(args)
        try:
            prices = self.client.get_coins_info()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices.head(parsy.limit))

    def show_coins_market(self, args):
        parser = MoonParser(
            prog="coins market info",
            add_help=True,
            description="get market info for all coins",
        )
        parser.add_limit_argument(default=500, help="Number of coins", dest="limit")
        parsy, _ = parser.parse_known_args(args)
        try:
            prices = self.client.get_coins_market_info()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices.head(parsy.limit))

    def show_coins_list(self, args):
        parser = MoonParser(
            prog="all coins",
            add_help=True,
            description="get list of coins",
        )
        parser.add_limit_argument(default=500, help="Number of coins", dest="limit")
        parsy, _ = parser.parse_known_args(args)
        try:
            prices = self.client.get_coins()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices.head(parsy.limit))

    def show_exchanges_info(self, args):
        parser = MoonParser(
            prog="exchanges info",
            add_help=True,
            description="show exchanges information",
        )
        parser.add_limit_argument(default=100, help="Number of records", dest="limit")
        parsy, _ = parser.parse_known_args(args)
        try:
            prices = self.client.get_exchanges_info()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices.head(parsy.limit))

    def show_exchanges_market(self, args):
        parser = MoonParser(
            prog="exchanges info",
            add_help=True,
            description="show exchanges information",
        )

        parser.add_exchange_argument(default="binance", required=False, dest="exchange")
        parser.add_limit_argument(default=100, help="Number of records", dest="limit")
        parsy, _ = parser.parse_known_args(args)
        try:
            prices = self.client.get_exchanges_market(exchange_id=parsy.exchange)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices.head(parsy.limit))

    def _show_coin_related(self, args):
        parser = MoonParser(
            prog="exchanges info",
            add_help=True,
            description="show exchanges information",
        )

        parser.add_coin_argument()
        parsy, _ = parser.parse_known_args(args)

        return parsy

    def show_coin_exchanges(self, args):
        parsy = self._show_coin_related(args)

        try:
            prices = self.client.get_coin_exchanges_by_id(coin_id=parsy.symbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices)

    def show_coin_events(self, args):
        parsy = self._show_coin_related(args)

        try:
            prices = self.client.get_coin_events_by_id(coin_id=parsy.symbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices)

    def show_coin_twitter(self, args):
        parsy = self._show_coin_related(args)
        try:
            prices = self.client.get_coin_twitter_timeline(coin_id=parsy.symbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices)

    def show_platforms(self, args):
        parser = MoonParser(
            prog="contract platforms",
            add_help=True,
            description="show all contract platforms",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            platforms = self.client.get_all_contract_platforms()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(platforms)

    def show_contracts(self, args):
        parser = MoonParser(
            prog="contract platforms",
            add_help=True,
            description="show all contract platforms",
        )
        parser.add_argument(
            "-p",
            "--p",
            "--platform",
            dest="platform",
            help="Smart contract platform id. Default: eth-ethereum.",
            required=False,
            default="eth-ethereum",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            platforms = self.client.get_contract_platform(parsy.platform)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(platforms)

    def show_global_market(self, args):
        parser = MoonParser(
            prog="global market info",
            add_help=True,
            description="show global market info",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.global_market()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_ohlc(self, args):
        parser = MoonParser(
            prog="coin ohlc",
            add_help=True,
            description="get open-high-low-close prices for given coin",
        )
        parser.add_coin_argument(default="btc-bitcoin", help="coin id", dest="symbol")
        parser.add_limit_argument(default=365, help="Number of days", dest="limit")
        parsy, _ = parser.parse_known_args(args)
        try:
            prices = self.client.get_ohlc(coin_id=parsy.symbol)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices.head(parsy.limit))

    def search(self, args):
        parser = MoonParser(
            prog="search",
            add_help=True,
            description="search coinpaprika",
        )
        parser.add_argument(
            "-q",
            "--q",
            "--query",
            required=True,
            type=str,
            help="Search query",
            dest="query",
        )
        parsy, _ = parser.parse_known_args(args)

        try:
            search = self.client.search(q=parsy.query)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(search)


def main():
    c = Controller()
    choices = c.base_commands + list(c.mapper.keys())
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(prog="paprika", add_help=False)
    parser.add_argument("cmd", choices=choices)

    print(LOGO)
    c.help()
    while True:

        an_input = input(f"{MOON}> ")
        try:
            parsy, others = parser.parse_known_args(an_input.split())
            cmd = parsy.cmd

            if cmd == "help":
                c.help()
            elif cmd in ["exit", "quit", "q"]:
                return True
            elif cmd == "r":
                return False

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
            time.sleep(0.1)
            print("")
            print("")
            continue


if __name__ == "__main__":
    main()
