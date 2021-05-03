import argparse
import pprint
import logging
from gecko import gecoin

logger = logging.getLogger("coingecko")


def help():
    print("Session started!")
    print("moon        gecko")
    print("help        help me please")
    print("quit        shut me down bro")
    print("\n")


def main():
    main_parser = argparse.ArgumentParser(prog="coingecko", add_help=False,)

    main_parser.add_argument("option", choices=["moon", "help", "quit"])

    print("Hello on the Moon!\nLets start research :)\n")
    print()
    help()

    while True:
        cmd_line = False
        user_input = input("> ")

        try:
            (ns_known_args, l_args) = main_parser.parse_known_args(
                user_input.split()
            )
        except SystemExit as e:
            logger.log(3, e)
            continue

        if ns_known_args.option == "moon":

            parser = argparse.ArgumentParser(
                prog="moonbag",
                description="Let's use Coingecko to screen my gecko gems ",
            )
            parser.add_argument(
                "-c",
                "--coin",
                action="store",
                dest="symbol",
                default="terra-luna",
                help="Coin Symbol",
            )

            try:
                (ns_parser, l_unknown_args) = parser.parse_known_args(l_args)
            except SystemExit as e:
                logger.log(3, e)
                continue

            if l_unknown_args:
                print(
                    f"The following args couldn't be interpreted: {l_unknown_args}"
                )

            try:
                data = gecoin.get_coin_data(ns_parser.symbol)
                print(data)
            except Exception as e:
                logger.log(3, e)
                continue

        elif arg.cmd == "help":
            help()

        elif arg.cmd == "quit" or "q":
            print("Moon is always with you my friend!\nSee you soon\n")
            break


if __name__ == "__main__":
    main()
