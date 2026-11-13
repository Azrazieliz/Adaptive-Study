#!/usr/bin/env python3
"""Recover the existing Noyau FC; quarantine old borrowed pages. NO new course IDs.

All historical JSON assets are backed up byte-identically. Source PDFs and
previous images are preserved. No OCR/automatic text is accepted as academic truth.
"""
import argparse,hashlib,json,pathlib,shutil,sys
try:
 import fitz
except ImportError:
 import pymupdf as fitz

INDEPENDENT="biocell_noyau"
EXPECTED_SHA="78c3a7f67e1838835f1e12c367398209f8ccfd0f2ff1e309c4c72af31f9ef79d"
DOC_ID=1858
SOURCE_NAME="FCactu_Noyau_2026-2027_original.pdf"
BACKUP_LABEL="before_original_noyau_20261113"
def h(path):
 sha=hashlib.sha256()
 with open(path,"rb") as f:
  for block in iter(lambda:f.read(1048576),b""):sha.update(block)
 return sha.hexdigest()
def load(path):return json.loads(path.read_text(encoding="utf-8"))
def dump(path,data):path.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
def prep_json(path):
 backup=path.with_name(path.stem+"."+BACKUP_LABEL+path.suffix)
 if backup.exists():assert h(backup)==h(path),"Backup collision "+path.name
 else:shutil.copy2(path,backup)
 return load(path)
def save_json(path,d):tmp=path.with_name(path.name+".tmp");dump(tmp,d);tmp.replace(path)

