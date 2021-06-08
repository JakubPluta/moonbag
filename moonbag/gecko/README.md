## How to use Gecko
There are to options to use CoinGecko views:
- gecko_coin - view in which you can see data for particular coin
- gecko_view - view in which you can see different data for defi, nft, top gainer, news etc.


## gecko_coin - see data for given coin

### 1. similar
primitive way to find coin names, and symbols with by search query  
required argument 
* -c, --coin # coin name
```
similar -c uniswap
```
### 2. load
load coin from CoinGecko.  
required argument 
* -c, --coin # coin symbol
```
load -c uniswap
```
### 3. coinlist  
show all available coins  
```
coinlist
```
### 4. info  
show info for loaded coin  
```
info
```
### 5. market  
show market date for loaded coin  
```
market
```
### 6. devs  
show data about coin development (Github, Bitbucket). For most coins data is unavailable
```
devs
```
### 7. ath  
show info all time high of loaded coin  
```
ath
```
### 8. atl  
show info all time low of loaded coin  
```
atl
```
### 9. web  
show web pages founded for loaded coin  
```
web
```
### 10. explorers  
show blockchain explorers links for loaded coin  
```
explorers
```



## gecko_view - see overall crypto data

### 1. news
show data for latest crypto news  
optional arguments  
 * -n, --num # number of records that you want to see
```
news -n 30 # displays 30 news
```
### 2. trending
show data for most trending coins on CoinGecko  
optional arguments  
 * -n, --num # number of records that you want to see
```
trending -n 30 # display 30 trending coins
```
### 3. recently  
show data for recently added coins on CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
recently -n 30 # display 30 trending coins
```
### 4. most_visited  
show data for most visited coins on CoinGecko  
optional arguments
 * -n, --num # number of records that you want to see
```
most_visited -n 30
```
### 5. most_voted  
show data for most voted coins on CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
most_voted -n 30
```
### 5. gainers
show data for top gainers on CoinGecko  
optional arguments
 * -n, --num # number of records that you want to see  
```
gainers -n 30
```
### 6. losers
show data for biggest losers on CoinGecko  
optional arguments
 * -n, --num # number of records that you want to see
```
losers -n 30
```
### 7. top_sentiment  
show data for coins with most positive sentiment on CoinGecko  
optional arguments
 * -n, --num # number of records that you want to see
```
top_sentiment -n 30
```
### 8. top_volume
show data for coins with highest volume on CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
top_volume -n 30
```
### 9. top_dexes  
show data for top decentralized exchanges on CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
top_dexes -n 30
```
### 10. top_defi
show data for top defi coins on CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
top_defi -n 30
```
### 11. info defi  
show overall data about defi market on CoinGecko  
```
info_defi
```
### 12. yield_farms  
show data for top yield farms  on CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
yield_farms
```
### 13. stables
show data for stablecoins on CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
stables
```
### 14. top_nft
show data for top non-fungible tokens on CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
top_nft
```
### 15. nft_market
show overall data bout non-fungible tokens market on CoinGecko  
```
nft_market
```
### 16. nft_of_day  
show nft of the day on CoinGecko  
```
nft_of_day
```
### 17. categories
show top crypto categories  CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
categories -n 30
```
### 18. derivatives
show derivatives  CoinGecko [long waiting time 15 sec]  
optional arguments 
* -n, --num # number of records that you want to see
```
derivatives -n 30
```
### 19. indexes
show indexes CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
indexes -n 30
```
### 20. fin_products  
show crypto financial products CoinGecko  
optional arguments 
* -n, --num # number of records that you want to see
```
fin_products -n 30
```
### 21. fin_platforms  
show crypto financial platforms CoinGecko  
optional arguments
 * -n, --num # number of records that you want to see
```
fin_platforms -n 30
```
### 22. btc_comp  
show companies that holds bitcoin CoinGecko
```
btc_comp
```
### 23. eth_comp  
show companies that holds ethereum CoinGecko  
```
eth_comp
```
### 24. eth_holdings  
show overall info about companies that holds ethereum CoinGecko  
```
eth_holdings
```
### 25. btc_holdings  
show overall info about companies that holds btc CoinGecko  
```
btc_holdings
```
### 26. exchanges  
show info about exchanges CoinGecko  
```
exchanges
```
### 27. ex_rates  
show info about exchange rates CoinGecko  
```
ex_rates
```