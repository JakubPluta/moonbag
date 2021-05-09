import argparse
import pandas as pd
from tabulate import tabulate
from moonbag.gecko.gecko import Overview, get_coin_list, Coin
import logging
from moonbag import LOGO, MOON
from typing import List
from moonbag.gecko.overview_menu import print_table

logger = logging.getLogger("parser")


def load_coin_from_coin_gecko(args: List[str]):
    """U can use id or symbol of coins"""
    parser = argparse.ArgumentParser(
        prog="load",
        add_help=False,
        description="Load coin from coingecko\n If you not sure what is the symbol or id of coin use method coinlist",
    )
    parser.add_argument(
        "-c", "--coin", help="Coin to get", dest="coin", required=True,type=str,
    )

    if "-" not in args[0]:
        args.insert(0, "-c")

    parsy, _ = parser.parse_known_args(args)
    if not parsy:
        return

    try:
        coin = Coin(parsy.coin)
    except ValueError as e:
        print(f"{parsy.coin} -> {e} ")

    if coin._coin_symbol is None:
        print(f"Could not find coin with the given id: {parsy.coin}")
    else:
        print(f"Coin loaded {coin._coin_symbol}")
        return coin


def show_coin_base_info(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    info = coin.base_info
    df = info.reset_index()
    import textwrap
    df = df.applymap(lambda x: '\n'.join(textwrap.wrap(x, width=150)) if isinstance(x, str) else x)
    df.columns = ['Metric', 'Value']
    print_table(df)


def show_list_of_coins():
    print_table(get_coin_list(),'plain')


def show_scores(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    df = coin.scores
    import textwrap
    df = df.applymap(lambda x: '\n'.join(textwrap.wrap(x, width=200)) if isinstance(x, str) else x)
    df.columns = ['Metric', 'Value']
    print_table(df)


def show_market(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    df = coin.market_data
    print_table(df)


def show_atl(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    df = coin.all_time_low
    print_table(df)


def show_ath(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    df = coin.all_time_high
    print_table(df)


def show_developers(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    df = coin.developers_data
    print_table(df)


def show_blockchainexplores(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    be = coin.blockchain_explorers
    print_table(be)


def show_socials(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    social = coin.social_media
    print_table(social)


def show_web(coin: Coin):
    if coin is None:
        print("You didn't load a coin, plase first use load -c symbol to load coin")
        return
    social = coin.websites
    print(social)


def main():
    choices = ['coinlist','load','info','market','ath','atl','scores','websites', 'bcexplorers',
               'social','devs','web']
    parser = argparse.ArgumentParser(prog="coin", add_help=False)
    parser.add_argument("cmd", choices=choices)
    print(LOGO)
    coin = None
    while True:
        an_input = input(f"> {MOON} ")
        try:
            parsy, others = parser.parse_known_args(an_input.split())
            if parsy.cmd == 'load':
                coin = load_coin_from_coin_gecko(others)
            elif parsy.cmd == 'info':
                show_coin_base_info(coin)
            elif parsy.cmd == 'scores':
                show_scores(coin)
            elif parsy.cmd == 'market':
                show_market(coin)
            elif parsy.cmd == 'atl':
                show_atl(coin)
            elif parsy.cmd == 'ath':
                show_ath(coin)
            elif parsy.cmd == 'bcexplorers':
                show_blockchainexplores(coin)
            elif parsy.cmd == 'devs':
                show_developers(coin)
            elif parsy.cmd == "social":
                show_socials(coin)
            elif parsy.cmd == "web":
                show_web(coin)
            elif parsy.cmd == 'coinlist':
                show_list_of_coins()

        except SystemExit:
            print("The command selected doesn't exist")
            print("\n")
            continue


if __name__ == "__main__":
    main()