def repair(root,source):
 a=root/"www"/"assets"
 assert root.is_dir() and source.is_file() and h(source)==EXPECTED_SHA
 studyfile=root/"study_data.json"
 study=prep_json(studyfile)
 current=study.get("courseMeta",{}).get(INDEPENDENT,{})
 assert current.get("isComposite",False) and len(study.get("coursePages",{}).get(INDEPENDENT,[]))==50,"Wrong input state; stop"
 legacy_dir=root.parent.parent.parent.parent/"Noyau_Original_FC_Recovery_Backups_20261113"
 legacy_dir.mkdir(parents=True,exist_ok=True)
 legacy_out=legacy_dir/"noyau_before_repair_records.json"
 if not legacy_out.exists():
  legacy={
    "metadata":current,"courseGuide":study["courseGuides"].get(INDEPENDENT),
    "coursePages":study["coursePages"].get(INDEPENDENT),
    "sourceDocument":study.get("courseSourceDocuments",{}).get(INDEPENDENT),
    "sourceVerifiedCoverage":study.get("sourceVerifiedLessonCoverage",{}).get(INDEPENDENT),
    "mindmap":study.get("mindMaps",{}).get(INDEPENDENT)}
  dump(legacy_out,legacy)
 doc=fitz.open(str(source))
 assert len(doc)==25,"Unexpected original FC page count; stop"
 imdir=a/"new-course-pages"/INDEPENDENT/"fc-1"
 imdir.mkdir(parents=True,exist_ok=True)
 images=[]
 for i in range(25):
  page=doc.load_page(i)
  pix=page.get_pixmap(matrix=fitz.Matrix(1.65,1.65),alpha=False)
  filename="%04d.jpg"%(i+1)
  dest=imdir/filename
  if not dest.exists():
   pix.save(str(dest),jpg_quality=87)
  assert dest.stat().st_size>12000 and dest.read_bytes()[:3]==b"\xff\xd8\xff",("Bad rendered page",i)
  images.append(f"assets/new-course-pages/{INDEPENDENT}/fc-1/{filename}")
 pdffile=a/"new-course-source"/INDEPENDENT/"fc-1.pdf"
 pdffile.parent.mkdir(parents=True,exist_ok=True)
 if pdffile.exists():assert h(pdffile)==EXPECTED_SHA,"Source destination collision"
 else:shutil.copy2(source,pdffile)
 assert h(pdffile)==EXPECTED_SHA and len(images)==len(set(images))==25
 doc.close()
 pdfrel=f"assets/new-course-source/{INDEPENDENT}/fc-1.pdf"
 chapters=[x for x in study["chapters"] if x["id"]==INDEPENDENT]
 assert len(chapters)==1
 course=chapters[0]
 for k in ["parentTheme","compositeParts","auditNote"]:course.pop(k,None)
 course.update({"available":True,"sourceOnly":True,
   "auditStatus":"ORIGINAL_INDEPENDENT_FC_25_PAGES_PRESENT__EDITORIAL_REVIEW_REQUIRED",
   "auditNote":"MediSUP Chap 11 Noyau, original FC actualisée 2026-2027, document 1858; 25 original pages preserved independently. Borrowed FC text and figures no longer presented as original."})
 course["sources"]=[{"kind":"Cours original","title":"FCactu Noyau, 2026–2027","documentId":DOC_ID,"sha256":EXPECTED_SHA}]
 study["courseGuides"][INDEPENDENT]={
   "sourceFile":SOURCE_NAME,"sourceVersion":"FC_ORIGINALE_MEDISUP_2026_2027",
   "guideCoverage":"SOURCE_IMAGES_COMPLETE__EDITORIAL_25_PAGES_PENDING",
   "independentSourceFilePresent":True,"totalSourcePages":25,
   "verifiedOriginalDocumentSha256":EXPECTED_SHA,"sections":[]
 }
 study["coursePages"][INDEPENDENT]=images
 study.setdefault("courseAssets",{})[INDEPENDENT]=pdfrel
 study.setdefault("courseSourceDocuments",{})[INDEPENDENT]=[{
   "docId":"fc-1","kind":"fc","label":"FC original — Noyau","sourceFile":SOURCE_NAME,
   "medisupDocumentId":DOC_ID,"sha256":EXPECTED_SHA,"pdf":pdfrel,"pageCount":25,"pages":images
 }]
 study.setdefault("sourceVerifiedLessonCoverage",{})[INDEPENDENT]={
   "status":"SOURCE_ORIGINAL_25_PAGES_VISIBLE__STUDY_TEXT_UNREVIEWED",
   "verifiedPages":[],"totalPages":25,"independentOriginalFC":True,
   "reviewedPageImageCoverage":25,"reviewedTextPageCoverage":0
 }
 study["courseMeta"][INDEPENDENT]={
   "pages":25,"source":"MediSUP original Chap 11 Noyau (2026–2027)",
   "sourceFile":SOURCE_NAME,"sourceVersion":"2026-2027 — FC Actu Noyau",
   "independentSourceFilePresent":True,"isComposite":False,
   "sourceSHA256":EXPECTED_SHA,"medisupDocumentId":DOC_ID,
   "importedFullFC":{"pdf":pdfrel,"sourceFile":SOURCE_NAME,"pages":25,"sha256":EXPECTED_SHA,"images":images}
 }
 study.setdefault("mindMaps",{}).pop(INDEPENDENT,None)
 save_json(studyfile,study)
 # Quarantine indexed content and comprehension using old unrelated FC records.
 for filename,outer,inner,default in [
  ("expert_comprehension_v3311.json","courses",INDEPENDENT,None),
  ("comprehension_texts.json","chapters",INDEPENDENT,None),
  ("complete_source_page_index_v3310.json","courses",INDEPENDENT,{"pageCount":25,"pages":{str(i):{"sourcePart":None,"facts":[]} for i in range(1,26)}}),
  ("essential_study_selection_v3310.json","courses",INDEPENDENT,{"indices":[],"sourcePages":25,"available":0,"selected":0,"coveredSourcePages":0,"coveredSections":0,"totalSections":0}),
  ("board_catalog.json",None,INDEPENDENT,None)
 ]:
  path=root/filename
  data=prep_json(path)
  target=data if outer is None else data[outer]
  if default is None:target.pop(inner,None)
  else:target[inner]=default
  save_json(path,data)
 result={"integrated":True,"courseId":INDEPENDENT,"standaloneSourcePages":25,
   "sourceSha256":EXPECTED_SHA,"sourceBytes":source.stat().st_size,"sourceCopiesPreserved":True,
   "renderedPageCount":len(images),"renderedBytes":sum((a/x[7:]).stat().st_size for x in images),
   "sourcePdfInPackage":str(pdffile),"historicalRecordsPreserved":str(legacy_out),
   "studyTextReviewedPages":0,"sourceAssetsRoot":str(a)}
 return result
if __name__=="__main__":
 p=argparse.ArgumentParser()
 p.add_argument("--assets",required=True)
 p.add_argument("--original",required=True)
 args=p.parse_args()
 print(json.dumps(repair(pathlib.Path(args.assets),pathlib.Path(args.original)),ensure_ascii=True),flush=True)
