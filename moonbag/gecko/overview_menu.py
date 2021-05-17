import argparse
import pandas as pd
from moonbag.gecko.gecko import Overview
import logging
from moonbag.common import LOGO, MOON, print_table
from typing import List

logger = logging.getLogger("parser")


def create_view(name, func, desc, n: List):
    """Method that wraps function with argparser, with top n argument as default"""
    parser = argparse.ArgumentParser(add_help=True, prog=name, description=desc)
    parser.add_argument(
        "-n",
        "--num",
        action="store",
        dest="n",
        type=int,
        default=50,
        help="Number of the records",
    )
    parsy, _ = parser.parse_known_args(n)
    if not parsy:
        return

    df = func(n=parsy.n)
    return df


class Controller:
    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="overview", add_help=False)
        self.parser.add_argument("cmd")
        self.o = Overview()
        self.base = {
            "help": self.help,
            "r": self.returner,
            "quit": self.quit,
            "exit": self.quit,
        }
        self.mapper = {
            "top_dexes": self.o.get_top_dexes,
            "most_visited": self.o.get_most_visited_coins,
            "gainers": self.o.get_top_gainers,
            "most_voted": self.o.get_most_voted_coins,
            "top_sentiment": self.o.get_positive_sentiment_coins,
            "top_volume": self.o.get_top_volume_coins,
            "trending": self.o.get_trending_coins,
            "yield_farms": self.o.get_yield_farms,
            "stables": self.o.get_stable_coins,
            "top_nft": self.o.get_top_nfts,
            "nft_market": self.o.get_nft_market_status,
            "categories": self.o.get_top_crypto_categories,
            "nft_of_day": self.o.get_nft_of_the_day,
            "recently": self.o.get_recently_added_coins,
            "btc_comp": self.o.get_companies_with_btc,
            "eth_comp": self.o.get_companies_with_eth,
            "losers": self.o.get_top_losers,
            "ex_rates": self.o.get_exchange_rates,
            "exchanges": self.o.get_exchanges,
            "derivatives": self.o.get_derivatives,
            "indexes": self.o.get_indexes,
            "eth_holdings": self.o.get_eth_holdings_public_companies_overview,
            "btc_holdings": self.o.get_btc_holdings_public_companies_overview,
            "news": self.o.get_news,
            "top_defi": self.o.get_top_defi_coins,
            "info_defi": self.o.get_global_defi_info,
            "fin_products": self.o.get_finance_products,
            "fin_platforms": self.o.get_financial_platforms,
        }

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("Crypto Overview      (use --n 25 for top N records)")
        print("   news              show latest crypto news [Coingecko]")
        print("   trending          show trending coins [Coingecko]")
        print("   recently          show recently added coins [Coingecko]")
        print("   most_visited      show most visited coins [Coingecko]")
        print("   most_voted        show most visited coins [Coingecko]")

        print("   gainers           show top gainers in last 1h [Coingecko]")
        print("   losers            show top losers in last 1h [Coingecko]")

        print(
            "   top_sentiment      show coins with most positive sentiment [Coingecko]"
        )
        print("   top_volume        show coins with highest volume [Coingecko]")

        print("   top_dexes         show top decentralized exchanges [Coingecko]")
        print("   top_defi          show top defi coins [Coingecko]")
        print("   info_defi         show overview of defi [Coingecko]")
        print("   yield_farms       show yield farms [Coingecko]")

        print("   stables           show stable coins [Coingecko]")

        print("   top_nft           show top nfts [Coingecko]")
        print("   nft_market        show nft market status [Coingecko]")
        print("   nft_of_day        show nft of a day [Coingecko]")

        print("   categories        show top crypto categories [Coingecko]")
        print(
            "   derivatives       show derivatives [Coingecko] !Waiting time ~ 10-15 sec!"
        )
        print("   indexes           show indexes [Coingecko]")
        print("   fin_products      show financial products [Coingecko]")
        print("   fin_platforms     show financial platforms [Coingecko]")

        print("   btc_comp          show companies that holds bitcoin [Coingecko]")
        print("   eth_comp          show companies that holds ethereum [Coingecko]")
        print("   eth_holdings      show eth holdings overview [Coingecko]")
        print("   btc_holdings      show btc holdings overview [Coingecko]")

        print("   exchanges         show info about exchanges [Coingecko]")
        print("   ex_rates          show exchanges rates [Coingecko]")

        print(" ")
        return

    @staticmethod
    def quit():
        return False

    @staticmethod
    def returner():
        return True

    def get_view(self, an_input):
        (known_args, others) = self.parser.parse_known_args(an_input.split())
        command = known_args.cmd
        if command in self.base:
            return self.base.get(command)()
        elif command in self.mapper:
            func = self.mapper.get(command)
            if func:
                view = create_view(name=known_args.cmd, func=func, desc="", n=others)
                return view
        else:
            print("Command not recognized")


def main():
    parser = argparse.ArgumentParser(prog="overview", add_help=False)
    c = Controller()
    choices = list(c.mapper.keys()) + list(c.base.keys())
    parser.add_argument("cmd", choices=choices)
    print(LOGO)
    c.help()
    while True:
        an_input = input(f"{MOON}> ")
        try:
            view = c.get_view(an_input)
            if view is None:
                continue
            elif isinstance(view, pd.DataFrame):
                print_table(view)
            else:
                return view

        except SystemExit:
            print("The command selected doesn't exist")
            print("\n")
            continue


if __name__ == "__main__":
    main()
