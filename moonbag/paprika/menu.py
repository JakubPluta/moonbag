#!/usr/bin/env python
import sys
import os
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
            "coins_list" : self.show_coins_list,
            "coins_info": self.show_coins_info,
            "coins_market" : self.show_coins_market,
            "exchanges_info" : self.show_exchanges_info,
            "exchanges_market": self.show_exchanges_market,
            "coin_exchanges" : self.show_coin_exchanges,
            "coin_twitter" : self.show_coin_twitter,
            "coin_events" : self.show_coin_events,
        }

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("Coinpaprika        ")
        print("   coins_list        show all coins available  [Coinpaprika]")
        print("   coins_info        show coins base information [Coinpaprika]")
        print("   coins_market      show coins market information [Coinpaprika]")
        print("   exchanges_info    show base information about exchanges [Coinpaprika]")
        print("   exchanges_market  show base information about exchanges [Coinpaprika]")
        print("   platforms         show all contract platforms  [Coinpaprika]")
        print("   coin_exchanges    show all exchanges for given coin. Use coin_id as input [Coinpaprika]")
        print("   coin_events       show all event for given coin Use coin_id as input [Coinpaprika]")
        print("   coin_twitter      show twitter timeline for given coin. Use coin_id as input [Coinpaprika]")

        print("   search            try to find coin, exchange [Coinpaprika]")
        print(" ")
        return

    def show_coins_info(self, args):
        parser = MoonParser(
            prog="coins info",
            add_help=True,
            description="get coin information",
        )
        parser.add_limit_argument(default=500, desc='Number of coins', dest='limit')
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
        parser.add_limit_argument(default=500, desc='Number of coins', dest='limit')
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
        parser.add_limit_argument(default=500, desc='Number of coins', dest='limit')
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
        parser.add_limit_argument(default=100, desc='Number of records', dest='limit')
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

        parser.add_exchange_argument(default='binance', required=False, dest='exchange')
        parser.add_limit_argument(default=100, desc='Number of records', dest='limit')
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


