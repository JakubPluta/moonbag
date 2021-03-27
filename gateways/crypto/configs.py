from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from dataclasses import dataclass


class RestConfig:
    BASE_URL: str
    RETRY_STRATEGY: Retry
    ADAPTER: HTTPAdapter

    @classmethod
    def from_dct(cls, dct):
        return cls()


class GeckoConfig(RestConfig):
    BASE_URL: str = 'https://api.coingecko.com/api/v3/'
    RETRY_STRATEGY: Retry = Retry(total=3, status_forcelist=[429, 500, 502, 503, 504],
                                   method_whitelist=["HEAD", "GET", "OPTIONS"])
    ADAPTER: HTTPAdapter = HTTPAdapter(max_retries=RETRY_STRATEGY)