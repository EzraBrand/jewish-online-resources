"""One-off edits requested by the author on 21-Oct-2026 (second batch, from the IDH Index review).

- Add: Scribes of the Cairo Geniza (Zooniverse) under Tools for Navigating Primary Texts >
  Tools for Transcription of manuscripts.
- Add: Alma, an open atlas of the Jewish world in antiquity, under Tools for Navigating
  Primary Texts > Visualizations and Data.
- Add: Talmud NLP Indexer gazetteers (the author's own) under Tools for Navigating Primary
  Texts > Databases.
"""
import json
from pathlib import Path

SEC = Path(__file__).resolve().parents[2] / "data" / "sections"
NEW = {"edition": "2026", "page": None, "number": ""}
CHECKED = "Checked live 21-Oct-2026."


def load(name):
    p = SEC / name
    return p, json.loads(p.read_text(encoding="utf-8"))


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


scribes = {
    "id": "scribes-of-the-cairo-geniza",
    "name": "Scribes of the Cairo Geniza",
    "name_he": "",
    "url": "https://www.scribesofthecairogeniza.org/",
    "access": "open",
    "languages": ["he", "ar", "en"],
    "summary": "Zooniverse citizen-science project in which volunteers sorted and transcribed "
               "Cairo Geniza fragments in Hebrew and Arabic script.",
    "annotation_md": (
        "- Led by the University of Pennsylvania Libraries with the Princeton Geniza Lab, the "
        "JTS Library, the Cambridge Genizah Research Unit, and other partners including the "
        "University of Haifa.\n"
        "- Workflows: sort fragments by script type and difficulty, then transcribe formal "
        "(easier) or informal (harder) Hebrew-script and Arabic-script fragments.\n"
        "- Transcription is now complete; results are listed on the "
        "[Zooniverse publications page](https://www.zooniverse.org/about/publications). The "
        "[Talk forum](https://www.zooniverse.org/projects/judaicadh/scribes-of-the-cairo-geniza/talk) "
        "keeps the volunteers' discussion of individual fragments."
    ),
    "footnotes_md": [],
    "tags": ["geniza", "manuscripts", "transcription"],
    "status_note": "Transcription complete (per the site). " + CHECKED,
    "origin": NEW,
}

alma = {
    "id": "alma-atlas",
    "name": "Alma - An Open Atlas of the Jewish World in Antiquity",
    "name_he": "",
    "url": "https://alma.haifa.ac.il/",
    "access": "open",
    "languages": ["en"],
    "summary": "University of Haifa GIS atlas of textual and archaeological evidence for Jewish "
               "presence, 4th century BCE to 7th century CE.",
    "annotation_md": (
        "- Led by Eyal Ben-Eliyahu (University of Haifa); launched 2015; supported by the Israel "
        "Science Foundation.\n"
        "- Maps geographic references to Jewish communities in Jewish and non-Jewish sources, "
        "using data from the Israel Antiquities Authority and the Academy of the Hebrew "
        "Language's Ma'agarim. Each source is tagged by region, date, language, medium, "
        "archaeological context and literary source.\n"
        "- Pages for the map, data, sources and archaeology (ESRI ArcGIS Experience). Analysis "
        "tools are planned.\n"
        "- Its range starts before this guide's period (c. 100 CE); the rabbinic-period layers "
        "are the relevant part here."
    ),
    "footnotes_md": [],
    "tags": ["geography", "history", "epigraphy", "visualization"],
    "status_note": CHECKED,
    "origin": NEW,
}

gazetteers = {
    "id": "talmud-nlp-indexer-gazetteers",
    "name": "Index of Personal Names, Place Names, and Key Terms in the Talmud "
            "(Talmud NLP Indexer gazetteers)",
    "name_he": "",
    "url": "https://ezrabrand.github.io/talmud-nlp-indexer/glossary/",
    "access": "open",
    "languages": ["en", "he"],
    "summary": "Searchable table of about 4,900 Talmud names, places and terms with variants, "
               "corpus counts, and Wikipedia and Wikidata links.",
    "annotation_md": (
        "- Built from curated gazetteers for tagging the Babylonian Talmud: Talmudic personal "
        "names, Talmudic toponyms, Talmudic concepts, biblical names, biblical places, and "
        "nations and demonyms.\n"
        "- Filter by category; sort by term or count. Entries link to search results on "
        "Bekiut, and many have Hebrew terms and English and Hebrew Wikipedia links; some sages "
        "have teachers, students and dates.\n"
        "- Documentation on [GitHub](https://github.com/EzraBrand/talmud-nlp-indexer/"
        "tree/main/data/glossary_initial)."
    ),
    "footnotes_md": [],
    "tags": ["talmud", "geography", "digital-humanities", "dictionary"],
    "status_note": "Disclosure: the author's own project. " + CHECKED,
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


add("Tools for Navigating Primary Texts", "Tools for Transcription of manuscripts", scribes)
add("Tools for Navigating Primary Texts", "Visualizations and Data", alma)
add("Tools for Navigating Primary Texts", "Databases", gazetteers)
save(p, d)
print("ok")
