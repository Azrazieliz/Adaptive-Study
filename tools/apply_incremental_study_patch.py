#!/usr/bin/env python3
"""Apply a *reviewed, chapter-scoped* patch without regenerating curriculum records.

Never writes to the base study_data.json. Always creates a separate candidate.
The candidate must pass verify_incremental_study_update before it is written.
This is a structural preservation gate, NOT academic or APK certification.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import sys
from pathlib import Path

from verify_incremental_study_update import COURSE_MAPS, compare, keyed

FORMAT = "adaptive-study-incremental-v1"
ALLOWED_FIELDS = COURSE_MAPS | {"chapter", "questions", "flashcards"}


def apply(base: dict, patch: dict, allowed: set[str],
          permit_new: bool = False) -> tuple[dict, dict]:
    if patch.get("format") != FORMAT:
        raise ValueError("Unsupported patch format")
    courses = patch.get("courses")
    if not isinstance(courses, dict) or not courses:
        raise ValueError("Patch must contain course-scoped changes")
    if set(courses) != allowed:
        raise ValueError("Patch courses must exactly match explicitly approved IDs")
    candidate = copy.deepcopy(base)
    originals = keyed(candidate["chapters"], "chapters")
    for cid, edits in courses.items():
        if not isinstance(edits, dict) or not edits:
            raise ValueError(f"{cid}: empty course patch")
        unknown = set(edits) - ALLOWED_FIELDS
        if unknown:
            raise ValueError(f"{cid}: unsupported fields {sorted(unknown)}")
        is_new = cid not in originals
        if is_new and not permit_new:
            raise ValueError(f"{cid}: adding a course requires --permit-new")
        if is_new:
            metadata = edits.get("courseMeta")
            if not isinstance(edits.get("chapter"), dict) or not edits.get("coursePages"):
                raise ValueError(f"{cid}: new course requires chapter and actual source-page registration")
            if not isinstance(metadata, dict) or not (
                metadata.get("importedFullFC") or metadata.get("originalFC") or
                metadata.get("sourceFile") or metadata.get("sourceDocuments")
            ):
                raise ValueError(f"{cid}: new course requires source-file provenance")
        for field, payload in edits.items():
            if payload is None:
                raise ValueError(f"{cid}:{field}: deletion is not supported")
            if field in COURSE_MAPS:
                if not isinstance(candidate.get(field), dict):
                    raise ValueError(f"{field}: expected original per-course map")
                candidate[field][cid] = copy.deepcopy(payload)
            elif field == "chapter":
                if not isinstance(payload, dict) or payload.get("id") != cid:
                    raise ValueError(f"{cid}: chapter stable ID mismatch")
                rows = candidate["chapters"]
                positions = [i for i, row in enumerate(rows) if row.get("id") == cid]
                if len(positions) > 1:
                    raise ValueError(f"{cid}: duplicate original chapter")
                if positions:
                    rows[positions[0]] = copy.deepcopy(payload)
                else:
                    rows.append(copy.deepcopy(payload))
            elif field in ("questions", "flashcards"):
                if not isinstance(payload, list):
                    raise ValueError(f"{cid}:{field}: expected list")
                if len({row.get("id") for row in payload if isinstance(row, dict)}) != len(payload):
                    raise ValueError(f"{cid}:{field}: duplicate or invalid patch IDs")
                target = candidate[field]
                positions = {row["id"]: i for i, row in enumerate(target)}
                for row in payload:
                    if not isinstance(row, dict) or not row.get("id") or row.get("chapterId") != cid:
                        raise ValueError(f"{cid}:{field}: unowned or invalid record")
                    rid = row["id"]
                    if rid in positions:
                        if target[positions[rid]].get("chapterId") != cid:
                            raise ValueError(f"{cid}:{field}: attempted to move a record from another chapter")
                        target[positions[rid]] = copy.deepcopy(row)
                    else:
                        positions[rid] = len(target)
                        target.append(copy.deepcopy(row))
    result = compare(base, candidate, allowed, permit_new=permit_new)
    if not result["approved"]:
        raise ValueError("Incremental gate rejected candidate: " + "; ".join(result["errors"]))
    return candidate, result


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("--base", required=True)
    p.add_argument("--patch", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--allow-chapters", required=True)
    p.add_argument("--permit-new", action="store_true")
    args = p.parse_args()
    try:
        base_path, output = Path(args.base), Path(args.output)
        if output.resolve() == base_path.resolve() or output.exists():
            raise ValueError("Refusing to overwrite base or any existing output")
        source = base_path.read_bytes()
        patch = json.loads(Path(args.patch).read_text(encoding="utf-8"))
        expected = patch.get("base_sha256")
        if expected != hashlib.sha256(source).hexdigest():
            raise ValueError("Base SHA-256 mismatch; stale or unauthorized patch")
        original = json.loads(source)
        allowed = {x.strip() for x in args.allow_chapters.split(",") if x.strip()}
        candidate, audit = apply(original, patch, allowed, args.permit_new)
        output.parent.mkdir(parents=True, exist_ok=True)
        with output.open("x", encoding="utf-8") as f:
            json.dump(candidate, f, ensure_ascii=False, separators=(",", ":"))
        print(json.dumps({
            "ok": True, "output": str(output),
            "changed": audit["changed"], "preserved": True,
            "academic_certified": False, "apk_built": False,
        }, ensure_ascii=False))
        return 0
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2


if __name__ == "__main__":
    sys.exit(main())
