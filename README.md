# Moon Bag Terminal

    ███╗   ███╗ ██████╗  ██████╗ ███╗   ██╗██████╗  █████╗  ██████╗ 
    ████╗ ████║██╔═══██╗██╔═══██╗████╗  ██║██╔══██╗██╔══██╗██╔════╝ 
    ██╔████╔██║██║   ██║██║   ██║██╔██╗ ██║██████╔╝███████║██║  ███╗
    ██║╚██╔╝██║██║   ██║██║   ██║██║╚██╗██║██╔══██╗██╔══██║██║   ██║
    ██║ ╚═╝ ██║╚██████╔╝╚██████╔╝██║ ╚████║██████╔╝██║  ██║╚██████╔╝
    ╚═╝     ╚═╝ ╚═════╝  ╚═════╝ ╚═╝  ╚═══╝╚═════╝ ╚═╝  ╚═╝ ╚═════╝

## About The Project   
Moonbag is Python Crypto CLI for exploring crypto trends, coins, DeFi protocols, NFTs and many others.
It's highly inspired by the famous GamestonkTerminal

## Let's fly to the Moon
### Installation 

## 1. Clone Repository:
```
git clone https://github.com/JakubPluta/moonbag.git
```
## 2. Open project folder
```
cd moonbag/
```
## 3. Create and activate virtual environment:**
```
python -m venv env
source env/Scripts/activate
```
## 4. Install Poetry:
```
pip install poetry
```
## 5. Install Dependencies
```
poetry install 
```

## 6. Configure API KEYS in order to be able to use all Moon Bag features.

You need to visit following places to get your API KEYS (all of them are free)
* CryptoCompare: https://min-api.cryptocompare.com/pricing ( "Get your free api key")
* Reddit: https://www.reddit.com/prefs/apps (get client id,  client secret and user agent)
* Wales: https://docs.whale-alert.io/#introduction (https://whale-alert.io/signup)
* Cryptopanic: https://cryptopanic.com/developers/api/
* Ethplorer: https://ethplorer.io/wallet/#api (It's not mandatory, u can use this API without key)
* BitQuery: https://bitquery.io/pricing

After you get your keys, you need to update it. You can do that in:
* /moonbag/common/keys.py
* or create .env file and store it there.

##### Adding keys to moonbag/common/keys.py
* Open key.py file in your editor and add your keys to relevant variables
```
WALES_API_KEY = <Enter your key>
CC_API_KEY = <Enter your key>
REDDIT_CLIENT_ID = <Enter your client id>
REDDIT_CLIENT_SECRET = <Enter your client secret>
REDDIT_USER_AGENT = <Enter your client user agent>
CRYPTO_PANIC_API = <Enter your key>
BIT_QUERY_API = <Enter your key>
```
##### Adding keys to .env file.
* Create .env file in your main folder
* Open .env file in your editor and add your keys:
```
CC_API_KEY=<Enter your key>
WALES_API_KEY=<Enter your key>
REDDIT_CLIENT_ID=<Enter your client id>
REDDIT_CLIENT_SECRET=<Enter your client secret>
REDDIT_USER_AGENT=<Enter your client user agent>
CRYPTO_PANIC_API=<Enter your key>
BIT_QUERY_API = <Enter your key>
```

## 7. Start Moon Bag terminal:
```
# In main directory write in terminal:
python moon.py
```

## Disclaimer:
Project is in alpha stage. There will be a lot of issues, bugs. Please feel free to report bugs.
Improvements, new functionalities and tests will be added systematically.

## Contributing
If you have an idea for improvement, new features -> Pull requests are welcome.

## License
[MIT](https://choosealicense.com/licenses/mit/)

## Available features. (updated: 5.06.2021)
- [x] Coingecko
- [x] Cryptocompare
- [x] Coinpaprika
- [x] UniSwap (GraphQL)
- [x] Funding rates
- [x] Wales txs
- [ ] Airdrops
- [x] DeFi stats
    - [x] Defi Pulse
    - [x] Lllama
- [x] Fear & Greed Index
- [ ] Blockchain explorers for most popular chains
    - [x] Ethereum
    - [x] TerraLuna
- [ ] Tests
- [ ] Charts
- [ ] Technical Analysis
- [ ] Social media data
    - [x] Reddit
    - [x] 4Chan
    - [ ] BitcoinTalk
