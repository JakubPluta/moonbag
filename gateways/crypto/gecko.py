# https://www.coingecko.com/en/api
import json
import requests
from gateways.crypto.configs import RestConfig
from gateways.crypto.configs import GeckoConfig


class GeckoClient:

    def __init__(self, config: RestConfig = GeckoConfig):
        self.config = config
        self.url = self.config.BASE_URL

        self.session = requests.Session()
        self.session.mount('http://', config.ADAPTER)

    def _build_url(self, endpoint):
        pass

    def _make_request(self, url):
        try:
            response = self.session.get(url)
            response.raise_for_status()
            content = json.loads(response.content.decode('utf-8'))

            print(content)
            return content
        except Exception as e:
            print(e)

    def ping(self):
        return self._make_request(self.url + '/ping')

g  = GeckoClient()
g.ping()
g.configuration