from json import encoder
from ethplorer._client import EthplorerClient
import pandas as pd
from datetime import datetime

encoder.FLOAT_REPR = lambda o: format(o, ".12f")

client = EthplorerClient()


class TokenInfo:
    def __init__(self, token_address):
        self.token_address = token_address
        self.token_info = client.get_token_info(token_address)
        self.token_history = client.get_token_history(token_address)

    def get_token_history_of_transactions(self, dct_parse=False):
        transactions = []
        token_history = self.token_history.get("operations")
        if token_history:
            for operation in token_history:
                operation_dct = {}
                token_info = operation.get("tokenInfo")
                operation_dct["timestamp"] = operation.get("timestamp")
                try:
                    operation_dct["datetime"] = datetime.fromtimestamp(
                        operation.get("timestamp")
                    )
                except TypeError:
                    pass
                operation_dct["valueTransferred"] = operation.get("value")
                operation_dct["transferredFrom"] = operation.get("from")
                operation_dct["transferredTo"] = operation.get("to")
                operation_dct["tokenSymbol"] = token_info.get("symbol")
                operation_dct["tokenName"] = token_info.get("name")
                operation_dct["totalSupply"] = token_info.get("totalSupply")
                try:
                    transferred_pct = round(
                        float(operation.get("value"))
                        / float(token_info.get("totalSupply")),
                        8,
                    )
                except ZeroDivisionError:
                    transferred_pct = None

                operation_dct["transferredPctOfTotalSupply"] = transferred_pct
                transactions.append(operation_dct)
            if dct_parse:
                return transactions
            else:
                return pd.DataFrame(transactions)

    def get_token_holders(self, dct_parse=False):
        token_holders = self.client.get_top_token_holders(self.token_address)
        if token_holders:
            holders = token_holders.get("holders")
            if dct_parse:
                return holders
            return pd.DataFrame(holders)

    def get_token_info(self):
        return pd.json_normalize(self.token_info).T

    def build_summary_of_token_transactions(self):
        token_history_cleaned = self.get_token_history_of_transactions(False)

        top_transferred_from = token_history_cleaned.groupby("transferredFrom").size()
        top_transferred_from.name = "countOfTransactionsTransferredFrom"
        top_transferred_from = top_transferred_from.sort_values(ascending=False).head(1)

        top_transferred_to = token_history_cleaned.groupby("transferredTo").size()
        top_transferred_to.name = "countOfTransactionsTransferredTo"
        top_transferred_to = top_transferred_from.sort_values(ascending=False).head(1)

        return {
            "totalTransactions": len(token_history_cleaned),
            "firstTransactionDate": token_history_cleaned["datetime"].min(),
            "lastTransactionDate": token_history_cleaned["datetime"].max(),
            "addressWithHighestNumberOfTransfersTo": top_transferred_to.index[0],
            "countTransfersTo": top_transferred_to.values[0],
            "addressWithHighestNumberOfTransfersFrom": top_transferred_from.index[0],
            "countTransfersFrom": top_transferred_from.values[0],
        }


# a = TokenInfo('0x1f9840a85d5af5bf1d1762f925bdaddc4201f984')
# print(a.get_token_history_of_transactions())


class CheckTokenCreator:
    def __init__(self, token_address: str):
        self.token_address = token_address
        self.token_info = client.get_address_info(token_address)

        self.creator_address = self.check_if_creator_data_exists(self.token_info)

    @staticmethod
    def check_if_creator_data_exists(token_info):
        contract_info = token_info.get("contractInfo")
        if contract_info and "creatorAddress" in contract_info:
            return contract_info.get("creatorAddress")
        else:
            return None


class TokenCreator:
    def __init__(self, creator_address):
        self.creator_address = creator_address

        self._creator_address_info = client.get_address_info(creator_address)
        self._creator_address_history = client.get_address_history(creator_address)

    def get_eth_balance(self):
        eth = self._creator_address_info.get("ETH")
        if eth:
            eth_balance = eth.get("balance")
            eth_current_price = eth.get("price").get("rate")
            usd_balance_value = round(float(eth_balance) * float(eth_current_price), 8)
            return {
                "ethBalance": eth.get("balance"),
                "ethPrice": eth.get("price").get("rate"),
                "usdBalance": usd_balance_value,
            }
        else:
            return None

    def get_transactions_count(self):
        return self._creator_address_info.get("countTxs")

    def get_info_about_creator_portfolio(self, dct_parse=False):
        portfolio_items = []
        portfolio = self._creator_address_info.get("tokens")
        if portfolio:
            for token in portfolio:
                token_dct = {}
                token_info = token.get("tokenInfo")
                balance = token.get("balance")
                token_dct["tokenAddress"] = token_info.get("address")
                token_dct["symbol"] = token_info.get("symbol")
                token_dct["name"] = token_info.get("name")
                token_dct["totalSupply"] = token_info.get("totalSupply")
                token_dct["balance"] = float(balance)
                try:
                    pct_of_supply = float(balance) / float(
                        token_info.get("totalSupply")
                    )
                except ZeroDivisionError:
                    pct_of_supply = None
                token_dct["pctOfTotalSupply"] = round(pct_of_supply, 8)
                portfolio_items.append(token_dct)
            if dct_parse:
                return portfolio_items
            else:
                return pd.DataFrame(portfolio_items)

    def get_transactions_info(self, dct_parse=False):
        transactions = []
        operations = self._creator_address_history.get("operations")
        if operations:
            for operation in operations:
                operation_dct = {}
                token_info = operation.get("tokenInfo")
                try:
                    operation_dct["datetime"] = datetime.fromtimestamp(
                        operation.get("timestamp")
                    )
                except TypeError:
                    pass

                operation_dct["valueTransferred"] = operation.get("value")
                operation_dct["transferredFrom"] = operation.get("from")
                operation_dct["transferredTo"] = operation.get("to")
                if self.creator_address == operation.get("to"):
                    operation_dct["transferredToCreator"] = True
                else:
                    operation_dct["transferredToCreator"] = False
                if self.creator_address == operation.get("from"):
                    operation_dct["transferredFromCreator"] = True
                else:
                    operation_dct["transferredFromCreator"] = False

                operation_dct["tokenSymbol"] = token_info.get("symbol")
                operation_dct["tokenName"] = token_info.get("name")
                operation_dct["totalSupply"] = token_info.get("totalSupply")

                try:
                    transferred_pct = round(
                        float(operation.get("value"))
                        / float(token_info.get("totalSupply")),
                        6,
                    )
                except ZeroDivisionError:
                    transferred_pct = None

                operation_dct["transferredPct"] = transferred_pct
                transactions.append(operation_dct)
            if dct_parse:
                return transactions
            else:
                return pd.DataFrame(transactions)
