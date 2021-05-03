import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os
from gateways.cryptocompare._client import CryptoCompareClient
from gateways.cryptocompare.utils import table_formatter

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)

load_dotenv()

API_KEY = os.getenv("CC_API_KEY")


class CryptoCompare(CryptoCompareClient):
    COMPARE_URL = "https://www.cryptocompare.com"

    def __init__(self, api_key):
        super().__init__(api_key)
        self.api_key = api_key

    @table_formatter
    def get_price(self, symbol="BTC", currency="USD", **kwargs):
        data = self._get_price(symbol, currency, **kwargs)["RAW"][symbol][currency]
        columns = [
            "FROMSYMBOL",
            "TOSYMBOL",
            "PRICE",
            "MEDIAN",
            "VOLUMEDAY",
            "VOLUME24HOUR",
            "OPENDAY",
            "OPEN24HOUR",
            "HIGH24HOUR",
            "LOW24HOUR",
            "MKTCAP",
            "SUPPLY",
            "TOTALVOLUME24H",
            "CHANGEDAY" "CHANGEPCTDAY",
            "CHANGEHOUR" "CHANGEPCTHOUR",
            "CHANGE24HOUR",
            "CHANGEPCT24HOUR",
        ]
        data = {k: v for k, v in data.items() if k in columns}
        return pd.Series(data)

    @table_formatter
    def get_top_list_by_market_cap(self, currency="USD", limit=100, **kwargs):
        data = self._get_top_list_by_market_cap(currency, limit, **kwargs)["Data"]
        data = [{"CoinInfo": d.get("CoinInfo"), "RAW": d.get("RAW")} for d in data]
        df = pd.json_normalize(data)
        df.columns = [col.split(".")[-1] for col in list(df.columns)]
        df["Url"] = df["Url"].apply(lambda x: self.COMPARE_URL + x)
        return df

    @table_formatter
    def get_top_exchanges(self, symbol="BTC", currency="USD", limit=100, **kwargs):
        data = self._get_top_exchanges(symbol, currency, limit, **kwargs)["Data"][
            "Exchanges"
        ]
        return pd.json_normalize(data)

    @table_formatter
    def get_exchanges_top_symbols_by_volume(
        self, exchange="Binance", limit=100, **kwargs
    ):
        data = self._get_exchanges_top_symbols_by_volume(exchange, limit, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df["volume"] = df["volume"].apply(lambda x: float(x))
        df = df[df["volume"] > 0]
        return df

    @table_formatter
    def get_top_list_by_pair_volume(self, currency="USD", limit=100, **kwargs):
        data = self._get_top_list_by_pair_volume(currency, limit, **kwargs)["Data"]
        return pd.DataFrame(data)

    @table_formatter
    def get_top_of_trading_pairs(self, symbol="ETH", limit=50, **kwargs):
        data = self._get_top_of_trading_pairs(symbol, limit, **kwargs)["Data"]
        return pd.DataFrame(data)

    def get_latest_social_coin_stats(self, coin_id=7605, **kwargs):
        data = self._get_latest_social_coin_stats(coin_id, **kwargs)["Data"]
        social_stats = {}
        for social in ["Twitter", "Reddit", "Facebook"]:
            social_stats[social] = data.get(social)

        repo = data["CodeRepository"]
        repo_dct = {}
        if "List" in repo and len(repo["List"]) > 0:
            for k, v in repo["List"][0].items():
                if not isinstance(v, (list, dict, set)):
                    repo_dct[k] = v
            social_stats["CodeRepository"] = repo_dct

        crypto_compare = data["CryptoCompare"]
        crypto_compare_dct = {}
        for k, v in crypto_compare.items():
            if not isinstance(v, (list, dict, set)):
                crypto_compare_dct[k] = v
            social_stats["CryptoCompare"] = crypto_compare_dct
        data = pd.json_normalize(social_stats)
        data.columns = [col.replace(".", "_").lower() for col in list(data.columns)]
        for col in [
            "twitter_account_creation",
            "reddit_community_creation",
            "coderepository_last_update",
            "coderepository_created_at",
            "coderepository_last_push",
        ]:
            data[col] = pd.to_datetime(data[col], unit="s")
        return data.T
