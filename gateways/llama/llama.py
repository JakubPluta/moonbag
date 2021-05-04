import requests
import pandas as pd
import cachetools.func
from retry import retry
from gateways.utils import table_formatter
from gateways.llama.utils import get_slug_mappings

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)


class LLama:
    URL = "https://api.llama.fi/"
    ENDPOINTS = {"protocols": "protocols", "protocol": "protocol/"}

    def __init__(self):
        self._symbols = get_slug_mappings(self._get_protocols())

    @cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
    def _get_protocols(self):
        resp = requests.get(self.URL + self.ENDPOINTS.get("protocols"))
        resp.raise_for_status()
        return resp.json()

    @table_formatter
    def get_protocols(self):
        df = pd.DataFrame.from_dict(self._get_protocols())[
            [
                "name",
                "symbol",
                "address",
                "category",
                "chains",
                "change_1h",
                "change_1d",
                "change_7d",
                "tvl",
                "url",
                "description",
                #"module",
                #"audits",
                #"gecko_id",
                #"cmcId",
            ]
        ].set_index("name")
        df["chains"] = df["chains"].apply(lambda x: ",".join(x))
        return df

    @property
    def symbols(self):
        return self._symbols

    @cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
    def _get_protocol(self, protocol: str):
        # https://api.llama.fi/protocol/:name
        protocol = str(protocol).lower()
        for slug, name in self.symbols.items():
            if protocol == name:
                protocol = slug
                break
            elif protocol == slug:
                break
        else:
            raise ValueError(
                f"Wrong protocol name\nPlease chose protocol name from list\n{self.symbols}"
            )

        resp = requests.get(self.URL + self.ENDPOINTS.get("protocol") + protocol)
        resp.raise_for_status()
        return resp.json()

    @table_formatter
    def get_protocol_info(self, protocol: str):
        data = self._get_protocol(protocol)
        for stat in ['tvl','tokensInUsd']:
            data.pop(stat)
        df = pd.json_normalize(data)
        df["chains"] = df["chains"].apply(lambda x: ",".join(x))
        return df.T

    @table_formatter
    def get_protocol_total_value_locked(self, protocol: str):
        data = self._get_protocol(protocol).get('tvl')
        if not data:
            return pd.DataFrame()
        df = pd.json_normalize(data)
        df["date"] = pd.to_datetime(df["date"], unit="s")
        return df.set_index('date')
