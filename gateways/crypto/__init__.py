import requests
from bs4 import BeautifulSoup
import pandas as pd
import re

pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)
pd.set_option("display.width", None)


def clean_question_marks(dct: dict):
    if isinstance(dct, dict):
        for k, v in dct.items():
            if v == "?":
                dct[k] = None


def gecko_scraper(url):
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="lxml")
    return soup


def get_top_crypto_categories():
    base = "https://www.coingecko.com"
    url = "https://www.coingecko.com/en/categories"
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []

    for row in rows:
        rank = row.find("td", class_="table-left tw-text-left tw-text-xs").text.strip()
        name = row.find("td", class_="coin-name").text.strip()
        href = base + row.find("td", class_="coin-name").a["href"]
        top_coins_urls = [
            base + a["href"]
            for a in row.find(
                "div", class_="tw-flex tw-justify-center lg:ml-4"
            ).find_all("a", href=True)
        ]

        top_coins = ", ".join([url.split("/")[-1] for url in top_coins_urls])

        hour, day, week = [change.text.strip() for change in row.find_all("span")]
        mcap, volume = [
            stats.text.strip()
            for stats in row.find_all("td", class_="coin-name tw-text-right")[-2:]
        ]
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
        clean_question_marks(coin)
        results.append(coin)
    return pd.DataFrame(results).set_index("rank")


def get_recently_added():

    base = "https://www.coingecko.com"
    url = "https://www.coingecko.com/en/coins/recently_added"
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []

    for row in rows:
        url = base + row.find("td", class_="py-0 coin-name").a["href"]
        name = row.find("td", class_="py-0 coin-name").a.text.strip()
        added = row.find(
            "td", class_="trade p-0 col-market pl-2 text-center"
        ).text.strip()
        price = row.find("td", class_="td-price price text-right").text.strip()
        hour = row.find(
            "td", class_="td-change1h change1h stat-percent text-right col-market"
        ).text.strip()
        day = row.find(
            "td", class_="td-change24h change24h stat-percent text-right col-market"
        ).text.strip()
        week = row.find(
            "td", class_="td-change7d change7d stat-percent text-right col-market"
        ).text.strip()
        volume = row.find(
            "td", class_="td-liquidity_score lit text-right %> col-market"
        ).text.strip()
        mcap = row.find(
            "td", class_="td-market_cap cap col-market cap-price text-right"
        ).text.strip()

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
        clean_question_marks(coin)
        results.append(coin)
    return pd.DataFrame(results)


def get_stable_coins():
    url = "https://www.coingecko.com/en/stablecoins"
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []
    for row in rows:
        rank = row.find("td", class_="table-number text-center text-xs").text.strip()
        name, symbol, *_ = row.find("td", class_="py-0 coin-name").text.strip().split()
        price = row.find("td", class_="td-price price text-right").text.strip()
        day = row.find(
            "td", class_="td-liquidity_score lit text-right %> col-market"
        ).text.strip()
        mcap = row.find("td", class_="text-right col-market").text.strip()
        month = row.find(
            "td", class_="stat-percent text-right col-market text-primary"
        ).text.strip()
        exchanges = row.find(
            "td", class_="text-right col-market text-primary"
        ).text.strip()
        stable = dict(
            rank=rank,
            name=name,
            symbol=symbol,
            price=price,
            volume_24h=day,
            market_cap_change_30d=month,
            market_cap=mcap,
            number_of_exchanges=exchanges,
        )
        clean_question_marks(stable)
        results.append(stable)
    return pd.DataFrame(results).set_index("rank")


def get_yield_farms():
    def _parse_row(row):
        parsed = []
        for n, i in enumerate(row):
            txt = i.text.strip()
            record = (
                re.sub(r"(\n){2,10}", " ", txt).replace("  ", " ").replace("\n", " ")
            )
            parsed.append(record)
        return parsed[:-1]

    cols = [
        "rank",
        "name",
        "pool",
        "audits",
        "collateral",
        "il risk",
        "value locked",
        "returns",
    ]
    url = "https://www.coingecko.com/en/yield-farming"
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []
    for r in rows:
        row = r.find_all("td")
        res = _parse_row(row)
        results.append(res)
    df = pd.DataFrame(results, columns=cols).set_index("rank")
    df.replace({"N/A": None}, inplace=True)
    df["audits"] = df["audits"].replace(to_replace=r"^[0-9]\s", value="", regex=True)
    df.applymap(lambda x: x.rstrip() if isinstance(x, str) else x)
    df.replace(to_replace=r"(\s){2,}", value=" ", regex=True, inplace=True)
    df["yearly returns"] = df["returns"].apply(lambda x: " ".join(x.split(" ")[:2]))
    df["hourly returns"] = df["returns"].apply(lambda x: " ".join(x.split(" ")[2:]))
    df["collateral"] = df["collateral"].apply(lambda x: ",".join(x.split()))
    return df.drop(["returns", "il risk"], axis=1)


