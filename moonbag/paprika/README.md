## How to use CoinPaprika
CoinPaprika has free api, so you don't need to generate eny api keys.

### 1. global_info
show global info about crypto market [Coinpaprika]
```
global_info
```
### 2. search
try to find coin, exchange [Coinpaprika]
arguments:  
* -q, --query # search query
```
search -q uni
```
### 3. coins_list
show available coins: symbol and names [Coinpaprika]  
```
coins
```
### 4. coins_info  
show base information about cryptocurrencies [Coinpaprika]  
arguments:  
 * -n, --limit # number of results  
```
coins_info -n 100
```
### 5. coins_market  
show market information about cryptocurrencies [Coinpaprika]  
arguments:  
 * -n, --limit # number of results  
```
coins_market -n 100
```
### 6. exchanges_info
show crypto exchanges information [Coinpaprika]  
arguments:  
 * -n, --limit # number of results  
```
exchanges_info -n 100
```
### 7. exchanges_market
show crypto exchanges market information [Coinpaprika]  
arguments:  
 * -n, --limit # number of results  
```
exchanges_market -n 100
```
### 8. platforms 
show all platforms with smart contracts   
```
platforms 
```
### 9. contracts  
show all contract platforms.  Default: eth-ethereum. 
To find platform name use, "platforms" command  
arguments:   
* -p , --platform  # platform id  
```
contracts -p eth-ethereum
```

### 10. coin_exchanges
show all exchanges for given coin. Use coin_id as input [Coinpaprika]   
For now you need to use coin_id like : eth-ethereum (to find all coins_ids use coins_list command)  
arguments:  
* -c , --coin  # coin symbol
```
coin_exchanges -c eth-ethereum
```
### 11. coin_events  
show all event for given coin Use coin_id as input [Coinpaprika]   
For now you need to use coin_id like : eth-ethereum (to find all coins_ids use coins_list command)  
arguments:  
* -c , --coin  # coin symbol
```
coin_events -c eth-ethereum
```
### 12. coin_twitter 
show twitter timeline for given coin. Use coin_id as input [Coinpaprika]   
For now you need to use coin_id like : eth-ethereum (to find all coins_ids use coins_list command)  
arguments:  
* -c , --coin  # coin symbol
```
coin_twitter -c eth-ethereum
```
### 13. coin_ohlc 
show coin open-high-low-close prices data for last year. Use coin_id as input [Coinpaprika]   
For now you need to use coin_id like : eth-ethereum (to find all coins_ids use coins_list command)  
arguments:  
* -c , --coin  # coin symbol
```
coin_ohlc -c eth-ethereum
```