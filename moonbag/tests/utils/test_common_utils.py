import pandas as pd
import datetime
from moonbag.common.utils import (
    formatter,
    underscores_to_newline_replace,
    wrap_headers_in_dataframe,
    created_date,
    MoonParser,
    BASE_PARSER_ARGUMENTS,
)


def test_formatter():
    assert formatter(5) == "5.00"
    assert formatter(0.2) == "0.200000"
    assert formatter(5555) == "5555.00"
    assert formatter("abc") == "abc"


def test_underscores_to_new_line():
    cols = ["column_number_one", "column_number_two"]
    assert underscores_to_newline_replace(cols) == [
        "column number\none",
        "column number\ntwo",
    ]
    assert underscores_to_newline_replace(["column", "col_one"]) == [
        "column",
        "col one",
    ]


def test_wrap_headers_in_df():
    df = pd.DataFrame(
        columns=["column_number_one", "column_number_two"], data=[[0, 2], [3, 4]]
    )
    assert wrap_headers_in_dataframe(df, 15, "_") == [
        "column number\none",
        "column number\ntwo",
    ]


def test_created_date():
    dt = 1622844000
    assert created_date(dt) == datetime.datetime(2021, 6, 5, 0, 0, 0)


def test_moon_parser():
    moon = MoonParser()
    dct = BASE_PARSER_ARGUMENTS["coin"]
    r = moon._modify_default_dict_of_arguments(
        dct=dct,
        dest="name",
        help="this is test name arg",
        type=str,
        fake=1,
    )
    assert r == {
        "help": "this is test name arg",
        "dest": "name",
        "required": True,
        "default": "ETH",
        "type": str,
    }
