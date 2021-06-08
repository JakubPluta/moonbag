## How to use CryptoCompare
To use crypto compare view. You need to have visit https://min-api.cryptocompare.com/, register and generate free api key.
After that go to moonbag/common/keys.py and paste it under CC_API_KEY = <paste your key>
or do that in .env file if you this approach

### 1. news
show latest crypto news [CryptoCompare]  
arguments:  
    -s, --sort {latest, popular}
```
news -s latest
```
### 2. similar
try to find coin symbol [CryptoCompare]  
arguments:  
* -c, --coin SYMBOL  
* -k, --key {symbol,name} # you can search by coin symbol, or by coin name
```
similar -c uniswap -k name
```
### 3. coins
show available coins: symbol and names [CryptoCompare]  
```
coins
```
### 4. top_mcap  
show top market cap coins [CryptoCompare]  
arguments:  
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD
 * -n, --limit # number of results
```
top_mcap -t USD -n 100
```
### 5. top_exchanges  
arguments:  
show top  exchanges for given pair: Default BTC/USD [CryptoCompare]  
 * -c , --coin  coin symbol # Default BTC
 * -t, --tsym ,--to  coin in which you want to see market cap data. Default USD
```
top_exchanges -c BTC -t USD
```
### 6. list_exchanges  
show names of all exchanges  [CryptoCompare]  
```
list_exchanges
```
### 7. top_symbols_ex
show top coins on given exchange [CryptoCompare]  
arguments:
* -e, --exchange # name of exchange
* -n, --limit # number of results
```
top_symbols_ex -e binance -n 30
```
### 8. orders
show  order book for given pair and exchange. LUNA/BTC,Binance [CryptoCompare]  
arguments:
*  -c , --coin  # coin symbol
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD
* -e, --exchange # name of exchange

```
orders -c LUNA -t BTC -e binance
```
### 9. orders_snap  
show  order book snapshot for given pair and exchange. LUNA/BTC,Binance [CryptoCompare]  
arguments:  
* -c , --coin  # coin symbol  
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD  
* -e, --exchange # name of exchange  
```
orders_snap -c LUNA -t BTC -e binance
```

### 10. price
show latest price info for given pair like BTC/USD [CryptoCompare]  
arguments:  
* -c , --coin  # coin symbol
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD
```
price -c ETH -t BTC
```
### 10. price_day  
show historical prices with 1 day interval [CryptoCompare]  
arguments:  
* -c , --coin  # coin symbol
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD
* -n, --limit # limit of records
```
price_day -c ETH -t BTC -n 100
```
### 11. price_hour 
show historical prices with 1 hour interval [CryptoCompare]  
arguments:  
* -c , --coin  # coin symbol
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD
* -n, --limit # limit of records
```
price_hour -c ETH -t BTC -n 100
```
### 12. price_minute
show latest price info for given pair like BTC/USD [CryptoCompare]
arguments:
* -c , --coin  # coin symbol
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD
* -n, --limit # limit of records
```
price_minute -c ETH -t BTC -n 100
```
### 13. volume_day
show daily volume for given pair. Default: BTC/USD [CryptoCompare] 
arguments:  
* -c , --coin  # coin symbol
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD
* -n, --limit # limit of records
```
volume_day -c ETH -t BTC -n 100
```
### 14. volume_hour
show hourly volume for given pair. Default: BTC/USD [CryptoCompare]  
arguments:  
* -c , --coin  # coin symbol
* -t, --tsym ,--to  # coin in which you want to see market cap data. Default USD
* -n, --limit # limit of records
```
volume_hour -c ETH -t BTC -n 100
```
### 15. trade_signals
show latest trading signals for given coin. Default ETH [CryptoCompare] (works only for few coins)  
arguments:  
* -c , --coin  # coin symbol
```
trade_signals -c ETH
```
### 16. pair_volume  
show latest volume for given pair of coins [CryptoCompare]  
arguments:  
* -t , --to, --tsym  # coin in which you want to see data.
```
pair_volume
```
### 17. top_trading  
show top trading pairs for given coin [CryptoCompare]. Default BTC  
arguments:  
* -c , --coin  # coin symbol  
```
top_trading -c BTC
```
### 18. list_bc_coins  
show list of coins with on-chain data available [CryptoCompare]  
```
list_bc_coins
```
### 19. coin_bc  
show on chain data for given coin [CryptoCompare]  
arguments:  
* -c , --coin  # coin symbol
```
coin_bc -c BTC
```
### 20. coin_bc_hist  
show historical on chain data for given coin [CryptoCompare]  
arguments:  
* -c , --coin  # coin symbol
```
coin_bc_hist -c BTC
```
### 21. wallets  
show all available wallets [CryptoCompare]  
```
wallets
```
### 22. gambling  
show all available gambling [CryptoCompare]  
```
gambling
```
### 23. recommended  
show all recommendation for wallets and exchanges [CryptoCompare]  
arguments:  
* -c , --coin  # coin symbol
* -k, --key {exchange,wallet} # recommended exchanges or wallets for given coin
```
recommended -c ETH -k wallet
```
### 24. social  
show latest social stats for given coins symbol  (works only for few coins)  
arguments:  
* -c , --coin  # coin symbol
```
social -c ETH
```
### 25. social  
show historical social stats for given coins symbol, weekly aggregated. Works only for few coins)  
arguments:  
* -c , --coin  # coin symbol
```
social_hist -c ETH
```
