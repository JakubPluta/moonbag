import argparse
import pandas as pd
from tabulate import tabulate
from moonbag.gecko.gecko import Overview
import logging
from moonbag import LOGO, MOON
from typing import List

logger = logging.getLogger("parser")


def print_table(df: pd.DataFrame, tablefmt='psql'):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Please use data frame as an input!")
    print(
        tabulate(
            df, headers=df.columns, floatfmt=".5f", showindex=False, tablefmt=tablefmt,
        )
    )
    print("")


def create_view(name, func, desc, n: List):
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
    o = Overview()
    mapper = {
        "topdexes": o.get_top_dexes,
        "mostvisited": o.get_most_visited_coins,
        "gainers": o.get_top_gainers,
        "mostvoted": o.get_most_voted_coins,
        "topsentiment": o.get_positive_sentiment_coins,
        "topvolume": o.get_top_volume_coins,
        "trending": o.get_trending_coins,
        "yieldfarms": o.get_yield_farms,
        "stables": o.get_stable_coins,
        "topnft": o.get_top_nfts,
        "nftmarket": o.get_nft_market_status,
        "categories": o.get_top_crypto_categories,
        "nftofday": o.get_nft_of_the_day,
        "recently": o.get_recently_added_coins,
        "btccompanies": o.get_companies_with_btc,
        "ethcompanies": o.get_companies_with_eth,
        "losers": o.get_top_losers,
        "exrates": o.get_exchange_rates,
        "exchanges": o.get_exchanges,
        "derivatives": o.get_derivatives,
        "indexes": o.get_indexes,
        "ethhold": o.get_eth_holdings_public_companies_overview,
        "btchold": o.get_btc_holdings_public_companies_overview,
        "news": o.get_news,
        "topdefi": o.get_top_defi_coins,
        "infodefi": o.get_global_defi_info,
        "finprod": o.get_finance_products,
        "finplat": o.get_financial_platforms,
    }

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="overview", add_help=False)
        self.parser.add_argument("cmd")
        self.base = {
            "help": self.help,
            "r": self.returner,
            "quit": self.quit,
            "exit": self.quit,
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
        print("   mostvisited       show most visited coins [Coingecko]")
        print("   mostvoted         show most visited coins [Coingecko]")

        print("   gainers           show top gainers in last 1h [Coingecko]")
        print("   losers            show top losers in last 1h [Coingecko]")

        print(
            "   topsentiment      show coins with most positive sentiment [Coingecko]"
        )
        print("   topvolume         show coins with highest volume [Coingecko]")

        print("   topdexes          show top decentralized exchanges [Coingecko]")
        print("   topdefi           show top defi coins [Coingecko]")
        print("   infodefi          show overview of defi [Coingecko]")
        print("   yieldfarms        show yield farms [Coingecko]")

        print("   stables           show stable coins [Coingecko]")

        print("   topnft            show top nfts [Coingecko]")
        print("   nftmarket         show nft market status [Coingecko]")
        print("   nftofday          show nft of a day [Coingecko]")

        print("   categories        show top crypto categories [Coingecko]")
        print(
            "   derivatives       show derivatives [Coingecko] !Waiting time ~ 10-15 sec!"
        )
        print("   indexes           show indexes [Coingecko]")
        print("   finprod           show financial products [Coingecko]")
        print("   finplat           show financial platforms [Coingecko]")

        print("   btccompanies      show companies that holds bitcoin [Coingecko]")
        print("   ethcompanies      show companies that holds ethereum [Coingecko]")
        print("   ethhold           show eth holdings overview [Coingecko]")
        print("   btchold           show btc holdings overview [Coingecko]")

        print("   exchanges         show info about exchanges [Coingecko]")
        print("   exrates           show exchanges rates [Coingecko]")

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
        an_input = input(f"> {MOON} ")
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
