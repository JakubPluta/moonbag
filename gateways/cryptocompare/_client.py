import pandas as pd
import numpy as np
import requests
# https://github.com/CryptoCompareLTD/api-guides/tree/master/python

from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv('CC_API_KEY')


ENDPOINTS = {
    "PRICE_SINGLE": "/data/price",
    "PRICE_MULTI": "/data/pricemulti",
    "PRICE_MULTI_FULL": "/data/pricemultifull",
    "GENERATE_AVERAGE": "/data/generateAvg",
    "HISTO_DAY": "/data/histoday",
    "HISTO_HOUR": "/data/histohour",
    "HISTO_MINUTE": "/data/histominute",
    "TOP_LIST_24": "/data/top/totalvolfull",
    "TOP_LIST_24_FULL": "/data/top/totaltoptiervolfull",
    "TOP_BY_MARKET_CAP": "/data/top/mktcapfull",
    "TOP_EXCHANGES_FULL_DATA": "/data/top/exchanges/full",
    'TOP_LIST_PAIR_VOLUME' : "/data/top/volumes",
    'TOP_LIST_OF_PAIRS' : 'data/top/pairs',
    "EXCHANGE_TOP_SYMBOLS": "/data/exchange/top/volume",
    "ALL_COINS_LIST": "/data/all/coinlist",
    "LATEST_COIN_SOCIAL_STATS": "/data/social/coin/latest",
    "HISTO_DAY_SOCIAL_STATS": '/data/social/coin/histo/day',
    "NEWS": "/data/v2/news/",
    "WALLETS": "/data/wallets/general",
    "GAMBLING": "/data/gambling/general",
    "MINING_CONTRACTS": "/data/mining/contracts/general",
    "MINING_COMPANIES": "/data/mining/companies/general",
    "RECOMMENDED": "/data/recommended/all",
    "FEEDS": "/data/news/feeds",
    'BLOCKCHAIN_COINS' : '/data/blockchain/list',
}


class CryptoCompareClient:
    BASE_URL = "https://min-api.cryptocompare.com"

    def __init__(self, api_key):
        self.api_key = api_key

    def _make_request(self, endpoint, payload=None, **kwargs):
        """You can use either endpoint key or endpoint value from dictionary ENDPOINTS
        All of request will be handled"""

        if endpoint in ENDPOINTS:
            endpoint_path = ENDPOINTS.get(endpoint)
        elif endpoint in list(ENDPOINTS.values()):
            endpoint_path = endpoint
        else:
            raise ValueError(f"Wrong endpoint\nPlease Use one from List {list(ENDPOINTS.keys())}")
        url = self.BASE_URL + endpoint_path
        if payload is None:
            payload = {}
        if kwargs:
            payload.update(kwargs)
        headers = {"authorization": "Apikey " + self.api_key}
        req = requests.get(url, params=payload, headers=headers)
        return req.json()

    def get_price(self, symbol='BTC', currency='USD', **kwargs):
        """Full data"""
        endpoint = ENDPOINTS["PRICE_MULTI_FULL"]
        payload = {
            'fsyms' : symbol,
            'tsyms' : currency,
            'relaxedValidation' : False,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_top_list_by_market_cap(self, currency='USD', limit=100, **kwargs):
        endpoint = ENDPOINTS["TOP_BY_MARKET_CAP"]
        payload = {
            'tsym': currency,
            'limit': limit
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_top_exchanges(self,  symbol='BTC', currency='USD', limit=100, **kwargs):
        endpoint = ENDPOINTS["TOP_EXCHANGES_FULL_DATA"]
        payload = {
            'fsym': symbol,
            'tsym': currency,
            'limit': limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_exchanges_top_symbols_by_volume(self, exchange='Binance', limit=100,**kwargs):
        "/data/exchange/top/volume?e=Binance&direction=TO"
        "e=Kraken"
        endpoint = ENDPOINTS["EXCHANGE_TOP_SYMBOLS"]
        payload = {
            'e' : exchange,
            'limit': limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_top_list_by_pair_volume(self, currency='USD', limit=100, **kwargs):
        endpoint = ENDPOINTS['TOP_LIST_PAIR_VOLUME']
        payload = {
            'tsym': currency,
            'limit' : limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_top_of_trading_pairs(self,symbol='BTC', limit=100, **kwargs):
        endpoint = ENDPOINTS['TOP_LIST_OF_PAIRS']
        payload = {
            'fsym': symbol,
            'limit': limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    # TODO --> Add mappings that use can use either coinId, symbol, or name for requests
    # TODO --> Maybe use regex ? To handle cases like bitcoin, Bitcoin, BITCOIN, btc, BTC etc
    def get_latest_social_coin_stats(self, coin_id=7605, **kwargs):
        endpoint = ENDPOINTS['LATEST_COIN_SOCIAL_STATS']
        payload = {"coinId": int(coin_id)}
        return self._make_request(endpoint, payload, **kwargs)

    def get_historical_social_stats(self, coin_id=7605,limit=2000,aggregate=1,**kwargs):
        endpoint = ENDPOINTS['HISTO_DAY_SOCIAL_STATS']
        payload = {
            "coinId": int(coin_id),
            'limit' : limit,
            'aggregate' : aggregate,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_latest_news(self,lang='EN',sort_order='latest' ,**kwargs):
        endpoint = ENDPOINTS["NEWS"]
        payload = {
            'lang' : lang,
            'sortOrder': sort_order
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_blockchain_available_coins_list(self):
        endpoint=ENDPOINTS['BLOCKCHAIN_COINS']
        return self._make_request(endpoint=endpoint)

    def get_all_coins_list(self,summary='true', **kwargs):
        endpoint = ENDPOINTS['ALL_COINS_LIST']
        if isinstance(summary, bool):
            summary = str(summary).lower()

        payload = {
            'summary' : summary
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_historical_day_prices(self, symbol='BTC', currency='USD', limit=2000, **kwargs):
        endpoint = ENDPOINTS["HISTO_DAY"]
        payload = {
            'fsym' : symbol,
            'tsym' : currency,
            'limit' : limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_historical_hour_prices(self, symbol='BTC', currency='USD', limit=2000, **kwargs):
        endpoint = ENDPOINTS["HISTO_HOUR"]
        payload = {
            'fsym' : symbol,
            'tsym' : currency,
            'limit' : limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def get_historical_minutes_prices(self, symbol='BTC', currency='USD', limit=2000, **kwargs):
        endpoint = ENDPOINTS["HISTO_MINUTE"]
        payload = {
            'fsym' : symbol,
            'tsym' : currency,
            'limit' : limit,
        }
        return self._make_request(endpoint, payload, **kwargs)





from pprint import pprint
compare = CryptoCompare(API_KEY)
coins = compare.get_historical_minutes_prices()
pprint(coins)
print(len(coins))