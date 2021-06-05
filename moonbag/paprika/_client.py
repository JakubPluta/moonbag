import datetime

import requests
from retry import retry
from requests.adapters import HTTPAdapter


ENDPOINTS = {
    "global": "/global",
    "coins": "/coins",
    "coin_tweeter": "/coins/{}/twitter",
    "coin_events": "/coins/{}/events",
    "coin_exchanges": "/coins/{}/exchanges",
    "coin_markets": "/coins/{}/markets",
    "ohlcv": "/coins/{}/ohlcv/latest",
    "ohlcv_hist": "/coins/{}/ohlcv/historical",
    "people": "/people/{}",
    "tickers": "/tickers",
    "ticker_info": "/tickers/{}",
    "exchanges": "/exchanges",
    "exchange_info": "/exchanges/{}",
    "exchange_markets": "/exchanges/{}/markets",
    "contract_platforms": "/contracts",
    "contract_platform_addresses": "/contracts/{}",
    "search": "/search",
}


class Client:
    BASE_URL = "https://api.coinpaprika.com/v1"

    def __init__(self):
        self.header = {"Accept": "application/json", "User-Agent": "moonbag"}
        self.s = requests.Session()
        self.s.mount(self.BASE_URL, HTTPAdapter(max_retries=5))

    @retry(tries=2, max_delay=5)
    def _make_request(self, endpoint, payload=None, **kwargs):
        url = self.BASE_URL + endpoint
        if payload is None:
            payload = {}
        if kwargs:
            payload.update(kwargs)
        return requests.get(url, params=payload).json()

    def _get_global_market(self):
        return self._make_request(ENDPOINTS["global"])

    def _get_coins(self):
        return self._make_request(ENDPOINTS["coins"])

    def _get_coin_twitter_timeline(self, coin_id="eth-ethereum"):
        return self._make_request(ENDPOINTS["coin_tweeter"].format(coin_id))

    def _get_coin_events_by_id(self, coin_id="eth-ethereum"):
        return self._make_request(ENDPOINTS["coin_events"].format(coin_id))

    def _get_coin_exchanges_by_id(self, coin_id="eth-ethereum"):
        return self._make_request(ENDPOINTS["coin_exchanges"].format(coin_id))

    def _get_coin_markets_by_id(self, coin_id="eth-ethereum", quotes="USD,BTC"):
        return self._make_request(
            ENDPOINTS["coin_markets"].format(coin_id), quotes=quotes
        )

    def _get_ohlc_last_day(self, coin_id="eth-ethereum", quotes="USD"):
        """ "string Default: "usd"
        returned data quote (available values: usd btc)"""
        return self._make_request(ENDPOINTS["ohlcv"].format(coin_id), quotes=quotes)

    def _get_ohlc_historical(
        self, coin_id="eth-ethereum", quotes="USD", start=None, end=None
    ):
        if end is None:
            end = datetime.datetime.now().strftime("%Y-%m-%d")

        if start is None:
            start = (datetime.datetime.now() - datetime.timedelta(days=365)).strftime(
                "%Y-%m-%d"
            )
        """"string Default: "usd"
        returned data quote (available values: usd btc)"""
        return self._make_request(
            ENDPOINTS["ohlcv_hist"].format(coin_id), quotes=quotes, start=start, end=end
        )

    def _get_people(self, person_id="vitalik-buterin"):
        return self._make_request(ENDPOINTS["people"].format(person_id))

    def _get_tickers_for_all_coins(self, quotes="USD,BTC"):
        return self._make_request(ENDPOINTS["tickers"], quotes=quotes)

    def _get_tickers_for_coin(self, coin_id="btc-bitcoin", quotes="USD,BTC"):
        return self._make_request(
            ENDPOINTS["ticker_info"].format(coin_id), quotes=quotes
        )

    def _get_exchanges(self, quotes="USD,BTC"):
        return self._make_request(ENDPOINTS["exchanges"], quotes=quotes)

    def _get_exchange_by_id(self, exchange_id="binance", quotes="USD,BTC"):
        return self._make_request(
            ENDPOINTS["exchange_info"].format(exchange_id), quotes=quotes
        )

    def _get_exchange_markets(self, exchange_id="binance", quotes="USD,BTC"):
        return self._make_request(
            ENDPOINTS["exchange_markets"].format(exchange_id), quotes=quotes
        )

    def _search(self, q, c=None, modifier=None):
        """
        q:  phrase for search

        c:  one or more categories (comma separated) to search.
            Available options: currencies|exchanges|icos|people|tags
            Default: currencies,exchanges,icos,people,tags

        modifier: set modifier for search results.
        Available options: symbol_search - search only by symbol (works for currencies only)
        """
        if c is None:
            c = "currencies,exchanges,icos,people,tags"
        return self._make_request(
            ENDPOINTS["search"], q=q, c=c, modifier=modifier, limit=100
        )

    def _get_all_contract_platforms(
        self,
    ):
        return self._make_request(ENDPOINTS["contract_platforms"])

    def _get_contract_platforms(self, platform_id="eth_ethereum"):
        return self._make_request(
            ENDPOINTS["contract_platform_addresses"].format(platform_id)
        )
