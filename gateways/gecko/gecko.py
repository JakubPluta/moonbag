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
    collateral_auditors_parse
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

    def _get_gainers_and_losers(self, period="1h", typ='gainers'):
        category = {
            'gainers': 0,
            'losers': 1,
        }

        if period not in PERIODS:
            raise ValueError(
                f"Wrong time period\nPlease chose one from list: {PERIODS.keys()}"
            )

        url = f"https://www.coingecko.com/en/coins/trending{PERIODS.get(period)}"
        rows = self.gecko_scraper(url).find_all("tbody")[category.get(typ)].find_all("tr")
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
        columns = ['rank', 'name', 'symbol', 'price', 'volume_24h', 'exchanges', 'market_cap', 'change_30d', 'link']
        url = "https://www.coingecko.com/en/stablecoins"
        rows = self.gecko_scraper(url).soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            link = self.BASE + row.find('a')['href']
            row_cleaned = clean_row(row)
            row_cleaned.append(None) if len(row_cleaned) == 8 else row_cleaned
            rank, name, *symbols, price, volume_24h, exchanges, market_cap, change_30d = row_cleaned
            symbol = symbols[0] if symbols else symbols
            results.append([rank, name, symbol, price, volume_24h, exchanges, market_cap, change_30d, link])
        return replace_qm(pd.DataFrame(results, columns=columns).set_index('rank'))

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
            auditors = ', '.join([aud.strip() for aud in auditors])
            collateral = ', '.join([coll.strip() for coll in collateral])
            results.append([rank, name, pool, auditors, collateral, value_locked, apy1, apy2])
        return pd.DataFrame(results, columns=columns).set_index('rank').replace({'': None})

    def get_top_volume_coins(self):
        columns = ['rank', 'name', 'symbol', 'price', 'change_1h', 'change_24h', 'change_7d', 'volume_24h',
                   'market_cap']
        url = "https://www.coingecko.com/pl/waluty/high_volume"
        rows = self.gecko_scraper(url).find("tbody").find_all("tr")
        results = []
        for row in rows:
            row_cleaned = clean_row(row)
            row_cleaned.insert(0, '?') if len(row_cleaned) == 9 else row_cleaned
            row_cleaned.pop(3)
            results.append(row_cleaned)
        return pd.DataFrame(results,
                            columns=columns
                            ).set_index("rank")

    def get_trending_coins(self):
        return self._discover_coins('trending')

    def get_most_voted_coins(self):
        return self._discover_coins('most_voted')

    def get_positive_sentiment_coins(self):
        return self._discover_coins('positive_sentiment')

    def get_most_visited_coins(self):
        return self._discover_coins('most_visited')

    def get_top_losers(self, period="1h"):
        return self._get_gainers_and_losers(period, typ='losers')

    def get_top_gainers(self, period="1h"):
        return self._get_gainers_and_losers(period, typ='gainers')

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
                row_cleaned.insert(4, '?')
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
        url = "https://www.coingecko.com/en/dex"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            row_txt = row.text.strip()
            if "Trading Incentives" in row_txt:
                row_txt = row_txt.replace("Trading Incentives", "")

            record = row_txt.split("\n")
            record = [r for r in record if r not in [" ", ""]]
            if len(record) == 8:
                record.insert(-3, "N/A")

            (
                rank,
                *names,
                volume_24h,
                num_coins,
                num_pairs,
                visits,
                most_trader_pairs,
                market_share_by_volume,
            ) = record
            results.append(
                [
                    rank,
                    " ".join(names).strip(),
                    volume_24h,
                    num_coins,
                    num_pairs,
                    visits,
                    most_trader_pairs,
                    market_share_by_volume,
                    url,
                ]
            )
        df = pd.DataFrame(
            results,
            columns=[
                "rank",
                "name",
                "volume_24h",
                "number_of_coins",
                "number_of_pairs",
                "number_of_visits",
                "most_traded_pairs",
                "market_share_by_volume",
                "url",
            ],
        )

        # @todo make it clean - > so ugly ....
        df["most_traded_pairs"] = df["most_traded_pairs"].str.replace(
            "\d+", "", regex=True
        )
        df["most_traded_pairs"] = df["most_traded_pairs"].str.replace(
            ".", "", regex=True
        )
        df["most_traded_pairs"] = df["most_traded_pairs"].str.replace(
            ",", "", regex=True
        )
        df["most_traded_pairs"] = df["most_traded_pairs"].str.replace(
            "$", "", regex=True
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

    def _get_trends(self):
        trending = self.client.get_search_trending().get("coins")
        coins = (
            {"id": coin["item"].get("id")}
            for coin in trending
            if coin.get("item") is not None
        )
        return coins

    def _get_coin_info(self, coin_id: str):
        params = dict(localization="false", tickers="false", sparkline=True)
        info = self.client.get_coin_by_id(coin_id, **params)
        links = info.get("links")
        platforms = info.get("platforms")
        market_data = info.get("market_data")

        # repos = links.get("repos_url")
        # dev = info.get("developer_data")

        return dict(
            mcap_rank=info.get("market_cap_rank"),
            id=info.get("id"),
            symbol=info.get("symbol"),
            name=info.get("name"),
            contract=info.get("contract_address"),
            categories=join_list_elements(info.get("categories")),
            platforms=join_list_elements(platforms),
            total_supply=market_data.get("total_supply"),
            max_supply=market_data.get("max_supply"),
            circulating_supply=market_data.get("circulating_supply"),
            change_pct_24h=market_data.get("price_change_percentage_24h"),
            change_pct_7d=market_data.get("price_change_percentage_7d"),
            homepage=filter_list(links.get("homepage"))[0]
            if links.get("homepage")
            else None,
            sentiment=info.get("sentiment_votes_up_percentage"),
            description=info.get("description").get("en"),
            # twitter='https://twitter.com/' + links.get("twitter_screen_name") if links.get("twitter_screen_name") else None,
            # telegram=links.get("telegram_channel_identifier"),
            # subreddit=links.get("subreddit_url"),
            # github=repos.get("github") if repos else None,
            # forums=filter_list(links.get("official_forum_url"))
            # if links.get("official_forum_url")
            # else None,
            # discord=find_discord(links.get("chat_url")),
            # community_data=info.get("community_data"),
            # public_interest=info.get("public_interest_stats"),
            ath_price_usd=market_data.get("ath").get("usd"),
            pct_from_ath_usd=market_data.get("ath_change_percentage").get("usd"),
            ath_date_usd=market_data.get("ath_date").get("usd"),
            days_from_ath_usd=calculate_time_delta(
                market_data.get("ath_date").get("usd")
            ),
        )

    def get_trends(self):
        dfs = []
        for coin in self._get_trends():
            jsn = self._get_coin_info(coin.get("id"))
            try:
                df = pd.json_normalize(jsn)
            except TypeError:
                df = pd.DataFrame()
            dfs.append(df)
        return pd.concat(dfs).set_index("mcap_rank")

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




