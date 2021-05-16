import textwrap
import pandas as pd


def formatter(x):
    if isinstance(x, int):
        return "{0:.2f}".format(x)
    elif isinstance(x, float):
        if x > 10:
            return "{0:.2f}".format(x)
        else:
            return "{0:.6f}".format(x)
    return x


def table_formatter(func):
    def wrapper(*args, **kwargs):
        df = func(*args, **kwargs)
        df = df.applymap(lambda x: formatter(x))
        return df

    return wrapper


def wrap_text_in_df(df: pd.DataFrame, w=55):
    return df.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=w))
        if isinstance(x, str)
        else x
    )