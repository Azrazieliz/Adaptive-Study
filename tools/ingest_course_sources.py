#!/usr/bin/env python3
"""Install user-owned medical course PDFs as readable local source pages.

This tool never generates study facts, flashcards, summaries or exam questions.
Public Git ignores local_instance: private PDF material stays on the device.
"""
from __future__ import annotations
import argparse
import json
import os
import re
import shutil
import tempfile
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = "window.STUDY_CONTENT = "
# Patterns are deliberately specific. Ambiguous filenames are skipped.
COURSE_MAP = [
    ("produits de sante", "sp_produits_sante", "sp", "Produits de santé"),
    ("precarite", "sp_precarite", "sp", "Précarité et inégalités de santé"),
    ("repliement des proteines", "bio_repliement", "bio", "Repliement des protéines"),
    ("cinetique enzymatique", "bio_enzymo", "bio", "Cinétique enzymatique — partie 1"),
    ("histoire des epidemies", "shs_epidemies", "shs", "Histoire des épidémies"),
    ("prelevement transplantation", "shs_prelevement_transplantation", "shs", "Prélèvement et transplantation"),
    ("ivg", "shs_ivg", "shs", "Interruption volontaire de grossesse (IVG)"),
    ("fecondation", "histo_fecondation", "histo", "Fécondation"),
    ("tissu osseux", "histo_osseux", "histo", "Tissu osseux"),
    ("tissus musculaires", "histo_muscles1", "histo", "Tissus musculaires — partie 1"),
    ("apoptose", "biocell_apoptose", "biocell", "Apoptose"),
    ("endocytose exocytose", "biocell_endocytose_exocytose", "biocell", "Endocytose et exocytose"),
    ("mitochondrie peroxysome", "biocell_mito_perox", "biocell", "Mitochondrie et peroxysome"),
    ("systeme endomembranaire", "biocell_endo", "biocell", "Système endomembranaire"),
]
def normalized(s: str) -> str:
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.findall(r"[a-z0-9]+", s))

def identify(path: Path):
    key = normalized(path.stem.split("@")[0])
    matches = [(id, subject, title) for phrase, id, subject, title in COURSE_MAP if phrase in key]
    if len(matches) == 1:
        return matches[0]
    return None

def load_content(path: Path):
    raw = path.read_text(encoding="utf-8").strip()
    if not raw.startswith(PREFIX):
        raise ValueError("content.js is not an Adaptive Study source-data document")
    return json.loads(raw[len(PREFIX):].rstrip(";"))

def persist_content(path: Path, data: dict):
    tmp = path.with_suffix(".js.tmp")
    tmp.write_text(PREFIX + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n", encoding="utf-8")
    os.replace(tmp, path)

def prepare_app(target: Path):
    target.mkdir(parents=True, exist_ok=True)
    for src in (ROOT / "app").iterdir():
        if src.is_file() and not (target / src.name).exists():
            shutil.copy2(src, target / src.name)

def ingest(pdf: Path, ident, app: Path, content: dict, dpi: int, replace: bool):
    id, subject, title = ident
    existing = content.setdefault("coursePages", {}).get(id) or []
    if existing and not replace:
        return {"course": id, "result": "skipped: course already installed", "pages": len(existing)}
    try:
        import fitz
    except ImportError as e:
        raise RuntimeError("PyMuPDF missing. Install with: python -m pip install pymupdf") from e
    assets = app / "assets"
    final_pages = assets / "course-pages" / id
    final_pdf = assets / "course-pdfs" / (id + ".pdf")
    final_pdf.parent.mkdir(parents=True, exist_ok=True)
    final_pages.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="adaptive-pdf-", dir=str(assets.parent)) as work:
        staging = Path(work)
        pages = staging / "pages"
        pages.mkdir()
        with fitz.open(pdf) as doc:
            if not len(doc):
                raise ValueError("Empty PDF: " + pdf.name)
            output_paths = []
            for i in range(len(doc)):
                pix = doc[i].get_pixmap(matrix=fitz.Matrix(dpi / 72, dpi / 72), alpha=False)
                filename = f"{i + 1:04d}.jpg"
                (pages / filename).write_bytes(pix.tobytes("jpg", jpg_quality=86))
                output_paths.append("assets/course-pages/" + id + "/" + filename)
            page_count = len(doc)
        shutil.copy2(pdf, staging / (id + ".pdf"))
        if len(list(pages.glob("*.jpg"))) != page_count:
            raise RuntimeError("Incomplete rasterized pages for " + id)
        if final_pages.exists():
            shutil.rmtree(final_pages)
        shutil.move(str(pages), final_pages)
        shutil.move(str(staging / (id + ".pdf")), final_pdf)
    existing_ids = {c["id"] for c in content.get("chapters", [])}
    if id not in existing_ids:
        content["chapters"].append(dict(id=id, subjectId=subject, title=title, available=True,
            examWeight=None, exerciseSupport=None, priority=None, summary="",
            highYield=[], traps=[], patterns=[], sources=[], parentTheme=None))
    else:
        next(c for c in content["chapters"] if c["id"] == id)["available"] = True
    content["coursePages"][id] = output_paths
    content.setdefault("courseAssets", {})[id] = "assets/course-pdfs/" + id + ".pdf"
    content.setdefault("courseMeta", {})[id] = dict(
        content.get("courseMeta", {}).get(id) or {},
        sourceVersion="FC_2026_2027_LOCAL",
        sourceFile=pdf.name, pages=page_count)
    return {"course": id, "result": "source installed", "pages": page_count}

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--pdf-dir", type=Path, required=True)
    ap.add_argument("--app", type=Path, default=ROOT / "local_instance" / "app")
    ap.add_argument("--dpi", type=int, default=165)
    ap.add_argument("--replace", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    if args.dpi < 100 or args.dpi > 300:
        ap.error("--dpi must be between 100 and 300")
    files = sorted(args.pdf_dir.glob("*.pdf"))
    detected = [(p, identify(p)) for p in files]
    identified = [(p, i) for p, i in detected if i]
    if args.dry_run:
        print(json.dumps({"identified":[{"file":p.name,"course":i[0]} for p, i in identified],
             "unmatched":[p.name for p, i in detected if i is None]}, ensure_ascii=False, indent=2))
        return
    prepare_app(args.app)
    path = args.app / "content.js"
    data = load_content(path)
    results = []
    for pdf, ident in identified:
        result = ingest(pdf, ident, args.app, data, args.dpi, args.replace)
        results.append(result)
        if result["result"] == "source installed":
            persist_content(path, data)
        print(json.dumps(result, ensure_ascii=False), flush=True)
    print(json.dumps({"installed":sum(r["result"] == "source installed" for r in results),
          "skipped":sum(r["result"].startswith("skipped") for r in results),
          "unmatched":[p.name for p, i in detected if i is None]}, ensure_ascii=False))
if __name__ == "__main__":
    main()
