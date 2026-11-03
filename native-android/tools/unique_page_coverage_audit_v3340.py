# -*- coding: utf-8 -*-
"""Trace physical FC image coverage, not duplicated composite course page references.
One original page reused in 7 composite chapters is counted exactly once.
Does not certify transcription or figures even if a page has one indexed fact.
"""
from pathlib import Path
import json,collections,hashlib
R=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets")
D=json.loads((R/"study_data.json").read_text("utf8"))
allpages=collections.defaultdict(lambda:{"used_by":[],"linked_facts":[],"file_exists":False})
chapters={}
for ch in D["chapters"]:
 cid=ch["id"]
 source=D["courseMeta"].get(cid,{})
 pages=D["coursePages"].get(cid,[])
 guide=D["courseGuides"].get(cid,{}).get("sections",[])
 composite=bool(D["courseGuides"].get(cid,{}).get("compositeParts"))
 has_facts=collections.Counter()
 for page_num,resource in enumerate(pages,1):
  allpages[resource]["used_by"].append({"courseId":cid,"position":page_num,
     "composite":composite})
  allpages[resource]["file_exists"]=(R/"www"/resource).is_file()
 for s in guide:
  for item in s.get("items",[]):
   try:n=int(item.get("page",0))
   except:n=0
   if 1<=n<=len(pages):
    asset=pages[n-1]
    allpages[asset]["linked_facts"].append({
      "courseId":cid,"coursePage":n,
      "sourceChapter":item.get("sourceChapter",cid),
      "label":item.get("label","")})
    has_facts[n]+=1
 unresolved=[i for i in range(2,len(pages)+1) if not has_facts[i]]
 chapters[cid]={"title":ch["title"],"source_page_positions":len(pages),
  "number_indexed_facts":sum(has_facts.values()),
  "indexed_page_positions":len(has_facts),
  "unindexed_page_positions":len(unresolved),
  "composite_of_related_source_FCs":composite,
  "source_review_status":"NOT_CERTIFIED_EXHAUSTIVE"}
unindexed=[(p,v) for p,v in allpages.items() if not v["linked_facts"]]
indexed=[(p,v) for p,v in allpages.items() if v["linked_facts"]]
missing=[p for p,v in allpages.items() if not v["file_exists"]]
summary={"chapter_count":len(chapters),
  "course_page_references":sum(len(x) for x in D["coursePages"].values()),
  "distinct_physical_page_images":len(allpages),
  "distinct_page_images_without_any_indexed_fact":len(unindexed),
  "distinct_page_images_with_one_or_more_indexed_facts":len(indexed),
  "physical_page_files_missing":len(missing),
  "diagnostic_warning":"An index match is NOT proof that an entire source page, its diagrams or its bold labels have been transcribed or verified.",
  "chapters":chapters,
  "pages":{k:{"references":len(v["used_by"]),
   "indexed_fact_occurrences":len(v["linked_facts"]),
   "indexed_by":sorted({x["courseId"] for x in v["linked_facts"]}),
   "exists":v["file_exists"],
   "source":v["used_by"][0] if v["used_by"] else None}
   for k,v in allpages.items()}}
(R/"source_asset_coverage_v3340.json").write_text(json.dumps(summary,ensure_ascii=False,indent=1),encoding="utf8")
out=Path(r"D:\AdaptiveStudyRecovery\unique_page_audit_v3340.txt")
out.write_text("PHYSICAL PAGES: "+str(len(allpages))+
"\nMISSING_INDEX: "+str(len(unindexed))+
"\nINDEXED: "+str(len(indexed))+
"\nMISSING_IMAGES: "+str(len(missing))+"\n"+
"\n".join("NOFACT "+p+" FROM "+v["used_by"][0]["courseId"] for p,v in unindexed[:250]),"utf8")
print("UNIQUE_PAGE_AUDIT",len(allpages),"WITH_FACTS",len(indexed),
 "NO_FACTS",len(unindexed),"MISSING_IMAGE_FILES",len(missing))
print("TOP_COURSE_GAPS")
for k,v in sorted(chapters.items(),key=lambda x:-x[1]["unindexed_page_positions"])[:15]:
 print(k,v["unindexed_page_positions"],"/",v["source_page_positions"],"COMPOSITE",v["composite_of_related_source_FCs"])
