from pycoingecko import CoinGeckoAPI
import json
from utils import (
    find_discord,
    filter_list,
    calculate_time_delta,
    get_eth_addresses_for_cg_coins,
)
import pandas as pd

COINS = "gecko_coins.json"


class Exchanges:
    def __init__(self):
        self._exchanges = []
        self._ids = set()

    def from_list_of_dicts(self, exchanges: [dict]):
        for e in exchanges:
            self.add_exchange(e)

    @staticmethod
    def _create_df(exchange: dict):
        df = pd.DataFrame(exchange, index=[0]).set_index("id")
        return df

    def add_exchange(self, exchange: dict):
        if exchange.get("id") and exchange.get("id") not in self._ids:
            exchange = self._create_df(exchange)
            self._exchanges.append(exchange)

    @property
    def exchanges(self):
        return pd.concat(self._exchanges).sort_values(by="trust_score_rank")


class GeckoRepo:
    def __init__(self):
        self.client = CoinGeckoAPI()
        self._ex = Exchanges()

    def get_coins_list(self):
        try:
            data = get_eth_addresses_for_cg_coins(COINS)
        except FileNotFoundError as e:
            data = pd.DataFrame(self.client.get_coins_list(include_platforms="true"))
            data["ethereum"] = data["platforms"].apply(
                lambda x: x.get("ethereum") if "ethereum" in x else None
            )
        return data

    def _get_trends(self):
        trending = self.client.get_search_trending().get("coins")
        coins = (
            {"id": coin["item"].get("id")}
            for coin in trending
            if coin.get("item") is not None
        )
        return coins

    def get_trends(self, return_json=False):
        dfs, jsons = [], []
        for coin in self._get_trends():
            jsn = self.coin_info(coin.get("id"))
            df = pd.json_normalize(jsn)
            jsons.append(jsn)
            dfs.append(df)
        if return_json:
            return pd.concat(dfs).set_index("id"), jsons
        return pd.concat(dfs).set_index("id")

    def get_coin_info(self, coin_id: str):
        params = dict(localization="false", tickers="false", sparkline=True)
        info = self.client.get_coin_by_id(coin_id, **params)
        links = info.get("links")
        repos = links.get("repos_url")
        platforms = info.get("platforms")
        dev = info.get("developer_data")
        market_data = info.get("market_data")

        return dict(
            id=info.get("id"),
            symbol=info.get("symbol"),
            name=info.get("name"),
            contract=info.get("contract_address"),
            categories=info.get("categories"),
            description=info.get("description").get("en"),
            twitter=links.get("twitter_screen_name"),
            telegram=links.get("telegram_channel_identifier"),
            subreddit=links.get("subreddit_url"),
            github=repos.get("github") if repos else None,
            bitbucket=repos.get("bitbucket") if repos else None,
            platforms=[k for k, v in platforms.items() if platforms],
            homepage=filter_list(links.get("homepage"))
            if links.get("homepage")
            else None,
            forums=filter_list(links.get("official_forum_url"))
            if links.get("official_forum_url")
            else None,
            explorers=filter_list(links.get("blockchain_site"))
            if links.get("blockchain_site")
            else None,
            discord=find_discord(links.get("chat_url")),
            bitcointalk=links.get("bitcointalk_thread_identifier"),
            sentiment=info.get("sentiment_votes_up_percentage"),
            market_cap_rank=info.get("market_cap_rank"),
            gecko_rank=info.get("coingecko_rank"),
            scores={
                "coingecko": info.get("coingecko_score"),
                "developers": info.get("developer_score"),
                "community": info.get("community_score"),
                "liquidity": info.get("liquidity_score"),
                "public_interest": info.get("public_interest_score"),
            },
            community_data=info.get("community_data"),
            developer_data=dev,
            public_interest=info.get("public_interest_stats"),
            ath_price={
                "usd": market_data.get("ath").get("usd"),
                "eth": market_data.get("ath").get("eth"),
                "btc": market_data.get("ath").get("btc"),
            },
            pct_from_ath={
                "usd": market_data.get("ath_change_percentage").get("usd"),
                "eth": market_data.get("ath_change_percentage").get("eth"),
                "btc": market_data.get("ath_change_percentage").get("btc"),
            },
            ath_date={
                "usd": market_data.get("ath_date").get("usd"),
                "eth": market_data.get("ath_date").get("eth"),
                "btc": market_data.get("ath_date").get("btc"),
            },
            days_from_ath={
                "usd": calculate_time_delta(market_data.get("ath_date").get("usd")),
                "eth": calculate_time_delta(market_data.get("ath_date").get("eth")),
                "btc": calculate_time_delta(market_data.get("ath_date").get("btc")),
            },
            market_cap={
                "usd": market_data.get("market_cap").get("usd"),
                "eth": market_data.get("market_cap").get("eth"),
                "btc": market_data.get("market_cap").get("btc"),
            },
            fully_diluted_valuation={
                "usd": market_data.get("fully_diluted_valuation").get("usd"),
                "eth": market_data.get("fully_diluted_valuation").get("eth"),
                "btc": market_data.get("fully_diluted_valuation").get("btc"),
            },
            total_volume={
                "usd": market_data.get("total_volume").get("usd"),
                "eth": market_data.get("total_volume").get("eth"),
                "btc": market_data.get("total_volume").get("btc"),
            },
            high_24h={
                "usd": market_data.get("high_24h").get("usd"),
                "eth": market_data.get("high_24h").get("eth"),
                "btc": market_data.get("high_24h").get("btc"),
            },
            low_24h={
                "usd": market_data.get("low_24h").get("usd"),
                "eth": market_data.get("low_24h").get("eth"),
                "btc": market_data.get("low_24h").get("btc"),
            },
            price_change_24h=market_data.get("price_change_24h"),
            price_change_percentage_24h=market_data.get("price_change_percentage_24h"),
            price_change_percentage_7d=market_data.get("price_change_percentage_7d"),
            price_change_percentage_14d=market_data.get("price_change_percentage_14d"),
            price_change_percentage_30d=market_data.get("price_change_percentage_30d"),
            price_change_percentage_60d=market_data.get("price_change_percentage_60d"),
            price_change_percentage_1y=market_data.get("price_change_percentage_1y"),
            market_cap_change_24h=market_data.get("market_cap_change_24h"),
            market_cap_change_percentage_24h=market_data.get(
                "market_cap_change_percentage_24h"
            ),
            total_supply=market_data.get("total_supply"),
            max_supply=market_data.get("max_supply"),
            circulating_supply=market_data.get("circulating_supply"),
            total_value_locked=market_data.get("total_value_locked"),
            mcap_to_tvl_ratio=market_data.get("mcap_to_tvl_ratio"),
            fdv_to_tvl_ratio=market_data.get("fdv_to_tvl_ratio"),
        )

    def get_coin_data(self, id: str):
        return pd.Series(self.get_coin_info(id))

    def get_(self):
        pass

    def feed_exchanges(self):
        cl = self.client.get_exchanges_list()
        self._ex.from_list_of_dicts(cl)

    def show_exchanges(self):
        print(self._ex.exchanges)


gecoin = GeckoRepo()
# gr.feed_exchanges()
# gr.show_exchanges()

# print(gecoin.get_coin_data('uniswap'))
