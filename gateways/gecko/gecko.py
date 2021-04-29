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
)

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
pd.set_option("display.float_format", lambda x: "%.1f" % x)


periods = {
    "1h": "?time=h1",
    "1d": "?time=h24",
    "7d": "?time=d7",
    "14d": "?time=d14",
    "30d": "?time=d30",
    "60d": "?time=d60",
    "1y": "?time=y1",
}

categories = {
    "trending": 0,
    "most_voted": 1,
    "positive_sentiment": 2,
    "recently_added": 3,
    "most_visited": 4,
}


class GeckoOverview:
    BASE = "https://www.coingecko.com"

    def __init__(self):
        self.client = CoinGeckoAPI()

    @staticmethod
    def gecko_scraper(url):
        req = requests.get(url)
        soup = BeautifulSoup(req.text, features="lxml")
        return soup

    def get_top_crypto_categories(self):
        url = "https://www.coingecko.com/en/categories"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []

        for row in rows:
            rank = row.find(
                "td", class_="table-left tw-text-left tw-text-xs"
            ).text.strip()
            name = row.find("td", class_="coin-name").text.strip()
            href = self.BASE + row.find("td", class_="coin-name").a["href"]
            top_coins_urls = [
                self.BASE + a["href"]
                for a in row.find(
                    "div", class_="tw-flex tw-justify-center lg:ml-4"
                ).find_all("a", href=True)
            ]

            top_coins = ", ".join([url.split("/")[-1] for url in top_coins_urls])

            hour, day, week = [change.text.strip() for change in row.find_all("span")]
            mcap, volume = [
                stats.text.strip()
                for stats in row.find_all("td", class_="coin-name tw-text-right")[-2:]
            ]
            coin = dict(
                category=name,
                rank=rank,
                url=href,
                top_coins=top_coins,
                last_1h=hour,
                last_day=day,
                last_week=week,
                market_cap=mcap,
                volume_24h=volume,
            )
            clean_question_marks(coin)
            results.append(coin)
        return pd.DataFrame(results).set_index("rank")

    def get_recently_added(self):
        url = "https://www.coingecko.com/en/coins/recently_added"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []

        for row in rows:
            url = self.BASE + row.find("td", class_="py-0 coin-name").a["href"]
            name = row.find("td", class_="py-0 coin-name").a.text.strip()
            added = row.find(
                "td", class_="trade p-0 col-market pl-2 text-center"
            ).text.strip()
            price = row.find("td", class_="td-price price text-right").text.strip()
            hour = row.find(
                "td", class_="td-change1h change1h stat-percent text-right col-market"
            ).text.strip()
            day = row.find(
                "td", class_="td-change24h change24h stat-percent text-right col-market"
            ).text.strip()
            week = row.find(
                "td", class_="td-change7d change7d stat-percent text-right col-market"
            ).text.strip()
            volume = row.find(
                "td", class_="td-liquidity_score lit text-right %> col-market"
            ).text.strip()
            mcap = row.find(
                "td", class_="td-market_cap cap col-market cap-price text-right"
            ).text.strip()

            coin = dict(
                name=name,
                price=price,
                last_added=added,
                url=url,
                last_1h=hour,
                last_day=day,
                last_week=week,
                market_cap=mcap,
                volume_24h=volume,
            )
            # clean dict
            clean_question_marks(coin)
            results.append(coin)
        return pd.DataFrame(results)

    def get_stable_coins(self):
        url = "https://www.coingecko.com/en/stablecoins"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            rank = row.find(
                "td", class_="table-number text-center text-xs"
            ).text.strip()
            name, symbol, *_ = (
                row.find("td", class_="py-0 coin-name").text.strip().split()
            )
            price = row.find("td", class_="td-price price text-right").text.strip()
            day = row.find(
                "td", class_="td-liquidity_score lit text-right %> col-market"
            ).text.strip()
            mcap = row.find("td", class_="text-right col-market").text.strip()
            month = row.find(
                "td", class_="stat-percent text-right col-market text-primary"
            ).text.strip()
            exchanges = row.find(
                "td", class_="text-right col-market text-primary"
            ).text.strip()
            stable = dict(
                rank=rank,
                name=name,
                symbol=symbol,
                price=price,
                volume_24h=day,
                market_cap_change_30d=month,
                market_cap=mcap,
                number_of_exchanges=exchanges,
            )
            clean_question_marks(stable)
            results.append(stable)
        return pd.DataFrame(results).set_index("rank")

    def get_yield_farms(self):
        def _parse_row(row):
            parsed = []
            for n, i in enumerate(row):
                txt = i.text.strip()
                record = (
                    re.sub(r"(\n){2,10}", " ", txt)
                    .replace("  ", " ")
                    .replace("\n", " ")
                )
                parsed.append(record)
            return parsed[:-1]

        cols = [
            "rank",
            "name",
            "pool",
            "audits",
            "collateral",
            "il risk",
            "value locked",
            "returns",
        ]
        url = "https://www.coingecko.com/en/yield-farming"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []
        for r in rows:
            row = r.find_all("td")
            res = _parse_row(row)
            results.append(res)
        df = pd.DataFrame(results, columns=cols).set_index("rank")
        df.replace({"N/A": None}, inplace=True)
        df["audits"] = df["audits"].replace(
            to_replace=r"^[0-9]\s", value="", regex=True
        )
        df.applymap(lambda x: x.rstrip() if isinstance(x, str) else x)
        df.replace(to_replace=r"(\s){2,}", value=" ", regex=True, inplace=True)
        df["yearly returns"] = df["returns"].apply(lambda x: " ".join(x.split(" ")[:2]))
        df["hourly returns"] = df["returns"].apply(lambda x: " ".join(x.split(" ")[2:]))
        df["collateral"] = df["collateral"].apply(lambda x: ",".join(x.split()))
        return df.drop(["returns", "il risk"], axis=1)

    def get_top_volume_coins(self):
        url = "https://www.coingecko.com/pl/waluty/high_volume"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            rank = row.find(
                "td", class_="table-number text-center text-xs"
            ).text.strip()
            name = row.find(
                "a",
                class_="tw-hidden lg:tw-flex font-bold tw-items-center tw-justify-between",
            ).text.strip()
            symbol = row.find("a", class_="d-lg-none font-bold").text.strip()
            price = row.find("td", class_="td-price price text-right").text.strip()
            last_1h = row.find(
                "td", class_="td-change1h change1h stat-percent text-right col-market"
            ).text.strip()
            last_24h = row.find(
                "td", class_="td-change24h change24h stat-percent text-right col-market"
            ).text.strip()
            last_week = row.find(
                "td", class_="td-change7d change7d stat-percent text-right col-market"
            ).text.strip()
            volume_24h = row.find(
                "td", class_="td-liquidity_score lit text-right %> col-market"
            ).text.strip()
            mcap = row.find(
                "td", class_="td-market_cap cap col-market cap-price text-right"
            ).text.strip()

            coin = dict(
                rank=rank,
                name=name,
                symbol=symbol,
                price=price,
                change_1h=last_1h,
                change_24h=last_24h,
                change_7d=last_week,
                volume_24h=volume_24h,
                market_cap=mcap,
            )
            clean_question_marks(coin)
            results.append(coin)
        return pd.DataFrame(results).set_index("rank")

    @staticmethod
    def get_btc_price(self):
        req = requests.get(
            "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap"
            "=false&include_24hr_vol=false&include_24hr_change=false&include_last_updated_at=false"
        )
        return req.json()["bitcoin"]["usd"]

    def discover_coins(self, category="trending"):
        if category not in categories:
            raise ValueError(
                f"Wrong category name\nPlease chose one from list: {categories.keys()}"
            )

        self.BASE = "https://www.coingecko.com"
        url = "https://www.coingecko.com/en/discover"
        soup = self.gecko_scraper(url)
        popular = soup.find_all("div", class_="col-12 col-sm-6 col-md-6 col-lg-4")[
            categories[category]
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

    def get_top_gainers(self, period="1h"):
        if period not in periods:
            raise ValueError(
                f"Wrong time period\nPlease chose one from list: {periods.keys()}"
            )

        url = f"https://www.coingecko.com/en/coins/trending{periods.get(period)}"
        soup = self.gecko_scraper(url)
        top_gainers = soup.find_all("tbody")[0]
        rows = top_gainers.find_all("tr")
        results = []
        for row in rows:
            url = self.BASE + row.find("a")["href"]
            record = [r for r in row.text.strip().split("\n") if r not in ["", " "]]
            symbol, name, *args, volume, price, change = record
            results.append([symbol, name, volume, price, change, url])
        return pd.DataFrame(
            results,
            columns=["symbol", "name", "volume", "price", f"change_{period}", "url"],
        )

    def get_top_losers(self, period="1h"):

        if period not in periods:
            raise ValueError(
                f"Wrong time period\nPlease chose one from list: {periods.keys()}"
            )
        url = f"https://www.coingecko.com/en/coins/trending{periods.get(period)}"
        soup = self.gecko_scraper(url)
        top_gainers = soup.find_all("tbody")[1]
        rows = top_gainers.find_all("tr")
        results = []
        for row in rows:
            url = self.BASE + row.find("a")["href"]
            record = [r for r in row.text.strip().split("\n") if r not in ["", " "]]
            symbol, name, *args, volume, price, change = record
            results.append([symbol, name, volume, price, change, url])
        return pd.DataFrame(
            results,
            columns=["symbol", "name", "volume", "price", f"change_{period}", "url"],
        )

    def get_defi_coins(self):
        url = "https://www.coingecko.com/en/defi"
        soup = self.gecko_scraper(url)
        rows = soup.find("tbody").find_all("tr")
        results = []
        for row in rows:
            url = self.BASE + row.find("a")["href"]
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
                full,
                ratio,
            ) = row.text.strip().split()
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
                    full,
                    ratio,
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
                "fully_diluted_market_cap",
                "macp/tvl ratio",
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


cg = GeckoOverview()

print(cg.get_global_defi_info())
