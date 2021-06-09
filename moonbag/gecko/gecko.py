import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pycoingecko import CoinGeckoAPI
import cachetools.func
from retry import retry
import math
import textwrap
from moonbag.common.utils import wrap_text_in_df, underscores_to_newline_replace
from moonbag.gecko.utils import (
    changes_parser,
    replace_qm,
    clean_row,
    collateral_auditors_parse,
    swap_columns,
    remove_keys,
    filter_list,
    find_discord,
    rename_columns_in_dct,
    create_dictionary_with_prefixes,
)
import logging

logger = logging.getLogger("gecko")


PERIODS = {
    "1h": "?time=h1",
    "1d": "?time=h24",
    "7d": "?time=d7",
    "14d": "?time=d14",
    "30d": "?time=d30",
    "60d": "?time=d60",
    "1y": "?time=y1",
}

CATEGORIES = {
    "trending": 0,
    "most_voted": 1,
    "positive_sentiment": 2,
    "recently_added": 3,
    "most_visited": 4,
}


COLUMNS = {
    "id": "id",
    "rank": "rank",
    "name": "name",
    "symbol": "symbol",
    "price": "price",
    "change_1h": "change_1h",
    "change_24h": "change_24h",
    "change_7d": "change_7d",
    "volume_24h": "volume_24h",
    "market_cap": "market_cap",
    "country": "country",
    "total_market_cap": "total_market_cap",
    "total_volume": "total_volume",
    "market_cap_percentage": "market_cap_percentage",
    "company": "company",
    "ticker": "ticker",
    "last_added": "last_added",
    "title": "title",
    "author": "author",
    "posted": "posted",
    "article": "article",
    "url": "url",
}

CHANNELS = {
    "telegram_channel_identifier": "telegram",
    "twitter_screen_name": "twitter",
    "subreddit_url": "subreddit",
    "bitcointalk_thread_identifier": "bitcointalk",
    "facebook_username": "facebook",
    "discord": "discord",
}

BASE_INFO = [
    "id",
    "name",
    "symbol",
    "asset_platform_id",
    "description",
    "contract_address",
    "market_cap_rank",
    "public_interest_score",
]

DENOMINATION = ("usd", "btc", "eth")


def get_coin_list():
    coins = CoinGeckoAPI().get_coins_list()
    df = pd.DataFrame(coins)
    return df


