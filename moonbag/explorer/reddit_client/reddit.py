import time

import pandas as pd
import textwrap
from moonbag.explorer.reddit_client._client import RedditClient, praw
import datetime
from typing import Union

CRYPTO_SUBREDDITS = [
    'CryptoCurrency',
    'CryptoMoonShots',
    'SatoshiStreetBets',
    'AltStreetBets',
    "altcoin",
    "dogecoin",
    "ethtrader",
    "bitcoin",
    "btc",
    "ethereum",
    "algotrading"

]

def created_date(timestamp):
    return datetime.datetime.fromtimestamp(timestamp)


class Reddit(RedditClient):
    subreddits = [
        'CryptoCurrency',
        'CryptoMoonShots',
        'SatoshiStreetBets',
        'AltStreetBets',
        "altcoin",
        "dogecoin",
        "ethtrader",
        "bitcoin"
    ]

    def get_subreddit(self, subreddit: str):
        sub = self._get_subbreddit(subreddit)
        return dict(
            id=sub.id,
            title=sub.title,
            name=sub.name,
            subscribers=sub.subscribers,
            created_date=created_date(sub.created),
            url=sub.url,
        )

    def get_subreddits(self, subreddits: list):
        return (self.get_subreddit(sub) for sub in subreddits)

    def get_submission(self, submission_id):
        s = self.client.submission(id=submission_id)
        return dict(
            created=created_date(s.created),
            score=s.score,
            upvotes=s.ups,
            shortlink=s.shortlink,
            title=s.title,
            comments=s.num_comments,
            subreddit_name_prefixed=s.subreddit_name_prefixed
        )

    def get_submissions(self, submission_ids: list):
        return (self._get_submission(submission_id) for submission_id in submission_ids)

    def get_submissions_for_subreddits(self, subreddits: Union[str,list], kind="top"):
        # kind = "top", "controversial", "hot"
        results = []
        if isinstance(subreddits, str):
            subreddits = [subreddits]
        for subreddit in subreddits:
            sub = self._get_subbreddit(subreddit)
            print(f"Fetching data for {sub}")
            if kind in ['top','controversial']:
                top = getattr(sub, kind)(time_filter='day')
            else:
                top = getattr(sub, kind)
            try:
                for s in top:
                    results.append(
                            dict(
                            created=created_date(s.created),
                            score=s.score,
                            upvotes=s.ups,
                            shortlink=s.shortlink,
                            title=s.title,
                            comments=s.num_comments,
                            subreddit_name_prefixed=s.subreddit_name_prefixed
                        ))
            except Exception as e:
                print(e)
        df = pd.DataFrame(results).sort_values(by='comments', ascending=False)
        df['title'] = df['title'].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=68)) if isinstance(x, str) else x
        )
        return df[df['comments'] >= 50]

    def get_comments_for_submission(self, submission_id):
        submission = self._get_submission(submission_id)
        data = [
            dict(
                id=c.id,
                submissionId=c.submission.id,
                subredditId=c.subreddit_id,
                author=c.author.name if c.author else None,
                body=c.body,
                score=c.score,
                upvotes=c.ups,
                created=created_date(c.created),
            )
            for c in submission.comments
            if not isinstance(c, praw.reddit.models.MoreComments)
        ]
        return pd.DataFrame(data)

    def discover_top_submissions(self, kind="top"):
        return self.get_submissions_for_subreddits(self.subreddits, kind)

    def search(self, query, data_type='submission'):
        now = (datetime.datetime.now() - datetime.timedelta(days=7)).timestamp()
        results = self._search_psaw_data(q=query,
                                        data_type=data_type,
                                        size=1000,
                                        sort_type="score",
                                        after=int(now),
                                        sort='desc',
                                         )
        data = results['data']
        results = []

        if data_type.lower() == 'comment':
            for s in data:
                results.append(
                    dict(
                        created=created_date(s.get('created_utc')),
                        #comments=s.get('num_comments'),
                        score=s.get('score'),
                        subreddit=s.get('subreddit'),
                        title=s.get('body'),

                    )
                )
        else:
            for s in data:
                results.append(
                    dict(
                        created=created_date(s.get('created_utc')),
                        comments=s.get('num_comments'),
                        score=s.get('score'),
                        subreddit=s.get('subreddit'),
                        title=s.get('title'),

                    )
                )
        df = pd.DataFrame(results).sort_values(by='score',ascending=False)
        df['title'] = df['title'].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=76)) if isinstance(x, str) else x
        )
        return df

    def get_popular_submissions(self):
        results = []
        for sub in CRYPTO_SUBREDDITS:
            print(f"Searching data for subreddit: {sub}")
            time.sleep(0.3)
            subm = self.psaw.search_submissions(subreddit=sub, limit=1000, score = ">50", after='7d')
            for s in subm:
                results.append(dict(
                        created=created_date(s.created_utc),
                        comments=s.num_comments,
                        score=s.score,
                        subreddit=s.subreddit,
                        title=s.title,

                    )
                )

        df = pd.DataFrame(results).sort_values(by='score', ascending=False)
        df['title'] = df['title'].apply(
            lambda x: "\n".join(textwrap.wrap(x, width=76)) if isinstance(x, str) else x
        )
        return df

a = Reddit()
from moonbag.common import print_table
print_table(a.search(query="Ethereum",data_type='comment'))
