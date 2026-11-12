#!/usr/bin/env python3
"""Structural and original-FC-reference validation for native visual learning boards.

No academic fact is accepted merely because it appears in OCR. A board is
release-visible only after manual page-image review with traceable evidence.
This tool never rewrites source course files or the visual pack.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
import zipfile
from collections import Counter
from pathlib import Path

ALLOWED_LAYOUTS = {"flow", "cycle", "comparison", "source_figure"}
ALLOWED_MODES = {"ESSENTIAL", "COMPLETE", "UNDERSTAND"}
ALLOWED_STATES = {"FC_OCR_CROSSCHECKED_PENDING_IMAGE", "PAGE_IMAGE_REVIEWED"}
INVENTED_COURSE_IDS = {
    "histo_embryo", "biocell_cytosq", "biocell_mec_integrine",
    "biocell_dev", "biocell_cycle",
}


def curriculum(path: Path) -> dict:
    if zipfile.is_zipfile(path):
        with zipfile.ZipFile(path) as archive:
            return json.loads(archive.read("assets/study_data.json"))
    return json.loads(path.read_text(encoding="utf-8"))


def validate(pack: dict, academic: dict, source_apk: Path | None = None) -> dict:
    failures, warnings = [], []
    if pack.get("schema") != "NATIVE_FC_VISUAL_BOARDS_V1":
        failures.append("Unknown visual-board schema")
    courses = pack.get("courses")
    if not isinstance(courses, dict):
        failures.append("courses must be a dictionary")
        courses = {}
    real_ids = {c.get("id") for c in academic.get("chapters", [])}
    pages = academic.get("coursePages", {})
    ids, total, visible = set(), 0, 0
    layouts = Counter()
    for cid, boards in courses.items():
        if cid not in real_ids or cid in INVENTED_COURSE_IDS:
            failures.append(f"{cid}: not a legitimate supplied course")
        if not isinstance(boards, list):
            failures.append(f"{cid}: boards must be a list")
            continue
        registered_pages = pages.get(cid, [])
        if not isinstance(registered_pages, list) or not registered_pages:
            failures.append(f"{cid}: no original FC pages registered")
        for index, board in enumerate(boards):
            total += 1
            if not isinstance(board, dict):
                failures.append(f"{cid}:{index}: board must be object")
                continue
            bid = board.get("id")
            if not isinstance(bid, str) or not bid or bid in ids:
                failures.append(f"{cid}:{index}: missing or duplicate stable board ID")
            ids.add(bid)
            layout = board.get("layout")
            if layout not in ALLOWED_LAYOUTS:
                failures.append(f"{cid}:{bid}: unsupported layout")
            layouts[layout] += 1
            title = board.get("title", "")
            if not isinstance(title, str) or not 5 <= len(title) <= 110:
                failures.append(f"{cid}:{bid}: missing/long title")
            modes = board.get("modes")
            if not isinstance(modes, list) or not modes or set(modes) - ALLOWED_MODES:
                failures.append(f"{cid}:{bid}: invalid study-mode registrations")
            source_pages = board.get("sourcePages")
            if (not isinstance(source_pages, list) or not source_pages or
                any(not isinstance(n, int) or not 1 <= n <= len(registered_pages)
                    for n in source_pages)):
                failures.append(f"{cid}:{bid}: nonexisting original-FC page")
                source_pages = []
            status = board.get("reviewStatus")
            if status not in ALLOWED_STATES:
                failures.append(f"{cid}:{bid}: unsupported review state")
            if status == "PAGE_IMAGE_REVIEWED":
                visible += 1
                proof = board.get("reviewEvidence")
                if (not isinstance(proof, dict) or
                    not proof.get("reviewer") or not proof.get("sourceImageSha256") or
                    not proof.get("reviewedPageNumbers")):
                    failures.append(f"{cid}:{bid}: reviewed state lacks original-page proof")
                elif set(proof["reviewedPageNumbers"]) != set(source_pages):
                    failures.append(f"{cid}:{bid}: not all cited pages image-reviewed")
            if layout == "source_figure":
                source_page = board.get("sourcePage")
                source_image = board.get("sourceImage")
                if (not isinstance(source_page, int) or
                    not 1 <= source_page <= len(registered_pages) or
                    registered_pages[source_page-1] != source_image or
                    source_pages != [source_page]):
                    failures.append(f"{cid}:{bid}: figure does not match registered original page")
                crop = board.get("crop")
                if (not isinstance(crop, list) or len(crop) != 4 or
                    any(not isinstance(n, (int,float)) or isinstance(n,bool) for n in crop) or
                    not (0 <= crop[0] < crop[2] <= 1 and
                         0 <= crop[1] < crop[3] <= 1) or
                    crop[2]-crop[0] <= 0.1 or crop[3]-crop[1] <= 0.06):
                    failures.append(f"{cid}:{bid}: invalid normalized figure crop")
                markers = board.get("recognition")
                if (not isinstance(markers, list) or not 1 <= len(markers) <= 8 or
                    any(not isinstance(m, dict) or not m.get("label") or
                            not m.get("value") or len(m["value"]) > 240
                            for m in markers)):
                    failures.append(f"{cid}:{bid}: missing/overlong identification criteria")
                if status == "PAGE_IMAGE_REVIEWED":
                    if source_apk is None:
                        failures.append(f"{cid}:{bid}: original APK required to verify figure hash")
                    else:
                        try:
                            with zipfile.ZipFile(source_apk) as apk:
                                raw = apk.read("assets/www/" + source_image)
                            expected = hashlib.sha256(raw).hexdigest()
                            if board.get("reviewEvidence",{}).get("sourceImageSha256") != expected:
                                failures.append(f"{cid}:{bid}: original figure checksum mismatch")
                        except (OSError, KeyError, TypeError, zipfile.BadZipFile):
                            failures.append(f"{cid}:{bid}: original image absent from source APK")
            if layout in {"flow", "cycle"}:
                steps = board.get("steps")
                if not isinstance(steps, list) or not 2 <= len(steps) <= 6:
                    failures.append(f"{cid}:{bid}: expected 2–6 steps")
                    continue
                for step in steps:
                    if not isinstance(step, dict):
                        failures.append(f"{cid}:{bid}: invalid step")
                        continue
                    if step.get("page") not in source_pages:
                        failures.append(f"{cid}:{bid}: step page not in board provenance")
                    if not 2 <= len(step.get("label", "")) <= 90:
                        failures.append(f"{cid}:{bid}: step label too short/long")
                    if len(step.get("detail", "")) > 210:
                        failures.append(f"{cid}:{bid}: step detail exceeds mobile limit")
            if layout == "comparison":
                cols = board.get("columns")
                if not isinstance(cols, list) or len(cols) != 2:
                    failures.append(f"{cid}:{bid}: compare must have exactly two columns")
                    continue
                for col in cols:
                    if (not isinstance(col, dict) or not col.get("name") or
                        not isinstance(col.get("points"), list) or
                        not 2 <= len(col["points"]) <= 5 or
                        any(not isinstance(p, str) or not p.strip() or len(p) > 165
                            for p in col["points"])):
                        failures.append(f"{cid}:{bid}: comparison overlong or incomplete")
            if len(board.get("deduction", "")) > 300:
                failures.append(f"{cid}:{bid}: deduction must be concise")
            if status != "PAGE_IMAGE_REVIEWED":
                warnings.append(f"{cid}:{bid}: NOT release-renderable pending image review")
    return {
        "valid_structure": not failures, "boards": total,
        "page_image_reviewed": visible, "pending": total - visible,
        "layouts": dict(layouts), "failures": failures, "warnings": warnings,
        "academic_exhaustiveness_certified": False,
        "release_approved": not failures and total > 0 and visible == total,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--visuals", required=True)
    parser.add_argument("--curriculum", required=True)
    parser.add_argument("--report")
    parser.add_argument("--source-apk", help="Existing source APK for verified figure hashes")
    args = parser.parse_args()
    try:
        result = validate(
            json.loads(Path(args.visuals).read_text(encoding="utf-8")),
            curriculum(Path(args.curriculum)),
            Path(args.source_apk) if args.source_apk else None,
        )
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        result = {"valid_structure": False, "release_approved": False,
                  "failures": [str(exc)]}
    output = json.dumps(result, indent=2, ensure_ascii=False)
    if args.report:
        Path(args.report).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if result["valid_structure"] else 2


if __name__ == "__main__":
    sys.exit(main())
