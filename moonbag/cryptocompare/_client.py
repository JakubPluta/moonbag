import os
import requests
from dotenv import load_dotenv
import cachetools.func
from retry import retry


load_dotenv()

API_KEY = os.getenv("CC_API_KEY")

ENDPOINTS = {
    "PRICE_MULTI_FULL": "/data/pricemultifull",
    "GENERATE_AVERAGE": "/data/generateAvg",
    "HISTO_DAY": "/data/histoday",
    "HISTO_HOUR": "/data/histohour",
    "HISTO_MINUTE": "/data/histominute",
    "TOP_LIST_24": "/data/top/totalvolfull",
    "TOP_LIST_24_FULL": "/data/top/totaltoptiervolfull",
    "TOP_BY_MARKET_CAP": "/data/top/mktcapfull",
    "TOP_EXCHANGES_FULL_DATA": "/data/top/exchanges/full",
    "TOP_LIST_PAIR_VOLUME": "/data/top/volumes",
    "TOP_LIST_OF_PAIRS": "/data/top/pairs",
    "EXCHANGE_TOP_SYMBOLS": "/data/exchange/top/volume",
    "ALL_COINS_LIST": "/data/all/coinlist",
    "LATEST_COIN_SOCIAL_STATS": "/data/social/coin/latest",
    "HISTO_DAY_SOCIAL_STATS": "/data/social/coin/histo/day",
    "DAILY_EXCHANGE_VOLUME": "/data/exchange/histoday",
    "HOURLY_EXCHANGE_VOLUME": "/data/exchange/histohour",
    "DAILY_SYMBOL_VOLUME": "/data/symbol/histoday",
    "HOURLY_SYMBOL_VOLUME": "/data/symbol/histohour",
    "LATEST_BLOCKCHAIN_DATA": "/data/blockchain/latest",
    "HISTO_BLOCKCHAIN_DATA": "/data/blockchain/histo/day",
    "TRADING_SIGNALS": "/data/tradingsignals/intotheblock/latest",
    "EXCHANGES_ORDER_BOOK": "/data/ob/exchanges",
    "ORDER_BOOK_L1_TOP": "/data/ob/l1/top",
    "ORDER_BOOK_L2_SNAPSHOT": "/data/v2/ob/l2/snapshot",
    "NEWS": "/data/v2/news/",
    "WALLETS": "/data/wallets/general",
    "GAMBLING": "/data/gambling/general",
    "MINING_CONTRACTS": "/data/mining/contracts/general",
    "MINING_COMPANIES": "/data/mining/companies/general",
    "RECOMMENDED": "/data/recommended/all",
    "FEEDS": "/data/news/feeds",
    "BLOCKCHAIN_COINS": "/data/blockchain/list",
    "EXCHANGES_PAIRS": "/data/v4/all/exchanges",
    "EXCHANGES_INFO": "/data/exchanges/general",
}


