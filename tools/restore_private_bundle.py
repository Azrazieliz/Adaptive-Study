#!/usr/bin/env python3
"""Restore user-owned educational data from a local Adaptive Study installer ZIP.

The public repository intentionally omits PDF content, page images, and
question/correction pages. No downloads or corpus generation occur here.
"""
import argparse
import pathlib
import shutil
import zipfile

ROOT = pathlib.Path(__file__).resolve().parents[1]
PRIVATE_PREFIX = 'AdaptiveStudyInstall/app/'
PRIVATE_FILES = {'content.js', 'original_corpus.js', 'exercises.js'}


def restore(bundle: pathlib.Path) -> int:
    count = 0
    with zipfile.ZipFile(bundle) as source:
        names = set(source.namelist())
        required = {PRIVATE_PREFIX + name for name in PRIVATE_FILES}
        if not required.issubset(names):
            raise ValueError('Archive incomplète : données privées de l’application absentes.')
        for item in source.infolist():
            if not item.filename.startswith(PRIVATE_PREFIX) or item.is_dir():
                continue
            relative = pathlib.PurePosixPath(item.filename[len(PRIVATE_PREFIX):])
            if relative.is_absolute() or '..' in relative.parts:
                raise ValueError('Chemin non valide dans l’archive.')
            if relative.parts[0] != 'assets' and str(relative) not in PRIVATE_FILES:
                continue
            destination = ROOT / 'app' / relative
            destination.parent.mkdir(parents=True, exist_ok=True)
            with source.open(item) as src, destination.open('wb') as dst:
                shutil.copyfileobj(src, dst)
            count += 1
    return count


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('archive', type=pathlib.Path, help='Archive privée AdaptiveStudy_Originaux_623_2026-09-28.zip')
    args = parser.parse_args()
    print(f'{restore(args.archive)} fichiers privés restaurés. Ne pas les publier sur GitHub.')
