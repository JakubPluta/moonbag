import webbrowser
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
import pandas as pd
from argparse import ArgumentError
import os
import sys


def airdrops():
    webbrowser.open("https://airdrops.io/")


def airdrop_alerts():
    webbrowser.open("https://airdropalert.com/")


def airdrops_cmc():
    webbrowser.open("https://coinmarketcap.com/en/airdrop/")


def airdrop_view(args):

    parser = argparse.ArgumentParser(prog="airdrop", add_help=True)
    parser.add_argument(
        "-w",
        "--web",
        choices=["cmc", "airdrops", "airdropalert"],
        default="airdrops",
        required=False,
        dest="airdrop",
    )
    parsy, others = parser.parse_known_args(args)
    if parsy.airdrop == "cmc":
        airdrops_cmc()
    elif parsy.airdrop == "airdrops":
        airdrops()
    elif parsy.airdrop == "airdropalert":
        airdrop_alerts()


def main():
    choices = ["airdrop", "quit", "q", "r"]
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(prog="cmc", add_help=False)
    parser.add_argument("cmd", choices=choices)

    print(LOGO)
    while True:
        an_input = input(f"{MOON}> ")
        try:
            parsy, others = parser.parse_known_args(an_input.split())
            cmd = parsy.cmd

            if cmd in ["exit", "quit", "q"]:
                return False
            elif cmd == "r":
                return True

            if cmd == "airdrop":
                airdrop_view(others)

        except ArgumentError:
            print("The command selected doesn't exist")
            print("\n")
            continue

        except SystemExit:
            print("\n")
            continue


if __name__ == "__main__":
    main()
