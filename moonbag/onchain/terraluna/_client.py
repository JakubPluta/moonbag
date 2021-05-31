import requests
from retry import retry
from requests.adapters import HTTPAdapter


class TerraClient:
    BASE_URL = 'https://fcd.terra.dev/'

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

    def _get_tx(self, address):
        return self._make_request(
            f'txs/{address}'
        )

    def _get_account(self, address):
        return self._make_request(f'auth/accounts/{address}')

    def _get_staking_info(self):
        return self._make_request('staking/pool')

    def _get_coins_supply(self):
        return self._make_request('supply/total')

    def _get_all_validators(self):
        return self._make_request('staking/validators')
