import requests
import bs4
from bs4 import BeautifulSoup
import pandas as pd
pd.set_option('display.max_columns', None)


def _gecko_scraper(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features='lxml')
    return soup

def get_top_crypto_categories():
    base = "https://www.coingecko.com"
    url = "https://www.coingecko.com/en/categories"
    soup = _gecko_scraper(url)
    rows = soup.find('tbody').find_all('tr')
    results = []

    for row in rows:
        rank = row.find('td', class_='table-left tw-text-left tw-text-xs').text.strip()
        name = row.find('td', class_='coin-name').text.strip()
        href = base + row.find('td', class_='coin-name').a['href']
        top_coins_urls = [base + a['href'] for a in
                     row.find('div', class_='tw-flex tw-justify-center lg:ml-4').find_all('a', href=True)]

        top_coins = ', '.join([url.split('/')[-1] for url in top_coins_urls])

        hour, day, week = [change.text.strip() for change in row.find_all('span')]
        mcap, volume = [stats.text.strip() for stats in row.find_all('td', class_='coin-name tw-text-right')[-2:]]
        coin = dict(
            category=name,
            rank=rank,
            url=href,
            top_coins=top_coins,
            last_1h=hour,
            last_day=day,
            last_week=week,
            market_cap=mcap,
            volume_24h=volume,

        )
        results.append(coin)
    return pd.DataFrame(results).set_index('rank')


def get_recently_added():

    base = "https://www.coingecko.com"
    url = 'https://www.coingecko.com/en/coins/recently_added'
    soup = _gecko_scraper(url)
    rows = soup.find('tbody').find_all('tr')
    results = []

    for row in rows:
        url = base+row.find('td', class_='py-0 coin-name').a['href']
        name = row.find('td', class_='py-0 coin-name').a.text.strip()
        added = row.find('td', class_='trade p-0 col-market pl-2 text-center').text.strip()
        price = row.find('td',class_='td-price price text-right').text.strip()
        hour = row.find('td',class_='td-change1h change1h stat-percent text-right col-market').text.strip()
        day = row.find('td',class_='td-change24h change24h stat-percent text-right col-market').text.strip()
        week = row.find('td',class_='td-change7d change7d stat-percent text-right col-market').text.strip()
        volume = row.find('td', class_='td-liquidity_score lit text-right %> col-market').text.strip()
        mcap = row.find('td', class_='td-market_cap cap col-market cap-price text-right').text.strip()

        coin = dict(
                name=name,
                price=price,
                last_added=added,
                url=url,
                last_1h=hour,
                last_day=day,
                last_week=week,
                market_cap=mcap,
                volume_24h=volume,

            )
        # clean dict
        for k, v in coin.items():
            if v == '?':
                coin[k] = None
        results.append(coin)
    return pd.DataFrame(results)




def get_stable_coins():
    url = 'https://www.coingecko.com/en/stablecoins'
    soup = _gecko_scraper(url)
    rows = soup.find('tbody').find_all('tr')
    results = []
    for row in rows:
        rank = row.find('td', class_='table-number text-center text-xs').text.strip()
        name, symbol, *_ = row.find('td', class_='py-0 coin-name').text.strip().split()
        price = row.find('td', class_='td-price price text-right').text.strip()
        day = row.find('td', class_='td-liquidity_score lit text-right %> col-market').text.strip()
        mcap = row.find('td', class_='text-right col-market').text.strip()
        month = row.find('td', class_='stat-percent text-right col-market text-primary').text.strip()
        exchanges = row.find('td', class_='text-right col-market text-primary').text.strip()
        stable = dict(
            rank = rank,
            name=name,
            symbol=symbol,
            price=price,
            volume_24h = day,
            market_cap_change_30d = month,
            market_cap=mcap,
            number_of_exchanges = exchanges

        )
        for k, v in stable.items():
            if v == '?':
                stable[k] = None
        results.append(stable)
    return pd.DataFrame(results)


