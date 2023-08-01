import requests
import pytz
import json
import datetime
import os
import sys
from eprint import eprint


def get_data():
    url = "https://pi.tgclab.com/logs/group/member/ranks"
    headers = {
        "user-agent": "Dart/2.19 (dart:io)",
        "accept-enconding": "gzip",
        "authorization": "JWT " + os.environ["JWT"],
        "host": "pi.tgclab.com",
    }
    dt = datetime.datetime.now(pytz.utc)
    params = {
        "type": "day",
        "countryID": 8,
        "categoryID": 0,
        "groupID": 2981723,
        "isCam": False,
        "date": str(dt.year) + "-" + str(dt.month) + "-" + str(dt.day),
        "page": 1,
    }

    r = requests.get(url, headers=headers, params=params)
    eprint("response from ypt server", r.status_code)
    ranks = json.loads(r.text)["ms"]

    data = {}
    for rank in ranks:
        name = rank["n"]
        diff = 0
        if rank["dl"]["is"]:
            name = "*" + name
            date_str = rank["dl"]["st"]
            format_str = "%Y-%m-%d %H:%M:%S.%f%z"
            parsed_date = datetime.datetime.strptime(date_str, format_str)
            diff = (dt - parsed_date).total_seconds()

        data[name] = datetime.timedelta(seconds=int(diff + rank["dl"]["sm"] / 1000))

    data = dict(sorted(data.items(), key=lambda item: item[1], reverse=True))
    return data


if __name__ == "__main__":
    data = get_data()
    for key in data.keys():
        print(key, data[key])
