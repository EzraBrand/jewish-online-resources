# Guide to Online Resources for Scholarly Jewish Study and Research – 2026

The 2026 update of Ezra Brand's *Guide to Online Resources for Scholarly Jewish Study and
Research – 2023* (v6, 4-Dec-2023, [Academia.edu](https://www.academia.edu/83334340/Guide_to_Online_Resources_for_Scholarly_Jewish_Study_and_Research_2023)).
The guide is now a data set plus a static website (GitHub Pages). The site has a
filterable table, the full annotated guide, a link-rot report, and a CSV export.

## Layout

| Path | What |
|---|---|
| `source/guide-2023.pdf` | The 2023 PDF (input, never edited). Local only, not in git. |
| `source/web/` | Saved copies of source pages (jewishai.me table). Local only, not in git. |
| `data/sections/*.json` | **The guide.** One file per part, one entry per resource. Schema: `docs/SCHEMA.md` |
| `data/linkcheck.csv` | Latest machine link check (status, final URL, page title, Wayback) |
| `data/link-overrides.csv` | Manual link verdicts. These win over the machine check. |
| `content/*.md` | Prose: 2026 preface, 2023 introduction |
| `templates/` | HTML shells for the generated pages |
| `site/` | The published site. `site/assets/` is hand-written; the rest is generated. |
| `scripts/` | Extraction, link check, build |
| `build/` | Scratch outputs (text dump, link lists, candidate reviews). Not published. |
| `docs/` | Schema, conversion notes, presentation options |

## Rebuild

```bash
py -3.13 -I scripts/build_site.py
```

## Re-check links

```bash
py -3.13 -I scripts/build_site.py --dump-urls build/all-urls.json
py -3.13 -I scripts/check_links.py build/all-urls.json data/linkcheck.csv
py -3.13 -I scripts/wayback_last.py data/linkcheck.csv
py -3.13 -I scripts/build_site.py
```

Some sites (NLI, academia.edu, Bar-Ilan, Herzog, Open Siddur) block scripted requests.
`wayback_last.py` accepts those as alive if the Wayback Machine has a 2025+ capture with
status 200. Otherwise they stay "unverified" in the report until someone checks them in a
browser and records the result in `data/link-overrides.csv`.

## Preview locally

```bash
py -3.13 -m http.server 8771 --directory site
```

## Review files

- `build/candidates-review.csv`: every candidate from Powered by Sefaria and jewishai.me,
  with the include/exclude decision and a reason.
- `build/link-report.html`: every link that is not plainly OK. Maintainer-only. It is not
  in `site/`, so GitHub Pages does not publish it.
