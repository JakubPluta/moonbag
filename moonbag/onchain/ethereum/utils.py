import numbers
import logging

def converter(num):
    if isinstance(num, numbers.Number):
        "{:.14f}".format(num)

def split_cols(x):
    if '.' in x:
        p1, p2 = x.split('.')
        p2 = manual_replace(p2,p2[0].upper(), 0)
        return p1+p2
    return x

def manual_replace(s, char, index):
    return s[:index] + char + s[index +1:]


def enrich_social_media(dct: dict):
    social_media = {
        'twitter' : 'https://www.twitter.com/',
        'reddit' : 'https://www.reddit.com/r/',
        'coingecko' : 'https://www.coingecko.com/en/coins/'
    }
    try:
        for k,v in social_media.items():
            if k in dct:
                dct[k] = v + dct[k]
    except Exception as e:
        logging.error(e)