class Overview:
    BASE = "https://www.coingecko.com"

    def __init__(self):
        self.client = CoinGeckoAPI()

    @staticmethod
    @cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
    def gecko_scraper(url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, features="lxml")
        return soup

    @staticmethod
    @cachetools.func.ttl_cache(maxsize=128, ttl=10 * 60)
    def get_btc_price():
        req = requests.get(
            "https://api.coingecko.com/api/v3/simple/"
            "price?ids=bitcoin&vs_currencies=usd&include_market_cap"
            "=false&include_24hr_vol"
            "=false&include_24hr_change=false&include_last_updated_at=false"
        )
        return req.json()["bitcoin"]["usd"]

    def _discover_coins(self, category="trending"):
        if category not in CATEGORIES:
            raise ValueError(
                f"Wrong category name\nPlease chose one from list: {CATEGORIES.keys()}"
            )

        self.BASE = "https://www.coingecko.com"
        url = "https://www.coingecko.com/en/discover"
        popular = self.gecko_scraper(url).find_all(
            "div", class_="col-12 col-sm-6 col-md-6 col-lg-4"
        )[CATEGORIES[category]]
        rows = popular.find_all("a")
        results = []

        btc_price = self.get_btc_price()

        for row in rows:
            name, *_, price = clean_row(row)
            url = self.BASE + row["href"]
            if price.startswith("BTC"):
                price = price.replace("BTC", "").replace(",", ".")

            price_usd = (int(btc_price) * float(price)) if btc_price else None
            results.append([name, price, price_usd, url])
        return pd.DataFrame(
            results,
            columns=[
                COLUMNS["name"],
                "price btc",
                "price_usd",
                COLUMNS["url"],
            ],
        )

    def _get_news(self, page=1):
        url = f"https://www.coingecko.com/en/news?page={page}"
        rows = self.gecko_scraper(url).find_all(COLUMNS["article"])
        results = []
        for row in rows:
            header = row.find("header")
            link = header.find("a")["href"]
            text = [t for t in header.text.strip().split("\n") if t not in ["", " "]]
            article = row.find("div", class_="post-body").text.strip()
            title, *by_who = text
            author, posted = " ".join(by_who).split("(")
            posted = posted.strip().replace(")", "")
            results.append([title, author.strip(), posted, article, link])
        return pd.DataFrame(
            results,
            columns=[
                COLUMNS["title"],
                COLUMNS["author"],
                COLUMNS["posted"],
                COLUMNS["article"],
                COLUMNS["url"],
            ],
        )

    def _get_holdings_overview(self, endpoint="bitcoin"):
        url = "https://www.coingecko.com/en/public-companies-" + endpoint
        soup = self.gecko_scraper(url)
        rows = soup.find_all("span", class_="overview-box d-inline-block p-3 mr-2")
        kpis = {}
        for row in rows:
            row_cleaned = clean_row(row)
            if row_cleaned:
                value, *kpi = row_cleaned
                name = " ".join(kpi)
                kpis[name] = value
        return kpis

    def _get_companies_assets(self, endpoint="bitcoin"):
        url = "https://www.coingecko.com/en/public-companies-" + endpoint
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            link = row.find("a")["href"]
            row_cleaned = clean_row(row)
            row_cleaned.append(link)
            results.append(row_cleaned)
        return pd.DataFrame(
            results,
            columns=[
                COLUMNS["rank"],
                COLUMNS["company"],
                COLUMNS["ticker"],
                COLUMNS["country"],
                "total_btc",
                "entry_value",
                "today_value",
                "pct_of_supply",
                COLUMNS["url"],
            ],
        ).set_index(COLUMNS["rank"])

    def _get_gainers_and_losers(self, period="1h", typ="gainers"):
        category = {
            "gainers": 0,
            "losers": 1,
        }

        if period not in PERIODS:
            raise ValueError(
                f"Wrong time period\nPlease chose one from list: {PERIODS.keys()}"
            )

        url = f"https://www.coingecko.com/en/coins/trending{PERIODS.get(period)}"
        rows = (
            self.gecko_scraper(url).find_all("tbody")[category.get(typ)].find_all("tr")
        )
        results = []
        for row in rows:
            url = self.BASE + row.find("a")["href"]
            symbol, name, *_, volume, price, change = clean_row(row)
            results.append([symbol, name, volume, price, change, url])
        return pd.DataFrame(
            results,
            columns=[
                COLUMNS["symbol"],
                COLUMNS["name"],
                "volume",
                COLUMNS["price"],
                f"change_{period}",
                COLUMNS["url"],
            ],
        )

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_crypto_categories(self, n=None):
        columns = [
            COLUMNS["rank"],
            COLUMNS["name"],
            COLUMNS["change_1h"],
            COLUMNS["change_24h"],
            COLUMNS["change_7d"],
            COLUMNS["market_cap"],
            COLUMNS["volume_24h"],
            "n_of_coins",
            COLUMNS["url"],
        ]
        url = "https://www.coingecko.com/en/categories"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []

        for row in rows:
            url = self.BASE + row.find("a")["href"]
            (
                rank,
                *names,
                change_1h,
                change_24h,
                change_7d,
                mcap,
                volume,
                n_of_coins,
            ) = row.text.strip().split()
            results.append(
                [
                    rank,
                    " ".join(names),
                    change_1h,
                    change_24h,
                    change_7d,
                    mcap,
                    volume,
                    n_of_coins,
                    url,
                ]
            )

        return pd.DataFrame(results, columns=columns).set_index(COLUMNS["rank"]).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_recently_added_coins(self, n=None):
        columns = [
            COLUMNS["name"],
            COLUMNS["symbol"],
            COLUMNS["price"],
            COLUMNS["change_1h"],
            COLUMNS["change_24h"],
            COLUMNS["volume_24h"],
            COLUMNS["market_cap"],
            COLUMNS["last_added"],
            COLUMNS["url"],
        ]

        url = "https://www.coingecko.com/en/coins/recently_added"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []

        for row in rows:
            url = self.BASE + row.find("a")["href"]

            row_cleaned = clean_row(row)
            (
                name,
                symbol,
                _,
                price,
                *changes,
                mcpa,
                volume,
                last_added,
            ) = row_cleaned
            change_1h, change_24h, _ = changes_parser(changes)
            results.append(
                [
                    name,
                    symbol,
                    price,
                    change_1h,
                    change_24h,
                    mcpa,
                    volume,
                    last_added,
                    url,
                ]
            )
        return replace_qm(pd.DataFrame(results, columns=columns)).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_stable_coins(self, n=None):
        columns = [
            COLUMNS["rank"],
            COLUMNS["name"],
            COLUMNS["symbol"],
            COLUMNS["price"],
            COLUMNS["change_24h"],
            "exchanges",
            COLUMNS["market_cap"],
            "change_30d",
            "link",
        ]
        url = "https://www.coingecko.com/en/stablecoins"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            link = self.BASE + row.find("a")["href"]
            row_cleaned = clean_row(row)
            if len(row_cleaned) == 8:
                row_cleaned.append(None)

            (
                rank,
                name,
                *symbols,
                price,
                volume_24h,
                exchanges,
                market_cap,
                change_30d,
            ) = row_cleaned
            symbol = symbols[0] if symbols else symbols
            results.append(
                [
                    rank,
                    name,
                    symbol,
                    price,
                    volume_24h,
                    exchanges,
                    market_cap,
                    change_30d,
                    link,
                ]
            )
        return replace_qm(
            pd.DataFrame(results, columns=columns).set_index("rank")
        ).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_yield_farms(self, n=None):
        columns = [
            COLUMNS["rank"],
            COLUMNS["name"],
            "pool",
            "audits",
            "collateral",
            "value locked",
            "returns_year",
            "returns_hour",
        ]
        url = "https://www.coingecko.com/en/yield-farming"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            row_cleaned = clean_row(row)[:-2]
            if len(row_cleaned) == 7:
                row_cleaned.insert(2, None)
            (
                rank,
                name,
                pool,
                *others,
                _,
                value_locked,
                apy1,
                apy2,
            ) = row_cleaned
            auditors, collateral = collateral_auditors_parse(others)
            auditors = ", ".join([aud.strip() for aud in auditors])
            collateral = ", ".join([coll.strip() for coll in collateral])
            results.append(
                [
                    rank,
                    name,
                    pool,
                    auditors,
                    collateral,
                    value_locked,
                    apy1,
                    apy2,
                ]
            )
        return (
            pd.DataFrame(results, columns=columns).set_index("rank").replace({"": None})
        ).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_volume_coins(self, n=None):
        columns = [
            COLUMNS["rank"],
            COLUMNS["name"],
            COLUMNS["symbol"],
            COLUMNS["price"],
            COLUMNS["change_1h"],
            COLUMNS["change_24h"],
            COLUMNS["change_7d"],
            COLUMNS["volume_24h"],
            COLUMNS["market_cap"],
        ]
        url = "https://www.coingecko.com/pl/waluty/high_volume"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            row_cleaned = clean_row(row)
            if len(row_cleaned) == 9:
                row_cleaned.insert(0, "?")
            row_cleaned.pop(3)
            results.append(row_cleaned)
        return pd.DataFrame(results, columns=columns).set_index(COLUMNS["rank"]).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_trending_coins(self, n=None):
        return self._discover_coins("trending").head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_most_voted_coins(self, n=None):
        return self._discover_coins("most_voted").head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_positive_sentiment_coins(self, n=None):
        return self._discover_coins("positive_sentiment").head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_most_visited_coins(self, n=None):
        return self._discover_coins("most_visited").head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_losers(self, period="1h", n=None):
        return self._get_gainers_and_losers(period, typ="losers").head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_gainers(self, period="1h", n=None):
        return self._get_gainers_and_losers(period, typ="gainers").head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_defi_coins(self, n=None):
        url = "https://www.coingecko.com/en/defi"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:

            row_cleaned = clean_row(row)
            row_cleaned.pop(2)
            url = self.BASE + row.find("a")["href"]
            row_cleaned.append(url)
            if len(row_cleaned) == 11:
                row_cleaned.insert(4, "?")
            results.append(row_cleaned)

        df = (
            pd.DataFrame(
                results,
                columns=[
                    COLUMNS["rank"],
                    COLUMNS["name"],
                    COLUMNS["symbol"],
                    COLUMNS["price"],
                    COLUMNS["change_1h"],
                    COLUMNS["change_24h"],
                    COLUMNS["change_7d"],
                    COLUMNS["volume_24h"],
                    COLUMNS["market_cap"],
                    "fully_diluted_market_cap",
                    "market_cap_to_tvl_ratio",
                    COLUMNS["url"],
                ],
            )
            .set_index(COLUMNS["rank"])
            .head(n)
        )
        df.drop(
            ["fully_diluted_market_cap", "market_cap_to_tvl_ratio"],
            axis=1,
            inplace=True,
        )
        df.columns = underscores_to_newline_replace(list(df.columns), 10)
        return df

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_dexes(self, n=None):
        columns = [
            COLUMNS["name"],
            COLUMNS["rank"],
            COLUMNS["volume_24h"],
            "number_of_coins",
            "number_of_pairs",
            "visits",
            "most_traded_pairs",
            "market_share_by_volume",
        ]
        url = "https://www.coingecko.com/en/dex"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            row_cleaned = clean_row(row)
            if " Trading Incentives" in row_cleaned:
                row_cleaned.remove(" Trading Incentives")
            if len(row_cleaned) == 8:
                row_cleaned.insert(-3, "N/A")
            results.append(row_cleaned)
        df = pd.DataFrame(results)
        df[COLUMNS["name"]] = df.iloc[:, 1] + " " + df.iloc[:, 2].replace("N/A", "")
        df.drop(df.columns[1:3], axis=1, inplace=True)
        df = swap_columns(df)
        df.columns = columns
        df["most_traded_pairs"] = (
            df["most_traded_pairs"]
            .apply(lambda x: x.split("$")[0])
            .str.replace(",", "", regex=True)
            .str.replace(".", "", regex=True)
        )
        df["most_traded_pairs"] = df["most_traded_pairs"].apply(
            lambda x: None if x.isdigit() else x
        )
        return df.set_index(COLUMNS["rank"]).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_nfts(self, n=None):
        url = "https://www.coingecko.com/en/nft"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            link = self.BASE + row.find("a")["href"]
            row_cleaned = clean_row(row)
            if len(row_cleaned) == 9:
                row_cleaned.insert(5, "N/A")
            row_cleaned.append(link)
            row_cleaned.pop(3)
            results.append(row_cleaned)
        df = pd.DataFrame(
                results,columns=[
                    COLUMNS["rank"],
                    COLUMNS["name"],
                    COLUMNS["symbol"],
                    COLUMNS["price"],
                    COLUMNS["change_1h"],
                    COLUMNS["change_24h"],
                    COLUMNS["change_7d"],
                    COLUMNS["volume_24h"],
                    COLUMNS["market_cap"],
                    COLUMNS["url"],
                ],
            ).set_index(COLUMNS["rank"]).head(n)
        df = df.applymap(
            lambda x: "\n".join(textwrap.wrap(x, width=55)) if isinstance(x, str) else x
        )
        return df

    @retry(tries=2, delay=3, max_delay=5)
    def get_nft_of_the_day(self, n=None):
        url = "https://www.coingecko.com/en/nft"
        soup = self.gecko_scraper(url)
        row = soup.find("div", class_="tw-px-4 tw-py-5 sm:tw-p-6")
        try:
            *author, description, _ = clean_row(row)
            if len(author) > 3:
                author, description = author[:3], author[3]
        except (ValueError, IndexError):
            return {}
        df = (
            pd.Series(
                {
                    COLUMNS["author"]: " ".join(author),
                    "desc": description,
                    COLUMNS["url"]: self.BASE + row.find("a")["href"],
                    "img": row.find("img")["src"],
                }
            )
            .to_frame()
            .reset_index()
        )
        df.columns = ["Metric", "Value"]
        df = wrap_text_in_df(df, w=100)
        return df.head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_nft_market_status(self, n=None):
        url = "https://www.coingecko.com/en/nft"
        soup = self.gecko_scraper(url)
        rows = soup.find_all("span", class_="overview-box d-inline-block p-3 mr-2")
        kpis = {}
        for row in rows:
            value, *kpi = clean_row(row)
            name = " ".join(kpi)
            kpis[name] = value
        df = pd.Series(kpis).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df.head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_news(self, n=None):
        n_of_pages = (math.ceil(n / 25) + 1) if n else 2
        dfs = []
        for page in range(1, n_of_pages):
            dfs.append(self._get_news(page))
        df = pd.concat(dfs, ignore_index=True).head(n)
        df = wrap_text_in_df(df, w=65)
        df.drop("article", axis=1, inplace=True)
        return df

    @retry(tries=2, delay=3, max_delay=5)
    def get_btc_holdings_public_companies_overview(self, n=None):
        df = pd.Series(self._get_holdings_overview("bitcoin")).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df.head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_eth_holdings_public_companies_overview(self, n=None):
        df = pd.Series(self._get_holdings_overview("ethereum")).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df.head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_companies_with_btc(self, n=None):
        df = self._get_companies_assets("bitcoin").head(n)
        df.drop("url", axis=1, inplace=True)
        return df

    @retry(tries=2, delay=3, max_delay=5)
    def get_companies_with_eth(self, n=None):
        df = self._get_companies_assets("ethereum").head(n)
        df.drop("url", axis=1, inplace=True)  # For now removed url
        return df

    @retry(tries=2, delay=3, max_delay=5)
    def get_coin_list(self, n=None):
        return (
            pd.DataFrame(
                self.client.get_coins_list(),
                columns=[COLUMNS["id"], COLUMNS["symbol"], COLUMNS["name"]],
            )
            .set_index(COLUMNS["id"])
            .head(n)
        )

    @retry(tries=2, delay=3, max_delay=5)
    def get_exchanges(self, n=None):
        df = pd.DataFrame(self.client.get_exchanges_list(per_page=250))
        df.replace({float(np.NaN): None}, inplace=True)
        return (
            df[
                [
                    "trust_score_rank",
                    "trust_score",
                    COLUMNS["id"],
                    COLUMNS["name"],
                    COLUMNS["country"],
                    "year_established",
                    "trade_volume_24h_btc",
                    COLUMNS["url"],
                ]
            ]
            .set_index("trust_score_rank")
            .head(n)
        )

    @retry(tries=2, delay=3, max_delay=5)
    def get_financial_platforms(self, n=None):
        return (
            pd.DataFrame(self.client.get_finance_platforms())
            .set_index(COLUMNS["name"])
            .head(n)
        )

    @retry(tries=2, delay=3, max_delay=5)
    def get_finance_products(self, n=None):
        return pd.DataFrame(
            self.client.get_finance_products(per_page=250),
            columns=[
                "platform",
                "identifier",
                "supply_rate_percentage",
                "borrow_rate_percentage",
            ],
        ).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_indexes(self, n=None):
        return pd.DataFrame(self.client.get_indexes(per_page=250)).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_derivatives(self, n=None):
        df = pd.DataFrame(
            self.client.get_derivatives(include_tickers="unexpired")
        ).head(n)
        df.drop(
            ["index", "last_traded_at", "expired_at", "index_id"], axis=1, inplace=True
        )

        df.rename(
            columns={"price_percentage_change_24h": "%  change 24h"}, inplace=True
        )
        return df

    @retry(tries=2, delay=3, max_delay=5)
    def get_exchange_rates(self, n=None):
        return (
            pd.DataFrame(self.client.get_exchange_rates()["rates"])
            .T.reset_index()
            .drop("index", axis=1)
        ).head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_global_info(self, n=None):
        results = self.client.get_global()
        for key in [
            COLUMNS["total_market_cap"],
            COLUMNS["total_volume"],
            COLUMNS["market_cap_percentage"],
        ]:
            del results[key]

        df = pd.Series(results).reset_index()
        df.columns = ["Metric", "Value"]
        return df.head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_global_markets_info(self, n=None):
        columns = [
            COLUMNS["total_market_cap"],
            COLUMNS["total_volume"],
            COLUMNS["market_cap_percentage"],
        ]
        data = []
        results = self.client.get_global()
        for key in columns:
            data.append(results.get(key))
        df = pd.DataFrame(data).T
        df.columns = columns
        return df.reset_index().head(n)

    @retry(tries=2, delay=3, max_delay=5)
    def get_global_defi_info(self, n=None):
        results = self.client.get_global_decentralized_finance_defi()
        for key, value in results.items():
            try:
                results[key] = round(float(value), 4)
            except (ValueError, TypeError):
                pass

        df = pd.Series(results).reset_index()
        df.columns = ["Metric", "Value"]
        return df.head(n)


