import praw
from functools import lru_cache
from moonbag.common import keys
from psaw import PushshiftAPI
import requests


class RedditClient:
    def __init__(self):
        self.client = praw.Reddit(
            client_id=keys.REDDIT_CLIENT_ID,
            client_secret=keys.REDDIT_CLIENT_SECRET,
            user_agent=keys.REDDIT_USER_AGENT,
        )
        self.psaw = PushshiftAPI()

    @lru_cache(maxsize=256)
    def _get_subbreddit(self, subreddit):
        return self.client.subreddit(subreddit)

    @lru_cache(maxsize=256)
    def _get_submission(self, submission_id):
        return self.client.submission(submission_id)

    @lru_cache(maxsize=256)
    def _get_comment(self, comment_id):
        return self.client.comment(comment_id)

    def _search_psaw_data(self, data_type, **kwargs):
        base_url = f"https://api.pushshift.io/reddit/{data_type}/search"
        payload = kwargs
        request = requests.get(base_url, params=payload)
        return request.json()
