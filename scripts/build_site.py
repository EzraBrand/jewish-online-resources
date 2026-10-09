"""Build the static site (GitHub Pages) from data/sections/*.json.

Outputs into site/:
  index.html            table view (filter / search / sort), client-side
  guide.html            full guide, section by section, with all annotations
  data/resources.json   flat list of entries with rendered HTML (feeds index.html)
  resources.csv         flat CSV export

Other modes:
  --dump-urls FILE      write every URL used in the data (for scripts/check_links.py)

Link status comes from data/linkcheck.csv (machine check) and
data/link-overrides.csv (manual verdicts, which win).

Usage: py -3.13 -I scripts/build_site.py [--dump-urls build/all-urls.json]
"""
import csv
import hashlib
import html
import json
import re
import sys
from collections import Counter, OrderedDict
from datetime import date
from pathlib import Path
from urllib.parse import quote, urlparse

import markdown

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
SITE = ROOT / "site"
TEMPLATES = ROOT / "templates"

EDITION = "2026"
BUILD_DATE = date.today().isoformat()

# Order of top-level sections on the site (2023 TOC order, AI appended).
SECTION_ORDER = [
    "Intro",
    "Primary Texts",
    "Tools for Navigating Primary Texts",
    "Secondary literature",
    "Tools for Navigating Secondary Literature",
    "Tertiary literature",
    "Popular Media and Platforms",
    "Artificial Intelligence (new in 2026)",
]

# Host moves that are safe to apply automatically when the checker saw the
# old URL redirect to the new host and the page loaded.
SAFE_HOST_MOVES = {
    "youtu.be": "youtube.com",
    "twitter.com": "x.com",
    "mobile.twitter.com": "x.com",
    "degruyter.com": "degruyterbrill.com",
    "brill.com": "referenceworks.brill.com",
    "digitalhumanities.org": "dhq.digitalhumanities.org",
    "readcoop.eu": "transkribus.org",
    "tashma.jewishoffice.co.il": "tashma.co.il",
    "bhol.co.il": "forums.bhol.co.il",
    "mosaicmagazine.com": "ideas.tikvah.org",
    "blogs.cul.columbia.edu": "blogs.library.columbia.edu",
    "library.brown.edu": "inscriptionsisraelpalestine.org",
    "ub.uni-frankfurt.de": "jewishstudies.de",
}

ACCESS_LABEL = {
    "open": "Open access",
    "registration": "Free, registration",
    "freemium": "Freemium",
    "subscription": "Subscription",
    "purchase": "Purchase",
    "unknown": "Unknown",
}


# ----------------------------------------------------------------------------
# Loading and normalizing


def slug(s):
    s = re.sub(r"[^\w\s-]", "", s.lower(), flags=re.U)
    return re.sub(r"[\s_]+", "-", s).strip("-")


def fix_list_indent(md):
    """Python-Markdown needs 4-space nesting. Rescale 2/3-space nesting."""
    lines = md.split("\n")
    indents = [len(m.group(1)) for m in
               (re.match(r"^( +)(?:[-*+]|\d+\.) ", ln) for ln in lines) if m]
    if not indents:
        return md
    unit = min(indents)
    if unit >= 4:
        return md
    out = []
    for ln in lines:
        m = re.match(r"^( +)(\S.*)$", ln)
        if m:
            level = len(m.group(1)) // unit
            ln = " " * (4 * level) + m.group(2)
        out.append(ln)
    return "\n".join(out)


def ensure_blank_before_lists(md):
    """A list right after a paragraph line needs a blank line in Markdown."""
    out = []
    lines = md.split("\n")
    for i, ln in enumerate(lines):
        if (i > 0 and re.match(r"^(?:[-*+]|\d+\.) ", ln) and lines[i - 1].strip()
                and not re.match(r"^\s*(?:[-*+]|\d+\.) ", lines[i - 1])):
            out.append("")
        out.append(ln)
    return "\n".join(out)


FN_MARK = re.compile(r"\[\^?(\d{1,3}[a-z]?)\](?!\()")


def load_sections():
    files = sorted((DATA / "sections").glob("*.json"))
    blocks = []
    for f in files:
        d = json.loads(f.read_text(encoding="utf-8"))
        for b in d["blocks"]:
            b["_file"] = f.name
            blocks.append(b)
    return blocks


def load_linkcheck():
    status = {}
    p = DATA / "linkcheck.csv"
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            status[r["url"]] = r
    return status


def load_overrides():
    ov = {}
    p = DATA / "link-overrides.csv"
    if p.exists():
        for r in csv.DictReader(open(p, encoding="utf-8-sig")):
            if r.get("url", "").strip():
                ov[r["url"].strip()] = r
    return ov


