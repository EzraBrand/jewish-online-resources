# Data schema

The guide is data-first. Every resource is one JSON entry. The website (table view,
section view) and any future export (Bekiut, PDF, CSV) are generated from these files.

## Files

- `data/sections/NN-<slug>.json` — one file per part of the guide (see `docs/SECTIONS.md`).
- `data/linkcheck.csv` — latest link-rot audit, joined to entries by URL at build time.

## Section file

```json
{
  "part": "B",
  "source_pages": [8, 13],
  "blocks": [
    {
      "section": "Primary Texts",
      "subsection": "Books - text format - popular editions",
      "group": "Open-access",
      "intro_md": "Markdown prose that comes before the list in this block (may be empty).",
      "entries": [ ... ],
      "notes_md": ["Footnotes that belong to the block, not to one entry."]
    }
  ]
}
```

`section` and `subsection` use the 2023 Table of Contents headings exactly.
`group` is a smaller heading inside a subsection ("Open-access", "Requires
subscription or purchase", "Guides by librarians", "Geniza", ...). Empty string if none.

## Entry

```json
{
  "id": "sefaria",
  "name": "Sefaria",
  "name_he": "ספריא",
  "url": "https://www.sefaria.org/texts",
  "access": "open",
  "languages": ["he", "en"],
  "summary": "Own-words summary for the table, max ~30 words.",
  "annotation_md": "The guide's full annotation, as Markdown. Sub-points become nested lists. Inline links as [anchor](url).",
  "footnotes_md": ["Footnote text for this entry, Markdown, links inline."],
  "tags": ["talmud", "translation"],
  "status_note": "",
  "origin": {"edition": "2023", "page": 8, "number": "1"}
}
```

| Field | Rule |
|---|---|
| `id` | Unique kebab-case slug. Prefix nothing. If a name repeats, add a qualifier (`otzar-hahochma-forum`). |
| `name` | English name as the guide gives it. |
| `name_he` | Hebrew name if the guide gives one, in correct logical order. Else `""`. |
| `url` | Primary link exactly as in `build/links-2023.json` (the link on the name). `""` if none. |
| `access` | `open`, `registration`, `freemium`, `subscription`, `purchase`, or `unknown`. |
| `languages` | ISO codes of the content: `he`, `en`, `arc`, `yi`, `de`, `fr`, `ar`, ... |
| `summary` | One sentence, own words, for the table view. |
| `annotation_md` | Everything the guide says about the entry. Keep the author's wording. Keep quotes. |
| `footnotes_md` | Footnotes attached to this entry (by footnote marker). |
| `tags` | Lower-case topic tags. Reuse: `talmud`, `mishnah`, `midrash`, `halakha`, `responsa`, `kabbalah`, `hasidut`, `piyyut`, `liturgy`, `bible-commentary`, `manuscripts`, `geniza`, `printed-books`, `catalog`, `bibliography`, `dictionary`, `encyclopedia`, `journal`, `blog`, `podcast`, `video`, `social-media`, `forum`, `app`, `search`, `ocr-htr`, `transcription`, `digital-humanities`, `ai`, `api`, `visualization`, `translation`, `critical-edition`, `hebrew-language`, `history`, `philosophy`, `epigraphy`, `geography`. |
| `status_note` | Free text if the guide or a later check says something about the state of the site. |
| `origin` | `edition`: `2023` for old entries, `2026` for new ones. `page`: PDF page. `number`: list number as printed. |

## Hebrew text from the PDF

The PDF text layer stores mixed Hebrew/English lines in visual order. Words are
correct, but word order inside a Hebrew run is often reversed, and parentheses and
periods land in the wrong place. Example: `Ben-Yehuda Project (פרויקט יהודה-בן . )`
is really `פרויקט בן-יהודה`. Fix the order by sense. Long Hebrew runs are broken one
word per line; join them.
