from moonbag.onchain.terraluna._client import TerraClient
import pandas as pd
import logging


class Terra(TerraClient):
    # https://fcd.terra.dev/swagger

    def get_coins_supply(self):
        df = pd.DataFrame(self._get_coins_supply()['result'])
        df['amount'] = df['amount'].apply(lambda x: int(x) / 1000000)
        return df

    def get_staking_pool(self):
        df = pd.Series(self._get_staking_info()['result']).to_frame().reset_index()
        df.columns = ['Metric', 'Value']
        return df

    def get_account(self, address):
        r = self._get_account(address)['result']
        df = pd.DataFrame()
        try:
            coins = r['value']['coins']
            address = r['value']['address']
            typ = r['type']
            acc_number = r['value']['account_number']
            for c in coins:
                c.update({'address': address, 'type': typ, 'account_number': acc_number})
            df = pd.DataFrame(coins)
            df['amount'] = df['amount'].apply(lambda x: int(x) / 1000000)
        except KeyError as e:
            logging.info(e)
        return df

    def get_tx(self, address):
        r = self._get_tx(address)
        try:
            logs = r.pop('logs')
            transaction_elements = []
            for log in logs:
                for event in log['events']:
                    for attr in event['attributes']:
                        attr.update(
                            {
                                'event': event['type'],
                                'index': log['msg_index'] + 1,
                                "txhash": r['txhash'],
                                "timestamp": r['timestamp']
                            })
                        transaction_elements.append(attr)
            cols = ['index', 'timestamp', 'event', 'key', 'value', 'txhash']
        except (KeyError, ValueError) as e:
            logging.info(e)
            return pd.DataFrame()
        return pd.DataFrame(transaction_elements)[cols]

    def get_validators(self):
        data = self._get_all_validators()['result']
        for v in data:
            commission = v.pop('commission')
            v['commission'] = commission['commission_rates']['rate']
            v['tokens'] = float(v['tokens']) / 1000000
            for col in ['unbonding_time', 'unbonding_height',
                        'consensus_pubkey' , 'status', 'delegator_shares','jailed']:
                v.pop(col)
            desc = v.pop('description')
            for i in ['security_contact','details','identity']:
                desc.pop(i)
            v.update(desc)
        return pd.DataFrame(data).sort_values(by='tokens', ascending=False)

