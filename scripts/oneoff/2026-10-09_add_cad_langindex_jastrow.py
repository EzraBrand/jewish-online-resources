"""One-off edits requested by the author on 9-Oct-2026.

- Jastrow: primary link -> Bekiut's modernized Jastrow (the author's own project).
- Add: CAD Digital Edition (demo) under Tertiary literature > Dictionaries.
- Add: Unified index for Hebrew language research (lang.emeiri.org) under
  Tools for Navigating Secondary Literature > Bibliographic Information and Indexes.
"""
import json
from pathlib import Path

SEC = Path(__file__).resolve().parents[2] / "data" / "sections"
NEW = {"edition": "2026", "page": None, "number": ""}


def load(name):
    p = SEC / name
    return p, json.loads(p.read_text(encoding="utf-8"))


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


# --- Jastrow -> Bekiut ------------------------------------------------------
p, d = load("60-articles-tertiary.json")
for b in d["blocks"]:
    for e in b["entries"]:
        if e["id"] == "jastrow-dictionary":
            e["url"] = "https://bekiut.com/jastrow"
            e["summary"] = ("Jastrow's English dictionary of Talmudic and Midrashic Hebrew and "
                            "Aramaic: a modernized, searchable edition on Bekiut, plus copies on "
                            "Sefaria, Wikisource, and Tyndale House.")
            bullet = ("- Bekiut: [here](https://bekiut.com/jastrow). Modernized presentation, with "
                      "expanded abbreviations, search, and browsing by letter. (Added 2026.)\n")
            if "bekiut.com/jastrow" not in e["annotation_md"]:
                e["annotation_md"] = e["annotation_md"].replace("In English:\n",
                                                                "In English:\n" + bullet, 1)
            e["status_note"] = "Disclosure: the Bekiut edition is the author's own project."
save(p, d)

# --- new entries ------------------------------------------------------------
cad = {
    "id": "cad-digital-edition",
    "name": "The Assyrian Dictionary (CAD): digital edition (demo)",
    "name_he": "",
    "url": "https://cad-demo-29bdca5fec.netlify.app/",
    "access": "open",
    "languages": ["en", "akk"],
    "summary": ("Searchable demo edition of five volumes of the Chicago Assyrian Dictionary, "
                "cross-linked to Akkadian citations in BDB, HALOT, DCH, CAL and Sokoloff."),
    "annotation_md": (
        "Demo covering CAD volumes P, R, T, Ṭ and U/W, parsed from the typeset volumes "
        "(no OCR), with the page facsimile alongside each article.\n\n"
        "- Search by headword or root, English definition, or full article text; filter by "
        "volume, part of speech, and etymology (Sumerian, Hurrian, Aramaic, West Semitic, ...).\n"
        "- \"Semitic concordance\": filters for entries that BDB, HALOT, DCH, CAL (Comprehensive "
        "Aramaic Lexicon) or Sokoloff cite as Akkadian comparanda, plus computed cognate "
        "candidates, which the site itself calls prompts for research, not etymologies.\n"
        "- Optional display of the Akkadian forms in Hebrew script with niqqud.\n"
        "- Useful for Akkadian loanwords and cognates in Talmudic and Targumic Aramaic."),
    "footnotes_md": [],
    "tags": ["dictionary", "hebrew-language", "digital-humanities"],
    "status_note": "Demo; checked live 9-Oct-2026.",
    "origin": NEW,
}
langindex = {
    "id": "unified-language-index",
    "name": "Unified index for Hebrew language research (Ephraim Meiri)",
    "name_he": "מפתח מאוחד ללשון חכמים",
    "url": "https://lang.emeiri.org/",
    "access": "open",
    "languages": ["he"],
    "summary": ("Searchable merged index of the word and topic indexes of scholarly books on the "
                "language of Rabbinic and later Hebrew and Aramaic sources."),
    "annotation_md": (
        "Combines the language indexes of research books on Hebrew and Aramaic of the sources and "
        "their interpretation, from the Tannaitic period to the revival of Hebrew (Biblical and "
        "Modern Hebrew are left out on purpose). The aim is to fill the gap left by the lack of an "
        "up-to-date research dictionary for post-biblical Hebrew.\n\n"
        "- Search entries, words, roots, phrases, patterns (משקלים) and linguistic phenomena; "
        "there is a [bibliography](https://lang.emeiri.org/bibliography) of the indexed books and "
        "an [about](https://lang.emeiri.org/about) page.\n"
        "- Started in 2025; several authors (among them Menahem Kister and the late Menahem I. "
        "Kahana) contributed the indexes of their books. Marked by the site as in development."),
    "footnotes_md": [],
    "tags": ["hebrew-language", "bibliography", "search"],
    "status_note": "In development; checked live 9-Oct-2026.",
    "origin": NEW,
}

p, d = load("90-new-2026.json")


def add(section, subsection, entry):
    for b in d["blocks"]:
        if (b["section"], b["subsection"], b["group"]) == (section, subsection, "New in 2026"):
            b["entries"] = [e for e in b["entries"] if e["id"] != entry["id"]] + [entry]
            return
    d["blocks"].append({"section": section, "subsection": subsection, "group": "New in 2026",
                        "intro_md": "", "entries": [entry], "notes_md": []})


add("Tertiary literature", "Dictionaries", cad)
add("Tools for Navigating Secondary Literature", "Bibliographic Information and Indexes", langindex)
save(p, d)
print("ok")
