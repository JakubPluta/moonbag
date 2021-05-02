import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pycoingecko import CoinGeckoAPI
import cachetools.func
from retry import retry
from gateways.gecko.utils import (
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

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.float_format", lambda x: "%.5f" % x)


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
    return CoinGeckoAPI().get_coins_list()


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
            results, columns=[COLUMNS["name"], "price btc", "price_usd", COLUMNS["url"]]
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
    def get_top_crypto_categories(self):
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

        return pd.DataFrame(results, columns=columns).set_index(COLUMNS["rank"])

    @retry(tries=2, delay=3, max_delay=5)
    def get_recently_added_coins(self):
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
            (name, symbol, _, price, *changes, mcpa, volume, last_added,) = row_cleaned
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
        return replace_qm(pd.DataFrame(results, columns=columns))

    @retry(tries=2, delay=3, max_delay=5)
    def get_stable_coins(self):
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
        return replace_qm(pd.DataFrame(results, columns=columns).set_index("rank"))

    @retry(tries=2, delay=3, max_delay=5)
    def get_yield_farms(self):
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
            rank, name, pool, *others, _, value_locked, apy1, apy2 = row_cleaned
            auditors, collateral = collateral_auditors_parse(others)
            auditors = ", ".join([aud.strip() for aud in auditors])
            collateral = ", ".join([coll.strip() for coll in collateral])
            results.append(
                [rank, name, pool, auditors, collateral, value_locked, apy1, apy2]
            )
        return (
            pd.DataFrame(results, columns=columns).set_index("rank").replace({"": None})
        )

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_volume_coins(self):
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
        return pd.DataFrame(results, columns=columns).set_index(COLUMNS["rank"])

    @retry(tries=2, delay=3, max_delay=5)
    def get_trending_coins(self):
        return self._discover_coins("trending")

    @retry(tries=2, delay=3, max_delay=5)
    def get_most_voted_coins(self):
        return self._discover_coins("most_voted")

    @retry(tries=2, delay=3, max_delay=5)
    def get_positive_sentiment_coins(self):
        return self._discover_coins("positive_sentiment")

    @retry(tries=2, delay=3, max_delay=5)
    def get_most_visited_coins(self):
        return self._discover_coins("most_visited")

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_losers(self, period="1h"):
        return self._get_gainers_and_losers(period, typ="losers")

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_gainers(self, period="1h"):
        return self._get_gainers_and_losers(period, typ="gainers")

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_defi_coins(self):
        url = "https://www.coingecko.com/en/defi"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            url = self.BASE + row.find("a")["href"]
            row_cleaned = clean_row(row)
            row_cleaned.pop(2)
            row_cleaned.append(url)
            if len(row_cleaned) == 11:
                row_cleaned.insert(4, "?")
            results.append(row_cleaned)

        return pd.DataFrame(
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
        ).set_index(COLUMNS["rank"])

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_dexes(self):
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
        return df.set_index(COLUMNS["rank"])

    @retry(tries=2, delay=3, max_delay=5)
    def get_top_nfts(self):
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
        return pd.DataFrame(
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
                COLUMNS["url"],
            ],
        ).set_index(COLUMNS["rank"])

    @retry(tries=2, delay=3, max_delay=5)
    def get_nft_of_the_day(self):
        url = "https://www.coingecko.com/en/nft"
        soup = self.gecko_scraper(url)
        row = soup.find("div", class_="tw-px-4 tw-py-5 sm:tw-p-6")
        try:
            *author, description, _ = clean_row(row)
            if len(author) > 3:
                author, description = author[:3], author[3]
            print(author)
        except (ValueError, IndexError):
            return {}
        return {
            COLUMNS["author"]: " ".join(author),
            "desc": description,
            COLUMNS["url"]: self.BASE + row.find("a")["href"],
            "img": row.find("img")["src"],
        }

    @retry(tries=2, delay=3, max_delay=5)
    def get_nft_market_status(self):
        url = "https://www.coingecko.com/en/nft"
        soup = self.gecko_scraper(url)
        rows = soup.find_all("span", class_="overview-box d-inline-block p-3 mr-2")
        kpis = {}
        for row in rows:
            value, *kpi = clean_row(row)
            name = " ".join(kpi)
            kpis[name] = value
        return kpis

    @retry(tries=2, delay=3, max_delay=5)
    def get_news(self, n_of_pages=10):
        dfs = []
        for page in range(1, n_of_pages):
            dfs.append(self._get_news(page))
        return pd.concat(dfs, ignore_index=True)

    @retry(tries=2, delay=3, max_delay=5)
    def get_btc_holdings_public_companies_overview(self):
        return self._get_holdings_overview("bitcoin")

    @retry(tries=2, delay=3, max_delay=5)
    def get_eth_holdings_public_companies_overview(self):
        return self._get_holdings_overview("ethereum")

    @retry(tries=2, delay=3, max_delay=5)
    def get_companies_with_btc(self):
        return self._get_companies_assets("bitcoin")

    @retry(tries=2, delay=3, max_delay=5)
    def get_companies_with_eth(self):
        return self._get_companies_assets("ethereum")

    @retry(tries=2, delay=3, max_delay=5)
    def get_coin_list(self):
        return pd.DataFrame(
            self.client.get_coins_list(),
            columns=[COLUMNS["id"], COLUMNS["symbol"], COLUMNS["name"]],
        ).set_index(COLUMNS["id"])

    @retry(tries=2, delay=3, max_delay=5)
    def get_exchanges(self):
        df = pd.DataFrame(self.client.get_exchanges_list(per_page=250))
        df.replace({float(np.NaN): None}, inplace=True)
        return df[
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
        ].set_index("trust_score_rank")

    @retry(tries=2, delay=3, max_delay=5)
    def get_financial_platforms(self):
        return pd.DataFrame(self.client.get_finance_platforms()).set_index(
            COLUMNS["name"]
        )

    @retry(tries=2, delay=3, max_delay=5)
    def get_finance_products(self):
        return pd.DataFrame(
            self.client.get_finance_products(per_page=250),
            columns=[
                "platform",
                "identifier",
                "supply_rate_percentage",
                "borrow_rate_percentage",
            ],
        )

    @retry(tries=2, delay=3, max_delay=5)
    def get_indexes(self):
        return pd.DataFrame(self.client.get_indexes(per_page=250))

    @retry(tries=2, delay=3, max_delay=5)
    def get_derivatives(self):
        return pd.DataFrame(self.client.get_derivatives(include_tickers="unexpired"))

    @retry(tries=2, delay=3, max_delay=5)
    def get_exchange_rates(self):
        return (
            pd.DataFrame(self.client.get_exchange_rates()["rates"])
            .T.reset_index()
            .drop("index", axis=1)
        )

    @retry(tries=2, delay=3, max_delay=5)
    def get_global_info(self, json=False):
        results = self.client.get_global()
        for key in [
            COLUMNS["total_market_cap"],
            COLUMNS["total_volume"],
            COLUMNS["market_cap_percentage"],
        ]:
            del results[key]
        if json:
            return results
        return pd.Series(results)

    @retry(tries=2, delay=3, max_delay=5)
    def get_global_markets_info(self):
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
        return df

    @retry(tries=2, delay=3, max_delay=5)
    def get_global_defi_info(self, json=False):
        results = self.client.get_global_decentralized_finance_defi()
        for key, value in results.items():
            try:
                results[key] = round(float(value), 4)
            except (ValueError, TypeError):
                pass
        if json:
            return results
        df = pd.Series(results).reset_index()
        df.columns = ["statistic", "value"]
        return df


