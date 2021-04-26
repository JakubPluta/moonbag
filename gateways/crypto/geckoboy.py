from pycoingecko import CoinGeckoAPI
import json
from gateways.crypto.utils import find_discord, filter_list, calculate_time_delta, get_eth_addresses_for_cg_coins
import datetime as dt
from datetime import timezone
from dateutil import parser


cg = CoinGeckoAPI()





def get_trends():
    trending = cg.get_search_trending().get("coins")
    coins = (
        {"id": coin["item"].get("id")}
        for coin in trending
        if coin.get("item") is not None
    )
    return coins


def coin_info(coin_id: str):
    params = dict(localization="false", tickers="false", sparkline=True)
    info = cg.get_coin_by_id(coin_id, **params)
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
        homepage=filter_list(links.get("homepage")) if links.get("homepage") else None,
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


from pprint import pprint

#r = coin_info("sushi")

d = cg.get_exchanges_list()


from dataclasses import dataclass
import pandas as pd


class Exchanges:
    _columns = ['name', 'country', 'url',  'trust_score', 'trust_score_rank','trade_volume_24h_btc']

    def __init__(self):
        self.client = CoinGeckoAPI()
        self._meta = None
        self._exchanges = self.get_exchanges()

    def get_exchanges(self):
        self._meta = self.client.get_exchanges_list(per_page=250)
        return pd.DataFrame(self._meta).set_index('id')

    @property
    def exchanges(self):
        return self._exchanges[self._columns].sort_values(by='trust_score_rank')

    def check_exchange(self, id):
        for i in self._meta:
            if id == i.get('id'):
                return self.client.get_exchanges_by_id(id)



ex = Exchanges()

ex.get_exchanges()
print(ex.exchanges)

print(ex.check_exchange('binance'))