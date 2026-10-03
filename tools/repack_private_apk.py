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
            arc = WEB_PREFIX + rel
            info = zipfile.ZipInfo(arc)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (path.stat().st_mode & 0xFFFF) << 16
            with path.open("rb") as f:
                dst.writestr(info, f.read())
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
