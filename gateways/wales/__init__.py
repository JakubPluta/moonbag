# WKa0Wu3HlSnez3Ij6mcAVwiXk3sFtlHh
import json

api_key = "WKa0Wu3HlSnez3Ij6mcAVwiXk3sFtlHh"
import requests
import time

int(time.time())

req = f"https://api.whale-alert.io/v1/transactions?api_key={api_key}"  # +'&min_value=10000&start=1550237797'
params = {"min_value": 500000, "start": int(time.time()) - 3600}

df = requests.get(url=req, params=params)
with open("wales.json", "w") as f:
    json.dump(df.json(), f)
