import pandas as pd
import pytest
from moonbag.gecko.utils import (
    find_discord,
    join_list_elements,
    filter_list,
    calculate_time_delta,
    clean_question_marks,
    replace_qm,
    swap_columns,
    changes_parser,
    remove_keys,
    rename_columns_in_dct,
    create_dictionary_with_prefixes,
)
import datetime as dt
from datetime import timezone


def test_should_properly_return_discord_if_exists():
    info = {"chat_url": ["https://discord.com/invite/NK4qdbv", "", ""]}
    assert find_discord(info.get("chat_url")) == "https://discord.com/invite/NK4qdbv"


def test_should_return_none_if_no_discord_or_no_object():
    info = {
        "chat_url": ["", "", ""],
    }
    info2 = {}

    assert find_discord(info.get("chat_url")) is None
    assert find_discord(info2.get("chat_url")) is None


def test_join_list_elements():
    assert join_list_elements({"one": 1, "two": 2, "three": 3}) == "one, two, three"
    assert join_list_elements(["one, two, three"]) == "one, two, three"
    with pytest.raises(ValueError) as e:
        join_list_elements([])
    assert "Elem is empty" in str(e.value)


def test_filter_list():
    assert filter_list([1, 2, 3, "", ""]) == [1, 2, 3]
    assert filter_list([]) is None
    assert filter_list(2) is None


def test_calculate_time_delta():
    date = dt.datetime.now(timezone.utc) - dt.timedelta(days=2)
    assert calculate_time_delta(date) == 2


def test_clean_question_marks():
    dct = {"key1": "?", "key2": "data", "key3": "?"}
    clean_question_marks(dct)
    assert dct == {"key1": None, "key2": "data", "key3": None}


def test_replace_qm_in_df():
    df = pd.DataFrame(
        columns=["a", "b", "c"], data=[["?", "1", "@"], ["A", "A", "A"], ["?", 1, 2]]
    )

    cleaned_df = pd.DataFrame(
        columns=["a", "b", "c"], data=[[None, "1", "@"], ["A", "A", "A"], [None, 1, 2]]
    )
    after_clean = replace_qm(df)
    assert after_clean.iloc[0, 0] == cleaned_df.iloc[0, 0]
    assert after_clean.iloc[2, 0] == cleaned_df.iloc[2, 0]


def test_swap_columns():
    df = pd.DataFrame(
        columns=["a", "b", "c"], data=[["?", "1", "@"], ["A", "A", "A"], ["?", 1, 2]]
    )

    assert swap_columns(df).columns.tolist() == ["c", "a", "b"]


def test_changes_parser():
    assert (
        changes_parser(
            [
                "fds",
                "fdsf",
            ]
        )
        == ["fds", "fdsf", None]
    )
    assert changes_parser(["fds", "fdsf", 1.2, 154, "asr"]) == [None, None, None]
    assert changes_parser([]) == [None, None, None]


def test_keys_removal():
    useless_keys = (
        "key2",
        "key3",
    )
    dct = {"key1": 1, "key2": 2, "key3": 3, "key4": 4}
    remove_keys(useless_keys, dct)
    assert dct == {"key1": 1, "key4": 4}


def test_rename_columns():
    mapper = {
        "key1": "a",
        "key2": "b",
    }
    dct = {"key1": 1, "key2": 2, "key3": 3}
    assert rename_columns_in_dct(dct, mapper) == {"a": 1, "b": 2, 3: 3}


def test_dictionary_with_pref():
    column = ["current_price"]
    den = ("usd", "btc", "eth")
    dct = {
        "current_price": {"usd": 1000, "btc": 200},
    }

    r = create_dictionary_with_prefixes(column, dct, den)
    assert r == {"current_price_usd": 1000, "current_price_btc": 200}
