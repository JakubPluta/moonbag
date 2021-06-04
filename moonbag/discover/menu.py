#!/usr/bin/env python
import sys
import os
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
from argparse import ArgumentError
from inspect import signature
from moonbag.cryptocompare.utils import MoonParser
from moonbag.discover.defi import graph, llama, pulse
from moonbag.discover.reddit_client import reddit
from moonbag.discover.wales import wales
from moonbag.discover.others import fng, funding, fourchan, cryptopanic

logger = logging.getLogger("discover-menu")


class Controller:
    def __init__(self):
        self.reddit = reddit.Reddit()
        self.graph = graph.GraphClient()
        self.parser = argparse.ArgumentParser(prog="discover", add_help=False)
        self.parser.add_argument("cmd")
        self.base_commands = ["help", "exit", "quit", "r", "q"]
        self.mapper = {
            "top_subs": self.show_popular_submissions,
            "search_reddit": self.search_reddit,
            "search_subs": self.search_subs,
            "dpi": self.show_defi_pulse_index,
            "defi": self.show_llama_protocols,
            "fng": self.show_fear_greed,
            "news": self.show_cryptopanic,
            "fundings": self.show_fundings,
            "4chan": self.show_4chan,
            "wales": self.show_wales,
            "recent_pairs": self.show_lastly_added_tokens,
            "dex_trades": self.show_dex_trades,
            "compound": self.show_compound_markets,
            "uni_tokens": self.show_uni_tokens,
            "uni_swaps": self.show_last_swaps_uni,
        }

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("       top_subs ")
        print("       search_reddit ")
        print("       search_subs")
        print("       dpi ")
        print("       defi")
        print("       fng")
        print("       news  ")
        print("       fundings  ")
        print("       4chan  ")
        print("       wales   ")
        print("recent_pairs  ")
        print("dex_trades  ")
        print("compound  ")
        print("uni_tokens  ")
        print("uni_swaps  ")
        print(" ")
        return

    def show_top_submissions(self, args):
        parser = MoonParser(
            prog="reddit",
            add_help=True,
            description="get reddit information",
        )
        parser.add_key_argument(
            default="top",
            choices=["top", "controversial", "hot"],
            help="Number of coins",
            dest="key",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            top_subs = self.reddit.discover_top_submissions(parsy.key)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(top_subs)

    def show_popular_submissions(self, args):
        parser = MoonParser(
            prog="reddit sumissions",
            add_help=True,
            description="get reddit information",
        )

        parsy, _ = parser.parse_known_args(args)
        try:
            top_subs = self.reddit.get_popular_submissions()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(top_subs)

    def search_reddit(self, args):
        parser = MoonParser(
            prog="reddit search",
            add_help=True,
            description="search on reddit",
        )
        parser.add_argument(
            "-q",
            "--q",
            "--query",
            help="search query",
            dest="query",
            required=True,
            type=str,
        )
        parser.add_argument(
            "-t",
            "--type",
            help="type of data: submission or comment",
            dest="type",
            required=False,
            type=str,
            choices=["submission", "comment"],
            default="submission",
        )

        parsy, _ = parser.parse_known_args(args)
        try:
            search_data = self.reddit.search(query=parsy.query, data_type=parsy.type)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(search_data)

    def search_subs(self, args):
        parser = MoonParser(
            prog="reddit search",
            add_help=True,
            description="search on reddit",
        )
        parser.add_argument(
            "-s",
            "--s",
            "--subreddit",
            help="subreddit name example: CryptoMoonShots ",
            dest="subreddit",
            required=True,
            type=str,
        )

        parsy, _ = parser.parse_known_args(args)
        try:
            search_data = self.reddit.get_submissions_for_subreddits(
                subreddits=parsy.subreddit
            )
        except ValueError as e:
            print(f"{e}")
            return
        print_table(search_data)

    @staticmethod
    def show_defi_pulse_index(args):
        parser = MoonParser(
            prog="dpi",
            add_help=True,
            description="get defi pulse data",
        )

        parsy, _ = parser.parse_known_args(args)
        try:
            dpi = pulse.get_dpi()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(dpi, floatfmt="0.0f")

    @staticmethod
    def show_llama_protocols(args):
        lama = llama.LLama()
        parser = MoonParser(
            prog="defi protocols [llama]",
            add_help=True,
            description="get defi protocols data from llama",
        )

        parsy, _ = parser.parse_known_args(args)
        try:
            dpi = lama.get_protocols()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(dpi, floatfmt="0.4f")

    @staticmethod
    def show_fear_greed(args):
        parser = MoonParser(
            prog="feer and greed index",
            add_help=True,
            description="feer and greed index",
        )
        parser.add_limit_argument(
            help="last N days", dest="limit", default=30, required=False
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            dpi = fng.get_fng(parsy.limit)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(dpi, floatfmt="0.0f")

    @staticmethod
    def show_cryptopanic(args):
        parser = MoonParser(
            prog="crypto panic news & media",
            add_help=True,
            description="crypto panic news & media",
        )
        cpanic = cryptopanic.CryptoPanic()

        parser.add_key_argument(
            dest="key", choices=["news", "media"], required=False, default="news"
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            news = cpanic.get_posts(kind=parsy.key)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(news, floatfmt="0.0f")

    @staticmethod
    def show_fundings(args):
        parser = MoonParser(
            prog="crypto fundings rate",
            add_help=True,
            description="crypto fundings rate",
        )
        parser.add_key_argument(
            dest="key", choices=["current", "avg"], required=False, default="current"
        )

        parsy, _ = parser.parse_known_args(args)
        try:
            if parsy.key == "avg":
                key = False
            else:
                key = True
            fundings = funding.get_funding_rates(current=key)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(fundings, floatfmt="0.0f")

    @staticmethod
    def show_4chan(args):
        parser = MoonParser(
            prog="last 4chan posts",
            add_help=True,
            description="last 4chan posts",
        )

        parsy, _ = parser.parse_known_args(args)
        try:
            chans = fourchan.get_last_4chans()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(chans, floatfmt="0.0f")

    @staticmethod
    def show_wales(args):
        parser = MoonParser(
            prog="wales",
            add_help=True,
            description="last wales txs",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            chans = wales.get_wales_stats()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(chans, floatfmt="0.0f")

    def show_uni_tokens(self, args):
        parser = MoonParser(
            prog="unitokens",
            add_help=True,
            description="show uni tokens",
        )
        parser.add_argument(
            "-s", "--skip", help="skip records", default=0, required=False, dest="skip"
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            tokens = self.graph.get_uni_tokens(skip=parsy.skip)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(tokens, floatfmt="0.2f")

    def show_dex_trades(self, args):
        parser = MoonParser(
            prog="dextrades",
            add_help=True,
            description="show dex trades by protocol",
        )
        parser.add_key_argument(
            help="Dex trades by protocol or by protocol/month",
            choices=["protocol", "moth"],
            default="protocol",
            required=False,
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            if parsy.key == "month":
                dexs = self.graph.get_dex_trades_monthly()
            else:
                dexs = self.graph.get_dex_trades_by_protocol()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(dexs, floatfmt="0.2f")

    def show_lastly_added_tokens(self, args):
        parser = MoonParser(
            prog="lastly added pairs on uniswap",
            add_help=True,
            description="lastly added pairs on uniswap",
        )

        parser.add_argument(
            "-d",
            "--d",
            "--days",
            help="last n of days",
            dest="day",
            default=14,
            required=False,
            type=int,
        )
        parser.add_argument(
            "-v",
            "--v",
            "--volume",
            help="min volume",
            dest="volume",
            default=1000,
            required=False,
            type=int,
        )
        parser.add_argument(
            "-l",
            "--l",
            "--liquid",
            help="min liquidity",
            dest="liquid",
            default=0,
            required=False,
            type=int,
        )
        parser.add_argument(
            "-t",
            "--t",
            "--txs",
            help="min transactions",
            dest="txs",
            default=1000,
            required=False,
            type=int,
        )

        parsy, _ = parser.parse_known_args(args)

        try:
            pairs = self.graph.get_uniswap_pool_lastly_added(
                last_days=parsy.day,
                min_volume=parsy.volume,
                min_liquidity=parsy.liquid,
                min_tx=parsy.txs,
            )
        except ValueError as e:
            print(f"{e}")
            return
        print_table(pairs, floatfmt="0.2f")

    def show_last_swaps_uni(self, args):
        parser = MoonParser(
            prog="last swaps uniswap",
            add_help=True,
            description="last swaps uniswap",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            comp = self.graph.get_last_swaps_uni()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(comp, floatfmt="0.2f")

    def show_compound_markets(self, args):
        parser = MoonParser(
            prog="compound",
            add_help=True,
            description="show compound markets",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            comp = self.graph.get_compound_markets()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(comp, floatfmt="0.2f")


def main():
    c = Controller()
    choices = c.base_commands + list(c.mapper.keys())
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(prog="discover mode", add_help=False)
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
