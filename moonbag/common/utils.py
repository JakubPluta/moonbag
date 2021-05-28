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


# FIXME Make this func more general
def wrap_text_in_df(df: pd.DataFrame, w=55):
    return df.applymap(
        lambda x: "\n".join(textwrap.wrap(x, width=w)) if isinstance(x, str) else x
    )


def underscores_to_newline_replace(cols: list, line: int = 13):
    return [
        textwrap.fill(c.replace("_", " "), line, break_long_words=False)
        for c in list(cols)
    ]


def wrap_headers_in_dataframe(df: pd.DataFrame, n=15, replace=None):
    if replace:
        return [
        textwrap.fill(c.replace(replace, " "), n, break_long_words=False)
            for c in list(df.columns)
    ]
    return [textwrap.fill(c, n, break_long_words=False) for c in list(df.columns)]