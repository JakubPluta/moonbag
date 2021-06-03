import pandas as pd
import requests
import datetime

# https://github.com/RaidasGrisk/reddit-coin-app/blob/master/app/main.py
# https://github.com/ssp0929/crypto-trend-tracker/tree/master/input_data


def get_fng(limit=60):
    url = f"https://api.alternative.me/fng/?limit={limit}"
    data = requests.get(url=url).json()['data']
    df = pd.DataFrame(data)[['timestamp','value_classification','value']]
    df['timestamp'] = df['timestamp'].apply(lambda x: datetime.datetime.fromtimestamp((int(x))))
    return df

