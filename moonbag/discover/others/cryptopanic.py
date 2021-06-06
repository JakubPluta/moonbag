import time
import pandas as pd
import textwrap
import requests
from requests.adapters import HTTPAdapter
from moonbag.common import print_table
from moonbag.common.keys import CRYPTO_PANIC_API


class CryptoPanic:
    BASE_URL = "https://cryptopanic.com/api/v1"

    def __init__(self):
        self.api_key = CRYPTO_PANIC_API or ""
        self.s = requests.Session()
        self.s.mount(self.BASE_URL, HTTPAdapter(max_retries=5))

    @staticmethod
    def parse_post(post):
        return {
            "published_at": post.get("published_at"),
            "domain": post.get("domain"),
            "title": post.get("title"),
            "negative_votes": post["votes"].get("negative"),
            "positive_votes": post["votes"].get("positive"),
        }

    def _get_posts(self, kind="news"):
        if kind not in ["news", "media"]:
            kind = "news"

        results = []

        url = f"{self.BASE_URL}/posts/?auth_token={self.api_key}" + f"&kind={kind}"
        print(f"Fetching page: 0")
        first_page = requests.get(url).json()

        if first_page == {
            "status": "Incomplete",
            "info": "Missing auth_token parameter",
        }:
            print(first_page)
            return None

        data, next_page = first_page["results"], first_page.get("next")

        for post in data:
            results.append(self.parse_post(post))

        counter = 0
        while next_page:
            counter += 1
            print(f"Fetching page: {counter}")
            try:
                time.sleep(0.1)
                res = requests.get(next_page).json()
                for post in res["results"]:
                    results.append(self.parse_post(post))
                next_page = res.get("next")
            except Exception as e:
                print(e)

        return results

    def get_posts(self, kind="news"):
        """kind: news or media"""
        pst = self._get_posts(kind)
        if not pst:
            print(
                "You need to provide API Key to use this feature. \nPlease visit https://cryptopanic.com/developers/api/ and get your API KEY"
            )
        df = pd.DataFrame(pst)
        df["title"] = df["title"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=66)) if isinstance(x, str) else x
        )
        return df
