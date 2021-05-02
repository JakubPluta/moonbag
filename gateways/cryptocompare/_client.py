import pandas as pd
import numpy as np
import requests
# https://github.com/CryptoCompareLTD/api-guides/tree/master/python

API_KEY = 'cee09c0bb9f3ecba3390beefe5c7b2bb4d0412be908b22b67a9a3e1664e91fda'

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
    "EXCHANGE_TOP_SYMBOLS": "/data/exchange/top/volume",
    "ALL_COINS_LIST": "/data/all/coinlist",
    "LATEST_COIN_SOCIAL_STATS": "/data/social/coin/latest",
    "SOCIAL_STATS": "https://www.cryptocompare.com/api/data/socialstats",
    "NEWS": "/data/v2/news/",
    "WALLETS": "/data/wallets/general",
    "GAMBLING": "/data/gambling/general",
    "MINING_CONTRACTS": "/data/mining/contracts/general",
    "MINING_COMPANIES": "/data/mining/companies/general",
    "RECOMMENDED": "/data/recommended/all",
    "FEEDS": "/data/news/feeds",
    "FEEDS_CATEGORIES": "data/news/feedsandcategories",
}


class CryptoCompare:
    BASE_URL = "https://min-api.cryptocompare.com"
    KEYS = [
        "fsym",
        "fsyms",
        "tsym",
        "tsyms",
        "ts",
        "e",
        "limit",
        "markets",
        "extraParams",
        "sign",
        "tots",
        "toTs",
        "tryConversion",
        "calculationType",
        "coinId",
        "id",
    ]

    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def _validate_params(**kwargs):
        for k, v in [kwargs.items()]:
            if v in [None, np.nan, False, ""]:
                raise ValueError(f"Enter Key")
        return True

    @staticmethod
    def _get_data(url):
        try:
            response = requests.get(url).json()
        except Exception as e:
            print(f"Error ---> {e}")
            return None
        if isinstance(response, list):
            if response[0].get("Response") == "Error":
                print(response[0].get("Message"))
                return None
        else:
            if response.get("Response") == "Error":
                print(response.get("Message"))
                return None
        return response

    def _build_request(self, kwargs):
        """
        :param kwargs:
            fsym: The cryptocurrency symbol of interest ex: BTC
            tsyms: Comma separated cryptocurrency symbols list to convert into ex: USD,JPY,EUR
        :return: response json
        """
        query, fsym, tsym = "?", "", ""
        if kwargs is not None and isinstance(kwargs, dict):
            for key, value in list(kwargs.items()):
                if key in ["fsym", "fsyms"]:
                    fsym = value
                elif key in ["tsym", "tsyms"]:
                    tsym = value

                if key in self.KEYS:
                    query = "{}&{}".format(query, "{}={}".format(key, value))

        return fsym, tsym, query + "&apikey=" + self.api_key

    def get_price(self, **kwargs):
        """
        ENDPOINT: "/data/price"
        Get the current price of any cryptocurrency in any other currency that you need.
        If the crypto does not trade directly into the toSymbol requested,
        BTC will be used for conversion. If the opposite pair trades we invert it (eg.: BTC-XMR)
        :param
                fsym -> Cryptocurrency symbol: BTC or fsyms > fsym -> Cryptocurrency symbols : "BTC,ETH"
                tsyms -> "USD,JPY,EUR": FIAT currency
        :return response
        """
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)

        if isinstance(fsym.split(","), list):
            url = self.BASE_URL + ENDPOINTS["PRICE_MULTI"]
        else:
            url = self.BASE_URL + ENDPOINTS["PRICE_SINGLE"]
        return self._get_data(url + query)

    def get_price_full_data(self, **kwargs):
        """ /data/pricemultifull
        ENDPOINT: "/data/pricemultifull",
        Get all the current trading info (price, vol, open, high, low etc) of any list of cryptocurrencies
        in any other currency that you need. If the crypto does not trade directly into the toSymbol requested,
        BTC will be used for conversion.
        This API also returns Display values for all the fields. If the opposite pair trades we invert it (eg.: BTC-XMR)
        :param
                fsyms > fsym -> Cryptocurrency symbols : "BTC,ETH"
                tsyms -> "USD,JPY,EUR": FIAT currency
        :return response
        """
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = self.BASE_URL + ENDPOINTS["PRICE_MULTI_FULL"]
        return self._get_data(url + query)


    def get_top_list_by_market_cap(self, **kwargs):
        "https://min-api.cryptocompare.com/data/top/mktcapfull?tsym=USD&page=2"
        "tsym=USD"
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)

        url = self.BASE_URL + ENDPOINTS["TOP_BY_MARKET_CAP"]
        return self._get_data(url + query)

    def get_top_exchanges(self, **kwargs):
        "https://min-api.cryptocompare.com/data/top/exchanges/full?fsym=ETH&tsym=USD"
        "tsym=USD"
        "fsym=BTC"

        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)

        url = self.BASE_URL + ENDPOINTS["TOP_EXCHANGES_FULL_DATA"]
        return self._get_data(url + query)

    def exchanges_top_symbols_by_volume(self, **kwargs):
        "/data/exchange/top/volume?e=Binance&direction=TO"
        "e=Kraken"
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = self.BASE_URL + ENDPOINTS["EXCHANGE_TOP_SYMBOLS"]
        return self._get_data(url + query)

    def get_historical_day_price(self, **kwargs):
        "HISTO_DAY"
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = self.BASE_URL + ENDPOINTS["HISTO_DAY"]
        return self._get_data(url + query)

    def get_historical_hour_price(self, **kwargs):
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = self.BASE_URL + ENDPOINTS["HISTO_HOUR"]
        return self._get_data(url + query)

    def get_historical_minute_price(self, **kwargs):
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = self.BASE_URL + ENDPOINTS["HISTO_MINUTE"]
        return self._get_data(url + query)

    def get_all_coins_list(self):
        return self._get_data(self.BASE_URL + ENDPOINTS["ALL_COINS_LIST"])

    def latest_social_coin_stats(self, **kwargs):
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = self.BASE_URL + ENDPOINTS["LATEST_COIN_SOCIAL_STATS"]
        return self._get_data(url + query)

    def social_stats(self, **kwargs):
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = ENDPOINTS["SOCIAL_STATS"]
        return self._get_data(url + query)

    def get_latest_news(self, **kwargs):
        # https://min-api.cryptocompare.com/data/v2/news/?lang=EN
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = self.BASE_URL + ENDPOINTS["NEWS"]
        return self._get_data(url + query)

    def get_news_feeds_and_categories(self, **kwargs):
        fsym, tsyms, query = self._build_request(kwargs)
        self._validate_params(fsym=fsym, tsyms=tsyms)
        url = self.BASE_URL + ENDPOINTS["FEEDS_CATEGORIES"]
        return self._get_data(url + query)

from pprint import pprint
compare = CryptoCompare(API_KEY)
coins = compare.get_top_list_by_market_cap(tsym='usd')
pprint(coins)