"""Check every unique URL for link rot.

Each URL gets a GET (first ~300 KB only). The script records status, final URL and
page <title>, then sorts the result into a bucket. Wikimedia hosts get a
policy-compliant User-Agent (their bot wall rejects browser-like UAs). For anything
that is not clearly OK, it asks the Wayback Machine for the closest snapshot.

A "blocked" result means the server refused a scripted request (403/429/bot
challenge). That is not proof of rot; verify those in a real browser.

Usage:
  py -3.13 -I scripts/check_links.py IN.json OUT.csv
IN.json is a list of objects with a "uri" or "url" key.
"""
import csv
import json
import re
import sys
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from html import unescape
from urllib.parse import urlparse

import requests
import urllib3

urllib3.disable_warnings()

BROWSER_UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
              "(KHTML, like Gecko) Chrome/130.0 Safari/537.36")
WIKI_UA = "JewishStudiesGuideLinkCheck/1.0 (https://github.com/; link-rot audit) python-requests"
TIMEOUT = 30
MAX_BYTES = 300_000

SOFT_404 = re.compile(r"\b(404|page not found|not found|no longer available|"
                      r"domain (is )?for sale|buy this domain|parked|inactive site|"
                      r"האתר אינו פעיל|הדף לא נמצא|העמוד לא נמצא)\b", re.I)
BOT_WALL = re.compile(r"(just a moment|attention required|cloudflare|captcha|"
                      r"access denied|perfdrive|are you a robot|verify you are human)", re.I)


def host_of(u):
    return urlparse(u).netloc.lower().removeprefix("www.").split(":")[0]


def fetch(url):
    wiki = any(h in host_of(url) for h in ("wikipedia.org", "wikisource.org",
                                           "wiktionary.org", "wikimedia.org"))
    headers = {"User-Agent": WIKI_UA if wiki else BROWSER_UA,
               "Accept": "text/html,application/xhtml+xml,*/*;q=0.8",
               "Accept-Language": "en,he;q=0.8"}
    r = requests.get(url, headers=headers, timeout=TIMEOUT, allow_redirects=True,
                     verify=False, stream=True)
    body = b""
    for chunk in r.iter_content(32_768):
        body += chunk
        if len(body) >= MAX_BYTES:
            break
    r.close()
    text = body.decode(r.encoding or "utf-8", errors="replace")
    m = re.search(r"<title[^>]*>(.*?)</title>", text, re.I | re.S)
    title = re.sub(r"\s+", " ", unescape(m.group(1))).strip()[:200] if m else ""
    return r.status_code, r.url, title, r.headers.get("content-type", "")


def classify(url, status, final, title, err):
    if err:
        e = err.lower()
        if "ssl" in e:
            return "ssl-error"
        if "nameresolution" in e or "getaddrinfo" in e or "failed to resolve" in e:
            return "dead-dns"
        if "timed out" in e or "timeout" in e:
            return "timeout"
        if "connection" in e:
            return "connection-refused"
        return "error"
    if status in (401, 403, 429, 999) or (status >= 400 and BOT_WALL.search(title or "")):
        return "blocked"
    if status >= 400:
        return f"dead-{status}"
    if BOT_WALL.search(title or "") or "perfdrive" in final:
        return "blocked"
    same_host = host_of(final) == host_of(url)
    if SOFT_404.search(title or ""):
        return "soft-404"
    if not same_host:
        return "moved-host"
    if final.rstrip("/") != url.rstrip("/"):
        return "redirect"
    return "ok"


def wayback(url):
    try:
        r = requests.get("https://archive.org/wayback/available", params={"url": url},
                         timeout=TIMEOUT)
        snap = r.json().get("archived_snapshots", {}).get("closest")
        if snap and snap.get("available"):
            return snap["url"], snap["timestamp"]
    except Exception:  # noqa: BLE001
        pass
    return "", ""


def check(url):
    row = {"url": url, "status": "", "final_url": "", "title": "", "result": "",
           "error": "", "wayback_url": "", "wayback_ts": ""}
    if not url.startswith("http"):
        row["result"] = "not-http"
        return row
    status, final, title, err = 0, "", "", ""
    for attempt in range(2):
        try:
            status, final, title, _ = fetch(url)
            err = ""
            break
        except Exception as e:  # noqa: BLE001
            err = f"{type(e).__name__}: {e}"[:300]
    row.update(status=status, final_url=final, title=title, error=err,
               result=classify(url, status, final, title, err))
    if row["result"] not in ("ok", "redirect"):
        row["wayback_url"], row["wayback_ts"] = wayback(url)
    return row


def main():
    src, out = sys.argv[1], sys.argv[2]
    items = json.load(open(src, encoding="utf-8"))
    urls = sorted({(i.get("uri") or i.get("url") or "").strip() for i in items} - {""})
    with ThreadPoolExecutor(max_workers=12) as ex:
        rows = list(ex.map(check, urls))
    with open(out, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(Counter(r["result"] for r in rows).most_common())


if __name__ == "__main__":
    main()
