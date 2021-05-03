import pandas as pd
import numpy as np
import requests
from dotenv import load_dotenv
import os
from gateways.cryptocompare._client import CryptoCompareClient

load_dotenv()

API_KEY = os.getenv("CC_API_KEY")


class CryptoCompare(CryptoCompareClient):
    def __init__(self, api_key):
        super().__init__(api_key)
        self.api_key = api_key
