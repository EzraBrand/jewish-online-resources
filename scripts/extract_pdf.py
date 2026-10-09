"""Extract text (with structure hints) and all hyperlinks from the 2023 guide PDF.

Usage: py -3.13 -I scripts/extract_pdf.py source/guide-2023.pdf build/
"""
import json
import sys
from pathlib import Path

import pymupdf

pdf_path, out_dir = Path(sys.argv[1]), Path(sys.argv[2])
out_dir.mkdir(parents=True, exist_ok=True)
doc = pymupdf.open(pdf_path)

links = []
text_parts = []
for pno, page in enumerate(doc, start=1):
    text_parts.append(f"\n=== PAGE {pno} ===\n")
    d = page.get_text("dict")
    for block in d["blocks"]:
        for line in block.get("lines", []):
            spans = line["spans"]
            s = "".join(sp["text"] for sp in spans)
            if not s.strip():
                continue
            size = max(sp["size"] for sp in spans)
            bold = any(sp["flags"] & 16 for sp in spans)
            text_parts.append(f"[{size:.0f}{'B' if bold else ''}] {s}\n")
    for ln in page.get_links():
        uri = ln.get("uri")
        if not uri:
            continue
        anchor = page.get_textbox(ln["from"]).strip().replace("\n", " ")
        links.append({"page": pno, "uri": uri, "anchor": anchor})

(out_dir / "guide-2023.txt").write_text("".join(text_parts), encoding="utf-8")
(out_dir / "links-2023.json").write_text(
    json.dumps(links, ensure_ascii=False, indent=1), encoding="utf-8"
)
print(f"pages={len(doc)} links={len(links)} unique={len({l['uri'] for l in links})}")
