import argparse
from moonbag.gecko.gecko import Overview
import logging
from tabulate import tabulate
import pandas as pd

logger = logging.getLogger('parser')

moon = "(🚀🚀)"


h = """
    ███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗██████╗  █████╗  ██████╗ 
    ████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔════╝ 
    ██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║██████╔╝███████║██║  ███╗
    ██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║   ██║
    ██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██║  ██║╚██████╔╝
    ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝

    Welcome in MoonBag Terminal!
"""

MAPPER = {
    'help': 'print_help'


}



def print_help():
    print("Overview Mode:")
    print("   help          show help")
    print("   r             return to previous menu")
    print("   quit          quit program")
    print("")
    print("   topdexes          show top decentralized exchanges [Coingecko]")
    print("   mostvisited       show most visited coins [Coingecko]")
    print("   gainers           show top gainers [Coingecko]")
    print("   mostvoted         show most visited coins [Coingecko]")
    print("   sentiment         show coins with most positive sentiment [Coingecko]")
    print("   topvolume         show coins with highest volume [Coingecko]")
    print("   trending          show trending coins [Coingecko]")
    print("   yieldfarms        show yield farms [Coingecko]")
    print("   stables           show stable coins [Coingecko]")
    print("   nft               show top nfts [Coingecko]")
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

    print("")
    return


def overview_menu():

    choices = ['help', 'r', 'quit',
               'topdexes', 'mostvisited',
               'gainers', 'mostvoted',
               'sentiment', 'topvolume',
               'trending', 'yieldfarms',
               'stables','nft','categories',
               'nftofday', 'recently','btccompanies','ethcompanies',
               'losers','exrates','derivatives','indexes', 'exrates',
               'ethhold', 'btchold', 'news'

               ]

    parser = argparse.ArgumentParser(prog='overview', add_help=False)
    parser.add_argument('cmd', choices=choices)
    print(h)
    print_help()
    ov = Overview()
    while True:
        as_input = input(f'{moon} ')
        try:
            (known_args, others) = parser.parse_known_args(as_input.split())
        except SystemExit:
            print("The command selected doesn't exist")
            print('\n')
            continue

        if known_args.cmd == 'help':
            print_help()
        elif known_args.cmd == 'r':
            return False
        elif known_args.cmd == 'quit':
            return True

        elif known_args.cmd == 'topdexes':
            df = ov.get_top_dexes().head(10)
            print(tabulate(
                    df,
                    headers=df.columns,
                    floatfmt=".5f",
                    showindex=False,
                    tablefmt="presto",
                )
            )
            print("")

        elif known_args.cmd == 'mostvisited':
            df = ov.get_most_visited_coins()
            print(tabulate(
                    df,
                    headers=df.columns,
                    floatfmt=".5f",
                    showindex=False,
                    tablefmt="presto",
                )
            )
            print("")

        elif known_args.cmd == 'mostvoted':
            df = ov.get_most_voted_coins()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".5f",
                showindex=False,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'sentiment':
            df = ov.get_positive_sentiment_coins()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=False,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'topvolume':
            df = ov.get_top_volume_coins()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")


        elif known_args.cmd == 'gainers':
            df = ov.get_top_gainers()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=False,
                tablefmt="presto",
            )
            )
            print("")


        elif known_args.cmd == 'trending':
            df = ov.get_trending_coins()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=False,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'yieldfarms':
            df = ov.get_yield_farms()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=False,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'stables':
            df = ov.get_stable_coins()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=False,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'nft':
            df = ov.get_top_nfts()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'categories':
            df = ov.get_top_crypto_categories()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'nftofday':
            df = pd.Series(ov.get_nft_of_the_day()).to_frame().reset_index()
            df.columns = ['Metric', 'Value']

            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'ethcompanies':
            df = ov.get_companies_with_eth()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'btccompanies':
            df = ov.get_companies_with_btc()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'recently':
            df = ov.get_recently_added_coins()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'derivatives':
            df = ov.get_derivatives()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'indexes':
            df = ov.get_indexes()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'exrates':
            df = ov.get_exchange_rates()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'losers':
            df = ov.get_top_losers()
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'btchold':
            df = pd.Series(ov.get_btc_holdings_public_companies_overview()).to_frame().reset_index()
            df.columns = ['Metric', 'Value']
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'ethhold':
            df = pd.Series(ov.get_eth_holdings_public_companies_overview()).to_frame().reset_index()
            df.columns = ['Metric', 'Value']

            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        elif known_args.cmd == 'news':
            df = ov._get_news().head(50)
            print(tabulate(
                df,
                headers=df.columns,
                floatfmt=".6f",
                showindex=True,
                tablefmt="presto",
            )
            )
            print("")

        else:
            print("Command not recognized!")


if __name__ == "__main__":
    overview_menu()