from moonbag.cryptocompare.utils import (
    get_closes_matches_by_name,
    get_closes_matches_by_symbol,
    create_dct_mapping_from_df,
)
import pandas as pd


def test_create_dct_mapping_for_df():
    df = pd.DataFrame({"col1": ["one", "two"], "col2": ["abc", "cde"]})
    assert create_dct_mapping_from_df(df, col1="col1", col2="col2") == {
        "one": "abc",
        "two": "cde",
    }
