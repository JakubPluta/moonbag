import requests
import time
from moonbag.common.keys import WALES_API_KEY
import pandas as pd
import textwrap


def _get_wales_stats(min_value=1000000):
    req = f"https://api.whale-alert.io/v1/transactions?api_key={WALES_API_KEY}"
    params = {"min_value": min_value, "start": int(time.time()) - 3000}
    return requests.get(url=req, params=params).json()["transactions"]


def get_wales_stats():
    data = _get_wales_stats()
    data = pd.json_normalize(data).sort_values("timestamp", ascending=False)
    data.drop(
        [
            "id",
            "transaction_count",
            "from.owner_type",
            "to.owner_type",
            "to.owner",
            "from.owner",
            "transaction_type",
            "hash",
        ],
        axis=1,
        inplace=True,
    )
    data["timestamp"] = pd.to_datetime(data["timestamp"], unit="s")
    data.columns = [col.replace(".address", "") for col in data.columns]
    data["to"] = data["to"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=46)) if isinstance(x, str) else x
    )
    data["from"] = data["from"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=46)) if isinstance(x, str) else x
    )
    return data.sort_values(by="amount_usd", ascending=False)
