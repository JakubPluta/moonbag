import json
import requests
import time
from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("WALES_API_KEY")


def get_wales_stats(min_value=1000000):
    req = f"https://api.whale-alert.io/v1/transactions?api_key={API_KEY}"
    params = {"min_value": min_value, "start": int(time.time()) - 3000}
    return requests.get(url=req, params=params).json()
