#!/usr/bin/env python3
"""Inventory original histology FC pages and identify candidate figures for manual review.

This is a visual authoring aid, NOT an academic image classifier and NOT a
source-to-lesson certification. It neither edits assets nor invents diagrams.
Inputs remain in their original read-only APK.
"""
import argparse
import io
import json
import zipfile
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont

REJECTED = {"histo_embryo"}


def score(im: Image.Image) -> float:
    """Rank varied original-page image content over mostly black text."""
    rgb = np.asarray(im.convert("RGB").resize((120, 170)), dtype=np.float32) / 255
    high = rgb.max(axis=2)
    low = rgb.min(axis=2)
    chroma = high - low
    midtones = (high > 0.24) & (high < 0.87)
    colored = (chroma > 0.16) & (high > 0.23)
    nonwhite = low < 0.88
    return round(float(midtones.mean() + colored.mean() * 2.3 + nonwhite.mean() * 0.06), 5)


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--apk", required=True)
    p.add_argument("--output", required=True)
    p.add_argument("--max-per-course", type=int, default=4)
    args = p.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    inventory = {}
    with zipfile.ZipFile(args.apk) as z:
        data = json.loads(z.read("assets/study_data.json"))
        for chapter in data["chapters"]:
            cid = chapter.get("id", "")
            if chapter.get("subjectId") != "histo" or cid in REJECTED:
                continue
            found = []
            for index, original_path in enumerate(data.get("coursePages", {}).get(cid, []), 1):
                archive_path = "assets/www/" + original_path
                try:
                    with z.open(archive_path) as src:
                        image = Image.open(io.BytesIO(src.read())).convert("RGB")
                    found.append({"page": index, "path": original_path,
                                  "score": score(image), "width": image.width,
                                  "height": image.height})
                except (KeyError, OSError, ValueError) as exc:
                    found.append({"page": index, "path": original_path,
                                  "error": str(exc)[:130]})
            ranked = sorted(
                (row for row in found if row.get("score") is not None and row["page"] > 1),
                key=lambda x: x["score"], reverse=True
            )[:args.max_per_course]
            inventory[cid] = {
                "title": chapter.get("title"), "totalPages": len(found),
                "rankedFigureCandidates": ranked, "missingPageFiles": [
                    x for x in found if "error" in x],
            }
        ordered = list(inventory)
        for group_start in range(0, len(ordered), 3):
            group = ordered[group_start:group_start + 3]
            w, h, tile_width, tile_height = 820, 980, 205, 245
            canvas = Image.new("RGB", (w, h), "white")
            draw = ImageDraw.Draw(canvas)
            for row, cid in enumerate(group):
                candidates = inventory[cid]["rankedFigureCandidates"]
                draw.text((8, row * 320 + 1), cid, fill=(20, 25, 36))
                for col, item in enumerate(candidates[:4]):
                    with z.open("assets/www/" + item["path"]) as src:
                        image = Image.open(io.BytesIO(src.read())).convert("RGB")
                    image.thumbnail((tile_width - 12, tile_height - 17))
                    left = col * tile_width + (tile_width - image.width)//2
                    top = row*320 + 24
                    canvas.paste(image, (left, top))
                    draw.text((col * tile_width + 5, row * 320 + tile_height + 28),
                              f"p{item['page']} / {item['score']:.2f}",
                              fill=(20, 25, 36))
            canvas.save(out / f"histo_sheet_{group_start // 3 + 1:02}.jpg",
                        format="JPEG", quality=55, optimize=True)
    with (out / "histo_original_figure_candidates.json").open("w", encoding="utf-8") as f:
        json.dump({"status": "VISUAL_HEURISTIC_ONLY_NOT_SCIENTIFIC",
                   "courses": inventory}, f, ensure_ascii=False, indent=2)
    print(json.dumps({
        "courses": len(inventory),
        "pages": sum(c["totalPages"] for c in inventory.values()),
        "missing": sum(len(c["missingPageFiles"]) for c in inventory.values()),
        "sheets": len(list(out.glob("histo_sheet_*.jpg"))),
        "selected": {cid: [x["page"] for x in v["rankedFigureCandidates"]]
                     for cid, v in inventory.items()},
    }, ensure_ascii=True))


if __name__ == "__main__":
    main()
