import datetime as dt
from datetime import timezone
from dateutil import parser
import json
import pandas as pd


def find_discord(item: list) -> list or None:
    if isinstance(item, list) and len(item) > 0:
        discord = [chat for chat in item if "discord" in chat]
        if len(discord) > 0:
            return discord[0]


def join_list_elements(elem):
    if not elem:
        raise ValueError("Elem is empty")
    if isinstance(elem, dict):
        return ", ".join([k for k, v in elem.items()])
    elif isinstance(elem, list):
        return ", ".join([k for k in elem])
    else:
        return None


def filter_list(lst: list) -> list:
    if isinstance(lst, list) and len(lst) > 0:
        return [i for i in lst if i != ""]


def calculate_time_delta(date: str):
    now = dt.datetime.now(timezone.utc)
    if not isinstance(date, dt.datetime):
        date = parser.parse(date)
    return (now - date).days


def get_eth_addresses_for_cg_coins(file):
    with open(file, "r") as f:
        data = json.load(f)
        df = pd.DataFrame(data)
        df["ethereum"] = df["platforms"].apply(
            lambda x: x.get("ethereum") if "ethereum" in x else None
        )
        return df


def clean_question_marks(dct: dict):
    if isinstance(dct, dict):
        for k, v in dct.items():
            if v == "?":
                dct[k] = None


def replace_qm(df):
    df.replace({'?':None ,' ?':None},inplace=True)
    return df


def get_url(url, elem):
    return url + elem.find("a")["href"]


def clean_row(row):
    return [
        r for r in row.text.strip().split("\n") if r not in ["", " "]
    ]


def collateral_auditors_parse(args):
    if args and args[0] == 'N/A':
        collateral = args[1:]
        auditors = []
    else:
        n_elem = int(args[0])
        auditors = args[1:n_elem + 1]
        collateral = args[n_elem + 1:]

    return auditors, collateral


def changes_parser(changes):
    if isinstance(changes, list) and len(changes) < 3:
        for i in range(3 - len(changes)):
            changes.append(None)
    else:
        changes = [None for i in range(3)]
    return changes
