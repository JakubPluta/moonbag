from pycoingecko import CoinGeckoAPI
import json
from gateways.crypto.utils import find_discord, filter_list, calculate_time_delta
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
    date = dt.datetime.now(timezone.utc)
    params = dict(localization="false", tickers="false", sparkline=True)
    info = cg.get_coin_by_id(coin_id, **params)
    links = info.get('links')
    repos = links.get("repos_url")
    platforms = info.get("platforms")
    dev = info.get('developer_data')
    market_data = info.get('market_data')
    if dev:
        del dev['last_4_weeks_commit_activity_series']

    return dict(
        id=info.get("id"),
        symbol=info.get("symbol"),
        name=info.get("name"),
        contract=info.get('contract_address'),
        categories=info.get("categories"),
        description=info.get("description").get("en"),
        twitter=links.get("twitter_screen_name"),
        telegram=links.get("telegram_channel_identifier"),
        subreddit=links.get("subreddit_url"),
        github=repos.get("github") if repos else None,
        bitbucket=repos.get("bitbucket") if repos else None,
        platforms=[k for k, v in platforms.items() if platforms],
        homepage=filter_list(links.get("homepage")) if links.get("homepage") else None,
        forums = filter_list(links.get('official_forum_url')) if links.get('official_forum_url') else None ,
        explorers=filter_list(links.get("blockchain_site")) if links.get("blockchain_site") else None,
        discord=find_discord(links.get('chat_url')),
        bitcointalk=links.get('bitcointalk_thread_identifier'),
        sentiment = info.get('sentiment_votes_up_percentage'),
        market_cap_rank = info.get('market_cap_rank'),
        gecko_rank= info.get('coingecko_rank'),
        scores={
            'coingecko' : info.get('coingecko_score'),
            'developers' : info.get('developer_score'),
            'community' : info.get('community_score'),
            'liquidity' : info.get('liquidity_score'),
            'public_interest' : info.get('public_interest_score'),
        },
        community_data = info.get('community_data'),
        developer_data = dev,
        public_interest=info.get('public_interest_stats'),
        ath_price= {
            'usd' : market_data.get('ath').get('usd'),
            'eth':  market_data.get('ath').get('eth'),
            'btc':  market_data.get('ath').get('btc'),
        },
        pct_from_ath =
        {
            'usd': market_data.get('ath_change_percentage').get('usd'),
            'eth': market_data.get('ath_change_percentage').get('eth'),
            'btc': market_data.get('ath_change_percentage').get('btc'),
        },
        ath_date =
        {
            'usd': market_data.get('ath_date').get('usd'),
            'eth': market_data.get('ath_date').get('eth'),
            'btc': market_data.get('ath_date').get('btc'),
        },
        days_from_ath=
        {
            'usd': calculate_time_delta(market_data.get('ath_date').get('usd')),
            'eth': calculate_time_delta(market_data.get('ath_date').get('eth')),
            'btc': calculate_time_delta(market_data.get('ath_date').get('btc')),
        },
        market_cap = {
            'usd': market_data.get('market_cap').get('usd'),
            'eth': market_data.get('market_cap').get('eth'),
            'btc': market_data.get('market_cap').get('btc'),
        },

        fully_diluted_valuation = {
        'usd': market_data.get('fully_diluted_valuation').get('usd'),
        'eth': market_data.get('fully_diluted_valuation').get('eth'),
        'btc': market_data.get('fully_diluted_valuation').get('btc'),
        }

    )



import pprint

r = coin_info('uniswap')
pprint.pprint(r)


