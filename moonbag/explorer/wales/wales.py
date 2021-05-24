import json
import requests
import time
from dotenv import load_dotenv
import os
import pandas as pd

load_dotenv()
API_KEY = os.getenv("WALES_API_KEY")


def _get_wales_stats(min_value=1000000):
    req = f"https://api.whale-alert.io/v1/transactions?api_key={API_KEY}"
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
            "transaction_type",
            "hash",
        ],
        axis=1,
        inplace=True,
    )
    data["timestamp"] = pd.to_datetime(data["timestamp"], unit="s")
    data.columns = [col.replace(".address", "") for col in data.columns]
    return data.set_index("timestamp")
