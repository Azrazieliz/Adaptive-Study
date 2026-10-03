#!/usr/bin/env python3
"""Restore a user-owned Adaptive Study private package into local_instance/."""
import argparse, json, pathlib, re, shutil, zipfile
ROOT=pathlib.Path(__file__).resolve().parents[1]
LOCAL_APP=ROOT/'local_instance'/'app'
PREFIX='AdaptiveStudyInstall/app/'
PRIVATE_FILES={'content.js','original_corpus.js','exercises.js'}
EXPECTED='3.25.0-standalone-clean'

def _content_version(raw: bytes):
    text=raw.decode('utf-8')
    prefix='window.STUDY_CONTENT = '
    if not text.startswith(prefix): return None
    body=text[len(prefix):].strip().rstrip(';')
    return json.loads(body).get('pack',{}).get('version')

def restore(bundle:pathlib.Path)->int:
    LOCAL_APP.mkdir(parents=True,exist_ok=True)
    for public in (ROOT/'app').iterdir():
        if public.is_file() and public.name not in PRIVATE_FILES:
            shutil.copy2(public,LOCAL_APP/public.name)
    count=0
    with zipfile.ZipFile(bundle) as source:
        names=set(source.namelist())
        required={PREFIX+n for n in PRIVATE_FILES}
        if not required.issubset(names): raise ValueError('Archive incomplète : données privées de l’application absentes.')
        version=_content_version(source.read(PREFIX+'content.js'))
        if version!=EXPECTED: raise ValueError(f'Build privé incompatible : {version!r}; attendu {EXPECTED!r}.')
        for item in source.infolist():
            if not item.filename.startswith(PREFIX) or item.is_dir(): continue
            relative=pathlib.PurePosixPath(item.filename[len(PREFIX):])
            if relative.is_absolute() or '..' in relative.parts: raise ValueError('Chemin non valide dans l’archive.')
            if relative.parts[0] != 'assets' and str(relative) not in PRIVATE_FILES: continue
            destination=LOCAL_APP/relative
            destination.parent.mkdir(parents=True,exist_ok=True)
            with source.open(item) as src,destination.open('wb') as dst: shutil.copyfileobj(src,dst)
            count+=1
    return count

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('archive',type=pathlib.Path);a=p.parse_args()
    print(f'{restore(a.archive)} fichiers privés restaurés dans {LOCAL_APP}.')