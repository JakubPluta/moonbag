import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os
from gateways.cryptocompare._client import CryptoCompareClient

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

load_dotenv()

API_KEY = os.getenv("CC_API_KEY")


class CryptoCompare(CryptoCompareClient):
    COMPARE_URL = 'https://www.cryptocompare.com'

    def __init__(self, api_key):
        super().__init__(api_key)
        self.api_key = api_key

    # TODO: ADD Another method to fetch multi coins data ?
    def get_price(self, symbol="BTC", currency="USD", **kwargs):
        data = self._get_price(symbol, currency, **kwargs)['RAW'][symbol][currency]
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
            "CHANGEDAY"
            "CHANGEPCTDAY",
            "CHANGEHOUR"
            "CHANGEPCTHOUR",
            "CHANGE24HOUR",
            "CHANGEPCT24HOUR",
        ]
        data = {k:v for k,v in data.items() if k in columns}
        return pd.Series(data)

    def get_top_list_by_market_cap(self, currency="USD", limit=100, **kwargs):
        data = self._get_top_list_by_market_cap(currency, limit, **kwargs)['Data']
        data = [{'CoinInfo':d.get('CoinInfo'),'RAW' : d.get('RAW')} for d in data]
        df = pd.json_normalize(data)
        df.columns = [col.split('.')[-1] for col in list(df.columns)]
        df['Url'] = df['Url'].apply(lambda x: self.COMPARE_URL + x)
        return df

    def get_top_exchanges(self, symbol="BTC", currency="USD", limit=100, **kwargs):
        data = self._get_top_exchanges(symbol,currency,limit,**kwargs)['Data']['Exchanges']
        return pd.json_normalize(data)

