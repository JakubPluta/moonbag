import argparse
import logging
import pandas as pd
from tabulate import tabulate
from moonbag.gecko.gecko import Overview
import logging

logger = logging.getLogger("parser")

MOON = "(🚀🚀)"


LOGO = """
    ███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗██████╗  █████╗  ██████╗ 
    ████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔════╝ 
    ██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║██████╔╝███████║██║  ███╗
    ██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║   ██║
    ██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██║  ██║╚██████╔╝
    ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝

    Welcome in MoonBag Terminal!
"""


def print_help():
    print("Main commands:")
    print("   help              show help")
    print("   r                 return to previous menu")
    print("   quit              quit program")
    print("")
    print("Crypto Overview Menu")
    print("   topdexes          show top decentralized exchanges [Coingecko]")
    print("   mostvisited       show most visited coins [Coingecko]")
    print("   gainers           show top gainers [Coingecko]")
    print("   mostvoted         show most visited coins [Coingecko]")
    print("   topsentiment      show coins with most positive sentiment [Coingecko]")
    print("   topvolume         show coins with highest volume [Coingecko]")
    print("   trending          show trending coins [Coingecko]")
    print("   yieldfarms        show yield farms [Coingecko]")
    print("   stables           show stable coins [Coingecko]")
    print("   topnft            show top nfts [Coingecko]")
    print("   nftmarket         show nft market status [Coingecko]")
    print("   categories        show top crypto categories [Coingecko]")
    print("   nftofday          show nft of a day [Coingecko]")
    print("   recently          show recently added coins [Coingecko]")
    print("   btccompanies      show companies that holds bitcoin [Coingecko]")
    print("   ethcompanies      show companies that holds ethereum [Coingecko]")
    print("   derivatives       show derivatives [Coingecko]")
    print("   indexes           show indexes [Coingecko]")
    print("   losers            show top losers [Coingecko]")
    print("   exrates           show exchanges rates [Coingecko]")
    print("   ethhold           show eth holdings overview [Coingecko]")
    print("   btchold           show btc holdings overview [Coingecko]")
    print("   news              show latest crypto news [Coingecko]")
    print("   topdefi           show top defi coins [Coingecko]")
    print("   infodefi          show overview of defi [Coingecko]")
    print(" ")
    return


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
    "news": o._get_news,
    "topdefi": o.get_top_defi_coins,
    "infodefi" : o.get_global_defi_info,
}


standard = {
    "help": print_help,
    "r": False,
    "quit": True,
}

# TODO ADD DECORATOR FOR EACH FUNCTION TO MAKE IT POSSIBLE TO ADD --limit Argument


def overview_menu():
    choices = list(mapper.keys()) + list(standard.keys())
    parser = argparse.ArgumentParser(prog="overview", add_help=False)
    parser.add_argument("cmd", choices=choices)
    print(LOGO)
    print_help()

    while True:
        as_input = input(f"{MOON} ")
        try:
            (known_args, others) = parser.parse_known_args(as_input.split())
        except SystemExit:
            print("The command selected doesn't exist")
            print("\n")
            continue

        cmd = mapper.get(known_args.cmd)

        if not cmd:
            base = standard.get(known_args.cmd)
            if callable(base):
                base()
            else:
                return base

        elif cmd and callable(cmd):
            df = cmd()
            if isinstance(df, dict):
                df = pd.Series(df).to_frame().reset_index()
                df.columns = ["Metric", "Value"]
            print(
                tabulate(
                    df,
                    headers=df.columns,
                    floatfmt=".5f",
                    showindex=False,
                    tablefmt="psql",
                )
            )
            print("")

        else:
            print("Command not recognized!")


if __name__ == "__main__":
    overview_menu()
