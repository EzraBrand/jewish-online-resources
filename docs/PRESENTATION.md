# Presentation options (brainstorm)

The 2023 guide is a 47-page PDF: nested numbered lists, long annotations, about 80
footnotes. That works for reading straight through. It does not work well for the
questions people usually bring to it ("is there a free Yerushalmi manuscript viewer?",
"what is open access in Hebrew?"), and it cannot show link status.

The repo is now **data-first**: one JSON entry per resource (`data/sections/*.json`,
schema in `docs/SCHEMA.md`). Each view below is a renderer over the same data. So the
views are not exclusive. We can try one and add another later.

## Built now

1. **Filterable table** (`site/index.html`). One row per resource: name (English and
   Hebrew), section, access, language, one-line summary, topic tags, and a "Notes"
   toggle with the full annotation and footnotes. There is free-text search (it ignores
   niqqud), filters for section, access, language, and topic, and toggles for "New in
   2026" and "hide dead links". The filter state goes into the URL, so a filtered view can
   be shared. Example: `index.html#tag=geniza&access=open`.
2. **Full guide** (`site/guide.html`). The traditional reading order, with a sticky
   table of contents, one card per resource, and footnotes kept with their resource.
   This replaces the PDF.
3. **Link report** (`site/link-report.html`). A public list of what rotted, moved, or
   was hijacked.
4. **CSV export** (`site/resources.csv`).

## Ideas for later

| Idea | Value | Cost |
|---|---|---|
| **Card grid with facets** (like jewishai.me "Cards") | Good on mobile, and good for browsing | Low. It is a second renderer over the same JSON. |
| **"Task" pathways**, e.g. "I want to: read a text / see a manuscript / find secondary literature / check a word" | Fits the questions readers ask. A short curated path per task, with links into the table. | Medium. It needs editorial writing, plus a `tasks` field on entries. |
| **Corpus × resource-type matrix** (rows: Bible commentary, Mishnah, Bavli, Yerushalmi, Midrash, Halakha, Kabbalah, Piyyut...; columns: text, translation, manuscripts, critical edition, dictionary, bibliography) | Shows coverage and gaps at a glance. A good "state of the field" figure for the talk or paper. | Medium. It needs a `corpus` tag per entry (the topic tags are part of the way there). |
| **Per-entry pages** (`/r/sefaria`) | Stable URLs to cite, and better for SEO | Low with the current build script |
| **Hebrew UI (RTL) toggle** | Most of the audience reads Hebrew, and many resources are Hebrew-only | Medium. It needs translated summaries. |
| **Change log / "what changed since 2023"** per entry | Shows the guide is maintained | Low. Diff `link_verdict` and the editions. |
| **Scheduled link check** (GitHub Action, monthly) that opens an issue for new rot | Keeps the guide honest without manual audits | Low. The scripts exist. |
| **Embed in Bekiut** | One home for the author's digital work | The data is plain JSON plus a small JS file. It can be served as-is under a Bekiut route, or fetched from the GitHub Pages URL. |

## Recommendation

Keep the table as the landing page and the full guide as the "read it" view. The next
step with the most value is the **corpus × resource-type matrix**, because it turns the
guide into an argument about where the field has gaps, not only a list. After that, add
**per-entry pages** and the **scheduled link check**.
