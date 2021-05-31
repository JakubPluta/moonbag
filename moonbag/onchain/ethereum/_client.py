import pandas as pd
import json
import requests
import logging
from moonbag.onchain.ethereum.utils import (
    manual_replace,
    enrich_social_media,
    split_cols,
)
from datetime import datetime


class EthplorerClient:
    def __init__(self, api_key=None):
        self.api_key = api_key if api_key else "freekey"
        self.api_query = f"?apiKey={self.api_key}"

    @staticmethod
    def _request_call(x):
        response = requests.request("GET", x)
        return json.loads(response.text)

    def _get_address_info(self, address):
        url = f"https://api.ethplorer.io/getAddressInfo/{address}{self.api_query}"
        return self._request_call(url)

    def _get_token_info(self, address):
        url = f"https://api.ethplorer.io/getTokenInfo/{address}{self.api_query}"
        return self._request_call(url)

    def _get_tx_info(self, tx_hash):
        url = f"https://api.ethplorer.io/getTxInfo/{tx_hash}{self.api_query}"
        return self._request_call(url)

    def _get_token_history(self, address):
        url = f"https://api.ethplorer.io/getTokenHistory/{address}{self.api_query}&limit=1000"
        return self._request_call(url)

    def _get_address_history(self, address):
        url = f"https://api.ethplorer.io/getAddressHistory/{address}{self.api_query}&limit=1000"
        return self._request_call(url)

    def _get_address_transactions(self, address):
        url = (
            f"https://api.ethplorer.io/getAddressTransactions/{address}{self.api_query}"
        )
        return self._request_call(url)

    def _get_token_price_history_grouped(self, address):
        url = f"https://api.ethplorer.io/getTokenPriceHistoryGrouped/{address}{self.api_query}"
        return self._request_call(url)

    def _get_token_history_grouped(self, address):
        url = (
            f"https://api.ethplorer.io/getTokenHistoryGrouped/{address}{self.api_query}"
        )
        return self._request_call(url)

    def _get_top_token_holders(self, address):
        url = f"https://api.ethplorer.io/getTopTokenHolders/{address}{self.api_query}&limit=100"
        return self._request_call(url)

    def _get_top_tokens(self):
        url = f"https://api.ethplorer.io/getTopTokens/{self.api_query}"
        return self._request_call(url)
