"""One-off edits requested by the author on 9-Oct-2026.

- New URLs: Qerovot-of-18, Seforim Chatter, Frankfurt "Online Resources Jewish Studies".
- Remove nine 2026 additions from 90-new-2026.json.
- Remove the AI "Readings" subsection from 80-ai.json.
"""
import json
from pathlib import Path

SEC = Path(__file__).resolve().parents[2] / "data" / "sections"

URL_FIXES = {
    "https://www.qerovot18.com/": "http://www.qerovot18.com/index.aspx",
    "https://www.ub.uni-frankfurt.de/judaica3/en/corona_en.html":
        "https://www.jewishstudies.de/en/service/informationssammlung/digitale-angebote/"
        "digitale-angebote-judische-studien/",
}
SEFORIM_CHATTER = "https://seforimchatter.com/episodes"

REMOVE_NAMES = {"Bavli Kilvavi", "Talmud.page", "Shitufta", "Otzaria", "Talmud Navigator",
                "Sefaria Sidebar Extension", "Jastrow App", "Jastrow Search", "Torah Tree"}


def load(name):
    p = SEC / name
    return p, json.loads(p.read_text(encoding="utf-8"))


def save(p, d):
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


changed = []
for p in sorted(SEC.glob("*.json")):
    d = json.loads(p.read_text(encoding="utf-8"))
    dirty = False
    for b in d["blocks"]:
        for e in b["entries"]:
            old = e.get("url", "")
            if old in URL_FIXES:
                e["url"] = URL_FIXES[old]
                e["annotation_md"] = e.get("annotation_md", "").replace(old, URL_FIXES[old])
                changed.append((p.name, e["name"], old, e["url"]))
                dirty = True
            if e["name"].startswith("Seforim Chatter") and b["section"] == "Popular Media and Platforms":
                changed.append((p.name, e["name"], old, SEFORIM_CHATTER))
                e["url"] = SEFORIM_CHATTER
                dirty = True
    if dirty:
        save(p, d)

p, d = load("90-new-2026.json")
removed = [e["name"] for b in d["blocks"] for e in b["entries"] if e["name"] in REMOVE_NAMES]
for b in d["blocks"]:
    b["entries"] = [e for e in b["entries"] if e["name"] not in REMOVE_NAMES]
d["blocks"] = [b for b in d["blocks"] if b["entries"]]
save(p, d)

p, d = load("80-ai.json")
n_read = sum(len(b["entries"]) for b in d["blocks"] if b["subsection"].startswith("Readings"))
d["blocks"] = [b for b in d["blocks"] if not b["subsection"].startswith("Readings")]
save(p, d)

for c in changed:
    print("url:", *c, sep=" | ")
print("removed from 90:", len(removed), sorted(removed))
print("removed AI readings:", n_read)
