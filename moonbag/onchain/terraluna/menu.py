#!/usr/bin/env python
import sys
import os
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
from argparse import ArgumentError
from inspect import signature
from moonbag.cryptocompare.utils import MoonParser
from moonbag.onchain.terraluna.terra import Terra

logger = logging.getLogger("terra-menu")


class Controller:
    def __init__(self):
        self.client = Terra()
        self.parser = argparse.ArgumentParser(prog="terra", add_help=False)
        self.parser.add_argument("cmd")
        self.base_commands = ["help", "exit", "quit", "r", "q"]
        self.mapper = {
            "supply": self.show_supply,
            "staking": self.show_staking,
            "account_info" : self.show_address_info,
            "transaction" : self.show_tx_info,
            "validators" : self.show_validators,
        }

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("Terra        ")
        print("   transaction      show info about transaction [Terra]")
        print("   account_info     show info about account_info [Terra]")
        print("   staking          show info about staking [Terra]")
        print("   supply           show info about terra coins supply [Terra]")
        print("   validators       show info about terra validators [Terra]")

        print(" ")
        return

    def show_tx_info(self, args):
        parser = MoonParser(
            prog="transaction info",
            add_help=True,
            description="transaction details",
        )
        parser.add_address_argument(help='transaction hash')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_tx(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_address_info(self, args):
        parser = MoonParser(
            prog="terra address info",
            add_help=True,
            description="get address details",
        )
        parser.add_address_argument(help='account address')
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_account(parsy.address)
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_staking(self, args):
        parser = MoonParser(
            prog="staking info",
            add_help=True,
            description="show staking details",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_staking_pool()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_supply(self, args):
        parser = MoonParser(
            prog="supply info",
            add_help=True,
            description="show terra coins supply details",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_coins_supply()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

    def show_validators(self, args):
        parser = MoonParser(
            prog="validators info",
            add_help=True,
            description="show terra validators",
        )
        parsy, _ = parser.parse_known_args(args)
        try:
            data = self.client.get_validators()
        except ValueError as e:
            print(f"{e}")
            return
        print_table(data)

def main():
    c = Controller()
    choices = c.base_commands + list(c.mapper.keys())
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(prog="terra", add_help=False)
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
            print(" ")
            continue

        except SystemExit:
            print(" ")
            print(" ")
            continue


if __name__ == "__main__":
    main()
