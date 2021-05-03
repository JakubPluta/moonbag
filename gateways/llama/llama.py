import requests
import pandas as pd

# TODO Write cron job, that pass all protocols to local database - > Use Mongo/Redis


class LLama:
    URL = "https://api.llama.fi/"
    ENDPOINTS = {"protocols": "protocols", "protocol": "protocol/"}

    def __init__(self):
        self._symbols = {
            s.get("name").rstrip(): s.get("id") for s in self.get_protocols()
        }

    def get_protocols(self, df=False):
        resp = requests.get(self.URL + self.ENDPOINTS.get("protocols"))
        resp.raise_for_status()
        results = resp.json()
        if not df:
            return results
        return results, pd.DataFrame.from_dict(results)

    @property
    def symbols(self):
        return self._symbols

    def get_protocol(self, protocol: str):
        # https://api.llama.fi/protocol/:name
        if protocol not in self.symbols:
            raise ValueError(
                f"Wrong protocol name\nPlease chose protocol name from list\n{self.symbols}"
            )
        resp = requests.get(
            self.URL + self.ENDPOINTS.get("protocol") + protocol
        )
        resp.raise_for_status()
        return resp.json()


l = LLama()
z, df = l.get_protocols(df=True)
