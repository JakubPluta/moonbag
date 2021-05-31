from moonbag.onchain.ethereum.utils import (
    enrich_social_media,
    split_cols,
)
from moonbag.onchain.ethereum._client import EthplorerClient
import logging
import pandas as pd
from datetime import datetime


class Eth(EthplorerClient):
    def __init__(self, api_key=None):
        super().__init__(api_key)

    def get_token_info(self, address):
        token = self._get_token_info(address)

        for v in [
            "decimals",
            "issuancesCount",
            "lastUpdated",
            "image",
            "transfersCount",
            "ethTransfersCount",
        ]:
            try:
                token.pop(v)
            except KeyError as e:
                logging.info(e)
        enrich_social_media(token)
        df = pd.json_normalize(token)
        df.columns = [split_cols(x) for x in df.columns.tolist()]
        if "priceTs" in df:
            df.drop("priceTs", axis=1, inplace=True)
        return df.T.reset_index()

    def get_tx_info(self, tx_hash):
        tx = self._get_tx_info(tx_hash)
        if 'error' in tx:
            return pd.DataFrame(tx).reset_index()
        try:
            tx.pop("logs")
            operations = tx.pop("operations")[0]
            if operations:
                operations.pop("addresses")
                token = operations.pop("tokenInfo")
                if token:
                    operations["token"] = token["name"]
                    operations["tokenAddress"] = token["address"]
                operations["timestamp"] = datetime.fromtimestamp(operations["timestamp"])
            tx.update(operations)
            df = pd.Series(tx).to_frame().reset_index()
            df.columns = ["Metric", "Value"]
        except KeyError as e:
            logging.info(e)
            return pd.DataFrame()
        return df

    def get_token_history(self, address):
        op = self._get_token_history(address)
        ops = []
        if 'error' in op:
            return pd.DataFrame(op).reset_index()
        try:
            operations = op["operations"]
            try:
                frow = operations[0]["tokenInfo"]
                name, addr = frow["name"], frow["address"]
                print(f"Fetching operations for {name}: {addr}\n")
            except Exception as e:
                logging.error(f"Didn't find data for {address}")
            for o in operations:
                o.pop("type")
                o.pop("tokenInfo")
                o["timestamp"] = datetime.fromtimestamp(o["timestamp"])
                ops.append(o)
        except KeyError as e:
            logging.error(e)
        return pd.DataFrame(ops)  # , (name, addr)

    def get_address_info(self, address):
        addr = self._get_address_info(address)
        if 'error' in addr:
            return pd.DataFrame(addr).reset_index()
        print(
            f"Fetching data for {address}. This address made {addr.get('countTxs')} transactions"
        )

        tokens = addr.pop("tokens")
        for token in tokens:
            token_info = token.pop("tokenInfo")
            t = {
                "tokenName": token_info["name"],
                "tokenSymbol": token_info["symbol"],
                "tokenAddress": token_info["address"],
            }
            token.update(t)
        return pd.DataFrame(tokens)[
            [
                "tokenName",
                "tokenSymbol",
                "tokenAddress",
                "rawBalance",
                "totalIn",
                "totalOut",
            ]
        ]

    def get_address_transactions(self, address):
        tx = self._get_address_transactions(address)
        if 'error' in tx:
            return pd.DataFrame(tx).reset_index()
        try:
            df = pd.DataFrame(tx)[["timestamp", "from", "to", "hash"]]
            df["timestamp"] = df["timestamp"].apply(lambda x: datetime.fromtimestamp(x))
        except Exception as e:
            logging.info(e)
            return pd.DataFrame()
        return df

    def get_address_history(self, address):
        tx = self._get_address_history(address)
        if 'error' in tx:
            return pd.DataFrame(tx).reset_index()
        operations = tx.pop("operations")
        if operations:
            for operation in operations:
                token = operation.pop("tokenInfo")
                if token:
                    operation["token"] = token["name"]
                    operation["tokenAddress"] = token["address"]
                operation["timestamp"] = datetime.fromtimestamp(operation["timestamp"])

        df = pd.DataFrame(operations)
        return df[["timestamp", "from", "to", "transactionHash"]]

    def get_top_token_holders(self, address):
        d = self._get_top_token_holders(address)
        if "error" in d:
            logging.info(d["error"])
            return pd.DataFrame(d).reset_index()
        return pd.DataFrame(d["holders"]).reset_index()

    def get_top_tokens(self):
        t = self._get_top_tokens()
        if 'error' in t:
            return pd.DataFrame(t).reset_index()
        tokens = t["tokens"]
        df = pd.DataFrame(tokens)
        cols = [
            "name",
            "symbol",
            "txsCount",
            "transfersCount",
            "holdersCount",
            "address",
            "twitter",
            "coingecko",
        ]
        return df[cols]

    def _get_token_price_history_helper(self, address):
        hist = self._get_token_price_history_grouped(address)
        if 'error' in hist:
            return pd.DataFrame(hist).reset_index()
        data = hist["history"]
        current = data.pop("current")
        txs = []
        for i in data["countTxs"]:
            txs.append({"ts": i["ts"], "cnt": i["cnt"]})
        txs_df = pd.DataFrame(txs)
        txs_df["ts"] = txs_df["ts"].apply(lambda x: datetime.fromtimestamp(x))
        prices_df = pd.DataFrame(data["prices"])
        prices_df["ts"] = prices_df["ts"].apply(lambda x: datetime.fromtimestamp(x))
        prices_df.drop("tmp", axis=1, inplace=True)
        return prices_df, txs_df

    def get_token_historical_price(self, address):
        try:
            df = self._get_token_price_history_helper(address)[0]
        except Exception as e:
            logging.info(e)
            return pd.DataFrame()
        return df

    def get_token_historical_txs(self, address):
        try:
            df = self._get_token_price_history_helper(address)[1]
        except Exception as e:
            logging.info(e)
            return pd.DataFrame()
        return df