def get_top_volume_coins():
    url = "https://www.coingecko.com/pl/waluty/high_volume"
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []
    for row in rows:
        rank = row.find("td", class_="table-number text-center text-xs").text.strip()
        name = row.find(
            "a",
            class_="tw-hidden lg:tw-flex font-bold tw-items-center tw-justify-between",
        ).text.strip()
        symbol = row.find("a", class_="d-lg-none font-bold").text.strip()
        price = row.find("td", class_="td-price price text-right").text.strip()
        last_1h = row.find(
            "td", class_="td-change1h change1h stat-percent text-right col-market"
        ).text.strip()
        last_24h = row.find(
            "td", class_="td-change24h change24h stat-percent text-right col-market"
        ).text.strip()
        last_week = row.find(
            "td", class_="td-change7d change7d stat-percent text-right col-market"
        ).text.strip()
        volume_24h = row.find(
            "td", class_="td-liquidity_score lit text-right %> col-market"
        ).text.strip()
        mcap = row.find(
            "td", class_="td-market_cap cap col-market cap-price text-right"
        ).text.strip()

        coin = dict(
            rank=rank,
            name=name,
            symbol=symbol,
            price=price,
            change_1h=last_1h,
            change_24h=last_24h,
            change_7d=last_week,
            volume_24h=volume_24h,
            market_cap=mcap,
        )
        clean_question_marks(coin)
        results.append(coin)
    return pd.DataFrame(results).set_index("rank")


def btc_price():
    req = requests.get(
        "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd&include_market_cap=false&include_24hr_vol=false&include_24hr_change=false&include_last_updated_at=false"
    )
    return req.json()["bitcoin"]["usd"]


def discover_coins(category="trending"):
    categories = {
        "trending": 0,
        "most_voted": 1,
        "positive_sentiment": 2,
        "recently_added": 3,
        "most_visited": 4,
    }

    if category not in categories:
        raise ValueError(
            f"Wrong category name\nPlease chose one from list: {categories.keys()}"
        )

    base = "https://www.coingecko.com"
    url = "https://www.coingecko.com/en/discover"
    soup = gecko_scraper(url)
    popular = soup.find_all("div", class_="col-12 col-sm-6 col-md-6 col-lg-4")[
        categories[category]
    ]
    rows = popular.find_all("a")
    results = []
    for row in rows:
        name, *args, price = row.text.strip().split("\n")
        url = base + row["href"]
        if price.startswith("BTC"):
            price = price.replace("BTC", "").replace(",", ".")
        results.append([name, price, url])
    return pd.DataFrame(results, columns=["name", "price btc", "url"])


def get_top_gainers(period="1h"):
    periods = {
        "1h": "?time=h1",
        "1d": "?time=h24",
        "7d": "?time=d7",
        "14d": "?time=d14",
        "30d": "?time=d30",
        "60d": "?time=d60",
        "1y": "?time=y1",
    }
    if period not in periods:
        raise ValueError(
            f"Wrong time period\nPlease chose one from list: {periods.keys()}"
        )

    base = "https://www.coingecko.com"
    url = f"https://www.coingecko.com/en/coins/trending{periods.get(period)}"
    soup = gecko_scraper(url)
    top_gainers = soup.find_all("tbody")[0]
    rows = top_gainers.find_all("tr")
    results = []
    for row in rows:
        url = base + row.find("a")["href"]
        record = [r for r in row.text.strip().split("\n") if r not in ["", " "]]
        symbol, name, *args, volume, price, change = record
        results.append([symbol, name, volume, price, change, url])
    return pd.DataFrame(
        results,
        columns=["symbol", "name", "volume", "price", f"change_{period}", "url"],
    )


