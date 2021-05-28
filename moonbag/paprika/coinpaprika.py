import pandas as pd
import logging
import textwrap
from moonbag.paprika._client import Client
from moonbag.common.utils import wrap_headers_in_dataframe as header_wrapper


class CoinPaprika(Client):
    def __init__(self):
        super().__init__()
        self._coins_list = self._get_coins()

    def _get_coins_info(self, quotes="USD"):
        tickers = self._get_tickers_for_all_coins(quotes)
        data = pd.json_normalize(tickers)
        try:
            data.columns = [
                col.replace("quotes.USD.", "") for col in data.columns.tolist()
            ]
        except KeyError as e:
            logging.error(e)

        data["name"] = data["name"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=20)) if isinstance(x, str) else x
        )
        return data

    def get_coins(self):
        df = pd.DataFrame(self._get_coins())
        df = df[df["is_active"] != False]
        return df[["rank", "id", "name", "symbol", "is_new", "type"]]

    def get_coin_exchanges_by_id(self, coin_id="eth-ethereum"):
        df = pd.DataFrame(self._get_coin_exchanges_by_id(coin_id))
        df["fiats"] = df["fiats"].apply(
            lambda x: [i.get("symbol") for i in x if x and len(x) > 0]
        )
        print(df)
        return df

    def get_coin_events_by_id(self, coin_id="eth-ethereum"):
        res = self._get_coin_events_by_id(coin_id)
        if not res:
            return pd.DataFrame()
        data = pd.DataFrame(res)
        data["description"] = data["description"].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=30)) if isinstance(x, str) else x
        )
        data.drop('id', axis=1, inplace=True)
        return data

    def get_coin_twitter_timeline(self, coin_id="eth-ethereum"):
        res = self._get_coin_twitter_timeline(coin_id)
        if "error" in res:
            print(res)
            return pd.DataFrame()
        df = pd.DataFrame(res)
        return df[["date", "user_name", "status", "retweet_count", "like_count"]]

    def get_all_contract_platforms(
        self,
    ):
        return pd.DataFrame(self._get_all_contract_platforms())

    def get_coins_info(self):
        cols = [
            "rank",
            "name",
            "symbol",
            "price",
            "volume_24h",
            "circulating_supply",
            "total_supply",
            "max_supply",
            "market_cap",
            "beta_value",
            "ath_price",
        ]
        coins = self._get_coins_info()
        df = pd.DataFrame(coins)[cols]
        df.columns = header_wrapper(df, n=12, replace='_')
        return df.sort_values(by="rank")

    def get_coins_market_info(self):
        cols = [
            "rank",
            "name",
            "symbol",
            "price",
            "volume_24h",
            "market_cap_change_24h",
            "percent_change_1h",
            "percent_change_24h",
            "percent_change_7d",
            "percent_change_30d",
            "ath_price",
            "percent_from_price_ath",
        ]
        coins = self._get_coins_info()
        df = pd.DataFrame(coins)[cols]
        df.columns = header_wrapper(df, n=12, replace='_')
        return df.sort_values(by="rank")

    def get_tickers_for_coin(self):
        df = pd.json_normalize(self._get_tickers_for_coin()).T.reset_index()
        df.columns = ["Metric", "Value"]
        return df

    def get_exchanges_info(self):
        data = pd.json_normalize(self._get_exchanges())
        try:
            data.columns = [
                col.replace("quotes.USD.", "") for col in data.columns.tolist()
            ]
        except KeyError as e:
            logging.error(e)
        df = data[data["active"]]
        cols = [
            "adjusted_rank",
            "name",
            "currencies",
            "markets",
            "fiats",
            "confidence_score",
            "reported_volume_24h",
            "reported_volume_7d",
            "reported_volume_30d",
            "sessions_per_month",
        ]
        df["fiats"] = (
            df["fiats"].copy().apply(lambda x: len([i["symbol"] for i in x if x]))
        )
        df = df[cols]
        df.columns = header_wrapper(df, n=12, replace='_')
        df = df.applymap(
            lambda x: "\n".join(textwrap.wrap(x, width=28)) if isinstance(x, str) else x
        )
        return df.sort_values(by="adjusted\nrank")

    def get_exchanges_market(self, exchange_id="binance", quotes="USD"):
        data = self._get_exchange_markets(exchange_id, quotes)
        if "error" in data:
            logging.error(f"Wrong exchange_id: {exchange_id}")
            return pd.DataFrame()
        cols = [
            "pair",
            "base_currency_name",
            "quote_currency_name",
            "market_url",
            "category",
            "reported_volume_24h_share",
            "trust_score",
        ]
        df = pd.DataFrame(data)[cols]
        df.columns = header_wrapper(df, n=15, replace='_')
        return df

    def search(self, q):
        results = []
        data = self._search(q)
        for item in data:
            category = data[item]
            for r in category:
                results.append(
                    {
                        "Category": item,
                        "Id": r.get("id"),
                        "Name": r.get("name"),
                    }
                )
        return pd.DataFrame(results)

