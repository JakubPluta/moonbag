import argparse
from moonbag.gecko.gecko import  get_coin_list, Coin
import logging
from moonbag import LOGO, MOON
from typing import List
from moonbag.gecko.overview_menu import print_table
import textwrap
from inspect import signature

logger = logging.getLogger("parser")


class Controller:

    def __init__(self):
        self.parser = argparse.ArgumentParser(prog="coin", add_help=False)
        self.parser.add_argument("cmd")
        self.base = {
                    'help' : self.help,
                    "r": self.returner,
                    "quit": self.quit,
                    "exit": self.quit,
                }

        self.mapper = {
            'load': self.load_coin,
            'web' : self.show_web,
            'info' : self.show_coin_base_info,
            'devs' : self.show_developers,
            'market' : self.show_market,
            'social' : self.show_socials,
            'ath' : self.show_ath,
            'atl' : self.show_atl,
            'coinlist' : self.show_list_of_coins,
            'explorers' : self.show_bcexplores,

                  }


        self.coin = None

    @staticmethod
    def help():
        print("Main commands:")
        print("   help              show help")
        print("   r                 return to previous menu")
        print("   quit              quit program")
        print("")
        print("Coin View            [Coingecko]")
        print("    load             load coin, example: 'load -c uniswap' [Coingecko]")
        print("    coinlist         show list of all coins available in [Coingecko]")
        print("    info             show info about loaded coin [Coingecko]")
        print("    market           show market info about loaded coin [Coingecko]")
        print("    devs             show development information about loaded coins [Coingecko]")
        print("    ath              show info all time high of loaded coin [Coingecko]")
        print("    atl              show info all time low of loaded coin [Coingecko]")
        print("    web              show web pages founded for loaded coin [Coingecko]")
        print("    explorers        show blockchain explorers links for loaded coin [Coingecko]")
        return

    @staticmethod
    def quit():
        return False

    @staticmethod
    def returner():
        return True

    def load_coin(self, args: List[str]):
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
            self.coin = Coin(parsy.coin)
        except ValueError as e:
            print(f"{e}, To check list of coins use command: coinlist ")
            return

        else:
            print(f"Coin loaded {self.coin.coin_symbol}")

    @property
    def _is_loaded(self):
        if self.coin is None:
            print("You didn't load a coin, plase first use load -c symbol to load coin")
            return False
        return True

    def show_coin_base_info(self, args):
        if self._is_loaded:
            df = self.coin.base_info.reset_index()
            df = df.applymap(lambda x: '\n'.join(textwrap.wrap(x, width=150)) if isinstance(x, str) else x)
            df.columns = ['Metric', 'Value']
            print_table(df)

    @staticmethod
    def show_list_of_coins(args):
        print_table(get_coin_list(),'plain')

    def show_scores(self,args):
        if self._is_loaded:
            df = self.coin.scores
            df = df.applymap(lambda x: '\n'.join(textwrap.wrap(x, width=200)) if isinstance(x, str) else x)
            df.columns = ['Metric', 'Value']
            print_table(df)

    def show_market(self, args):
        if self._is_loaded:
            df = self.coin.market_data
            print_table(df)

    def show_atl(self, args):
        if self._is_loaded:
            print_table(self.coin.all_time_low)

    def show_ath(self, args):
        if self._is_loaded:
            df = self.coin.all_time_high
            print_table(df)

    def show_developers(self, args):
        if self._is_loaded:
            print_table(self.coin.developers_data)

    def show_bcexplores(self, args):
        if self._is_loaded:
            print_table(self.coin.blockchain_explorers)

    def show_socials(self,args):
        if self._is_loaded:
            print_table(self.coin.social_media)

    def show_web(self, args):
        if self._is_loaded:
            print_table(self.coin.websites)



def main():
    c = Controller()
    choices = list(c.mapper.keys()) + list(c.base.keys())

    parser = argparse.ArgumentParser(prog="coin", add_help=False)
    parser.add_argument("cmd", choices=choices)
    print(LOGO)
    c.help()
    while True:
        an_input = input(f"> {MOON} ")

        # TODO: Clean this code, make it more elegant
        try:
            parsy, others = parser.parse_known_args(an_input.split())
            cmd = parsy.cmd

            view = c.base.get(cmd)

            if view and cmd == 'help':
                view()
                continue
            elif view:
                return view()

            view = c.mapper.get(cmd)
            if view is None:
                continue
            elif callable(view):
                if len(signature(view).parameters) > 0:
                    view(others)
                else:
                    view()


        except SystemExit:
            print("The command selected doesn't exist")
            print("\n")
            continue


if __name__ == "__main__":
    main()
