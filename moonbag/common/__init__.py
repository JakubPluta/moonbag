import pandas as pd
from tabulate import tabulate


MOON = "(Ⓜ☯Ⓑ)"


LOGO = """
    ███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗██████╗  █████╗  ██████╗ 
    ████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔════╝ 
    ██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║██████╔╝███████║██║  ███╗
    ██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║   ██║
    ██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██║  ██║╚██████╔╝
    ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝
                           .:::::/|::::.
                          ::::::/ V|:::::
                         ::::::/'  |::::::
                         ::::<_,   (::::::
                          :::::|    \::::
                           '::/      \::'
    
                   Welcome in MoonBag Terminal!
"""


def print_table(df: pd.DataFrame, floatfmt=".4f", tablefmt="psql"):
    if not isinstance(df, pd.DataFrame):
        raise TypeError("Please use data frame as an input!")
    print(
        tabulate(
            df,
            headers=df.columns,
            floatfmt=floatfmt,
            showindex=False,
            tablefmt=tablefmt,
        )
    )
    print("")

