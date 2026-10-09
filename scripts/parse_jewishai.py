"""Pull the inline SERVER_DATA records out of the saved jewishai.me/table.html.

Usage: py -3.13 -I scripts/parse_jewishai.py source/web/jewishai-table.html build/jewishai-records.csv
"""
import csv
import json
import sys
from collections import Counter

html = open(sys.argv[1], encoding="utf-8").read()
start = html.index("{", html.index("const SERVER_DATA"))
data, _ = json.JSONDecoder().raw_decode(html[start:])
recs = data["records"]
cols = ["Title", "URL", "Author", "Year", "Resource Type", "Area", "Denomination",
        "Level/Audience", "Text"]
with open(sys.argv[2], "w", newline="", encoding="utf-8-sig") as f:
    w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
    w.writeheader()
    w.writerows(recs)
print(len(recs), "records")
print(Counter(r.get("Resource Type", "") for r in recs).most_common())
print(Counter(r.get("Level/Audience", "") for r in recs).most_common())
