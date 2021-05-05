import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os
import cachetools.func
from retry import retry
from gateways.cryptocompare._client import CryptoCompareClient
from gateways.utils import table_formatter

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)
# pd.set_option('display.max_colwidth', 30)

load_dotenv()

API_KEY = os.getenv("CC_API_KEY")


class CryptoCompare(CryptoCompareClient):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.api_key = api_key
        self.coin_list = self.get_all_coins_list()

    @table_formatter
    def get_price(self, symbol="BTC", currency="USD", **kwargs):
        data = self._get_price(symbol, currency, **kwargs)["RAW"][symbol][currency]
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
        return pd.Series(data)

    @table_formatter
    def get_top_list_by_market_cap(self, currency="USD", limit=100, **kwargs):
        data = self._get_top_list_by_market_cap(currency, limit, **kwargs)["Data"]
        data = [{"CoinInfo": d.get("CoinInfo"), "RAW": d.get("RAW")} for d in data]
        df = pd.json_normalize(data)
        df.columns = [col.split(".")[-1] for col in list(df.columns)]
        df["Url"] = df["Url"].apply(lambda x: self.COMPARE_URL + x)
        return df

    @table_formatter
    def get_top_exchanges(self, symbol="BTC", currency="USD", limit=100, **kwargs):
        data = self._get_top_exchanges(symbol, currency, limit, **kwargs)["Data"][
            "Exchanges"
        ]
        return pd.json_normalize(data)

    @table_formatter
    def get_exchanges_top_symbols_by_volume(
        self, exchange="Binance", limit=100, **kwargs
    ):
        data = self._get_exchanges_top_symbols_by_volume(exchange, limit, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df["volume"] = df["volume"].apply(lambda x: float(x))
        df = df[df["volume"] > 0]
        return df

    @table_formatter
    def get_top_list_by_pair_volume(self, currency="USD", limit=100, **kwargs):
        data = self._get_top_list_by_pair_volume(currency, limit, **kwargs)["Data"]
        return pd.DataFrame(data)

    @table_formatter
    def get_top_of_trading_pairs(self, symbol="ETH", limit=50, **kwargs):
        data = self._get_top_of_trading_pairs(symbol, limit, **kwargs)["Data"]
        return pd.DataFrame(data)

    def get_latest_social_coin_stats(self, coin_id=7605, **kwargs):
        data = self._get_latest_social_coin_stats(coin_id, **kwargs)["Data"]
        social_stats = {}
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
            df[col] = pd.to_datetime(df[col], unit="s")
        return df.T

    def get_historical_social_stats(
        self, coin_id=7605, limit=104, aggregate=7, **kwargs
    ):
        data = self._get_historical_social_stats(coin_id, limit, aggregate, **kwargs)[
            "Data"
        ]
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
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
        return df.set_index("published_on")

    def get_blockchain_available_coins_list(self):
        data = self._get_blockchain_available_coins_list()["Data"]
        df = pd.DataFrame(data).T
        df["data_available_from"] = pd.to_datetime(df["data_available_from"], unit="s")
        return df.set_index("id")

    def get_all_coins_list(self, summary="true", **kwargs):
        data = self._get_all_coins_list(summary, **kwargs)["Data"]
        return pd.DataFrame(data).T[["Id", "Symbol", "FullName"]].set_index("Id")

    @table_formatter
    def get_historical_day_prices(self, symbol="BTC", currency="USD", limit=365, **kwargs):
        data = self._get_historical_day_prices(symbol, currency, limit, **kwargs)['Data']
        df = pd.DataFrame(data)
        df.drop(['volumefrom','conversionType','conversionSymbol'],axis=1, inplace=True)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df.set_index('time')

    @table_formatter
    def get_historical_day_prices(self, symbol="BTC", currency="USD", limit=365, **kwargs):
        data = self._get_historical_day_prices(symbol, currency, limit, **kwargs)['Data']
        df = pd.DataFrame(data)
        df.drop(['volumefrom','conversionType','conversionSymbol'],axis=1, inplace=True)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df.set_index('time')

    @table_formatter
    def get_historical_hour_prices(self, symbol="BTC", currency="USD", limit=60*24, **kwargs):
        data = self._get_historical_hour_prices(symbol, currency, limit, **kwargs)['Data']
        df = pd.DataFrame(data)
        df.drop(['volumefrom','conversionType','conversionSymbol'],axis=1, inplace=True)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df.set_index('time')

    @table_formatter
    def get_historical_minutes_prices(self, symbol="BTC", currency="USD", limit=60*24, **kwargs):
        data = self._get_historical_minutes_prices(symbol, currency, limit, **kwargs)['Data']
        df = pd.DataFrame(data)
        df.drop(['volumefrom', 'conversionType', 'conversionSymbol'], axis=1, inplace=True)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df.set_index('time')

    @table_formatter
    def get_daily_exchange_volume(self, currency="USD", exchange="CCCAGG", limit=365, **kwargs):
        data = self._get_daily_exchange_volume(currency, exchange, limit, **kwargs)['Data']
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    @table_formatter
    def get_hourly_exchange_volume(
        self, currency="USD", exchange="CCCAGG", limit=60 * 24, **kwargs
    ):
        data = self._get_hourly_exchange_volume(currency, exchange, limit, **kwargs)['Data']
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    @table_formatter
    def get_daily_symbol_volume(
        self, symbol="BTC", currency="USD", limit=365, **kwargs
    ):
        data = self._get_daily_symbol_volume(symbol, currency, limit, **kwargs)['Data']
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df[[
             'time','top_tier_volume_total', 'total_volume_total'
        ]].set_index('time')

    @table_formatter
    def get_hourly_symbol_volume(
        self, symbol="BTC", currency="USD", limit=365, **kwargs
    ):
        data = self._get_hourly_symbol_volume(symbol, currency, limit, **kwargs)['Data']
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df[[
             'time','top_tier_volume_total', 'total_volume_total'
        ]].set_index('time')

    def get_latest_blockchain_data(self, symbol="BTC", **kwargs):
        data = self._get_latest_blockchain_data(symbol, **kwargs)['Data']
        df = pd.Series(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    @table_formatter
    def get_historical_blockchain_data(self, symbol="ETH", limit=365, **kwargs):
        data = self._get_historical_blockchain_data(symbol, limit, **kwargs)['Data']['Data']
        df = pd.DataFrame(data)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        df.drop(['id','block_height', 'hashrate','difficulty' ,'block_time' , 'block_size'], axis=1, inplace=True)
        return df.set_index('time')

    def get_latest_trading_signals(self, symbol="ETH", **kwargs):
        data = self._get_latest_trading_signals(symbol, **kwargs)['Data']
        df = pd.DataFrame(data)
        df.drop(['id','partner_symbol'],inplace=True,axis=1)
        df["time"] = pd.to_datetime(df["time"], unit="s")
        return df

    def get_order_books_exchanges(self, **kwargs):
        data = self._get_order_books_exchanges(**kwargs)['Data']
        df = pd.DataFrame(data).T
        df['orderBookAvailability'] = df['orderBookAvailability'].apply(lambda x: ', '.join(x) if isinstance(x, list) else x)
        return df

    def get_order_book_top(
        self, symbol="LUNA", to_symbol="BTC", exchange="binance", **kwargs
    ):
        data = self._get_order_book_top(symbol, to_symbol, exchange, **kwargs)['Data']['RAW']
        df = pd.json_normalize(data)
        df.columns = [c.replace('.','_') for c in df.columns]
        df.drop(df.columns[0], axis=1, inplace=True)
        return df

    def get_order_book_snapshot(
            self, symbol="LUNA", to_symbol="BTC", exchange="binance", **kwargs
    ):
        data = self._get_order_book_snapshot(symbol, to_symbol, exchange, **kwargs)['Data']
        bid = pd.DataFrame(data.pop('BID'))
        ask = pd.DataFrame(data.pop('ASK'))
        bid.columns = ['Bid_price','Bid_Quantity']
        ask.columns = ['Ask_price','Ask_Quantity']
        df = pd.concat([ask,bid],axis=1)
        df['Exchange'] = data.get('M')
        df['From_Symbol'] = data.get('FSYM')
        df['To_Symbol'] = data.get('FSYM')
        return df

    def get_all_exchanges_info(self, symbol="BTC", **kwargs):
        data = self._get_all_exchanges_info(symbol, **kwargs)['Data']
        return pd.DataFrame(data).T

    def get_all_wallet_info(self, **kwargs):
        data = self._get_all_wallet_info( **kwargs)['Data']
        df = pd.DataFrame(data).T
        cols = ['Name','Security','Anonymity', 'EaseOfUse','WalletFeatures', 'Coins', 'Platforms',
        'SourceCodeUrl','Avg','Votes']
        df['Avg'] = df['Rating'].apply(lambda x: x.get('Avg'))
        df['Votes'] = df['Rating'].apply(lambda x: x.get('TotalUsers'))
        joins = ['WalletFeatures','Platforms','Coins']
        for col in joins:
            df[col] = df[col].apply(lambda x: ', '.join(x))
        return df[cols].sort_values(by='Votes', ascending=False).set_index('Name')

    def get_all_gambling_info(self, **kwargs):
        data = self._get_all_gambling_info(**kwargs)['Data']
        df = pd.DataFrame(data).T
        columns = ['Name', 'GameTypes', 'Coins',
         'GamblingFeatures', 'Platforms', 'Twitter', 'Reddit',
         'Avg','Votes']
        joins = ['GameTypes', 'Coins',
         'GamblingFeatures', 'Platforms',]
        df['Avg'] = df['Rating'].apply(lambda x: x.get('Avg'))
        df['Votes'] = df['Rating'].apply(lambda x: x.get('TotalUsers'))

        for col in joins:
            df[col] = df[col].apply(lambda x: ', '.join(x))

        return df[columns].sort_values(by='Votes', ascending=False).set_index('Name')

    def get_recommended_wallets(self, symbol="BTC", **kwargs):
        data = self._get_recommendations(symbol, **kwargs)['Data']['wallets']
        df = pd.DataFrame(data).T
        cols = ['Name', 'Security', 'Anonymity', 'EaseOfUse', 'WalletFeatures', 'Coins', 'Platforms',
                'SourceCodeUrl', 'Avg', 'Votes']
        df['Avg'] = df['Rating'].apply(lambda x: x.get('Avg'))
        df['Votes'] = df['Rating'].apply(lambda x: x.get('TotalUsers'))
        joins = ['WalletFeatures', 'Platforms', 'Coins']
        for col in joins:
            df[col] = df[col].apply(lambda x: ', '.join(x))
        return df[cols].sort_values(by='Votes', ascending=False).set_index('Name')

    def get_recommended_exchanges(self, symbol="BTC", **kwargs):
        data = self._get_recommendations(symbol, **kwargs)['Data']['exchanges']
        df = pd.DataFrame(data).T
        columns = ['Name',  'ItemType', 'CentralizationType', 'GradePoints', 'Grade',
                    'Country',
                   'FullAddress', 'DepositMethods',
                   'WithdrawalMethods',
                   'Avg', 'Votes']
        for col in ['FullAddress', 'DepositMethods',
                   'WithdrawalMethods']:
            df[col] = df[col].apply(lambda x: x.replace('\n\n', ', '))
            df[col] = df[col].apply(lambda x: x.replace(',\n', ', '))
            df[col] = df[col].apply(lambda x: x.replace('\n', ', '))
        df['Avg'] = df['Rating'].apply(lambda x: x.get('Avg'))
        df['Votes'] = df['Rating'].apply(lambda x: x.get('TotalUsers'))
        df['ItemType'] = df['ItemType'].apply(lambda x: ', '.join(x))
        return df[columns].set_index('Name').sort_values(by='Votes',ascending=False)

c = CryptoCompare(API_KEY)
print(c.get_recommended_exchanges())