class Coin:
    def __init__(self, symbol):
        self.client = CoinGeckoAPI()
        self._coin_list = self.client.get_coins_list()
        self._coin_symbol = self._validate_coin(symbol)

        if self._coin_symbol:
            self.coin = self._get_coin_info()

    def _validate_coin(self, symbol):
        coin = None
        for dct in self._coin_list:
            if symbol.lower() in list(dct.values()):
                coin = dct.get("id")
        if not coin:
            raise ValueError(
                f"Could not find coin with the given id: {symbol}\nTo check available coins use: get_coin_list method"
            )
        return coin

    @property
    @cachetools.func.ttl_cache(maxsize=128, ttl=30 * 60)
    def coin_list(self):
        return [token.get("id") for token in self._coin_list]

    @retry(tries=2, delay=3, max_delay=5)
    @cachetools.func.ttl_cache(maxsize=128, ttl=30 * 60)
    def _get_coin_info(self):
        params = dict(localization="false", tickers="false", sparkline=True)
        return self.client.get_coin_by_id(self._coin_symbol, **params)

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
        return pd.Series(dev)

    @property
    def blockchain_explorers(self):
        blockchain = self._get_links().get("blockchain_site")
        if blockchain:
            return filter_list(blockchain)

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
        return rename_columns_in_dct(social_dct, CHANNELS)

    @property
    def websites(self):
        websites_dct = {}
        links = self._get_links()
        sites = ["homepage", "official_forum_url", "announcement_url"]
        for site in sites:
            websites_dct[site] = filter_list(links.get(site))
        return websites_dct

    @property
    def categories(self):
        return self.coin.get("categories")

    # TODO: Make it more elegant
    def _get_base_market_data_info(self):
        market_dct = {}
        market_data = self.coin.get("market_data")

        market_dct["price_usd"] = market_data.get("current_price").get("usd")
        market_dct["price_eth"] = market_data.get("current_price").get("eth")
        market_dct["price_btc"] = market_data.get("current_price").get("btc")
        market_dct["total_supply"] = market_data.get("total_supply")
        market_dct["max_supply"] = market_data.get("max_supply")
        market_dct["circulating_supply"] = market_data.get("circulating_supply")
        market_dct["price_change_pct_24h"] = market_data.get(
            "price_change_percentage_24h"
        )
        market_dct["price_change_pct_7d"] = market_data.get(
            "price_change_percentage_7d"
        )
        market_dct["price_change_pct_30d"] = market_data.get(
            "price_change_percentage_30d"
        )
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
        except ZeroDivisionError:
            ...
        return pd.Series(single_stats)

    @property
    def all_time_high(self):
        market_data = self.coin.get("market_data")
        ath_columns = ["current_price", "ath", "ath_date", "ath_change_percentage"]
        results = create_dictionary_with_prefixes(
            ath_columns, market_data, DENOMINATION
        )
        return results

    @property
    def all_time_low(self):
        market_data = self.coin.get("market_data")
        ath_columns = ["current_price", "atl", "atl_date", "atl_change_percentage"]
        results = create_dictionary_with_prefixes(
            ath_columns, market_data, DENOMINATION
        )
        return pd.Series(results)

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
            "public_interest_stats"
        ]
        # for col in score_columns:
        #     single_stats[col] = self.coin.get(col)
        single_stats = {col : self.coin.get(col) for col in score_columns[:-2]}

        nested_stats = {}
        for col in score_columns[-2:]:
            _dct = self.coin.get(col)
            for k,v in _dct.items():
                nested_stats[k] = _dct.get(k)

        single_stats.update(nested_stats)
        return pd.Series(single_stats)

            # "community_data",
            # "public_interest_stats",


    # idea: if token has eth address use blockchain explorer to get some stats
    def ether_scanner(self):
        pass


c = Coin("uniswap")
print(c.scores)
