from moonbag.onchain.ethereum.utils import manual_replace, enrich_social_media, split_cols
from moonbag.onchain.ethereum._client import EthplorerClient
import logging
import pandas as pd



class Eth(EthplorerClient):
    def __init__(self, api_key=None):
        super().__init__(api_key)

    def get_token_info(self, address):
        token = self._get_token_info(address)

        for v in ['decimals','issuancesCount','lastUpdated','image','transfersCount','ethTransfersCount']:
            try:
                token.pop(v)
            except KeyError as e:
                logging.error(e)
        enrich_social_media(token)
        df = pd.json_normalize(token)
        df.columns = [split_cols(x) for x in df.columns.tolist()]
        if 'priceTs' in df:
            df.drop('priceTs', axis=1, inplace=True)
        return df.T

    def get_tx_info(self, tx_hash):
        tx = self._get_tx_info(tx_hash)
        tx.pop('logs')
        operations = tx.pop('operations')[0]
        if operations:
            operations.pop('addresses')
            token = operations.pop('tokenInfo')
            if token:
                operations['token'] = token['name']
                operations['tokenAddress'] = token['address']
            operations['timestamp'] = datetime.fromtimestamp(operations['timestamp'])
        tx.update(operations)
        df = pd.Series(tx).to_frame().reset_index()
        df.columns = ['Metric', "Value"]
        return df

    def get_token_history(self, address):
        operations = self._get_token_history(address)['operations']
        ops = []
        try:
            frow = operations[0]['tokenInfo']
            name, addr = frow['name'], frow['address']
            print(f"Fetching operations for {name}: {addr}\n")
        except Exception as e:
            logging.error(f"Didn't find data for {address}")
        for o in operations:
            o.pop('type')
            o.pop('tokenInfo')
            o['timestamp'] = datetime.fromtimestamp(o['timestamp'])
            ops.append(o)

        return pd.DataFrame(ops) # , (name, addr)

    def get_address_info(self, address):
        addr = self._get_address_info(address)
        print(f"Fetching data for {address}. This address made {addr.get('countTxs')} transactions")
        tokens = addr.pop('tokens')
        for token in tokens:
            token_info = token.pop('tokenInfo')
            t = {
                "tokenName" : token_info['name'],
                "tokenSymbol" : token_info['symbol'],
                "tokenAddress" : token_info['address']

            }
            token.update(t)
        return pd.DataFrame(tokens)[["tokenName","tokenSymbol","tokenAddress","rawBalance","totalIn", "totalOut"]]

    def get_address_transactions(self, address):
        tx = self._get_address_transactions(address)
        try:
            df = pd.DataFrame(tx)[['timestamp','from','to','hash']]
            df['timestamp'] = df['timestamp'].apply(lambda x: datetime.fromtimestamp(x))
        except Exception as e:
            logging.error(e)
            return pd.DataFrame()
        return df

    def get_address_history(self, address):
        tx = self._get_address_history(address)
        operations = tx.pop('operations')
        if operations:
            for operation in operations:
                token = operation.pop('tokenInfo')
                if token:
                    operation['token'] = token['name']
                    operation['tokenAddress'] = token['address']
                operation['timestamp'] = datetime.fromtimestamp(operation['timestamp'])

        df = pd.DataFrame(operations)
        return df[['timestamp','from','to','transactionHash']]

    def get_top_token_holders(self, address):
        d = self._get_top_token_holders(address)
        if 'error' in d:
            logging.error(d['error'])
            return pd.DataFrame()
        return pd.DataFrame(d['holders']).reset_index()

    def get_top_tokens(self):
        tokens = self._get_top_tokens()['tokens']
        df = pd.DataFrame(tokens)
        cols = ['name', 'symbol','txsCount','transfersCount','holdersCount','address','twitter','coingecko']
        return df[cols]

    def _get_token_price_history_helper(self, address):
        data = self._get_token_price_history_grouped(address)['history']
        current = data.pop('current')
        txs = []
        for i in data['countTxs']:
            txs.append({'ts' : i['ts'], 'cnt' : i['cnt']})
        txs_df = pd.DataFrame(txs)
        txs_df['ts'] = txs_df['ts'].apply(lambda x: datetime.fromtimestamp(x))
        prices_df = pd.DataFrame(data['prices'])
        prices_df['ts'] = prices_df['ts'].apply(lambda x: datetime.fromtimestamp(x))
        prices_df.drop('tmp', axis=1, inplace=True)
        return prices_df, txs_df

    def get_token_historical_price(self, address):
        try:
           df = self._get_token_price_history_helper(address)[0]
        except Exception as e:
            logging.error(e)
            return pd.DataFrame()
        return df

    def get_token_historical_txs(self, address):
        try:
            df = self._get_token_price_history_helper(address)[1]
        except Exception as e:
            logging.error(e)
            return pd.DataFrame()
        return df