def get_top_losers(period="1h"):
    periods = {
        "1h": "?time=h1",
        "1d": "?time=h24",
        "7d": "?time=d7",
        "14d": "?time=d14",
        "30d": "?time=d30",
        "60d": "?time=d60",
        "1y": "?time=y1",
    }
    if period not in periods:
        raise ValueError(
            f"Wrong time period\nPlease chose one from list: {periods.keys()}"
        )

    base = "https://www.coingecko.com"
    url = f"https://www.coingecko.com/en/coins/trending{periods.get(period)}"
    soup = gecko_scraper(url)
    top_gainers = soup.find_all("tbody")[1]
    rows = top_gainers.find_all("tr")
    results = []
    for row in rows:
        url = base + row.find("a")["href"]
        record = [r for r in row.text.strip().split("\n") if r not in ["", " "]]
        symbol, name, *args, volume, price, change = record
        results.append([symbol, name, volume, price, change, url])
    return pd.DataFrame(
        results,
        columns=["symbol", "name", "volume", "price", f"change_{period}", "url"],
    )


def get_defi_coins():
    base = "https://www.coingecko.com"
    url = "https://www.coingecko.com/en/defi"
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []
    for row in rows:
        url = base + row.find("a")["href"]
        (
            rank,
            *names,
            symbol,
            symbol2,
            price,
            change,
            change1,
            change2,
            volume,
            mcap,
            full,
            ratio,
        ) = row.text.strip().split()
        results.append(
            [
                rank,
                " ".join(names),
                symbol,
                price,
                change,
                change1,
                change2,
                volume,
                mcap,
                full,
                ratio,
                url,
            ]
        )

    return pd.DataFrame(
        results,
        columns=[
            "rank",
            "name",
            "symbol",
            "price",
            "change_1h",
            "change_24h",
            "change_7d",
            "volume_24h",
            "market_cap",
            "fully_diluted_market_cap",
            "macp/tvl ratio",
            "url",
        ],
    ).set_index("rank")


def get_dexes():
    url = "https://www.coingecko.com/en/dex"
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []
    for row in rows:
        row_txt = row.text.strip()
        if "Trading Incentives" in row_txt:
            row_txt = row_txt.replace("Trading Incentives", "")

        record = row_txt.split("\n")
        record = [r for r in record if r not in [" ", ""]]
        if len(record) == 8:
            record.insert(-3, "N/A")

        (
            rank,
            *names,
            volume_24h,
            num_coins,
            num_pairs,
            visits,
            most_trader_pairs,
            market_share_by_volume,
        ) = record
        results.append(
            [
                rank,
                " ".join(names).strip(),
                volume_24h,
                num_coins,
                num_pairs,
                visits,
                most_trader_pairs,
                market_share_by_volume,
                url,
            ]
        )
    df = pd.DataFrame(
        results,
        columns=[
            "rank",
            "name",
            "volume_24h",
            "number_of_coins",
            "number_of_pairs",
            "number_of_visits",
            "most_traded_pairs",
            "market_share_by_volume",
            "url",
        ],
    )

    # @todo make it clean - > so ugly ....
    df["most_traded_pairs"] = df["most_traded_pairs"].str.replace("\d+", "", regex=True)
    df["most_traded_pairs"] = df["most_traded_pairs"].str.replace(".", "", regex=True)
    df["most_traded_pairs"] = df["most_traded_pairs"].str.replace(",", "", regex=True)
    df["most_traded_pairs"] = df["most_traded_pairs"].str.replace("$", "", regex=True)

    return df.set_index("rank")


def get_top_nfts():
    base = "https://www.coingecko.com/"
    url = "https://www.coingecko.com/en/nft"
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []
    for row in rows:
        url = base + row.find("a")["href"]
        cleaned_row = [i for i in row.text.strip().split("\n") if i not in [" ", ""]]
        if len(cleaned_row) == 9:
            cleaned_row.insert(5, "N/A")

        (
            rank,
            *names,
            symbol,
            symbol2,
            price,
            change,
            change1,
            change2,
            volume,
            mcap,
        ) = cleaned_row
        results.append(
            [
                rank,
                " ".join(names),
                symbol,
                price,
                change,
                change1,
                change2,
                volume,
                mcap,
                url,
            ]
        )

    return pd.DataFrame(
        results,
        columns=[
            "rank",
            "name",
            "symbol",
            "price",
            "change_1h",
            "change_24h",
            "change_7d",
            "volume_24h",
            "market_cap",
            "url",
        ],
    )


