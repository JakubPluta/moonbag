from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dataclasses import dataclass


class RestConfig:
    _BASE_URL: str
    _RETRY_STRATEGY: Retry
    _ADAPTER: HTTPAdapter

    @classmethod
    def from_dct(cls, dct):
        return cls()

    @property
    def adapter(self):
        return self._ADAPTER

    @adapter.setter
    def adapter(self, adapter: HTTPAdapter):
        self._ADAPTER = adapter

    @property
    def retry_strategy(self):
        return self._RETRY_STRATEGY

    @retry_strategy.setter
    def retry_strategy(self, strategy: Retry):
        self._RETRY_STRATEGY = strategy

    @property
    def base_url(self):
        return self._BASE_URL

    @base_url.setter
    def base_url(self, base_url):
        self._BASE_URL = base_url


class GeckoConfig(RestConfig):
    _BASE_URL: str = 'https://api.coingecko.com/api/v3/'
    _RETRY_STRATEGY: Retry = Retry(total=3, status_forcelist=[429, 500, 502, 503, 504],
                                   method_whitelist=["HEAD", "GET", "OPTIONS"])
    _ADAPTER: HTTPAdapter = HTTPAdapter(max_retries=_RETRY_STRATEGY)