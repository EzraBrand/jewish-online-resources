# Conversion parts

The 2023 PDF was split into parts for conversion to JSON. Line numbers refer to
`build/guide-2023.txt` (output of `scripts/extract_pdf.py`).

| Part | Lines | Covers (2023 TOC headings) | Output |
|---|---|---|---|
| A | 1–414 | Front matter, Intro, Electronic vs. physical, Existing Guides, This Guide, Primary Texts intro | `content/intro-2023.md`, `data/sections/00-existing-guides.json` |
| B | 415–769 | Books - text format - popular editions; Books - text format - scholarly editions | `data/sections/10-books-text.json` |
| C | 770–1051 | Books - PDF format; Manuscripts - General | `data/sections/20-books-pdf-manuscripts.json` |
| D | 1052–1431 | Manuscripts - by Topic | `data/sections/30-manuscripts-by-topic.json` |
| E | 1432–1783 | Tools for Navigating Primary Texts (search, transcription, bibliographic info general and by topic, databases) | `data/sections/40-tools-primary.json` |
| F | 1784–2253 | Secondary literature: Books, Journals | `data/sections/50-secondary-books-journals.json` |
| G | 2254–2590 | Secondary: Articles; Tools for Navigating Secondary Literature; Tertiary literature | `data/sections/60-articles-tertiary.json` |
| H | 2591–end | Popular Media and Platforms | `data/sections/70-popular-media.json` |
| AI | — | New in 2026: AI section, plus new non-AI projects from Powered by Sefaria and jewishai.me | `data/sections/80-ai.json`, `data/sections/90-new-2026.json` |
