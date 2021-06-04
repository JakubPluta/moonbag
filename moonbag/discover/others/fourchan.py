import pandas as pd
import datetime
import textwrap
import requests
import numpy as np
import re


def html_clearer(text):
    regex = re.compile("<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});")
    return re.sub(regex, "", text)


def get_last_4chans():
    r = requests.get("https://a.4cdn.org/biz/catalog.json").json()
    data = []
    for item in r:
        threads = item["threads"]
        for i, t in enumerate(threads):
            res = {
                "sub": t.get("sub") or "",
                "com": t.get("com"),
                "replies": t.get("replies"),
                "last_modified": datetime.datetime.fromtimestamp(
                    t.get("last_modified")
                ),
            }
            data.append(res)

    df = pd.DataFrame(data).sort_values(by="last_modified", ascending=False)
    df["com"] = df["com"].apply(lambda x: html_clearer(str(x)))
    df["sub"] = df["sub"].apply(lambda x: html_clearer(str(x)))
    df["com"] = df["com"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=86)) if isinstance(x, str) else x
    )
    df["sub"] = df["sub"].apply(
        lambda x: "\n".join(textwrap.wrap(x, width=26)) if isinstance(x, str) else x
    )
    df["com"] = df["com"].apply(lambda x: "" if x in ["None", None, np.NaN] else x)
    df = df[df["last_modified"] >= datetime.datetime.now() - datetime.timedelta(days=7)]
    return df[["last_modified", "replies", "sub", "com"]].sort_values(
        by="last_modified", ascending=False
    )
