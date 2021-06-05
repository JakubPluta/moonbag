#!/usr/bin/env python
import sys
import os
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
from argparse import ArgumentError
from inspect import signature
from moonbag.cryptocompare.utils import MoonParser
from moonbag.onchain.ethereum.eth import Eth

logger = logging.getLogger("ethereum-menu")


class Controller:
    def __init__(self):
        self.client = Eth()
        self.parser = argparse.ArgumentParser(prog="eth", add_help=False)
        self.parser.add_argument("cmd")
        self.base_commands = ["help", "exit", "quit", "r", "q"]
        self.mapper = {
            "token_info": self.show_token_info,
            "tx_info": self.show_tx_info,
            "address_info" : self.show_address_info,
            "address_tx" : self.show_address_tx,
            "address_hist" : self.show_address_hist,
            "top_tokens": self.show_top_tokens,
            "token_holders": self.show_top_token_holders,
            "token_price": self.show_token_price,
            "token_hist" : self.show_token_history,
            "token_txs": self.show_token_txs,
        }

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("Ethplorer        ")
        print("   token_info       show info about erc20 token [Ethplorer]")
        print("   tx_info          show info about transaction on ethereum blockchain [Ethplorer]")
        print("   address_info     show info about ethereum address [Ethplorer]")
        print("   address_tx       show ethereum address transactions [Ethplorer]")
        print("   top_tokens       show most popular coin on ethplorer [Ethplorer]")

        print("   token_holders    show info about token holders [Ethplorer]")

        print("   token_price      show info about historical token prices [Ethplorer]")
        print("   token_hist       show historical info about erc20 token [Ethplorer]")
        print("   token_txs        show info about historical token transactions [Ethplorer]")

        print(" ")
        return

    def show_token_info(self, args):
        parser = MoonParser(
            prog="token info",
            add_help=True,
            description="get token information",
        )
        parser.add_address_argument()
        parsy, _ = parser.parse_known_args(args)
        try:
            prices = self.client.get_token_info(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices)

    def show_token_history(self, args):
        parser = MoonParser(
            prog="token history",
            add_help=True,
            description="get token history",
        )
        parser.add_address_argument()
        parsy, _ = parser.parse_known_args(args)
        try:
            prices = self.client.get_token_history(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(prices)

    def show_tx_info(self, args):
        parser = MoonParser(
            prog="ethereum transaction info",
            add_help=True,
            description="get transaction details",
        )
        parser.add_address_argument(help='Ethereum transaction hash')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_tx_info(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_address_info(self, args):
        parser = MoonParser(
            prog="ethereum address info",
            add_help=True,
            description="get address details",
        )
        parser.add_address_argument(help='Ethereum address')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_address_info(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_address_tx(self, args):
        parser = MoonParser(
            prog="ethereum address transactions info",
            add_help=True,
            description="show address transactions details",
        )
        parser.add_address_argument(help='Ethereum address')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_address_transactions(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_address_hist(self, args):
        parser = MoonParser(
            prog="ethereum address history",
            add_help=True,
            description="show address history",
        )
        parser.add_address_argument(help='Ethereum address')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_address_history(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_top_token_holders(self, args):
        parser = MoonParser(
            prog="ethereum token holders",
            add_help=True,
            description="show top token holders",
        )
        parser.add_address_argument(help='Ethereum token address')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_top_token_holders(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_top_tokens(self, args):
        parser = MoonParser(
            prog="ethereum top tokens",
            add_help=True,
            description="show top tokens",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_top_tokens()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_token_price(self, args):
        parser = MoonParser(
            prog="token price",
            add_help=True,
            description="show token prices",
        )
        parser.add_address_argument(help='Ethereum token address')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_token_historical_price(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_token_txs(self, args):
        parser = MoonParser(
            prog="token transactions",
            add_help=True,
            description="show token transactions",
        )
        parser.add_address_argument(help='Ethereum token address')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_token_historical_txs(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)


def main():
    c = Controller()
    choices = c.base_commands + list(c.mapper.keys())
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(prog="ethereum", add_help=False)
    parser.add_argument("cmd", choices=choices)

    print(LOGO)
    c.help()
    while True:

        an_input = input(f"{MOON}> (ethereum) ")
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
            print("")
            continue

        except SystemExit:
            print("")
            print("")
            continue

