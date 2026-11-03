# -*- coding:utf-8 -*-
"""One-time safe removal of redundant original annale/QE PDF viewers from shipped app.
Keep originals, corrections and question-page scans outside packaged Android project.
Only new authored QCM/QROC remain in study_data.json.
"""
from pathlib import Path
import json,hashlib,shutil,os,collections,time
ROOT=Path(r"D:\AdaptiveStudyRecovery")
ASSETS=ROOT/"AdaptiveStudyNative/app/src/main/assets"
WWW=ASSETS/"www"
VAULT=ROOT/"source_transfer/private_exam_assets_removed_from_app_v3330"
MANIFEST=VAULT/"manifest.json"
DATA=ASSETS/"study_data.json"
EXAM=ASSETS/"original_assessment_catalog.json"
QCAT=ASSETS/"original_question_catalog.json"
paths=[
 ASSETS/"original_assessments",
 WWW/"original_assessments",
 WWW/"assets"/"original_questions",
 WWW/"assets"/"new-course-preview",
 EXAM,QCAT
]
data=json.loads(DATA.read_text("utf8"))
original_data=ROOT/"source_transfer/private_exam_assets_removed_from_app_v3330"/"study_data_before_exam_removal.json"
VAULT.mkdir(parents=True,exist_ok=True)
if not original_data.exists():shutil.copy2(DATA,original_data)
safe=[]
# Prove none of the source FCs or original maps that the user wants kept are in removed trees.
must_keep=set()
for value in data["coursePages"].values():
 for s in value:must_keep.add((WWW/s).resolve())
for value in data["mindMaps"].values():
 if not isinstance(value,dict):continue
 for s in [value.get("path")]+[b.get("path") for b in value.get("subMaps",[]) if isinstance(b,dict)]:
  if s:must_keep.add((WWW/s).resolve())
for s in data["courseAssets"].values():
 if s:must_keep.add((WWW/s).resolve())
for p in paths:
 if not p.exists():continue
 if p.is_dir():safe.extend(f for f in p.rglob("*") if f.is_file())
 else:safe.append(p)
assert safe
removed=set(f.resolve() for f in safe)
assert not removed.intersection(must_keep),[str(s) for s in removed.intersection(must_keep)]
# Additional assessment PDFs stored among FC assets: choose metadata type, NEVER path substrings.
for cid,docs in data.get("courseSourceDocuments",{}).items():
 if not isinstance(docs,list):continue
 for doc in docs:
  kind=str(doc.get("kind","")).lower()
  if not any(x in kind for x in ("qe","annale","acc_","qcm_","correction")):continue
  path=doc.get("pdf")
  if path:
   p=(WWW/path).resolve()
   if p.is_file() and p not in must_keep and p not in removed:
    safe.append(p);removed.add(p)
  for link in doc.get("pages",[]):
   p=(WWW/link).resolve()
   if p.is_file() and p not in must_keep and p not in removed:
    safe.append(p);removed.add(p)
# Retain all course FC sources and imagery. Any course source itself mentioned as annale is not touched.
records=[]
for f in sorted(set(safe)):
 relative=f.relative_to(ASSETS) if f.is_relative_to(ASSETS) else Path("external")/f.name
 out=VAULT/relative;out.parent.mkdir(parents=True,exist_ok=True)
 shutil.copy2(f,out)
 h=hashlib.sha256(out.read_bytes()).hexdigest()
 assert h==hashlib.sha256(f.read_bytes()).hexdigest()
 records.append({"path":str(relative).replace("\\","/"),"sha256":h,"bytes":f.stat().st_size})
stats=collections.Counter()
for f in safe:stats[f.suffix.lower()]+=1
MANIFEST.write_text(json.dumps({
 "description":"Removed from shipped native APK only by explicit user request. Original exam PDFs and image scans preserved privately for future exam-style question authoring.",
 "source_data_backup":"study_data_before_exam_removal.json",
 "excluded_paths":[str(f.relative_to(ASSETS)).replace("\\","/") for f in paths if f.is_relative_to(ASSETS)],
 "file_count":len(records),"total_bytes":sum(v["bytes"] for v in records),
 "by_extension":dict(stats),"files":records},indent=2,ensure_ascii=False),encoding="utf8")
# Data: strip only exam-source references; never touch pedagogical/FC docs, graded authored questions, cards, progress.
stripped=collections.Counter()
for cid,docs in list(data.get("courseSourceDocuments",{}).items()):
 if not isinstance(docs,list):continue
 new=[]
 for doc in docs:
  kind=str(doc.get("kind","")).lower()
  if any(x in kind for x in ("qe","annale","acc_","qcm_","correction")):
   stripped["exam_source_docs"]+=1;continue
  new.append(doc)
 data["courseSourceDocuments"][cid]=new
DATA.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf8")
for f in sorted(set(safe),key=lambda p:len(str(p)),reverse=True):
 assert (VAULT/(f.relative_to(ASSETS) if f.is_relative_to(ASSETS) else Path("external")/f.name)).exists()
 f.unlink()
for p in paths:
 if p.is_dir() and p.exists():shutil.rmtree(p)
for root,dirs,files in os.walk(WWW,topdown=False):
 if not os.listdir(root):os.rmdir(root)
print("REMOVAL_ONLY_FROM_APP","FILE_COUNT",len(records),"MB",round(sum(x["bytes"] for x in records)/1e6,1),"BY_TYPE",dict(stats),
"STRIPPED_METADATA",dict(stripped))
print("PRIVATE_ARCHIVE",VAULT)
print("PRESERVED",len(data["chapters"]),"CHAPTERS",len(data["questions"]),"AUTHORED_QCM_QROC",len(data["flashcards"]),"CARDS")
