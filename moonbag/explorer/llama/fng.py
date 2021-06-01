import pandas as pd
import json
import requests
import time

# https://github.com/RaidasGrisk/reddit-coin-app/blob/master/app/main.py
# https://github.com/ssp0929/crypto-trend-tracker/tree/master/input_data
def get_fng(limit=30):
    req = f"https://api.alternative.me/fng/?limit={limit}"
    return requests.get(url=req).json()

print(get_fng(30))