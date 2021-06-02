import pandas as pd
import requests
from bs4 import BeautifulSoup


def get_funding_rates(current=True):
    url = 'https://defirate.com/funding/'
    req = requests.get(url)
    soup = BeautifulSoup(req.text, features="lxml")
    if current:
        print("\nDisplaying current Funding Rates\n")
        table = soup.find('div',class_='table-container').find('table')
    else:
        print("\nDisplaying 30 day average Funding Rates\n")
        table = soup.find('div', class_='table-container table-hidden').find('table')
    items = []
    first_row = table.find('thead').text.strip().split()
    headers = [r for r in first_row if r!='Trade']
    headers.insert(0, 'Symbol')
    for i in table.find_all('td'):
        items.append(i.text.strip())
    fundings = [items[i:i + 5] for i in range(0, len(items), 5)]
    df = pd.DataFrame(columns=headers, data=fundings)
    return df

