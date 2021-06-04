import datetime
from moonbag.common.utils import created_date
import requests
import pandas as pd


class GraphClient:
    UNI = "https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2"
    BQ = "https://graphql.bitquery.io"
    CMP = "https://api.thegraph.com/subgraphs/name/graphprotocol/compound-v2"

    @staticmethod
    def run_query(
        url, query
    ):  # A simple function to use requests.post to make the API call. Note the json= section.
        request = requests.post(url, json={"query": query})
        if request.status_code == 200:
            return request.json()["data"]
        else:
            raise Exception(
                "Query failed to run by returning code of {}. {}".format(
                    request.status_code, query
                )
            )

    def get_uni_tokens(self, skip=0):
        q = (
            """
            {
            tokens(first: 1000, skip:%s) {
                symbol
                name
                tradeVolumeUSD
                totalLiquidity
                txCount
                }
            }
        """
            % skip
        )
        data = self.run_query(self.UNI, q)
        return pd.DataFrame(data["tokens"])

    def get_dex_trades_by_protocol(self):
        q = """
        {
          ethereum {
            dexTrades(options: {limit: 100, desc: "count"}) {
              protocol
              count
              tradeAmount(in: USD)
            }
          }
        }

        """
        data = self.run_query(self.BQ, q)
        return pd.DataFrame(data["ethereum"]["dexTrades"])

    def get_dex_trades_monthly(self):
        q = """
        {
          ethereum {
            dexTrades(options: {limit: 1000, desc: ["count","protocol", "date.year","date.month"]}) {
              protocol
              count
              tradeAmount(in: USD)
              date {
                year
                month
                }
            }
          }
        }

        """
        data = self.run_query(self.BQ, q)
        return pd.json_normalize(data["ethereum"]["dexTrades"])

    def get_uniswap_pool_lastly_added(
        self, last_days=14, min_volume=100, min_liquidity=0, min_tx=100
    ):
        days = int(
            (datetime.datetime.now() - datetime.timedelta(days=last_days)).timestamp()
        )
        q = """
            {
              pairs(first: 1000, where: {createdAtTimestamp_gt: "%s", volumeUSD_gt: "%s", reserveUSD_gt: "%s", txCount_gt: "%s" }, 
              orderBy: createdAtTimestamp, orderDirection: desc) {

                token0 {
                  symbol
                  name
                }
                token1 {
                  symbol
                  name
                }
                reserveUSD
                volumeUSD
                createdAtTimestamp
                totalSupply
                txCount

              }
            }

        """ % (
            days,
            min_volume,
            min_liquidity,
            min_tx,
        )
        data = self.run_query(self.UNI, q)
        df = pd.json_normalize(data["pairs"])
        df["createdAtTimestamp"] = df["createdAtTimestamp"].apply(
            lambda x: created_date(int(x))
        )
        df["pair"] = df["token0.symbol"] + "/" + df["token1.symbol"]
        return df[
            [
                "createdAtTimestamp",
                "pair",
                "token0.name",
                "token1.name",
                "volumeUSD",
                "txCount",
                "totalSupply",
                "reserveUSD",
            ]
        ]

    def get_uniswap_pools_by_volume(self):
        q = """
            {
              pairs(first: 1000, where: {reserveUSD_gt: "1000", volumeUSD_gt: "10000"}, 
              orderBy: volumeUSD, orderDirection: desc) {

                token0 {
                  symbol
                  name
                }
                token1 {
                  symbol
                  name
                }
                volumeUSD
                txCount

              }
            }

        """
        data = self.run_query(self.UNI, q)
        df = pd.json_normalize(data["pairs"])

        df = df[df["token0.name"] != "You don't blacklist delta.financial"]
        df = df[df["token1.name"] != "You don't blacklist delta.financial"]
        return df[
            [
                "token0.name",
                "token0.symbol",
                "token1.name",
                "token1.symbol",
                "volumeUSD",
                "txCount",
            ]
        ]

    def get_uniswap_stats(self):
        q = """
        {
         uniswapFactory(id: "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"){
          totalVolumeUSD
          totalLiquidityUSD
          pairCount
          txCount
          totalLiquidityUSD
          totalLiquidityETH

         }
        }
        """
        data = self.run_query(self.UNI, q)["uniswapFactory"]
        return pd.Series(data).reset_index()

    def get_compound_markets(self):
        q = """
            {
              markets(first: 100) {
                name
                symbol
                borrowRate
                collateralFactor
                exchangeRate
                supplyRate
                totalBorrows
                totalSupply
                underlyingPriceUSD
              }
            }


        """
        data = self.run_query(self.CMP, q)["markets"]
        return pd.DataFrame(data)

    def get_last_swaps_uni(self):
        q = """
        {
            swaps(first: 1000, orderBy: timestamp, orderDirection: desc) {
              timestamp
              pair {
                token0 {
                  symbol
                }
                token1 {
                  symbol
                }
              }
              amountUSD
            }
        }

        """

        data = self.run_query(self.UNI, q)["swaps"]
        df = pd.json_normalize(data)

        df["timestamp"] = df["timestamp"].apply(lambda x: created_date(int(x)))
        df.columns = ["amountUSD", "timestamp", "token0", "token1"]
        return df[["timestamp", "token0", "token1", "amountUSD", "timestamp"]]
