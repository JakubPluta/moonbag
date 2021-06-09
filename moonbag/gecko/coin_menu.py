import argparse
from moonbag.gecko.gecko import get_coin_list, Coin
import logging
from moonbag.common import LOGO, MOON, print_table
from typing import List
import textwrap
from inspect import signature
import difflib
import pandas as pd
from argparse import ArgumentError

logger = logging.getLogger("gecko-menu")


class Controller:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="coin", add_help=False)
        self.parser.add_argument("cmd")
        self.base_commands = ["help", "exit", "quit", "r", "q"]
        self.mapper = {
            "similar": self.find_similar_coins,
            "load": self.load_coin,
            "web": self.show_web,
            "info": self.show_coin_base_info,
            "devs": self.show_developers,
            "market": self.show_market,
            "social": self.show_socials,
            "ath": self.show_ath,
            "atl": self.show_atl,
            "coinlist": self.show_list_of_coins,
            "explorers": self.show_bcexplores,
        }

        self.coin = None

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("Coin View            [Coingecko]")
        print(
            "    similar          don't remember symbol of coin ? Look for closest matches [Coingecko]"
        )
        print("    load             load coin, example: 'load -c uniswap' [Coingecko]")
        print("    coinlist         show list of all coins available in [Coingecko]")
        print("    info             show info about loaded coin [Coingecko]")
        print("    market           show market info about loaded coin [Coingecko]")
        print(
            "    devs             show development information about loaded coins [Coingecko]"
        )
        print("    ath              show info all time high of loaded coin [Coingecko]")
        print("    atl              show info all time low of loaded coin [Coingecko]")
        print("    web              show web pages founded for loaded coin [Coingecko]")
        print(
            "    explorers        show blockchain explorers links for loaded coin [Coingecko]"
        )
        return

    def load_coin(self, args: List[str]):
        """U can use id or symbol of coins"""
        parser = argparse.ArgumentParser(
            prog="load",
            add_help=True,
            description="Load coin from coingecko\n If you not sure what is the symbol or id of coin use method coinlist",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Coin to get",
            dest="coin",
            required=True,
            type=str,
        )

        if not args:
            return

        if "-" not in args[0]:
            args.insert(0, "-c")

        parsy, _ = parser.parse_known_args(args)
        if not parsy:
            return

        try:
            self.coin = Coin(parsy.coin)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coinlist ")
            return

        else:
            print(f"Coin loaded {self.coin.coin_symbol}")

    @property
    def _is_loaded(self):
        if self.coin is None:
            print("You didn't load a coin, plase first use load -c symbol to load coin")
            return False
        return True

    def show_coin_base_info(self):
        if self._is_loaded:
            df = self.coin.base_info.reset_index()
            df = df.applymap(
                lambda x: "\n".join(textwrap.wrap(x, width=120))
                if isinstance(x, str)
                else x
            )
            df.columns = ["Metric", "Value"]
            print_table(df)

    @staticmethod
    def show_list_of_coins():
        print_table(get_coin_list(), "plain")

    def show_scores(
        self,
    ):
        if self._is_loaded:
            df = self.coin.scores
            df = df.applymap(
                lambda x: "\n".join(textwrap.wrap(x, width=200))
                if isinstance(x, str)
                else x
            )
            df.columns = ["Metric", "Value"]
            print_table(df)

    def show_market(self):
        if self._is_loaded:
            df = self.coin.market_data
            print_table(df)

    def show_atl(
        self,
    ):
        if self._is_loaded:
            print_table(self.coin.all_time_low)

    def show_ath(
        self,
    ):
        if self._is_loaded:
            df = self.coin.all_time_high
            print_table(df)

    def show_developers(
        self,
    ):
        if self._is_loaded:
            print_table(self.coin.developers_data)

    def show_bcexplores(
        self,
    ):
        if self._is_loaded:
            print_table(self.coin.blockchain_explorers)

    def show_socials(
        self,
    ):
        if self._is_loaded:
            print_table(self.coin.social_media)

    def show_web(
        self,
    ):
        if self._is_loaded:
            print_table(self.coin.websites)

    @staticmethod
    def find_similar_coins(args):
        parser = argparse.ArgumentParser(
            prog="similar",
            add_help=True,
            description="Find similar coins",
        )
        parser.add_argument(
            "-c",
            "--coin",
            help="Symbol/Name of Coin",
            dest="symbol",
            required=True,
            type=str,
        )

        if not args:
            print("You didn't pass coin symbol. Please use similar -c symbol")
            return

        parsy, others = parser.parse_known_args(args)
        if not parsy or parsy.symbol is None:
            return

        coins = get_coin_list().id.to_list()
        sim = difflib.get_close_matches(parsy.symbol, coins, 10)
        df = pd.Series(sim).to_frame().reset_index()
        df.columns = ["Index", "Name"]
        print_table(df)


def main():
    c = Controller()
    choices = list(c.mapper.keys()) + c.base_commands

    parser = argparse.ArgumentParser(prog="coin", add_help=False)
    parser.add_argument("cmd", choices=choices)
    print(LOGO)
    c.help()
    while True:
        an_input = input(f"{MOON}> (gecko_coin) ")

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
            if c.coin:
                print("\n>>> Loaded coin: ", c.coin, " <<<")
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
