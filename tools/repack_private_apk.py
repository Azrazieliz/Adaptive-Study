#!/usr/bin/env python3
"""Inject a private Adaptive Study web bundle into an unsigned Android shell APK.

This script deliberately preserves Android's compiled entries instead of extracting and
rezipping the whole APK. In particular, resources.arsc remains ZIP_STORED. Recompressing
that entry can make an otherwise signed APK uninstallable on modern Android.

The output is still unsigned. Run zipalign and apksigner afterwards.
"""
from __future__ import annotations
import argparse
from pathlib import Path
import shutil
import zipfile
import json
import re

SIG_PREFIX = "META-INF/"
WEB_PREFIX = "assets/www/"

def clone_info(info: zipfile.ZipInfo) -> zipfile.ZipInfo:
    out = zipfile.ZipInfo(info.filename, info.date_time)
    out.comment = info.comment
    out.extra = info.extra
    out.internal_attr = info.internal_attr
    out.external_attr = info.external_attr
    out.create_system = info.create_system
    out.flag_bits = info.flag_bits
    out.compress_type = zipfile.ZIP_STORED if info.filename == "resources.arsc" else info.compress_type
    return out

def student_content_bytes(path: Path) -> bytes:
    """Keep examination models and private authoring paths off the phone.

    The original 122 PDF records remain in the PC authoring corpus unchanged.
    No exam-source PDF is copied and no user-watermarked filename is exposed.
    """
    raw = path.read_text(encoding="utf-8")
    prefix = "window.STUDY_CONTENT = "
    if not raw.startswith(prefix):
        raise ValueError("Unrecognized content.js format; refusing unsafe package")
    data = json.loads(raw[len(prefix):].strip().rstrip(";"))
    source = data.get("courseSourceDocuments", {})
    data["courseSourceDocuments"] = {
        chapter: [doc for doc in docs if doc.get("kind") in {"fc", "addendum"}]
        for chapter, docs in source.items()
        if any(doc.get("kind") in {"fc", "addendum"} for doc in docs)
    }
    def clean(value):
        if isinstance(value, list):
            return [clean(v) for v in value]
        if isinstance(value, dict):
            result = {}
            for key, item in value.items():
                if key == "authoringPath":
                    continue
                if key == "sourceFile" and isinstance(item, str):
                    stem = Path(item.replace(chr(92), "/")).name
                    lower = stem.lower()
                    marker = lower.find("_watermarked")
                    if marker >= 0:
                        stem = stem[:marker] + ".pdf"
                    result[key] = stem
                else:
                    result[key] = clean(item)
            return result
        if isinstance(value, str) and "_watermarked" in value.lower():
            # Source-document titles may carry identifying watermark suffixes.
            return re.sub(r"_watermarked[^/\\]*?(?=\.pdf|$)", "", value, flags=re.I)
        return value
    data = clean(data)
    return (prefix + json.dumps(data, ensure_ascii=False, separators=(",", ":")) + ";\n").encode("utf-8")

def repack(shell: Path, app_dir: Path, output: Path) -> None:
    if not shell.is_file():
        raise SystemExit(f"Shell APK not found: {shell}")
    if not (app_dir / "index.html").is_file():
        raise SystemExit(f"App directory is not an Adaptive Study web bundle: {app_dir}")
    output.parent.mkdir(parents=True, exist_ok=True)
    tmp = output.with_suffix(output.suffix + ".tmp")
    with zipfile.ZipFile(shell, "r") as src, zipfile.ZipFile(tmp, "w", allowZip64=True) as dst:
        for info in src.infolist():
            if info.filename.startswith(SIG_PREFIX) or info.filename.startswith(WEB_PREFIX):
                continue
            dst.writestr(clone_info(info), src.read(info.filename))
        for path in sorted(app_dir.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(app_dir).as_posix()
            # Release package contains only original lesson/addendum PDFs.
            # Exam PDFs are authoring inputs, not part of the student APK.
            if rel.startswith("assets/new-course-source/") and rel.lower().endswith(".pdf"):
                if not Path(rel).name.startswith(("fc-", "addendum-")):
                    continue
            if rel.startswith(("assets/new-course-preview/", "assets/archives/", "assets/original_questions/")):
                continue
            if rel in ("original_corpus.js", "original_question_adapter.js"):
                continue
            if rel.startswith(("content-before-", "content-before-revision-", "flashcard_rebuild_audit")):
                continue
            arc = WEB_PREFIX + rel
            info = zipfile.ZipInfo(arc)
            # JPEG/WEBP/PDF files are already compressed. Store them directly
            # to avoid minutes of redundant compression on the phone corpus.
            info.compress_type = (zipfile.ZIP_STORED if path.suffix.lower() in
                                  {'.jpg', '.jpeg', '.webp', '.png', '.pdf', '.zip', '.mp4'}
                                  else zipfile.ZIP_DEFLATED)
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            # Stream large course assets to avoid Windows single-read failures.
            try:
                if rel == "content.js":
                    payload = student_content_bytes(path)
                    with dst.open(info, "w") as target:
                        target.write(payload)
                else:
                    with path.open("rb") as source, dst.open(info, "w") as target:
                        shutil.copyfileobj(source, target, length=1024 * 1024)
            except OSError as exc:
                raise OSError(f"Cannot package {path} ({path.stat().st_size} bytes): {exc}") from exc
    with zipfile.ZipFile(tmp, "r") as check:
        if check.getinfo("resources.arsc").compress_type != zipfile.ZIP_STORED:
            raise SystemExit("resources.arsc was compressed; refusing broken APK")
        if "assets/www/index.html" not in check.namelist():
            raise SystemExit("web bundle injection failed")
    shutil.move(tmp, output)

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("shell_apk", type=Path)
    ap.add_argument("app_dir", type=Path)
    ap.add_argument("output_apk", type=Path)
    args = ap.parse_args()
    repack(args.shell_apk, args.app_dir, args.output_apk)
    print(args.output_apk)
