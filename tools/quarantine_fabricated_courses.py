#!/usr/bin/env python3
"""Remove five owner-rejected fabricated course records into a private quarantine.

Fails closed, creates distinct candidate and archival files, never overwrites the
supplied curriculum, never deletes original PDFs or user progress on a phone.
A human must inspect archived questions/cards before any future reassignment.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

FABRICATED = {
    "histo_embryo", "biocell_cytosq", "biocell_mec_integrine",
    "biocell_dev", "biocell_cycle",
}
LISTS = {"chapters", "questions", "flashcards"}


def quarantine(data: dict) -> tuple[dict, dict, dict]:
    candidate = copy.deepcopy(data)
    archived: dict = {"courseIds": sorted(FABRICATED), "records": {}}
    changed: dict[str, int] = {}
    originals = {x["id"] for x in candidate["chapters"]}
    if not FABRICATED <= originals:
        raise ValueError("Fabricated course IDs differ from the documented original")
    for key, value in data.items():
        if key in LISTS:
            if not isinstance(value, list):
                raise ValueError(f"{key} is not a record list")
            predicate = (lambda v: v.get("id") in FABRICATED) if key == "chapters" else (
                lambda v: v.get("chapterId") in FABRICATED
            )
            excluded = [copy.deepcopy(v) for v in value if predicate(v)]
            candidate[key] = [copy.deepcopy(v) for v in value if not predicate(v)]
            if excluded:
                archived["records"][key] = excluded
                changed[key] = len(excluded)
        elif isinstance(value, dict) and FABRICATED.intersection(value):
            excluded = {key_id: copy.deepcopy(value[key_id])
                        for key_id in FABRICATED if key_id in value}
            candidate[key] = copy.deepcopy(value)
            for key_id in excluded:
                del candidate[key][key_id]
            archived["records"][key] = excluded
            changed[key] = len(excluded)
    unchanged_real_chapters = {x["id"]: x for x in data["chapters"]
                               if x["id"] not in FABRICATED}
    new_real_chapters = {x["id"]: x for x in candidate["chapters"]}
    if unchanged_real_chapters != new_real_chapters:
        raise AssertionError("Genuine chapter identity or contents changed")
    remaining = json.dumps(candidate, ensure_ascii=False)
    residual_references = {id_: remaining.count(id_) for id_ in sorted(FABRICATED)
                           if id_ in remaining}
    result = {
        "archived_course_ids": sorted(FABRICATED),
        "remaining_genuine_course_records": len(candidate["chapters"]),
        "archived_record_counts": changed,
        "unremoved_references_in_other_fields": residual_references,
        "app_modified": False,
        "apk_built": False,
    }
    return candidate, archived, result


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True, help="Exact existing study_data.json")
    ap.add_argument("--expected-sha256", required=True)
    ap.add_argument("--output", required=True, help="New, separate candidate JSON")
    ap.add_argument("--archive", required=True, help="New private quarantine JSON")
    args = ap.parse_args()
    try:
        original = Path(args.input).read_bytes()
        source_hash = hashlib.sha256(original).hexdigest()
        if source_hash.lower() != args.expected_sha256.lower():
            raise ValueError("Source checksum mismatch; cannot quarantine")
        output, archive = Path(args.output), Path(args.archive)
        if output.resolve() == Path(args.input).resolve():
            raise ValueError("Cannot overwrite the input")
        if output.exists() or archive.exists() or output.resolve() == archive.resolve():
            raise ValueError("Refusing to overwrite existing output/archive")
        candidate, excluded, report = quarantine(json.loads(original))
        archive.parent.mkdir(parents=True, exist_ok=True)
        output.parent.mkdir(parents=True, exist_ok=True)
        excluded["original_sha256"] = source_hash
        excluded["note"] = "PRIVATE ARCHIVE; NOT deleted from original app or reassigned"
        with archive.open("x", encoding="utf-8") as f:
            json.dump(excluded, f, ensure_ascii=False, indent=2)
        with output.open("x", encoding="utf-8") as f:
            json.dump(candidate, f, ensure_ascii=False, separators=(",", ":"))
        report["candidate_sha256"] = hashlib.sha256(output.read_bytes()).hexdigest()
        report["archive_sha256"] = hashlib.sha256(archive.read_bytes()).hexdigest()
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except (OSError, ValueError, KeyError, AssertionError) as e:
        print(json.dumps({"ok": False, "error": str(e)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
