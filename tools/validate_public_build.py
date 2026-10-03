#!/usr/bin/env python3
from pathlib import Path
import json,sys
ROOT=Path(__file__).resolve().parents[1];APP=ROOT/'app';EXPECTED='3.25.0-standalone-clean';errors=[]
def chk(c,m):
    if not c: errors.append(m)
app=(APP/'app.js').read_text();idx=(APP/'index.html').read_text();sw=(APP/'sw.js').read_text();ex=(APP/'exercises.js').read_text();oc=(APP/'original_corpus.js').read_text();ct=(APP/'content.js').read_text()
chk(f"window.__ADAPTIVE_BUILD='{EXPECTED}'" in app,'engine build')
chk(f"const EXPECTED='{EXPECTED}'" in idx,'index expected build')
chk(f"window.__EXERCISES_BUILD='{EXPECTED}'" in ex,'exercise build')
chk(f"window.__ORIGINAL_CORPUS_BUILD='{EXPECTED}'" in oc,'original corpus build')
chk('adaptive-study-v3-25-0-core' in sw and 'build=3250' in sw,'service worker build')
prefix='window.STUDY_CONTENT = ';d=json.loads(ct[len(prefix):].strip().rstrip(';'))
chk(d.get('pack',{}).get('version')==EXPECTED,'content build');chk(len(d.get('subjects',[]))==7,'subject count');chk(not d.get('questions'),'public questions must stay empty');chk(not d.get('flashcards'),'public flashcards must stay empty')
if errors:
    print('FAILED:',', '.join(errors));sys.exit(1)
print('OK',EXPECTED)