def get_nft_of_the_day():
    base = "https://www.coingecko.com/"
    url = "https://www.coingecko.com/en/nft"
    soup = gecko_scraper(url)
    row = soup.find("div", class_="tw-px-4 tw-py-5 sm:tw-p-6")
    try:
        *author, description, other = [
            r for r in row.text.strip().split("\n") if r not in ["", " "]
        ]
    except ValueError:
        return {}
    return {
        "author": " ".join(author),
        "desc": description,
        "url": base + row.find("a")["href"],
        "img": row.find("img")["src"],
    }


def get_nft_market_status():
    url = "https://www.coingecko.com/en/nft"
    soup = gecko_scraper(url)
    row = soup.find_all("span", class_="overview-box d-inline-block p-3 mr-2")
    kpis = {}
    for r in row:
        value, *kpi = r.text.strip().split()
        name = " ".join(kpi)
        kpis[name] = value
    return kpis


def _get_news(page=1):
    url = f'https://www.coingecko.com/en/news?page={page}'
    soup = gecko_scraper(url)
    row = soup.find_all("article")
    results = []
    for r in row:
        header = r.find('header')
        link =  header.find('a')['href']
        text = [t for t in header.text.strip().split('\n') if t not in ['',' ']]
        article = r.find('div', class_='post-body').text.strip()
        title, *by = text
        author, posted = ' '.join(by).split('(')
        posted = posted.strip().replace(')','')
        results.append([title, author.strip(),posted ,article,link])
    return pd.DataFrame(results, columns=['title','author','posted','article', 'url'])


def get_news(n_of_pages=10):
    dfs = []
    for page in range(1, n_of_pages):
        dfs.append(_get_news(page))
    return pd.concat(dfs, ignore_index=True)

# https://www.codingforentrepreneurs.com/blog/python-asyncio-web-scraping/


def get_btc_holdings_public_companies_overview():
    url = 'https://www.coingecko.com/en/public-companies-bitcoin'
    soup = gecko_scraper(url)
    rows = soup.find_all("span", class_='overview-box d-inline-block p-3 mr-2')
    kpis = {}
    for row in rows:
        r = row.text.strip().split()
        if r:
            value, *kpi = r
            name = " ".join(kpi)
            kpis[name] = value
    return kpis


def get_eth_holdings_public_companies_overview():
    url = 'https://www.coingecko.com/en/public-companies-ethereum'
    soup = gecko_scraper(url)
    rows = soup.find_all("span", class_='overview-box d-inline-block p-3 mr-2')
    kpis = {}
    for row in rows:
        r = row.text.strip().split()
        if r:
            value, *kpi = r
            name = " ".join(kpi)
            kpis[name] = value
    return kpis



def get_companies_with_btc():
    url = 'https://www.coingecko.com/en/public-companies-bitcoin'
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []
    for row in rows:
        link = row.find('a')['href']
        r = [r for r in row.text.strip().split('\n') if r not in ['',' ']]
        rank, *name, symbol, country, total_btc, entry_value, today_value, pct_of_supply = r
        results.append([rank, ' '.join(name), symbol,country, total_btc, entry_value, today_value, pct_of_supply, link])
    return pd.DataFrame(results, columns=[
        'rank','company','ticker','country','total_btc', 'entry_value','today_value','pct_of_supply','url'
    ]).set_index('rank')


def get_companies_with_eth():
    url = 'https://www.coingecko.com/en/public-companies-ethereum'
    soup = gecko_scraper(url)
    rows = soup.find("tbody").find_all("tr")
    results = []
    for row in rows:
        link = row.find('a')['href']
        r = [r for r in row.text.strip().split('\n') if r not in ['',' ']]
        rank, *name, symbol, country, total_btc, entry_value, today_value, pct_of_supply = r
        results.append([rank, ' '.join(name), symbol,country, total_btc, entry_value, today_value, pct_of_supply, link])
    return pd.DataFrame(results, columns=[
        'rank','company','ticker','country','total_eth', 'entry_value','today_value','pct_of_supply','url'
    ]).set_index('rank')