class CryptoCompareClient:
    BASE_URL = "https://min-api.cryptocompare.com"
    COMPARE_URL = "https://www.cryptocompare.com"

    def __init__(self, api_key):
        self.api_key = api_key

    @retry(tries=2, delay=3, max_delay=5)
    def _make_request(self, endpoint, payload=None, **kwargs):
        """You can use either endpoint key or endpoint value from dictionary ENDPOINTS
        All of request will be handled"""

        if endpoint in ENDPOINTS:
            endpoint_path = ENDPOINTS.get(endpoint)
        elif endpoint in list(ENDPOINTS.values()):
            endpoint_path = endpoint
        else:
            raise ValueError(
                f"Wrong endpoint\nPlease Use one from List {list(ENDPOINTS.keys())}"
            )
        url = self.BASE_URL + endpoint_path
        if payload is None:
            payload = {}
        if kwargs:
            payload.update(kwargs)
        headers = {"authorization": "Apikey " + self.api_key}
        req = requests.get(url, params=payload, headers=headers)
        return req.json()

    def _get_price(self, symbol="BTC", currency="USD", **kwargs):
        """Full data"""
        endpoint = ENDPOINTS["PRICE_MULTI_FULL"]
        payload = {
            "fsyms": symbol,
            "tsyms": currency,
            "relaxedValidation": "false",
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_top_list_by_market_cap(self, currency="USD", limit=100, **kwargs):
        endpoint = ENDPOINTS["TOP_BY_MARKET_CAP"]
        payload = {"tsym": currency, "limit": limit}
        return self._make_request(endpoint, payload, **kwargs)

    def _get_top_exchanges(self, symbol="BTC", currency="USD", limit=100, **kwargs):
        endpoint = ENDPOINTS["TOP_EXCHANGES_FULL_DATA"]
        payload = {
            "fsym": symbol,
            "tsym": currency,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_exchanges_top_symbols_by_volume(
        self, exchange="Binance", limit=100,**kwargs
    ):
        "/data/exchange/top/volume?e=Binance&direction=TO"
        "e=Kraken"
        endpoint = ENDPOINTS["EXCHANGE_TOP_SYMBOLS"]
        payload = {
            "e": exchange.capitalize(),
            "limit": limit,
            'direction' : 'TO'
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_top_list_by_pair_volume(self, currency="USD", limit=100, **kwargs):
        endpoint = ENDPOINTS["TOP_LIST_PAIR_VOLUME"]
        payload = {
            "tsym": currency,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_top_of_trading_pairs(self, symbol="ETH", limit=50, **kwargs):
        endpoint = ENDPOINTS["TOP_LIST_OF_PAIRS"]
        payload = {
            "fsym": symbol,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    # TODO --> Add mappings that use can use either coinId, symbol, or name for requests
    def _get_latest_social_coin_stats(self, coin_id=7605, **kwargs):
        endpoint = ENDPOINTS["LATEST_COIN_SOCIAL_STATS"]
        payload = {"coinId": int(coin_id)}
        return self._make_request(endpoint, payload, **kwargs)

    def _get_historical_social_stats(
        self, coin_id=7605, limit=2000, aggregate=1, **kwargs
    ):
        endpoint = ENDPOINTS["HISTO_DAY_SOCIAL_STATS"]
        payload = {
            "coinId": int(coin_id),
            "limit": limit,
            "aggregate": aggregate,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_latest_news(self, lang="EN", sort_order="latest", **kwargs):
        endpoint = ENDPOINTS["NEWS"]
        payload = {"lang": lang, "sortOrder": sort_order}
        return self._make_request(endpoint, payload, **kwargs)

    def _get_blockchain_available_coins_list(self):
        endpoint = ENDPOINTS["BLOCKCHAIN_COINS"]
        return self._make_request(endpoint=endpoint)

    def _get_all_coins_list(self, summary="true", **kwargs):
        endpoint = ENDPOINTS["ALL_COINS_LIST"]
        if isinstance(summary, bool):
            summary = str(summary).lower()

        payload = {"summary": summary}
        return self._make_request(endpoint, payload, **kwargs)

    def _get_historical_day_prices(
        self, symbol="BTC", currency="USD", limit=2000, **kwargs
    ):
        endpoint = ENDPOINTS["HISTO_DAY"]
        payload = {
            "fsym": symbol,
            "tsym": currency,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_historical_hour_prices(
        self, symbol="BTC", currency="USD", limit=2000, **kwargs
    ):
        endpoint = ENDPOINTS["HISTO_HOUR"]
        payload = {
            "fsym": symbol,
            "tsym": currency,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_historical_minutes_prices(
        self, symbol="BTC", currency="USD", limit=2000, **kwargs
    ):
        endpoint = ENDPOINTS["HISTO_MINUTE"]
        payload = {
            "fsym": symbol,
            "tsym": currency,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_daily_exchange_volume(
        self, currency="USD", exchange="CCCAGG", limit=365, **kwargs
    ):
        """The CCCAGG is calculated for each crypto coin in each currency it is trading in (example: CCCAGG BTC-USD)
        See more: https://www.cryptocompare.com/media/12318004/cccagg.pdf
        """
        endpoint = ENDPOINTS["DAILY_EXCHANGE_VOLUME"]
        payload = {
            "tsym": currency,
            "e": exchange,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_hourly_exchange_volume(
        self, currency="USD", exchange="CCCAGG", limit=60 * 24, **kwargs
    ):
        """The CCCAGG is calculated for each crypto coin in each currency it is trading in (example: CCCAGG BTC-USD)
        See more: https://www.cryptocompare.com/media/12318004/cccagg.pdf
        """
        endpoint = ENDPOINTS["HOURLY_EXCHANGE_VOLUME"]
        payload = {
            "tsym": currency,
            "e": exchange,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_daily_symbol_volume(
        self, symbol="BTC", currency="USD", limit=365, **kwargs
    ):
        endpoint = ENDPOINTS["DAILY_SYMBOL_VOLUME"]
        payload = {
            "fsym": symbol,
            "tsym": currency,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_hourly_symbol_volume(
        self, symbol="BTC", currency="USD", limit=60 * 24, **kwargs
    ):
        endpoint = ENDPOINTS["HOURLY_SYMBOL_VOLUME"]
        payload = {
            "fsym": symbol,
            "tsym": currency,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_latest_blockchain_data(self, symbol="BTC", **kwargs):
        endpoint = ENDPOINTS["LATEST_BLOCKCHAIN_DATA"]
        payload = {
            "fsym": symbol,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_historical_blockchain_data(self, symbol="BTC", limit=365, **kwargs):
        endpoint = ENDPOINTS["HISTO_BLOCKCHAIN_DATA"]
        payload = {
            "fsym": symbol,
            "limit": limit,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_latest_trading_signals(self, symbol="BTC", **kwargs):
        endpoint = ENDPOINTS["TRADING_SIGNALS"]
        payload = {
            "fsym": symbol,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_order_books_exchanges(self, **kwargs):
        endpoint = ENDPOINTS["EXCHANGES_ORDER_BOOK"]
        return self._make_request(endpoint, {}, **kwargs)

    def _get_order_book_top(
        self, symbol="ETH", to_symbol="BTC", exchange="binance", **kwargs
    ):
        """Returns latest order book Level 1 bid/ask values
        for the requested exchange and pairs in both raw and display formats"""
        endpoint = ENDPOINTS["ORDER_BOOK_L1_TOP"]
        payload = {
            "fsyms": symbol,
            "tsyms": to_symbol,
            "e": exchange,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_order_book_snapshot(
        self, symbol="ETH", to_symbol="BTC", exchange="binance", **kwargs
    ):
        """Returns latest order book Level 2 data snapshot for the requested exchang"""
        endpoint = ENDPOINTS["ORDER_BOOK_L2_SNAPSHOT"]
        payload = {
            "fsyms": symbol,
            "tsyms": to_symbol,
            "e": exchange,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_all_exchanges_and_trading_pairs(
        self, symbol=None, exchange=None, top_tier="false", **kwargs
    ):
        endpoint = ENDPOINTS["EXCHANGES_PAIRS"]
        payload = {
            "fsym": symbol,
            "e": exchange,
            "topTier": top_tier,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_all_exchanges_info(self, symbol="BTC", **kwargs):
        endpoint = ENDPOINTS["EXCHANGES_INFO"]
        payload = {
            "tsym": symbol,
        }
        return self._make_request(endpoint, payload, **kwargs)

    def _get_all_wallet_info(self, **kwargs):
        endpoint = ENDPOINTS["WALLETS"]
        payload = {}
        return self._make_request(endpoint, payload, **kwargs)

    def _get_all_gambling_info(self, **kwargs):
        endpoint = ENDPOINTS["GAMBLING"]
        payload = {}
        return self._make_request(endpoint, payload, **kwargs)

    def _get_recommendations(self, symbol="BTC", **kwargs):
        """Returns general info about our recommended entities.
            * wallets,
            * gambling
            * mining companies
            * exchanges
        """
        endpoint = ENDPOINTS["RECOMMENDED"]
        payload = {"tsym": symbol}
        return self._make_request(endpoint, payload, **kwargs)
