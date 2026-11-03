import json, pathlib,re,collections,statistics,hashlib
root=pathlib.Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets")
d=json.loads((root/"study_data.json").read_text("utf8"))
obj=json.loads((root/"comprehension_texts.json").read_text("utf8"))
assert len(obj["chapters"])==len(d["chapters"])==73
err=[];stats=collections.Counter()
for c in d["chapters"]:
 cid=c["id"];entry=obj["chapters"][cid];sec=entry["sections"]
 assert sec,cid
 all_evidence=[x for s in sec for x in s["evidence"]]
 stats["facts"]+=len(all_evidence);stats["paragraphs"]+=sum(len(s["paragraphs"]) for s in sec)
 if cid in d["courseGuides"]:
  truefacts=[i for s in d["courseGuides"][cid]["sections"] for i in s.get("items",[]) if str(i.get("value") or i.get("text") or "").strip()]
  if len(truefacts)!=len(all_evidence):err.append((cid,"MISCOUNT",len(truefacts),len(all_evidence)))
 else:
  assert "RELATED_CONTENT_ONLY" in entry["coverageStatus"],cid
 for si,s in enumerate(sec):
  for p in s["paragraphs"]:
   for pattern in ["la FC", "le pdf page", "un interruption", "[p.", "que retenir de", "l'acoustique apparaît parce"]:
    if pattern.lower() in p.lower():stats["prose_dubious_"+pattern]+=1
   if len(p)>1700:stats["long_paragraph"]+=1
  for fact in s["evidence"]:
   if not fact.get("value"):err.append((cid,"EMPTY_EVIDENCE",si))
   if fact.get("sourceChapter")==cid and entry["sourcePageTotal"] and isinstance(fact.get("sourcePage"),int) and fact["sourcePage"]>entry["sourcePageTotal"]:
    err.append((cid,"PAGE_OUT_OF_RANGE",fact["sourcePage"]))
stats["courses"]=len(obj["chapters"])
print("AUDIT",dict(stats),"ERRORS",err[:40], "COUNT",len(err))
assert not err
print("EXAM_SOURCE_CORPUS",len(d["questions"]),"Q","PACK",d["pack"]["version"])
