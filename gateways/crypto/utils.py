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


def filter_list(lst: list) -> list:
    if isinstance(lst, list) and len(lst) > 0:
        return [i for i in lst if i != ""]


def calculate_time_delta(date: str):
    now = dt.datetime.now(timezone.utc)
    if not isinstance(date, dt.datetime):
        date = parser.parse(date)
    return (now - date).days


def get_eth_addresses_for_cg_coins(file):
    with open(file, 'r') as f:
        data = json.load(f)
        df = pd.DataFrame(data)
        df['ethereum'] = df['platforms'].apply(lambda x: x.get('ethereum') if 'ethereum' in x else None)
        return df