def host(u):
    return urlparse(u).netloc.lower().removeprefix("www.").split(":")[0]


def verdict_for(url, checks, overrides):
    """Return dict(verdict, href, note, archive) for one URL.

    verdict: ok | moved | dead | hijacked | unverified
    """
    if url in overrides:
        o = overrides[url]
        v = o["verdict"].strip()
        repl = o.get("replacement", "").strip()
        if v == "hijacked" and repl:
            v = "moved"  # old domain is spam, but the content has a new home
        return {"verdict": v, "href": repl or url,
                "note": o.get("note", "").strip(),
                "archive": o.get("archive", "").strip()
                or (checks.get(url, {}).get("wayback_url") or "")}
    c = checks.get(url)
    if not c:
        return {"verdict": "unverified", "href": url, "note": "Not checked yet.",
                "archive": ""}
    res = c["result"]
    arch = c.get("wayback_url", "")
    if res in ("ok", "redirect"):
        return {"verdict": "ok", "href": url, "note": "", "archive": ""}
    if res == "moved-host":
        old, new = host(url), host(c["final_url"])
        if SAFE_HOST_MOVES.get(old) and new.endswith(SAFE_HOST_MOVES[old]):
            return {"verdict": "moved", "href": c["final_url"].replace(":443", ""),
                    "note": f"Moved from {old} to {new}.", "archive": ""}
        return {"verdict": "unverified", "href": url,
                "note": f"Redirects to {new}; needs review.", "archive": arch}
    if res == "blocked":
        st = c.get("wb_last_status", "")
        ts = c.get("wb_last_ts", "")
        if st == "200" and ts[:4] >= "2025":
            return {"verdict": "ok", "href": url,
                    "note": f"Site blocks scripts; archived OK {ts[:4]}-{ts[4:6]}.",
                    "archive": ""}
        return {"verdict": "unverified", "href": url,
                "note": "Site blocks automated checks; verify by hand.", "archive": arch}
    if res == "timeout":
        return {"verdict": "unverified", "href": url, "note": "Timed out during check.",
                "archive": arch}
    return {"verdict": "dead", "href": url, "note": f"Check result: {res}.",
            "archive": arch}


# ----------------------------------------------------------------------------
# Rendering

MD = markdown.Markdown(extensions=["sane_lists"])


def md_to_html(text, entry_id):
    if not text:
        return ""
    text = fix_list_indent(ensure_blank_before_lists(text))
    text = FN_MARK.sub(lambda m: f"@@FN{m.group(1)}@@", text)
    out = MD.reset().convert(text)
    out = re.sub(r"@@FN(\w+)@@",
                 lambda m: f'<sup class="fn"><a href="#fn-{entry_id}-{m.group(1)}">'
                           f'{m.group(1)}</a></sup>', out)
    return out


def footnotes_html(fns, entry_id):
    items = []
    for fn in fns or []:
        m = re.match(r"^\s*\[\^?(\w+)\]:?\s*", fn) or re.match(r"^\s*(\d+)[.)]?\s+", fn)
        num = m.group(1) if m else ""
        body = fn[m.end():] if m else fn
        body_html = md_to_html(body, entry_id)
        body_html = re.sub(r"^<p>(.*)</p>$", r"\1", body_html, flags=re.S)
        items.append(f'<li id="fn-{entry_id}-{num}"><span class="fn-num">{num}</span> '
                     f"{body_html}</li>")
    return f'<ol class="footnotes">{"".join(items)}</ol>' if items else ""


A_TAG = re.compile(r'<a href="([^"]+)"([^>]*)>(.*?)</a>', re.S)


def apply_link_status(htm, checks, overrides, seen):
    def repl(m):
        url, rest, text = html.unescape(m.group(1)), m.group(2), m.group(3)
        if url.startswith("#"):
            return m.group(0)
        v = verdict_for(url, checks, overrides)
        seen[url] = v
        href = html.escape(v["href"], quote=True)
        note = html.escape(v["note"], quote=True)
        arch = html.escape(v["archive"], quote=True)
        if v["verdict"] == "hijacked":
            a = f' <a class="archive" href="{arch}">[archived copy]</a>' if arch else ""
            return (f'<span class="link-removed" title="{note}">{text}</span>'
                    f'<span class="badge bad">link removed</span>{a}')
        if v["verdict"] == "dead":
            a = f' <a class="archive" href="{arch}">[archived copy]</a>' if arch else ""
            return (f'<a class="dead" href="{href}" title="{note}">{text}</a>'
                    f'<span class="badge bad">dead link</span>{a}')
        cls = {"moved": "moved", "unverified": "unverified"}.get(v["verdict"], "")
        c = f' class="{cls}"' if cls else ""
        t = f' title="{note}"' if note else ""
        return f'<a href="{href}"{c}{t}>{text}</a>'
    return A_TAG.sub(repl, htm)


