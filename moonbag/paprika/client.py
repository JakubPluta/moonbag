import datetime

import requests
from retry import retry
from requests.adapters import HTTPAdapter


ENDPOINTS = {
    'global': '/global',
    'coins': '/coins',
    'coin_tweeter': '/coins/{}/twitter',
    'coin_events': '/coins/{}/events',
    'coin_exchanges': '/coins/{}/exchanges',
    'coin_markets': '/coins/{}/markets',
    'ohlcv': '/coins/{}/ohlcv/latest',
    'ohlcv_hist' : '/coins/{}/ohlcv/historical'
}


class Client:
    BASE_URL = "https://api.coinpaprika.com/v1"

    def __init__(self):
        self.header = {'Accept': 'application/json','User-Agent': 'moonbag'}
        self.s = requests.Session()
        self.s.mount(self.BASE_URL, HTTPAdapter(max_retries=5))

    @retry(tries=2, delay=3, max_delay=5)
    def _make_request(self, endpoint, payload=None, **kwargs):
        url = self.BASE_URL + endpoint
        if payload is None:
            payload = {}
        if kwargs:
            payload.update(kwargs)
        return requests.get(url, params=payload).json()

    def get_global_market(self):
        return self._make_request(ENDPOINTS['global'])

    def get_coins(self):
        return self._make_request(ENDPOINTS['coins'])

    def get_coin_twitter_timeline(self, coin_id='eth-ethereum'):
        return self._make_request(ENDPOINTS['coin_tweeter'].format(coin_id))

    def get_coin_events_by_id(self, coin_id='eth-ethereum'):
        return self._make_request(ENDPOINTS['coin_events'].format(coin_id))

    def get_coin_exchanges_by_id(self, coin_id='eth-ethereum'):
        return self._make_request(ENDPOINTS['coin_exchanges'].format(coin_id))

    def get_coin_markets_by_id(self, coin_id='eth-ethereum', quotes='USD,BTC'):
        return self._make_request(ENDPOINTS['coin_markets'].format(coin_id), quotes=quotes)

    def get_ohlc_last_day(self, coin_id='eth-ethereum', quotes='USD'):
        """"string Default: "usd"
        returned data quote (available values: usd btc)"""
        return self._make_request(ENDPOINTS['ohlcv'].format(coin_id), quotes=quotes)

    def get_ohlc_histo(self, coin_id='eth-ethereum', quotes='USD', start="2020-06-15", end=None):
        if end is None:
            end = datetime.datetime.now().strftime("%Y-%m-%d")
        """"string Default: "usd"
        returned data quote (available values: usd btc)"""
        return self._make_request(ENDPOINTS['ohlcv_hist'].format(coin_id), quotes=quotes, start=start, end=end)


