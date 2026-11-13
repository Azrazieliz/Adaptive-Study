#!/usr/bin/env python3
"""Complete page navigation from already present guide facts.

No new academic assertions, OCR, generated explanations or course records.
Writes provenance for every additional index fact and audits physical source
images; does not certify that unread original PDF pages are comprehensively taught.
"""
import collections,hashlib,json,pathlib,sys,shutil,argparse
NON_INDEPENDENT={"bio_proteines","bio_biomol","chim_atoliais","chim_protons","phys_energie_elec","phys_fluides"}
OLDER_INACTIVE={"histo_embryo","biocell_cytosq","biocell_mec_integrine","biocell_dev","biocell_cycle"}
IGNORE=NON_INDEPENDENT|OLDER_INACTIVE
def getjson(p):return json.loads(p.read_text(encoding="utf-8"))
def putjson(p,data):
 tmp=p.with_suffix(p.suffix+".tmp")
 tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
 tmp.replace(p)
def h(x):return hashlib.sha256(x.read_bytes()).hexdigest()
def main():
 parser=argparse.ArgumentParser()
 parser.add_argument("--assets",required=True)
 args=parser.parse_args()
 root=pathlib.Path(args.assets); web=root/"www"
 datafile=root/"study_data.json"
 data=getjson(datafile)
 before=h(datafile)
 idxfile=root/"complete_source_page_index_v3310.json"
 idx=getjson(idxfile)
 archive=idxfile.with_name("complete_source_page_index_v3310.before_existing_index_fill_20261113.json")
 if archive.exists():assert h(archive)==h(idxfile),"Index backup collision"
 else:shutil.copy2(idxfile,archive)
 active=[x for x in data['chapters'] if x['id'] not in IGNORE]
 assert len(active)==70,len(active)
 assert len(data['chapters'])==81 and len(data['questions'])==617 and len(data['flashcards'])==8270
 added=collections.Counter();pages_added=collections.Counter();total_validated_paths=0;missing_assets=[]
 n_original_source_pages=0;unreviewed=collections.Counter()
 for course in active:
  cid=course['id']
  pages=data['coursePages'].get(cid,[])
  assert isinstance(pages,list) and pages
  n_original_source_pages+=len(pages)
  for i,rel in enumerate(pages):
   file=web/rel
   if not file.is_file() or file.stat().st_size<400:
    missing_assets.append({"course":cid,"page":i+1,"path":rel})
   else:total_validated_paths+=1
  existing=idx['courses'].get(cid)
  if existing is None:existing={"pageCount":len(pages),"pages":{}}
  page_map=existing.setdefault('pages',{})
  existing['pageCount']=len(pages)
  if cid in {"biocell_noyau","shs_sante_environnement"}:
   # Authentic Noyau source is image-only; Sante environnement OCR has no review.
   idx['courses'][cid]=existing
   continue
  guide=data['courseGuides'].get(cid,{})
  for si,section in enumerate(guide.get('sections',[])):
   title=section.get('title',"")
   if 'questions' in title.lower() or 'entraînement' in title.lower():continue
   for fi,item in enumerate(section.get('items',[])):
    if not isinstance(item,dict):continue
    page=item.get('page')
    if not isinstance(page,int) or page<1 or page>len(pages):continue
    if item.get('sourceQuality') in ('AUTOMATIC_OCR_UNVERIFIED','UNREVIEWED_OCR'):continue
    value=item.get('value') or item.get('text') or ''
    if not isinstance(value,str) or not value.strip():continue
    if 'tableau à insérer' in value.lower() or 'page pdf' in value.lower() and 'remplac' in value.lower():continue
    key=str(page)
    entry=page_map.setdefault(key,{"sourcePart":None,"facts":[]})
    facts=entry.setdefault('facts',[])
    if any(f.get('section')==si and f.get('item')==fi and f.get('originalChapter',cid)==cid for f in facts):
     continue
    original_page_review=data.get('sourceVerifiedLessonCoverage',{}).get(cid,{})
    verified_set=set(original_page_review.get('verifiedPages',[]))
    unreviewed_source=original_page_review.get('status')=='PARTIAL' and page not in verified_set
    fact={
      "section":si,"item":fi,"label":item.get('label',''),
      "value":value,"topic":title,"originalChapter":cid,
      "isAdministrative":bool(item.get('isAdministrative',False)),
      "sourcePage":page,
      "provenance":"EXISTING_STUDY_GUIDE_FACT__NO_NEW_INTERPRETATION",
      "requiresManualReview":unreviewed_source,
    }
    facts.append(fact)
    added[cid]+=1
    if unreviewed_source:unreviewed[cid]+=1
  idx['courses'][cid]=existing
  pages_added[cid]=sum(bool(x.get('facts')) for x in page_map.values() if isinstance(x,dict))
 # Existing source images from already-present assets must resolve, no silently lost pages.
 assert not missing_assets,("MISSING_ORIGINAL_IMAGES",missing_assets[:20],len(missing_assets))
 assert h(datafile)==before,"ACADEMIC_SOURCE_DATA_CHANGED"
 assert idx['courses']['biocell_noyau']['pageCount']==25
 assert len(idx['courses']['biocell_noyau']['pages'])==25
 putjson(idxfile,idx)
 summary={
  "status":"VERIFIED_SOURCE_PATHS__INDEX_ONLY",
  "activeGenuineCourses":len(active),
  "activeOriginalSourceImages":n_original_source_pages,
  "physicalSourceImagesVerified":total_validated_paths,
  "missingOriginalSourceImages":missing_assets,
  "newIndexFactsLinkedFromExistingGuide":sum(added.values()),
  "newIndexFactsByCourse":dict(added),
  "indexedPagesByCourse":dict(pages_added),
  "newIndexFactsFlaggedForManualReview":dict(unreviewed),
  "sourceDataSha256Untouched":before,
  "indexSha256":h(idxfile),
  "originalNoyauPages":25,
  "academicCoverageCertifiedComplete":False,
  "notes":"This indexes existing facts and original assets for navigation, not new editorial certification. Automatic OCR is excluded."
 }
 report=pathlib.Path(args.assets).parent.parent.parent.parent/"PRESERVATION_20261112_NO_APK_BUILD"/"EXISTING_70_COURSE_NATIVE_SOURCE_INDEX_AUDIT_20261113.json"
 report.parent.mkdir(parents=True,exist_ok=True)
 putjson(report,summary)
 print(json.dumps({k:v for k,v in summary.items() if k not in ("newIndexFactsByCourse","indexedPagesByCourse","sourceDataSha256Untouched")},ensure_ascii=True),flush=True)
 print("LARGEST_GAPS",json.dumps(sorted(added.items(),key=lambda x:x[1],reverse=True)[:15],ensure_ascii=True),flush=True)
if __name__=="__main__":main()
