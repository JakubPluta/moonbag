import argparse
from moonbag.gecko.gecko import Overview
import logging

logger = logging.getLogger('parser')

rocketman = "(🚀🚀)"


h = """
    ███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗██████╗  █████╗  ██████╗ 
    ████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔════╝ 
    ██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║██████╔╝███████║██║  ███╗
    ██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║   ██║
    ██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██║  ██║╚██████╔╝
    ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝

    Welcome in MoonBag Terminal!
"""


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
    print("   ethhold           show eth_holdings_public_companies_overview")
    print("   btchold           show eth_holdings_public_companies_overview")

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
               'ethhold', 'btchold'

               ]

    parser = argparse.ArgumentParser(prog='overview', add_help=False)
    parser.add_argument('cmd', choices=choices)
    print(h)
    print_help()
    overview = Overview()
    while True:
        as_input = input(f'{rocketman} ')
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
            print(overview.get_top_dexes())

        elif known_args.cmd == 'mostvisited':
            print(overview.get_most_visited_coins())

        elif known_args.cmd == 'mostvoted':
            print(overview.get_most_voted_coins())

        elif known_args.cmd == 'sentiment':
            print(overview.get_positive_sentiment_coins())

        elif known_args.cmd == 'topvolume':
            print(overview.get_top_volume_coins())

        elif known_args.cmd == 'gainers':
            print(overview.get_top_gainers())

        elif known_args.cmd == 'trending':
            print(overview.get_trending_coins())

        elif known_args.cmd == 'yieldfarms':
            print(overview.get_yield_farms())

        elif known_args.cmd == 'stables':
            print(overview.get_stable_coins())

        elif known_args.cmd == 'nft':
            print(overview.get_top_nfts())

        elif known_args.cmd == 'categories':
            print(overview.get_top_crypto_categories())

        elif known_args.cmd == 'nftofday':
            print(overview.get_nft_of_the_day())

        elif known_args.cmd == 'ethcompanies':
            print(overview.get_companies_with_eth())

        elif known_args.cmd == 'btccompanies':
            print(overview.get_companies_with_btc())

        elif known_args.cmd == 'recently':
            print(overview.get_recently_added_coins())

        elif known_args.cmd == 'derivatives':
            print(overview.get_derivatives())

        elif known_args.cmd == 'indexes':
            print(overview.get_indexes())

        elif known_args.cmd == 'exrates':
            print(overview.get_exchange_rates())

        elif known_args.cmd == 'losers':
            print(overview.get_top_losers())

        elif known_args.cmd == 'btchold':
            print(overview.get_btc_holdings_public_companies_overview())

        elif known_args.cmd == 'ethhold':
            print(overview.get_eth_holdings_public_companies_overview())

        else:
            print("Command not recognized!")




if __name__ == "__main__":
    overview_menu()