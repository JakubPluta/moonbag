import re
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
from pycoingecko import CoinGeckoAPI
from gateways.gecko.utils import (
    find_discord,
    filter_list,
    calculate_time_delta,
    get_eth_addresses_for_cg_coins,
    clean_question_marks,
    join_list_elements,
    changes_parser,
    replace_qm,
    clean_row,
    collateral_auditors_parse,
)

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.float_format", lambda x: "%.1f" % x)


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


class Overview:
    BASE = "https://www.coingecko.com"

    def __init__(self):
        self.client = CoinGeckoAPI()

    @staticmethod
    def gecko_scraper(url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, features="lxml")
        return soup

    @staticmethod
    def get_btc_price():
        req = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap"
            "=false&include_24hr_vol=false&include_24hr_change=false&include_last_updated_at=false"
        )
        return req.json()["bitcoin"]["usd"]

    def _discover_coins(self, category="trending"):
        if category not in CATEGORIES:
            raise ValueError(
                f"Wrong category name\nPlease chose one from list: {CATEGORIES.keys()}"
            )

        self.BASE = "https://www.coingecko.com"
        url = "https://www.coingecko.com/en/discover"
        soup = self.gecko_scraper(url)
        popular = soup.find_all("div", class_="col-12 col-sm-6 col-md-6 col-lg-4")[
            CATEGORIES[category]
        ]
        rows = popular.find_all("a")
        results = []
        for row in rows:
            name, *args, price = row.text.strip().split("\n")
            url = self.BASE + row["href"]
            if price.startswith("BTC"):
                price = price.replace("BTC", "").replace(",", ".")
            results.append([name, price, url])
        return pd.DataFrame(results, columns=["name", "price btc", "url"])

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
            symbol, name, *args, volume, price, change = clean_row(row)
            results.append([symbol, name, volume, price, change, url])
        return pd.DataFrame(
            results,
            columns=["symbol", "name", "volume", "price", f"change_{period}", "url"],
        )

    def get_top_crypto_categories(self):
        columns = [
            "rank",
            "name",
            "change_1h",
            "change_24h",
            "change_7d",
            "market_cap",
            "volume_24h",
            "n_of_coins",
            "url",
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

        return pd.DataFrame(results, columns=columns).set_index("rank")

    def get_recently_added_coins(self):
        columns = [
            "name",
            "symbol",
            "price",
            "change_1h",
            "change_24h",
            "volume_24h",
            "market_cap",
            "last_added",
            "url",
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
                symbol2,
                price,
                *changes,
                mcpa,
                volume,
                last_added,
            ) = row_cleaned
            change_1h, change_24h, change_7d = changes_parser(changes)
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

    def get_stable_coins(self):
        columns = [
            "rank",
            "name",
            "symbol",
            "price",
            "volume_24h",
            "exchanges",
            "market_cap",
            "change_30d",
            "link",
        ]
        url = "https://www.coingecko.com/en/stablecoins"
        rows = self.gecko_scraper(url).soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            link = self.BASE + row.find("a")["href"]
            row_cleaned = clean_row(row)
            row_cleaned.append(None) if len(row_cleaned) == 8 else row_cleaned
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

    def get_yield_farms(self):
        columns = [
            "rank",
            "name",
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
            rank, name, pool, *others, il_risk, value_locked, apy1, apy2 = row_cleaned
            auditors, collateral = collateral_auditors_parse(others)
            auditors = ", ".join([aud.strip() for aud in auditors])
            collateral = ", ".join([coll.strip() for coll in collateral])
            results.append(
                [rank, name, pool, auditors, collateral, value_locked, apy1, apy2]
            )
        return (
            pd.DataFrame(results, columns=columns).set_index("rank").replace({"": None})
        )

    def get_top_volume_coins(self):
        columns = [
            "rank",
            "name",
            "symbol",
            "price",
            "change_1h",
            "change_24h",
            "change_7d",
            "volume_24h",
            "market_cap",
        ]
        url = "https://www.coingecko.com/pl/waluty/high_volume"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            row_cleaned = clean_row(row)
            row_cleaned.insert(0, "?") if len(row_cleaned) == 9 else row_cleaned
            row_cleaned.pop(3)
            results.append(row_cleaned)
        return pd.DataFrame(results, columns=columns).set_index("rank")

    def get_trending_coins(self):
        return self._discover_coins("trending")

    def get_most_voted_coins(self):
        return self._discover_coins("most_voted")

    def get_positive_sentiment_coins(self):
        return self._discover_coins("positive_sentiment")

    def get_most_visited_coins(self):
        return self._discover_coins("most_visited")

    def get_top_losers(self, period="1h"):
        return self._get_gainers_and_losers(period, typ="losers")

    def get_top_gainers(self, period="1h"):
        return self._get_gainers_and_losers(period, typ="gainers")

    def get_defi_coins(self):
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
                "rank",
                "name",
                "symbol",
                "price",
                "change_1h",
                "change_24h",
                "change_7d",
                "volume_24h",
                "market_cap",
                "fully_diluted_market_cap",
                "market_cap_to_tvl_ratio",
                "url",
            ],
        ).set_index("rank")

    def get_dexes(self):
        columns = [
            "name",
            "rank",
            "volume_24h",
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
        df["name"] = df.iloc[:, 1] + " " + df.iloc[:, 2].replace("N/A", "")
        df.drop(df.columns[1:3], axis=1, inplace=True)
        cols = list(df.columns)
        cols = [cols[-1]] + cols[:-1]
        df = df[cols]
        df.columns = columns
        df["most_traded_pairs"] = df["most_traded_pairs"].apply(
            lambda x: x.split("$")[0]
        )
        return df.set_index("rank")

    def get_top_nfts(self):
        url = "https://www.coingecko.com/en/nft"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            url = self.BASE + row.find("a")["href"]
            cleaned_row = [
                i for i in row.text.strip().split("\n") if i not in [" ", ""]
            ]
            if len(cleaned_row) == 9:
                cleaned_row.insert(5, "N/A")

            (
                rank,
                *names,
                symbol,
                symbol2,
                price,
                change,
                change1,
                change2,
                volume,
                mcap,
            ) = cleaned_row
            results.append(
                [
                    rank,
                    " ".join(names),
                    symbol,
                    price,
                    change,
                    change1,
                    change2,
                    volume,
                    mcap,
                    url,
                ]
            )

        return pd.DataFrame(
            results,
            columns=[
                "rank",
                "name",
                "symbol",
                "price",
                "change_1h",
                "change_24h",
                "change_7d",
                "volume_24h",
                "market_cap",
                "url",
            ],
        )

    def get_nft_of_the_day(self):
        url = "https://www.coingecko.com/en/nft"
        soup = self.gecko_scraper(url)
        row = soup.find("div", class_="tw-px-4 tw-py-5 sm:tw-p-6")
        try:
            *author, description, _ = [
                r for r in row.text.strip().split("\n") if r not in ["", " "]
            ]
        except ValueError:
            return {}
        return {
            "author": " ".join(author),
            "desc": description,
            "url": self.BASE + row.find("a")["href"],
            "img": row.find("img")["src"],
        }

    def get_nft_market_status(self):
        url = "https://www.coingecko.com/en/nft"
        soup = self.gecko_scraper(url)
        row = soup.find_all("span", class_="overview-box d-inline-block p-3 mr-2")
        kpis = {}
        for r in row:
            value, *kpi = r.text.strip().split()
            name = " ".join(kpi)
            kpis[name] = value
        return kpis

    def _get_news(self, page=1):
        url = f"https://www.coingecko.com/en/news?page={page}"
        soup = self.gecko_scraper(url)
        row = soup.find_all("article")
        results = []
        for r in row:
            header = r.find("header")
            link = header.find("a")["href"]
            text = [t for t in header.text.strip().split("\n") if t not in ["", " "]]
            article = r.find("div", class_="post-body").text.strip()
            title, *by = text
            author, posted = " ".join(by).split("(")
            posted = posted.strip().replace(")", "")
            results.append([title, author.strip(), posted, article, link])
        return pd.DataFrame(
            results, columns=["title", "author", "posted", "article", "url"]
        )

    def get_news(self, n_of_pages=10):
        dfs = []
        for page in range(1, n_of_pages):
            dfs.append(self._get_news(page))
        return pd.concat(dfs, ignore_index=True)

    def get_btc_holdings_public_companies_overview(self):
        url = "https://www.coingecko.com/en/public-companies-bitcoin"
        soup = self.gecko_scraper(url)
        rows = soup.find_all("span", class_="overview-box d-inline-block p-3 mr-2")
        kpis = {}
        for row in rows:
            r = row.text.strip().split()
            if r:
                value, *kpi = r
                name = " ".join(kpi)
                kpis[name] = value
        return kpis

    def get_eth_holdings_public_companies_overview(self):
        url = "https://www.coingecko.com/en/public-companies-ethereum"
        soup = self.gecko_scraper(url)
        rows = soup.find_all("span", class_="overview-box d-inline-block p-3 mr-2")
        kpis = {}
        for row in rows:
            r = row.text.strip().split()
            if r:
                value, *kpi = r
                name = " ".join(kpi)
                kpis[name] = value
        return kpis

    def get_companies_with_btc(self):
        url = "https://www.coingecko.com/en/public-companies-bitcoin"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            link = row.find("a")["href"]
            r = [r for r in row.text.strip().split("\n") if r not in ["", " "]]
            (
                rank,
                *name,
                symbol,
                country,
                total_btc,
                entry_value,
                today_value,
                pct_of_supply,
            ) = r
            results.append(
                [
                    rank,
                    " ".join(name),
                    symbol,
                    country,
                    total_btc,
                    entry_value,
                    today_value,
                    pct_of_supply,
                    link,
                ]
            )
        return pd.DataFrame(
            results,
            columns=[
                "rank",
                "company",
                "ticker",
                "country",
                "total_btc",
                "entry_value",
                "today_value",
                "pct_of_supply",
                "url",
            ],
        ).set_index("rank")

    def get_companies_with_eth(self):
        url = "https://www.coingecko.com/en/public-companies-ethereum"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            link = row.find("a")["href"]
            r = [r for r in row.text.strip().split("\n") if r not in ["", " "]]
            (
                rank,
                *name,
                symbol,
                country,
                total_btc,
                entry_value,
                today_value,
                pct_of_supply,
            ) = r
            results.append(
                [
                    rank,
                    " ".join(name),
                    symbol,
                    country,
                    total_btc,
                    entry_value,
                    today_value,
                    pct_of_supply,
                    link,
                ]
            )
        return pd.DataFrame(
            results,
            columns=[
                "rank",
                "company",
                "ticker",
                "country",
                "total_eth",
                "entry_value",
                "today_value",
                "pct_of_supply",
                "url",
            ],
        ).set_index("rank")

    def get_coin_list(self):
        return pd.DataFrame(
            self.client.get_coins_list(), columns=["id", "symbol", "name"]
        ).set_index("id")

    def get_exchanges(self):
        df = pd.DataFrame(self.client.get_exchanges_list(per_page=250))
        df.replace({float(np.NaN): None}, inplace=True)
        return df[
            [
                "trust_score_rank",
                "trust_score",
                "id",
                "name",
                "country",
                "year_established",
                "trade_volume_24h_btc",
                "url",
            ]
        ].set_index("trust_score_rank")

    def get_financial_platforms(self):
        return pd.DataFrame(self.client.get_finance_platforms()).set_index("name")

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

    def get_indexes(self):
        return pd.DataFrame(self.client.get_indexes(per_page=250))

    def get_derivatives(self):
        return pd.DataFrame(self.client.get_derivatives(include_tickers="unexpired"))

    def get_exchange_rates(self):
        return (
            pd.DataFrame(self.client.get_exchange_rates()["rates"])
            .T.reset_index()
            .drop("index", axis=1)
        )

    def get_global_info(self, json=False):
        results = self.client.get_global()
        for key in ["total_market_cap", "total_volume", "market_cap_percentage"]:
            del results[key]
        if json:
            return results
        return pd.Series(results)

    def get_global_markets_info(self):
        columns = ["total_market_cap", "total_volume", "market_cap_percentage"]
        data = []
        results = self.client.get_global()
        for key in columns:
            data.append(results.get(key))
        df = pd.DataFrame(data).T
        df.columns = columns
        return df

    def get_global_defi_info(self, json=False):
        results = self.client.get_global_decentralized_finance_defi()
        for k, v in results.items():
            try:
                results[k] = round(float(v), 4)
            except (ValueError, TypeError):
                pass
        if json:
            return results
        df = pd.Series(results).reset_index()
        df.columns = ["statistic", "value"]
        return df


BASE = "https://www.coingecko.com"


def gecko_scraper(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="lxml")
    return soup


cg = Overview()
print(cg.get_dexes())