def flatten(blocks, checks, overrides):
    entries, seen_ids, link_seen = [], Counter(), {}
    for b in blocks:
        for i, e in enumerate(b["entries"]):
            eid = e.get("id") or slug(e["name"])
            seen_ids[eid] += 1
            if seen_ids[eid] > 1:
                eid = f"{eid}-{seen_ids[eid]}"
            ann = md_to_html(e.get("annotation_md", ""), eid)
            fns = footnotes_html(e.get("footnotes_md"), eid)
            ann = external_new_tab(apply_link_status(ann, checks, overrides, link_seen))
            fns = external_new_tab(apply_link_status(fns, checks, overrides, link_seen))
            url = e.get("url", "")
            uv = verdict_for(url, checks, overrides) if url else None
            if url:
                link_seen[url] = uv
            origin = e.get("origin", {}) or {}
            entries.append({
                "id": eid,
                "name": e["name"],
                "name_he": e.get("name_he", ""),
                "url": uv["href"] if uv else "",
                "url_original": url,
                "link_verdict": uv["verdict"] if uv else "none",
                "link_note": uv["note"] if uv else "",
                "link_archive": uv["archive"] if uv else "",
                "section": b["section"],
                "subsection": b.get("subsection", ""),
                "group": b.get("group", ""),
                "access": e.get("access", "unknown"),
                "languages": e.get("languages", []),
                "summary": e.get("summary", ""),
                "tags": e.get("tags", []),
                "status_note": e.get("status_note", ""),
                "edition": str(origin.get("edition", "2023")),
                "page": origin.get("page"),
                "number": origin.get("number", ""),
                "annotation_html": ann,
                "footnotes_html": fns,
            })
    return entries, link_seen


def section_key(s):
    return SECTION_ORDER.index(s) if s in SECTION_ORDER else len(SECTION_ORDER)


def render_guide(blocks, entries, checks, overrides, link_seen):
    by_block = {}
    it = iter(entries)
    for bi, b in enumerate(blocks):
        by_block[bi] = [next(it) for _ in b["entries"]]
    tree = OrderedDict()
    order = sorted(range(len(blocks)), key=lambda i: (section_key(blocks[i]["section"]), i))
    for bi in order:
        b = blocks[bi]
        tree.setdefault(b["section"], OrderedDict()).setdefault(
            b.get("subsection", ""), []).append(bi)

    toc, body = [], []
    for sec, subs in tree.items():
        sid = slug(sec)
        toc.append(f'<li><a href="#{sid}">{html.escape(sec)}</a><ul>')
        body.append(f'<section id="{sid}"><h2>{html.escape(sec)}</h2>')
        for sub, bis in subs.items():
            ssid = f"{sid}--{slug(sub)}" if sub else sid
            if sub:
                toc.append(f'<li><a href="#{ssid}">{html.escape(sub)}</a></li>')
                body.append(f'<h3 id="{ssid}">{html.escape(sub)}</h3>')
            for bi in bis:
                b = blocks[bi]
                if b.get("group"):
                    body.append(f'<h4>{html.escape(b["group"])}</h4>')
                if b.get("intro_md"):
                    intro = apply_link_status(md_to_html(b["intro_md"], f"b{bi}"),
                                              checks, overrides, link_seen)
                    body.append(f'<div class="block-intro">{intro}</div>')
                for e in by_block[bi]:
                    body.append(entry_card(e))
                notes = b.get("notes_md") or []
                if notes:
                    nh = footnotes_html(notes, f"b{bi}")
                    body.append('<div class="block-notes">'
                                + apply_link_status(nh, checks, overrides, link_seen)
                                + "</div>")
        toc.append("</ul></li>")
        body.append("</section>")
    return "\n".join(toc), "\n".join(body)


def access_badge(a):
    return f'<span class="badge acc-{a}">{ACCESS_LABEL.get(a, a)}</span>'


def entry_card(e):
    he = (f' <span class="he" dir="rtl" lang="he">{html.escape(e["name_he"])}</span>'
          if e["name_he"] else "")
    if e["url"] and e["link_verdict"] == "hijacked":
        name = f'<span class="link-removed">{html.escape(e["name"])}</span>'
    elif e["url"]:
        cls = " dead" if e["link_verdict"] == "dead" else ""
        name = f'<a class="entry-link{cls}" href="{html.escape(e["url"], quote=True)}">{html.escape(e["name"])}</a>'
    else:
        name = html.escape(e["name"])
    badges = [access_badge(e["access"])]
    if e["edition"] == EDITION:
        badges.append('<span class="badge new">New in 2026</span>')
    if e["link_verdict"] in ("dead", "hijacked"):
        badges.append('<span class="badge bad">dead link</span>')
        if e["link_archive"]:
            badges.append(f'<a class="archive" href="{html.escape(e["link_archive"], quote=True)}">[archived copy]</a>')
    elif e["link_verdict"] == "moved":
        badges.append('<span class="badge moved" title="'
                      + html.escape(e["link_note"], quote=True) + '">link updated</span>')
    status = (f'<p class="status-note">{html.escape(e["status_note"])}</p>'
              if e["status_note"] else "")
    return (f'<article class="entry" id="{e["id"]}"><h5>{name}{he} {" ".join(badges)}</h5>'
            f'{status}<div class="annotation">{e["annotation_html"]}</div>'
            f'{e["footnotes_html"]}</article>')


