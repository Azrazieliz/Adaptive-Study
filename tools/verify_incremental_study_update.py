#!/usr/bin/env python3
"""Fail-closed, read-only gate for incremental Adaptive Study curriculum edits.

Compares existing private study_data.json or an APK's bundled study_data.json.
Does not write/transform either input, build an APK, or certify academic accuracy.
"""
from __future__ import annotations

import argparse
import json
import sys
import zipfile
from pathlib import Path

COURSE_MAPS = {
    "courseGuides", "coursePages", "courseAssets", "courseMeta",
    "mindMaps", "sourceVerifiedLessonCoverage", "courseSourceDocuments",
    "legacyGuideArchive",
}
RECORD_LISTS = {"chapters", "questions", "flashcards"}
VERSION_FIELDS = {"version", "versionCode", "versionName", "updatedAt"}


def load(path: str) -> dict:
    p = Path(path)
    if zipfile.is_zipfile(p):
        with zipfile.ZipFile(p) as archive:
            document = json.loads(archive.read("assets/study_data.json"))
    else:
        document = json.loads(p.read_text(encoding="utf-8"))
    if not isinstance(document, dict):
        raise ValueError("Curriculum root must be an object")
    return document


def keyed(rows: list, kind: str) -> dict:
    if not isinstance(rows, list):
        raise ValueError(f"{kind} must be an array")
    result = {}
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError(f"{kind} contains a record with no stable ID")
        if row["id"] in result:
            raise ValueError(f"{kind} contains duplicate ID {row['id']}")
        result[row["id"]] = row
    return result


def compare(before: dict, after: dict, allow: set[str],
            permit_new: bool = False, permit_version: bool = False) -> dict:
    errors, changes = [], {}
    for kind in RECORD_LISTS:
        keyed(before.get(kind, []), kind)
        keyed(after.get(kind, []), kind)
    before_chapters = keyed(before.get("chapters", []), "chapters")
    after_chapters = keyed(after.get("chapters", []), "chapters")
    if not allow:
        errors.append("No allowed course IDs provided")
    for chapter in allow:
        if chapter not in before_chapters and not permit_new:
            errors.append(f"Unrecognized chapter {chapter}; new courses need --permit-new")
        if chapter not in after_chapters:
            errors.append(f"Allowed chapter {chapter} absent from candidate")
    for key in sorted(set(before) | set(after)):
        a, b = before.get(key), after.get(key)
        if a == b:
            continue
        if key in COURSE_MAPS:
            if not isinstance(a, dict) or not isinstance(b, dict):
                errors.append(f"{key}: expected per-course dictionaries")
                continue
            changed = sorted(cid for cid in set(a) | set(b) if a.get(cid) != b.get(cid))
            changes[key] = changed
            for cid in changed:
                if cid not in allow:
                    errors.append(f"{key}: unrelated course {cid} modified")
                if cid in a and cid not in b:
                    errors.append(f"{key}: course data removed for {cid}")
                if cid not in before_chapters and not permit_new:
                    errors.append(f"{key}: new course {cid} needs --permit-new")
        elif key in RECORD_LISTS:
            original, current = keyed(a or [], key), keyed(b or [], key)
            changed = sorted(rid for rid in set(original) | set(current)
                             if original.get(rid) != current.get(rid))
            changes[key] = changed
            for rid in changed:
                old, new = original.get(rid), current.get(rid)
                if new is None:
                    errors.append(f"{key}: existing record {rid} removed")
                    continue
                cid = rid if key == "chapters" else new.get("chapterId")
                old_cid = rid if key == "chapters" else (old or {}).get("chapterId")
                if not cid or (old and old_cid != cid):
                    errors.append(f"{key}: record {rid} lost or changed chapter identity")
                if cid not in allow:
                    errors.append(f"{key}: unrelated record {rid} changed")
                if old is None and (cid not in before_chapters or key == "chapters") and not permit_new:
                    errors.append(f"{key}: new-course entry {rid} requires --permit-new")
        elif key == "pack" and permit_version and isinstance(a, dict) and isinstance(b, dict):
            modified = sorted(k for k in set(a) | set(b) if a.get(k) != b.get(k))
            changes[key] = modified
            if not set(modified).issubset(VERSION_FIELDS):
                errors.append("pack: non-version content changed")
        else:
            errors.append(f"Unscoped root field {key} changed")
    return {
        "approved": not errors, "allowed_chapters": sorted(allow),
        "changed": changes, "errors": sorted(set(errors)),
        "scope": "structural update isolation only; NOT course, diagram or answer certification",
    }


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--before", required=True)
    p.add_argument("--after", required=True)
    p.add_argument("--allow-chapters", required=True, help="Comma-separated chapter IDs")
    p.add_argument("--permit-new", action="store_true")
    p.add_argument("--permit-version-only", action="store_true")
    p.add_argument("--report", help="Optional diagnostic JSON output; never edits source")
    args = p.parse_args()
    try:
        outcome = compare(load(args.before), load(args.after),
                          {x.strip() for x in args.allow_chapters.split(",") if x.strip()},
                          args.permit_new, args.permit_version_only)
    except (OSError, ValueError, KeyError, zipfile.BadZipFile) as exc:
        outcome = {"approved": False, "errors": [str(exc)]}
    output = json.dumps(outcome, ensure_ascii=False, indent=2)
    if args.report:
        Path(args.report).write_text(output + "\n", encoding="utf-8")
    print(output)
    return 0 if outcome["approved"] else 2


if __name__ == "__main__":
    sys.exit(main())
