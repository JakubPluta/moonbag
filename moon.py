#!/usr/bin/env python
import sys
import os
import argparse
import logging
from argparse import ArgumentError
from moonbag.common import LOGO, MOON
from moonbag.onchain.ethereum import menu as eth_menu
from moonbag.onchain.terraluna import menu as terra_menu
from moonbag.cryptocompare import menu as cc_menu
from moonbag.gecko import coin_menu as coin_menu
from moonbag.gecko import overview_menu as overview_menu
from moonbag.paprika import menu as paprika_menu
from moonbag.discover import menu as disc_menu

logger = logging.getLogger("main-menu")


def help():
    print("Main commands:")
    print("   help              show help")
    print("   r                 return to previous menu")
    print("   quit              quit program")
    print("")
    print("Crypto Overview        ")
    print("   compare        explore crypto-compare data. API key needed [Cryptocompare]")
    print("   paprika        explore coinpaprika data [Coinpaprika]")
    print("   gecko_coin     explore CoinGecko data for chosen Coin. [CoinGecko]")
    print("   gecko_view     explore CoinGecko overview data. [CoinGecko]")
    print("   discover       explore other Crypto data")
    print("")
    print("On-chain data        ")
    print("   ethereum       explore on-chain data for ethereum [Ethplorer]")
    print("   terra          explore on-chain data for terra  [TerraAPI]")
    print("")


mapper = {
    "ethereum" : eth_menu.main,
    "terra" : terra_menu.main,
    "compare" : cc_menu.main,
    "gecko_coin" : coin_menu.main,
    "gecko_view" : overview_menu.main,
    "paprika" : paprika_menu.main,
    "discover" : disc_menu.main,


}


def main():
    choices = ["help", "exit", "quit", "r", "q", "terra", "ethereum", "paprika","gecko_coin", "gecko_view", "compare", "discover"]
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(prog="moonbag", add_help=False)
    parser.add_argument("cmd", choices=choices)

    show_help = True
    print(LOGO)

    while True:

        try:
            sys.stdin.reconfigure(encoding="utf-8")
            sys.stdout.reconfigure(encoding="utf-8")
            sys.stdout.encoding = 'cp65001'

        except Exception as e:
            print(e, "\n")

        home = False

        if show_help:
            help()
            show_help = False

        an_input = input(f"{MOON}> ")
        if not an_input:
            print("")
            continue

        try:
            parsy, others = parser.parse_known_args(an_input.split())
            cmd = parsy.cmd

        except ArgumentError:
            print("The command selected doesn't exist")
            print("")
            continue

        except SystemExit:
            print("The command selected doesn't exist")
            print("")
            continue

        menu = False

        if cmd == "help":
            show_help = True

        elif cmd in ["exit", "quit", "q", 'r']:
            break

        view = mapper.get(cmd)
        if view is None:
            continue
        elif callable(view):
            print(f"Going to {cmd}")
            menu = view()
        else:
            print("Something went wrong")

        if menu:
            break

        if not home:
            show_help = True

    print("Let the moonlight always fill your bags. See you again!")


if __name__ == "__main__":
    main()
