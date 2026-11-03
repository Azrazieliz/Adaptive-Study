from pathlib import Path
import json,collections,hashlib,re
r=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets")
d=json.loads((r/"study_data.json").read_text("utf8"))
sel=json.loads((r/"essential_study_selection_v3310.json").read_text("utf8"))["courses"]
pages=json.loads((r/"complete_source_page_index_v3310.json").read_text("utf8"))["courses"]
comp=json.loads((r/"comprehension_texts.json").read_text("utf8"))["chapters"]
orig=json.loads((r/"original_question_catalog.json").read_text("utf8"))["items"]
errors=[];stats=collections.Counter()
for ch in d["chapters"]:
 cid=ch["id"];g=d["courseGuides"].get(cid);a=d["coursePages"].get(cid)
 if g is None or a is None:errors.append((cid,"NO_GUIDE_OR_PAGES"));continue
 if cid not in sel or cid not in pages or cid not in comp:errors.append((cid,"NO_INDEX"))
 sec=g.get("sections",[])
 for i,j in sel[cid]["indices"]:
  if i>=len(sec) or j>=len(sec[i].get("items",[])):errors.append((cid,"INVALID_ESSENTIAL",i,j))
 stats["essential"]+=len(sel[cid]["indices"])
 if len(pages[cid]["pages"])!=len(a):errors.append((cid,"PAGE_NUMBER_MISMATCH",len(pages[cid]["pages"]),len(a)))
 for k,path in enumerate(a):
  if not (r/"www"/path).exists() and not (Path(r"D:\AdaptiveStudyRecovery\Adaptive-Study\local_instance\private_app\app")/path).exists():errors.append((cid,"MISSING_PAGE",k,path))
 stats["pages"]+=len(a)
 stats["facts"]+=sum(len(x.get("items",[])) for x in sec)
 if g.get("sourceVersion")=="COMPOSITE_OF_EXISTING_COURSES":stats["composites"]+=1
 if cid not in comp or not comp[cid].get("sections"):errors.append((cid,"NO_EXPLANATION"))
 stats["explanatory_paragraphs"]+=sum(len(x["paragraphs"]) for x in comp[cid]["sections"])
assert len(d["questions"])==309 and len(d["flashcards"])==2088 and len(orig)==969
assert not errors,errors[:20]
print("ALL_COURSE_PAGE_LINKS_OK",len(d["chapters"]),"GUIDES",len(d["courseGuides"]),dict(stats))
print("SOURCE_IMAGES_UNIQUE",len({p for v in d["coursePages"].values() for p in v}))
print("ORIGINAL_QUESTIONS",len(orig),"AUTHORED",len(d["questions"]),"FLASH",len(d["flashcards"]))
