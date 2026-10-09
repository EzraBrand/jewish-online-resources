"""For links the live check could not settle (bot walls, timeouts), look up the most
recent Wayback Machine capture and its HTTP status.

Adds columns `wb_last_ts` and `wb_last_status` to the link-check CSV, in place.

Usage: py -3.13 -I scripts/wayback_last.py build/linkcheck-2023.csv
"""
import csv
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import requests

UNSETTLED = {"blocked", "timeout", "connection-refused", "error", "ssl-error"}


def last_capture(url):
    for attempt in range(3):
        try:
            r = requests.get("https://web.archive.org/cdx/search/cdx",
                             params={"url": url, "output": "json", "limit": "-3",
                                     "fl": "timestamp,statuscode"}, timeout=60)
            rows = r.json()[1:]
            if not rows:
                return "", ""
            ok = [x for x in rows if x[1] == "200"]
            ts, st = (ok or rows)[-1]
            return ts, st
        except Exception:  # noqa: BLE001
            time.sleep(3 * (attempt + 1))
    return "", "lookup-failed"


def main():
    path = sys.argv[1]
    rows = list(csv.DictReader(open(path, encoding="utf-8-sig")))
    todo = [r for r in rows if r["result"] in UNSETTLED]
    with ThreadPoolExecutor(max_workers=4) as ex:
        res = list(ex.map(lambda r: last_capture(r["url"]), todo))
    for r, (ts, st) in zip(todo, res):
        r["wb_last_ts"], r["wb_last_status"] = ts, st
    fields = list(rows[0].keys() | {"wb_last_ts", "wb_last_status"})
    order = [f for f in ["url", "status", "final_url", "title", "result", "error",
                         "wayback_url", "wayback_ts", "wb_last_ts", "wb_last_status"]
             if f in fields]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=order, restval="")
        w.writeheader()
        w.writerows(rows)
    for r, (ts, st) in zip(todo, res):
        print(r["result"], ts[:8], st, r["url"][:90].encode("ascii", "replace").decode())


if __name__ == "__main__":
    main()