def render_intro():
    parts = []
    for name in ("preface-2026.md", "intro-2023.md"):
        p = ROOT / "content" / name
        if p.exists():
            parts.append(markdown.markdown(p.read_text(encoding="utf-8"),
                                           extensions=["footnotes", "sane_lists"]))
    return "\n<hr>\n".join(parts)


def write_csv(entries, path):
    cols = ["id", "name", "name_he", "url", "link_verdict", "section", "subsection",
            "group", "access", "languages", "tags", "summary", "edition", "page",
            "number", "status_note"]
    with open(path, "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=cols, extrasaction="ignore")
        w.writeheader()
        for e in entries:
            row = dict(e)
            row["languages"] = ", ".join(e["languages"])
            row["tags"] = ", ".join(e["tags"])
            w.writerow(row)


EXTERNAL_A = re.compile(r'<a (?![^>]*\btarget=)([^>]*\bhref="https?://[^"]*"[^>]*)>')


def external_new_tab(htm):
    """Open every external link in a new tab."""
    return EXTERNAL_A.sub(r'<a \1 target="_blank" rel="noopener">', htm)


def fill(template, **kw):
    t = (TEMPLATES / template).read_text(encoding="utf-8")
    for k, v in kw.items():
        t = t.replace("{{" + k + "}}", str(v))
    return external_new_tab(t)


def all_urls(blocks):
    urls = set()
    rx = re.compile(r"\]\((https?://[^)\s]+(?:\([^)\s]*\)[^)\s]*)*)\)")
    for b in blocks:
        for txt in [b.get("intro_md", "")] + list(b.get("notes_md") or []):
            urls.update(rx.findall(txt or ""))
        for e in b["entries"]:
            if e.get("url"):
                urls.add(e["url"])
            for txt in [e.get("annotation_md", "")] + list(e.get("footnotes_md") or []):
                urls.update(rx.findall(txt or ""))
    return sorted(urls)


def main():
    blocks = load_sections()
    if "--dump-urls" in sys.argv:
        out = Path(sys.argv[sys.argv.index("--dump-urls") + 1])
        urls = all_urls(blocks)
        out.write_text(json.dumps([{"url": u} for u in urls], indent=0), encoding="utf-8")
        print(f"{len(urls)} urls -> {out}")
        return
    checks, overrides = load_linkcheck(), load_overrides()
    entries, link_seen = flatten(blocks, checks, overrides)
    toc, body = render_guide(blocks, entries, checks, overrides, link_seen)
    intro = apply_link_status(render_intro(), checks, overrides, link_seen)

    (SITE / "data").mkdir(parents=True, exist_ok=True)
    (SITE / "data" / "resources.json").write_text(
        json.dumps({"edition": EDITION, "built": BUILD_DATE,
                    "sections": SECTION_ORDER, "entries": entries},
                   ensure_ascii=False), encoding="utf-8")
    write_csv(entries, SITE / "resources.csv")

    n_new = sum(e["edition"] == EDITION for e in entries)
    # Content hashes as ?v= stamps, so browsers and the Pages CDN never serve a
    # stale CSS/JS/data file after a deploy.
    def v(path):
        return hashlib.sha1((SITE / path).read_bytes()).hexdigest()[:10]
    common = dict(built=BUILD_DATE, n_entries=len(entries), n_new=n_new,
                  v_css=v("assets/style.css"), v_app=v("assets/app.js"),
                  v_guide=v("assets/guide.js"), v_data=v("data/resources.json"))
    (SITE / "guide.html").write_text(
        fill("guide.html", toc=toc, body=body, intro=intro, **common), encoding="utf-8")
    (SITE / "index.html").write_text(fill("index.html", **common), encoding="utf-8")
    counts = Counter(v["verdict"] for v in link_seen.values())
    summary = ", ".join(f"{k}: {n}" for k, n in counts.most_common())
    print(f"entries={len(entries)} new={n_new} links={len(link_seen)} {summary}")


if __name__ == "__main__":
    main()
