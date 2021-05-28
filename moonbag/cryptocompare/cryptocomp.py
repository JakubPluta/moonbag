import pandas as pd
from dotenv import load_dotenv
import os
from moonbag.cryptocompare._client import CryptoCompareClient
from moonbag.common.utils import table_formatter, wrap_text_in_df
from moonbag.cryptocompare.utils import create_dct_mapping_from_df
import logging
import textwrap

logger = logging.getLogger("cmc")

load_dotenv()

API_KEY = os.getenv("CC_API_KEY")


class CryptoCompare(CryptoCompareClient):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.api_key = api_key
        self.coin_list = self.get_all_coins_list()
        self.coin_mapping = create_dct_mapping_from_df(self.coin_list, "Symbol", "Id")

    def get_price(self, symbol="BTC", currency="USD", **kwargs):
        data = self._get_price(symbol, currency, **kwargs)
        if "Response" in data and data["Response"] == "Error":
            return pd.DataFrame()
        data = data["RAW"][symbol][currency]
        columns = [
            "FROMSYMBOL",
            "TOSYMBOL",
            "PRICE",
            "MEDIAN",
            "VOLUMEDAY",
            "VOLUME24HOUR",
            "OPENDAY",
            "OPEN24HOUR",
            "HIGH24HOUR",
            "LOW24HOUR",
            "MKTCAP",
            "SUPPLY",
            "TOTALVOLUME24H",
            "CHANGEDAY" "CHANGEPCTDAY",
            "CHANGEHOUR" "CHANGEPCTHOUR",
            "CHANGE24HOUR",
            "CHANGEPCT24HOUR",
        ]
        data = {k: v for k, v in data.items() if k in columns}
        df = pd.Series(data).to_frame().reset_index()
        df.columns = ["Metric", "Value"]
        return df

    def get_top_list_by_market_cap(self, currency="USD", limit=100, **kwargs):
        limit = 10 if limit < 10 else limit
        data = self._get_top_list_by_market_cap(currency, limit, **kwargs)["Data"]
        data = [{"CoinInfo": d.get("CoinInfo"), "RAW": d.get("RAW")} for d in data]
        df = pd.json_normalize(data)
        df.columns = [col.split(".")[-1] for col in list(df.columns)]
        df = wrap_text_in_df(df)

        df.rename(
            columns={
                "TechnologyAdoptionRating": "TechRating",
                "MarketPerformanceRating": "MarketRating",
                "AssetLaunchDate": "Launched",
                "TOSYMBOL": "ToSymbol",
                "PRICE": "Price",
                "MEDIAN": "Median",
                "MKTCAP": "MarketCap",
                "SUPPLY": "Supply",
                "CHANGEPCT24HOUR": "% change 24h",
                "CHANGEPCTHOUR": "% change 1h",
                "TOTALVOLUME24H": "Volume 24h",
            },
            inplace=True,
        )
        columns = [
            "Name",
            "FullName",
            "ProofType",
            "Rating",
            "Launched",
            "ToSymbol",
            "Price",
            "MarketCap",
            "Supply",
            "% change 24h",
            "% change 1h",
            "Volume 24h",
        ]
        return df[columns]

    def get_top_exchanges(self, symbol="BTC", currency="USD", limit=100, **kwargs):
        try:
            data = self._get_top_exchanges(symbol, currency, limit, **kwargs)["Data"][
                "Exchanges"
            ]
        except KeyError as e:
            logger.error(e)
            return pd.DataFrame()

        df = pd.json_normalize(data)
        columns = [
            "MARKET",
            "FROMSYMBOL",
            "TOSYMBOL",
            "PRICE",
            "VOLUME24HOUR",
            "OPENDAY",
            "HIGHDAY",
            "LOWDAY",
            "CHANGEPCT24HOUR",
            "CHANGEPCTHOUR",
        ]

        return df[columns]

    def get_exchanges_top_symbols_by_volume(
        self, exchange="Binance", limit=100, **kwargs
    ):
        data = self._get_exchanges_top_symbols_by_volume(exchange, limit, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        try:
            df["volume"] = df["volume"].apply(lambda x: float(x))
            df = df[df["volume"] > 0]
        except KeyError as e:
            logger.log(2, e)
        return df

    def get_top_list_by_pair_volume(self, currency="USD", limit=100, **kwargs):
        data = self._get_top_list_by_pair_volume(currency, limit, **kwargs)["Data"]
        df = pd.DataFrame(data)
        columns = ["SYMBOL", "NAME", "FULLNAME", "SUPPLY", "VOLUME24HOURTO"]
        return df[columns]

    def get_top_of_trading_pairs(self, symbol="ETH", limit=50, **kwargs):
        data = self._get_top_of_trading_pairs(symbol, limit, **kwargs)["Data"]
        return pd.DataFrame(data)

    def get_latest_social_coin_stats(self, coin_id=7605, **kwargs):
        data = self._get_latest_social_coin_stats(coin_id, **kwargs)["Data"]
        social_stats = {}

        general = pd.Series(data.get("General")).to_frame().reset_index()
        for social in ["Twitter", "Reddit", "Facebook"]:
            social_stats[social] = data.get(social)

        repo = data["CodeRepository"]
        repo_dct = {}
        if "List" in repo and len(repo["List"]) > 0:
            for k, v in repo["List"][0].items():
                if not isinstance(v, (list, dict, set)):
                    repo_dct[k] = v
            social_stats["repository"] = repo_dct

        df = pd.json_normalize(social_stats)
        df.columns = [col.replace(".", "_").lower() for col in list(df.columns)]
        for col in [
            "twitter_account_creation",
            "reddit_community_creation",
            "repository_last_update",
            "repository_created_at",
            "repository_last_push",
        ]:
            try:
                df[col] = pd.to_datetime(df[col], unit="s")
            except KeyError as e:
                logger.log(2, e)
        df = df.T.reset_index()
        df = pd.concat([general, df])
        df.columns = ["Metric", "Value"]
        return df

    def get_historical_social_stats(
        self, coin_id=7605, limit=150, aggregate=7, **kwargs
    ):
        data = self._get_historical_social_stats(coin_id, limit, aggregate, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df["time"] = df["time"].dt.strftime("%Y/%m/%d")
        df.drop(
            [
                "comments",
                "posts",
                "followers",
                "points",
                "overview_page_views",
                "analysis_page_views",
                "markets_page_views",
                "charts_page_views",
                "trades_page_views",
                "forum_page_views",
                "influence_page_views",
                "total_page_views",
            ],
            axis=1,
            inplace=True,
        )
        df = wrap_text_in_df(df, w=40)
        cols = [
            "time",
            "fb_likes",
            "twitter_followers",
            "reddit_subscribers",
            "reddit_active_users",
            "reddit_posts_per_day",
            "reddit_comments_per_hour",
            "reddit_comments_per_day",
            "code_repo_stars",
            "code_repo_forks",
            "code_repo_subscribers",
            "code_repo_closed_issues",
            "code_repo_contributors",
        ]
        df = df[cols]
        df.columns = [
            textwrap.fill(c.replace("_", " "), 13, break_long_words=False)
            for c in list(df.columns)
        ]
        return df

    def get_latest_news(self, lang="EN", sort_order="latest", **kwargs):
        data = self._get_latest_news(lang, sort_order, **kwargs)["Data"]
        df = pd.DataFrame(data)
        df.drop(
            ["upvotes", "downvotes", "lang", "source_info", "imageurl", "id", "url"],
            axis=1,
            inplace=True,
        )
        df["published_on"] = pd.to_datetime(df["published_on"], unit="s")

        # 'tags','categories','guid','body'

        df = df[["published_on", "title", "source", "guid"]]

        df = df.applymap(
            lambda x: "\n".join(textwrap.wrap(x, width=75)) if isinstance(x, str) else x
        )
        return df

    def get_blockchain_available_coins_list(self):
        data = self._get_blockchain_available_coins_list()["Data"]
        df = pd.DataFrame(data).T
        df["data_available_from"] = pd.to_datetime(df["data_available_from"], unit="s")
        return df

    @property
    def blockchain_coins_list(self):
        return self.get_blockchain_available_coins_list()["symbol"].to_list()

    def get_all_coins_list(self, summary="true", **kwargs):
        data = self._get_all_coins_list(summary, **kwargs)["Data"]
        return pd.DataFrame(data).T[["Id", "Symbol", "FullName"]]

    
    def get_historical_day_prices(
        self, symbol="BTC", currency="USD", limit=365, **kwargs
    ):
        data = self._get_historical_day_prices(symbol, currency, limit, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df.drop(
            ["volumefrom", "conversionType", "conversionSymbol"], axis=1, inplace=True
        )
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    
    def get_historical_hour_prices(
        self, symbol="BTC", currency="USD", limit=60 * 24, **kwargs
    ):
        data = self._get_historical_hour_prices(symbol, currency, limit, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df.drop(
            ["volumefrom", "conversionType", "conversionSymbol"], axis=1, inplace=True
        )
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    
    def get_historical_minutes_prices(
        self, symbol="BTC", currency="USD", limit=60 * 24, **kwargs
    ):
        data = self._get_historical_minutes_prices(symbol, currency, limit, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df.drop(
            ["volumefrom", "conversionType", "conversionSymbol"], axis=1, inplace=True
        )
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    
    def get_daily_exchange_volume(
        self, currency="USD", exchange="CCCAGG", limit=365, **kwargs
    ):
        data = self._get_daily_exchange_volume(currency, exchange, limit, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    
    def get_hourly_exchange_volume(
        self, currency="USD", exchange="CCCAGG", limit=60 * 24, **kwargs
    ):
        data = self._get_hourly_exchange_volume(currency, exchange, limit, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    
    def get_daily_symbol_volume(
        self, symbol="BTC", currency="USD", limit=365, **kwargs
    ):
        data = self._get_daily_symbol_volume(symbol, currency, limit, **kwargs)["Data"]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df[["time", "top_tier_volume_total", "total_volume_total"]]

    
    def get_hourly_symbol_volume(
        self, symbol="BTC", currency="USD", limit=365, **kwargs
    ):
        data = self._get_hourly_symbol_volume(symbol, currency, limit, **kwargs)["Data"]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df[["time", "top_tier_volume_total", "total_volume_total"]]

    def get_latest_blockchain_data(self, symbol="BTC", **kwargs):
        try:
            data = self._get_latest_blockchain_data(symbol, **kwargs)["Data"]
            df = pd.Series(data)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            df = df.to_frame().reset_index()
            df.columns = ["Metric", "Value"]
            return df
        except KeyError as e:
            logger.log(2, e)
            return pd.DataFrame()

    def get_historical_blockchain_data(self, symbol="ETH", limit=365, **kwargs):
        try:
            data = self._get_historical_blockchain_data(symbol, limit, **kwargs)[
                "Data"
            ]["Data"]
            df = pd.DataFrame(data)
            df["time"] = pd.to_datetime(df["time"], unit="s")
            df.drop(
                [
                    "id",
                    "block_height",
                    "hashrate",
                    "difficulty",
                    "block_time",
                    "block_size",
                ],
                axis=1,
                inplace=True,
            )

            return df
        except KeyError as e:
            logger.log(2, e)
            return pd.DataFrame()

    def get_latest_trading_signals(self, symbol="ETH", **kwargs):
        data = self._get_latest_trading_signals(symbol, **kwargs)["Data"]
        df = pd.DataFrame(data)
        try:
            df.drop(["id", "partner_symbol"], inplace=True, axis=1)
            df["time"] = pd.to_datetime(df["time"], unit="s")
        except KeyError as e:
            logger.log(2, e)
        return df

    def get_order_books_exchanges(self, **kwargs):
        data = self._get_order_books_exchanges(**kwargs)["Data"]
        df = pd.DataFrame(data).T
        df["orderBookAvailability"] = df["orderBookAvailability"].apply(
            lambda x: ", ".join(x) if isinstance(x, list) else x
        )
        return df

    def get_order_book_top(
        self, symbol="LUNA", to_symbol="BTC", exchange="binance", **kwargs
    ):

        data = self._get_order_book_top(
            symbol.upper(), to_symbol.upper(), exchange.capitalize(), **kwargs
        )["Data"]
        if not data:
            return pd.DataFrame()
        df = pd.json_normalize(data["RAW"])
        df.columns = [c.replace(".", "_") for c in df.columns]
        df.drop(df.columns[0], axis=1, inplace=True)
        return df

    def get_order_book_snapshot(
        self, symbol="LUNA", to_symbol="BTC", exchange="binance", **kwargs
    ):
        data = self._get_order_book_snapshot(symbol, to_symbol, exchange, **kwargs)[
            "Data"
        ]
        bid = pd.DataFrame(data.pop("BID"))
        ask = pd.DataFrame(data.pop("ASK"))
        bid.columns = ["Bid_price", "Bid_Quantity"]
        ask.columns = ["Ask_price", "Ask_Quantity"]
        df = pd.concat([ask, bid], axis=1)
        df["Exchange"] = data.get("M")
        df["From_Symbol"] = data.get("FSYM")
        df["To_Symbol"] = data.get("FSYM")
        return df

    def get_all_exchanges_info(self, symbol="BTC", **kwargs):
        data = self._get_all_exchanges_info(symbol, **kwargs)["Data"]
        return pd.DataFrame(data).T

    def get_all_exchanges_names(self):
        exchanges = list(
            self._get_all_exchanges_and_trading_pairs()["Data"]["exchanges"].keys()
        )
        df = pd.Series(exchanges).to_frame().reset_index()
        df.columns = ["Index", "Name"]
        return df

    def get_all_wallet_info(self, **kwargs):
        data = self._get_all_wallet_info(**kwargs)["Data"]
        df = pd.DataFrame(data).T
        cols = [
            "Name",
            # "Security",
            "Anonymity",
            "EaseOfUse",
            # "WalletFeatures",
            "Coins",
            # "Platforms",
            # "SourceCodeUrl",
            "Avg",
            "Votes",
        ]
        df["Avg"] = df["Rating"].apply(lambda x: x.get("Avg"))
        df["Votes"] = df["Rating"].apply(lambda x: x.get("TotalUsers"))
        joins = ["WalletFeatures", "Platforms", "Coins"]
        for col in joins:
            df[col] = df[col].apply(lambda x: ", ".join(x))

        df = df[cols].sort_values(by="Votes", ascending=False)
        df = df.applymap(
            lambda x: "\n".join(textwrap.wrap(x, width=85)) if isinstance(x, str) else x
        )
        return df

    def get_all_gambling_info(self, **kwargs):
        data = self._get_all_gambling_info(**kwargs)["Data"]
        df = pd.DataFrame(data).T
        columns = [
            "Name",
            "GameTypes",
            "Coins",
            # "GamblingFeatures",
            # "Platforms",
            "Twitter",
            "Reddit",
            "Avg",
            "Votes",
        ]
        joins = [
            "GameTypes",
            "Coins",
        ]
        df["Avg"] = df["Rating"].apply(lambda x: x.get("Avg"))
        df["Votes"] = df["Rating"].apply(lambda x: x.get("TotalUsers"))

        for col in joins:
            df[col] = df[col].apply(lambda x: ", ".join(x))

        df = df[columns].sort_values(by="Votes", ascending=False)

        df = df.applymap(
            lambda x: "\n".join(textwrap.wrap(x, width=55)) if isinstance(x, str) else x
        )
        return df

    def get_recommended_wallets(self, symbol="BTC", **kwargs):
        try:
            data = self._get_recommendations(symbol, **kwargs)["Data"]["wallets"]
            df = pd.DataFrame(data).T
            cols = [
                "Name",
                "Security",
                "Anonymity",
                "EaseOfUse",
                # "WalletFeatures",
                "Coins",
                # "Platforms",
                "SourceCodeUrl",
                "Avg",
                "Votes",
            ]
            df["Avg"] = df["Rating"].apply(lambda x: x.get("Avg"))
            df["Votes"] = df["Rating"].apply(lambda x: x.get("TotalUsers"))
            joins = ["WalletFeatures", "Platforms", "Coins"]
            for col in joins:
                df[col] = df[col].apply(lambda x: ", ".join(x))
            df = wrap_text_in_df(df, w=40)
            return df[cols].sort_values(by="Votes", ascending=False)
        except KeyError as e:
            logger.log(2, e)
            return pd.DataFrame()

    def get_recommended_exchanges(self, symbol="BTC", **kwargs):
        try:
            data = self._get_recommendations(symbol, **kwargs)["Data"]["exchanges"]
            df = pd.DataFrame(data).T
            columns = [
                "Name",
                "ItemType",
                "CentralizationType",
                "GradePoints",
                "Grade",
                "Country",
                "DepositMethods",
                "Avg",
                "Votes",
            ]
            for col in ["FullAddress", "DepositMethods", "WithdrawalMethods"]:
                df[col] = df[col].apply(lambda x: x.replace("\n\n", ", "))
                df[col] = df[col].apply(lambda x: x.replace(",\n", ", "))
                df[col] = df[col].apply(lambda x: x.replace("\n", ", "))
            df["Avg"] = df["Rating"].apply(lambda x: x.get("Avg"))
            df["Votes"] = df["Rating"].apply(lambda x: x.get("TotalUsers"))
            df["ItemType"] = df["ItemType"].apply(lambda x: ", ".join(x))
            df = wrap_text_in_df(df, w=40)
            return df[columns].sort_values(by="Votes", ascending=False)
        except KeyError as e:
            logger.log(2, e)
            return pd.DataFrame()