class Coin:
    def __init__(self, symbol):
        self.client = CoinGeckoAPI()
        self._coin_list = self.client.get_coins_list()
        self.coin_symbol = self._validate_coin(symbol)

        if self.coin_symbol:
            self.coin = self._get_coin_info()

    def __str__(self):
        return f"{self.coin_symbol}"

    def _validate_coin(self, symbol):
        coin = None
        for dct in self._coin_list:
            if symbol.lower() in list(dct.values()):
                coin = dct.get("id")
        if not coin:
            raise ValueError(f"Could not find coin with the given id: {symbol}\n")
        return coin

    @property
    @cachetools.func.ttl_cache(maxsize=128, ttl=30 * 60)
    def coin_list(self):
        return [token.get("id") for token in self._coin_list]

    @retry(tries=2, delay=3, max_delay=5)
    @cachetools.func.ttl_cache(maxsize=128, ttl=30 * 60)
    def _get_coin_info(self):
        params = dict(localization="false", tickers="false", sparkline=True)
        return self.client.get_coin_by_id(self.coin_symbol, **params)

    @cachetools.func.ttl_cache(maxsize=128, ttl=30 * 60)
    def _get_links(self):
        return self.coin.get("links")

    @property
    def repositories(self):
        return self._get_links().get("repos_url")

    @property
    def developers_data(self):
        dev = self.coin.get("developer_data")
        useless_keys = (
            "code_additions_deletions_4_weeks",
            "last_4_weeks_commit_activity_series",
        )
        remove_keys(useless_keys, dev)
        df = pd.Series(dev).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def blockchain_explorers(self):
        blockchain = self._get_links().get("blockchain_site")
        if blockchain:
            dct = filter_list(blockchain)
            df = pd.Series(dct).to_frame().reset_index()
            df.columns = ["Metric", "Value"]
            return df
        return None

    @property
    def social_media(self):
        social_dct = {}
        links = self._get_links()
        for channel in CHANNELS.keys():
            if channel in links:
                value = links.get(channel)
                if channel == "twitter_screen_name":
                    value = "https://twitter.com/" + value
                elif channel == "bitcointalk_thread_identifier" and value is not None:
                    value = f"https://bitcointalk.org/index.php?topic={value}"
                social_dct[channel] = value
        social_dct["discord"] = find_discord(links.get("chat_url"))
        dct = rename_columns_in_dct(social_dct, CHANNELS)
        df = pd.Series(dct).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def websites(self):
        websites_dct = {}
        links = self._get_links()
        sites = ["homepage", "official_forum_url", "announcement_url"]
        for site in sites:
            websites_dct[site] = filter_list(links.get(site))
        df = pd.Series(websites_dct).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        df["Value"] = df["Value"].apply(lambda x: ",".join(x))
        return df

    @property
    def categories(self):
        return self.coin.get("categories")

    def _get_base_market_data_info(self):
        market_dct = {}
        market_data = self.coin.get("market_data")
        for stat in [
            "total_supply",
            "max_supply",
            "circulating_supply",
            "price_change_percentage_24h",
            "price_change_percentage_7d",
            "price_change_percentage_30d",
        ]:
            market_dct[stat] = market_data.get(stat)
        prices = create_dictionary_with_prefixes(
            ["current_price"], market_data, DENOMINATION
        )
        market_dct.update(prices)
        return market_dct

    @property
    def base_info(self):
        results = {}
        for attr in BASE_INFO:
            info_obj = self.coin.get(attr)
            if attr == "description":
                info_obj = info_obj.get("en")
            results[attr] = info_obj
        results.update(self._get_base_market_data_info())
        return pd.Series(results)

    @property
    def market_data(self):
        market_data = self.coin.get("market_data")
        market_columns_denominated = [
            "market_cap",
            "fully_diluted_valuation",
            "total_volume",
            "high_24h",
            "low_24h",
        ]
        denominated_data = create_dictionary_with_prefixes(
            market_columns_denominated, market_data, DENOMINATION
        )

        market_single_columns = [
            "market_cap_rank",
            "total_supply",
            "max_supply",
            "circulating_supply",
            "price_change_percentage_24h",
            "price_change_percentage_7d",
            "price_change_percentage_30d",
            "price_change_percentage_60d",
            "price_change_percentage_1y",
            "market_cap_change_24h",
        ]
        single_stats = {}
        for col in market_single_columns:
            single_stats[col] = market_data.get(col)
        single_stats.update(denominated_data)

        try:
            single_stats["circulating_supply_to_total_supply_ratio"] = (
                single_stats["circulating_supply"] / single_stats["total_supply"]
            )
        except (ZeroDivisionError, TypeError) as e:
            logger.log(2, e)
        df = pd.Series(single_stats).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def all_time_high(self):
        market_data = self.coin.get("market_data")
        ath_columns = [
            "current_price",
            "ath",
            "ath_date",
            "ath_change_percentage",
        ]
        results = create_dictionary_with_prefixes(
            ath_columns, market_data, DENOMINATION
        )
        df = pd.Series(results).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def all_time_low(self):
        market_data = self.coin.get("market_data")
        ath_columns = [
            "current_price",
            "atl",
            "atl_date",
            "atl_change_percentage",
        ]
        results = create_dictionary_with_prefixes(
            ath_columns, market_data, DENOMINATION
        )
        df = pd.Series(results).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    @property
    def scores(self):
        score_columns = [
            "coingecko_rank",
            "coingecko_score",
            "developer_score",
            "community_score",
            "liquidity_score",
            "sentiment_votes_up_percentage",
            "sentiment_votes_down_percentage",
            "public_interest_score",
            "community_data",
            "public_interest_stats",
        ]

        single_stats = {col: self.coin.get(col) for col in score_columns[:-2]}
        nested_stats = {}
        for col in score_columns[-2:]:
            _dct = self.coin.get(col)
            for k, _ in _dct.items():
                nested_stats[k] = _dct.get(k)

        single_stats.update(nested_stats)
        df = pd.Series(single_stats).reset_index()
        df.replace({0: ""}, inplace=True)
        df = df.fillna("")
        df.columns = ["Metric", "Value"]
        return df
