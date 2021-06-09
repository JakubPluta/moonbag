## How to use discover menu
discover menu contains different features that helps to explore crypto world.

### 1. top_subs
find top submissions on most popular crypto subreddits  [Reddit]      
```
top_subs
```
### 2. search_subs
show given subreddit for most popular submissions in last days  [Reddit]  
required argument   
* -s, --subreddit [subreddit name]
```
search_subs -s CryptoMoonShots
```
### 3. search_reddit
search on reddit with you own query  [Reddit]     
required argument  
* -q, --query [your query]
```
search_reddit -q ethereum
```
### 4. dpi
show defi pulse index protocols  [DefiPulse]   
```
dpi
```
### 5. defi
show DeFi protocols stats [LLama]  
```
defi
```
### 6. fng
show fear and greed index for last n days  [Fear and greed]   
required argument  
* -n, --limit [last N days]
```
fng -n 30
```
### 7. news
show last crypto news  [Cryptopanic]     
```
news
```
### 8. fundings 
show crypto funding rates  [Defirate]     
```
fundings 
```
### 9. 4chan 
show last 4chan submissions  [4chan]     
```
4chan 
```
### 10. wales 
show wales transactions  [Whale-Alert]  
```
wales
```
### 11.  uni_pairs
show recently added pairs on UniSwap  [TheGraph]  
optional arguments:          
  -d, --d, --days  [last n of days]  
  -v, --v, --volume  [min volume]  
  -l, --l, --liquid  [min liquidity]  
  -t --t --txs [min transactions]  
```
 uni_pairs  -d 20 -v 1000 -l 1000 -t 100
```
### 10. uni_tokens 
show tokens available on UniSwap  [TheGraph]   
optional arguments:        
  -s, --skip [you can only query 1000 records.]
```
# first page
uni_tokens
# 2nd page
uni_tokens -s 1000
# 5th page
uni_tokens -s 5000
```
### 11. uni_swaps
show recent coins swaps on on UniSwap  [TheGraph]    
```
uni_swaps
```
### 12. dex_trades
show stats about DeFi dex trades  [TheGraph]      
```
dex_trades
```
### 13. compound 
show available compound markets  [TheGraph]      
```
compound
```