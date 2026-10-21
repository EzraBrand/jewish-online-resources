"""One-off edits requested by the author on 21-Oct-2026.

- Add: Dicta Genizah Search (Hillel Gershuni) under Primary Texts > Manuscripts - by Topic.
- Add: Girsology (Joshua Waxman) under Primary Texts > Books - text format - popular editions.
- Add: RabbiNet (JEWDIT Lab, Bar-Ilan) under Tools for Navigating Primary Texts >
  Visualizations and Data.
- AI section: add Iluy (Dicta's combined AI answer tool) and Dicta-LM 3.0; point the
  Dicta tools entry to both.
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


genizah_search = {
    "id": "dicta-genizah-search",
    "name": "Dicta Genizah Search",
    "name_he": "חיפוש בגניזה הקהירית",
    "url": "https://genizahsearch.com/",
    "access": "open",
    "languages": ["he", "arc", "ar", "en"],
    "summary": "Full-text search over the MiDRASH automatic transcriptions of about 255,000 "
               "Cairo Genizah manuscripts, with images, parallels and join search.",
    "annotation_md": (
        "- Built by Hillel Gershuni; presented at the ISF workshop on AI and Talmudic research "
        "(Hemdat, Oct-2026).\n"
        "- Searches the MiDRASH project's computer-read transcriptions (about 232,000 automatic "
        "and 27,000 scholarly transcriptions; over 1 million pages). The site warns that the "
        "automatic readings contain errors.\n"
        "- Tools: exact, spelling-variant and regex search; parallel detection for a pasted "
        "text; a Joins Lab for possible physical joins; browsing by shelfmark and by "
        "identification (domain, author, work); computed identifications to review; and a "
        "beta Genizah Atlas.\n"
        "- Also offers a ChatGPT connector. Login is optional for saved lists."
    ),
    "footnotes_md": [],
    "tags": ["geniza", "manuscripts", "search", "ocr-htr", "transcription", "ai"],
    "status_note": CHECKED,
    "origin": NEW,
}

girsology = {
    "id": "girsology",
    "name": "Girsology",
    "name_he": "",
    "url": "https://www.girsology.com/",
    "access": "open",
    "languages": ["he", "arc", "en"],
    "summary": "Joshua Waxman's Talmud site in the Vilna tzurat ha-daf layout, with sugya "
               "outlines, a who-asks-whom graph of the sages, and a logic engine for sugyot.",
    "annotation_md": (
        "- Designed and coded by Joshua Waxman; texts mainly from Sefaria. Presented at the ISF "
        "workshop on AI and Talmudic research (Hemdat, Oct-2026).\n"
        "- Each daf keeps the look of the Vilna page. On top of it, sample sugyot have three "
        "layers: the people in the sugya and who asks, answers or disputes whom; the argument "
        "as an outline of question, answer and objection; and the argument encoded as facts "
        "and rules, with what a solver derives from them.\n"
        "- Also: sugya outlines and the Vilna and Steinsaltz sugya divisions by tractate; the "
        "Rif with Ran and Nimukei Yosef in page layout; vocalized Rosh; and research notebooks "
        "(Google Colab).\n"
        "- Waxman has permission to use the Hachi Garsinan manuscript images, so the site plans "
        "to show manuscript variants (girsaot)."
    ),
    "footnotes_md": [],
    "tags": ["talmud", "visualization", "digital-humanities", "manuscripts"],
    "status_note": "Work in progress. " + CHECKED,
    "origin": NEW,
}

rabbinet = {
    "id": "rabbinet",
    "name": "RabbiNet",
    "name_he": "",
    "url": "https://rabbinet.netlify.app/",
    "access": "open",
    "languages": ["en", "he"],
    "summary": "Interactive citation network of 257 medieval rabbinic scholars (8th-16th c.): "
               "who cites whom, filterable by century and region.",
    "annotation_md": (
        "- From the Bar-Ilan JEWDIT Lab (Digital Lab for Jewish Heritage): the project "
        "*Digital Mapping of Intellectual Affinities in the Literature of the Rishonim*, "
        "presented by Binyamin Katzoff and the Bar-Ilan team at the ISF workshop on AI and "
        "Talmudic research (Hemdat, Oct-2026).\n"
        "- Filter citing and cited scholars by century and region (Ashkenaz, France, Italy, "
        "Middle East, North Africa, Provence, Spain). Networks can be saved and reloaded.\n"
        "- Method papers: Ben-Gigi, Zhitomirsky-Geffet, Schler and Katzoff, "
        "\"[Automatic Construction of the Citation Network from the Medieval Jewish Responsa "
        "Literature](https://dl.acm.org/doi/full/10.1145/3712013)\"; and "
        "\"[Citation network analysis for viewpoint plurality assessment of historical corpora: "
        "The case of the medieval rabbinic literature]"
        "(https://journals.plos.org/plosone/article?id=10.1371/journal.pone.0307115)\" "
        "(PLOS ONE, 2024)."
    ),
    "footnotes_md": [],
    "tags": ["responsa", "history", "visualization", "digital-humanities"],
    "status_note": CHECKED,
    "origin": NEW,
}

iluy = {
    "id": "dicta-iluy",
    "name": "Iluy (Dicta)",
    "name_he": "עילוי",
    "url": "https://iluy.dicta.org.il/",
    "access": "open",
    "languages": ["he", "en"],
    "summary": "Dicta's AI tool that answers questions from retrieved rabbinic sources, each "
               "claim with a reference to check; replaces Dicta's two earlier chatbots.",
    "annotation_md": (
        "- Dicta's two earlier, separate chatbot tools are now combined in this one site.\n"
        "- Covers Talmud and lomdus, Bible commentary, thought, Hasidut and musar, and "
        "halakha. In halakha it sets out the sources and does not give a ruling.\n"
        "- Answers are built on sources it actually retrieved, not on the model's memory, "
        "with links to each source. It finds sources that use different wording from the "
        "question.\n"
        "- Five answer styles: sources only, short, fluent modern Hebrew, lamdani "
        "(rabbinic Hebrew), and responsum. You can ask in one language and get the answer in "
        "another.\n"
        "- No free follow-up questions yet; instead you can get an explanation of a source, "
        "re-answer in another style, or retrieve more sources. A public archive of answers "
        "is at [all-questions](https://iluy.dicta.org.il/all-questions)."
    ),
    "footnotes_md": [],
    "tags": ["ai", "search", "halakha", "talmud"],
    "status_note": CHECKED,
    "origin": NEW,
}

dicta_lm = {
    "id": "dicta-lm-3",
    "name": "Dicta-LM 3.0",
    "name_he": "",
    "url": "https://dicta.org.il/dicta-lm-3",
    "access": "open",
    "languages": ["he", "en"],
    "summary": "Dicta's open-weight Hebrew-English language models (24B, 12B, 1.7B), "
               "Apache-2.0, built with Israel's National NLP Program.",
    "annotation_md": (
        "- Released by Dicta with the DDR&D / Israeli National Program for NLP.\n"
        "- Continued pretraining of open base models (Mistral Small 3.1, NVIDIA Nemotron Nano "
        "V2, Qwen3) on about 150B tokens, 75% Hebrew and 25% English, then SFT and RL into "
        "instruct and reasoning chat models.\n"
        "- 65k-token context (about 26k Hebrew words) and tool calling. The 24B model leads "
        "the Open Hebrew LLM Leaderboard among models up to 70B, per Dicta.\n"
        "- Weights: [DictaLM 3.0 collection on Hugging Face]"
        "(https://huggingface.co/collections/dicta-il/dictalm-30-collection); "
        "[technical report](https://dicta.org.il/publications/DictaLM_3_0___Techincal_Report.pdf)."
    ),
    "footnotes_md": [],
    "tags": ["ai", "hebrew-language"],
    "status_note": CHECKED,
    "origin": NEW,
}

# --- 90-new-2026: Genizah Search, Girsology, RabbiNet ----------------------
p, d = load("90-new-2026.json")


def add(section, subsection, entry):
    for b in d["blocks"]:
        if (b["section"], b["subsection"], b["group"]) == (section, subsection, "New in 2026"):
            b["entries"] = [e for e in b["entries"] if e["id"] != entry["id"]] + [entry]
            return
    d["blocks"].append({"section": section, "subsection": subsection, "group": "New in 2026",
                        "intro_md": "", "entries": [entry], "notes_md": []})


add("Primary Texts", "Manuscripts - by Topic", genizah_search)
add("Primary Texts", "Books - text format - popular editions", girsology)
add("Tools for Navigating Primary Texts", "Visualizations and Data", rabbinet)
save(p, d)

# --- 80-ai: Iluy, Dicta-LM 3.0, Dicta tools pointer ------------------------
p, d = load("80-ai.json")


def put(group, entry, after=None):
    for b in d["blocks"]:
        if b["group"] == group:
            es = [e for e in b["entries"] if e["id"] != entry["id"]]
            ids = [e["id"] for e in es]
            i = ids.index(after) + 1 if after in ids else len(es)
            b["entries"] = es[:i] + [entry] + es[i:]
            return
    raise SystemExit("group not found: " + group)


put("Retrieval with citations", iluy, after="sefaria-ai-library-assistant")
put("Models and datasets", dicta_lm, after="dicta-hugging-face")

old = ("- Dicta, led by Moshe Koppel, also publishes open language models "
       "(see the Dicta Hugging Face entry below).")
new = ("- Dicta, led by Moshe Koppel, also runs [Iluy](https://iluy.dicta.org.il/), its AI "
       "answer tool over rabbinic sources (see the Iluy entry above), and publishes open "
       "language models (see the Dicta-LM 3.0 and Dicta Hugging Face entries below).")
for b in d["blocks"]:
    for e in b["entries"]:
        if e["id"] == "dicta-tools-2026":
            assert old in e["annotation_md"] or "iluy.dicta" in e["annotation_md"]
            e["annotation_md"] = e["annotation_md"].replace(old, new)
        if e["id"] == "dicta-hugging-face" and "dicta-lm-3" not in e["annotation_md"]:
            e["annotation_md"] = e["annotation_md"].replace(
                "- **DictaLM 3.0** (late 2025):",
                "- **DictaLM 3.0** (late 2025; [release page](https://dicta.org.il/dicta-lm-3)):", 1)
save(p, d)
print("ok")
