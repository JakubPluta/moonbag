import pandas as pd
import json
import requests


class EthplorerClient:
    def __init__(self, api_key=None):
        self.api_key = api_key or "freekey"
        self.api_query = f"?apiKey={api_key}"

    @staticmethod
    def _request_call(x):
        response = requests.request("GET", x)
        return json.loads(response.text)

    def get_address_info(self, address):
        url = f"https://api.ethplorer.io/getAddressInfo/{address}{self.api_query}"
        resp = self._request_call(url)
        return resp

    def get_token_info(self, address):
        url = f"https://api.ethplorer.io/getTokenInfo/{address}{self.api_query}"
        resp = self._request_call(url)
        return resp

    def get_tx_info(self, tx_hash):
        url = f"https://api.ethplorer.io/getTxInfo/{tx_hash}{self.api_query}"
        resp = self._request_call(url)
        return resp

    def get_token_history(self, address):
        url = f"https://api.ethplorer.io/getTokenHistory/{address}{self.api_query}&limit=1000"
        resp = self._request_call(url)
        return resp

    def get_address_history(self, address):
        url = f"https://api.ethplorer.io/getAddressHistory/{address}{self.api_query}&limit=1000"
        resp = self._request_call(url)
        return resp

    def get_address_transactions(self, address):
        url = (
            f"https://api.ethplorer.io/getAddressTransactions/{address}{self.api_query}"
        )
        resp = self._request_call(url)
        return resp

    def get_token_price_history_grouped(self, address):
        url = f"https://api.ethplorer.io/getTokenPriceHistoryGrouped/{address}{self.api_query}"
        resp = self._request_call(url)
        return resp

    def get_token_history_grouped(self, address):
        url = (
            f"https://api.ethplorer.io/getTokenHistoryGrouped/{address}{self.api_query}"
        )
        resp = self._request_call(url)
        return resp

    def get_top_token_holders(self, address):
        url = f"https://api.ethplorer.io/getTopTokenHolders/{address}{self.api_query}"
        resp = self._request_call(url)
        return resp
