import pandas as pd
import praw
import dotenv
import os
import textwrap

dotenv.load_dotenv()

sub = ['CryptoCurrency','CryptoMoonShots','SatoshiStreetBets','CryptoMarkets', 'AltStreetBets']

coins = [
    'ALGO', 'DASH', 'OXT', 'ATOM', 'KNC', 'XRP', 'REP', 'MKR', 'CGLD',
    'COMP', 'NMR', 'OMG', 'BAND', 'UMA', 'XLM', 'EOS', 'ZRX', 'BAT',
    'LOOM', 'UNI', 'YFI', 'LRC', 'CVC', 'DNT', 'MANA', 'GNT', 'REN',
    'LINK', 'BTC', 'BAL', 'LTC', 'ETH', 'BCH', 'ETC', 'USDC', 'ZEC',
    'XTZ', 'DAI', 'WBTC', 'NU', 'FIL', 'AAVE', 'SNX', 'BNT', 'GRT',
    'SUSHI', 'MATIC', 'ADA', 'ANKR', 'CRV', 'STORJ', 'SKL', '1INCH',
    'ENJ', 'NKN', 'OGN', 'DOGE', 'DOT', 'NEO', 'CEL', 'NANO', 'IOTA',
    'XMR', 'USDT', 'BNB', 'NEM', 'TRON', 'BTG', 'VET', 'SHIB', 'ICP',
    'MIR', 'RLC', 'FORTH', 'TRB', 'CTSI', 'XMR', 'LTO'
]


reddit = praw.Reddit(
    client_id=os.getenv('REDDIT_CLIENT_ID'),
            client_secret=os.getenv('REDDIT_CLIENT_SECRET'),
            user_agent=os.getenv('REDDIT_USER_AGENT'),
        )


import datetime

def created_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)

def trending():
    r = []
    for i in sub:
        s = reddit.subreddit(i)
        for h in s.top(time_filter='day'):
            if h.num_comments > 30:
                r.append({
                    'created': created_date(h.created),
                    'comments': h.num_comments,
                    'score': h.score,
                    'subreddit': h.subreddit_name_prefixed,
                    'awards': h.total_awards_received,
                    #'upratio': h.upvote_ratio,
                    'title': h.title,
                    "link": h.shortlink

                })

    #
    df = pd.DataFrame(r).sort_values(by='comments', ascending=False)
    df['title'] = df['title'].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=68)) if isinstance(x, str) else x
    )
    return df




# from moonbag.common import print_table
# a = trending()
# print_table(a)
