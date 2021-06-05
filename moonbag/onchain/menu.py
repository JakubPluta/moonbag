#!/usr/bin/env python
import sys
import os
import time
import argparse
import logging
from moonbag.common import LOGO, MOON, print_table
from argparse import ArgumentError
from inspect import signature
from moonbag.onchain.ethereum import menu as eth_menu
from moonbag.onchain.terraluna import menu as terra_menu

logger = logging.getLogger("paprika-menu")


def help():
    print("Main commands:")
    print("   help              show help")
    print("   r                 return to previous menu")
    print("   quit              quit program")
    print("")
    print("On-chain data        ")
    print("   ethereum       explore on-chain data for ethereum [Ethplorer]")
    print("   terra          explore on-chain data for terra  [TerraAPI]")
    print("")

mapper = {
    "ethereum" : eth_menu.main,
    "terra" : terra_menu.main,

}

oc_menu = False

def main():
    choices = ["help", "exit", "quit", "r", "q", "terra", "ethereum"]
    if sys.platform == "win32":
        os.system("")

    parser = argparse.ArgumentParser(prog="onchain", add_help=False)
    parser.add_argument("cmd", choices=choices)

    print(LOGO)
    help()

    while True:
        an_input = input(f"{MOON}> ")
        try:
            parsy, others = parser.parse_known_args(an_input.split())
            cmd = parsy.cmd

            if cmd == "help":
                help()
            elif cmd in ["exit", "quit", "q"]:
                return False
            elif cmd == "r":
                return True

            view = mapper.get(cmd)
            if view is None:
                continue
            elif callable(view):
                print(f"Going to {cmd}")
                view()

        except ArgumentError:
            print("The command selected doesn't exist")
            print("\n")
            continue

        except SystemExit:
            time.sleep(0.1)
            print("")
            print("")
            continue

if __name__ == "__main__":
    main()
