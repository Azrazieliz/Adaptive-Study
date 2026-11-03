import json,pathlib,shutil,copy,collections
root=pathlib.Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets")
p=root/"study_data.json"
backup=root/"study_data_before_umbrella_composites.json"
if not backup.exists():shutil.copy2(p,backup)
d=json.loads(p.read_text("utf8"))
chap={c["id"]:c for c in d["chapters"]}
composites={
  "chim_atoliais":["chim_atoms","chim_liaison"],
  "chim_protons":["chim_acide_base","chim_redox"],
  "phys_energie_elec":["phys_energies","phys_electro"],
  "phys_fluides":["phys_fluides_parfaits","phys_fluides_visqueux"],
  "bio_proteines":["bio_aa","bio_structure","bio_repliement"]
}
assert all(cid in chap for cid in composites)
stats=collections.Counter()
for cid,children in composites.items():
 if d["courseGuides"].get(cid,{}).get("sections") and d["courseGuides"][cid].get("sourceVersion")!="COMPOSITE_OF_EXISTING_COURSES":
  raise RuntimeError("Course already has independent guide: "+cid)
 sections=[];merged_pages=[];segments=[]
 offset=0
 for srcid in children:
  guide=d["courseGuides"].get(srcid);pages=d["coursePages"].get(srcid)
  if not guide or not pages:raise RuntimeError("Missing component "+srcid)
  src_title=chap[srcid]["title"]
  segment={"sourceChapter":srcid,"sourceTitle":src_title,
     "startPage":offset+1,"endPage":offset+len(pages),
     "pages":len(pages),"sourceVersion":guide.get("sourceVersion","FC")}
  segments.append(segment)
  for sec in guide["sections"]:
   if not sec.get("items"):continue
   copysec=copy.deepcopy(sec)
   copysec["title"]=src_title+" — "+sec["title"]
   copysec["originChapter"]=srcid
   copysec["sourceVersion"]=guide.get("sourceVersion","")
   for item in copysec["items"]:
    original_page=item.get("page")
    item["sourceChapter"]=srcid
    if isinstance(original_page,int) and original_page>0:
     item["originalSourcePage"]=original_page
     if original_page>len(pages):
      raise ValueError(f"Page index outside source {srcid} {original_page}/{len(pages)}")
     item["page"]=original_page+offset
   sections.append(copysec)
  merged_pages+=pages
  offset+=len(pages)
  stats["source_component_courses"]+=1
 if not sections or not merged_pages:raise RuntimeError("Empty composite "+cid)
 d["courseGuides"][cid]={"sourceFile":"Regroupement de cours existants (aucune FC autonome fournie)",
      "sourceVersion":"COMPOSITE_OF_EXISTING_COURSES",
      "guideCoverage":"RELATED_COURSES__NOT_EXHAUSTIVE_AS_INDEPENDENT_CHAPTER",
      "sections":sections,
      "compositeParts":segments,
      "independentSourceFilePresent":False}
 d["coursePages"][cid]=merged_pages
 d["courseMeta"][cid]={"pages":len(merged_pages),"isComposite":True,
       "compositeParts":segments,"independentSourceFilePresent":False}
 d["courseSourceDocuments"][cid]={"kind":"COMPOSITE","chapters":children,
       "independentOriginalFC":False}
 ch=chap[cid];ch["auditStatus"]="COMPOSITE_FROM_EXISTING_SOURCE_COURSES__NOT_ORIGINAL_FC"
 ch["auditNote"]="The summary and pages are assembled from separately supplied source chapters; this is not a transcription of an original FC under this umbrella title."
 stats["composite_chapters"]+=1
 stats["new_pages"]+=len(merged_pages)
 stats["new_sections"]+=len(sections)
 stats["new_facts"]+=sum(len(s["items"]) for s in sections)
print("COMPOSITES",dict(stats))
p.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("CURRENT_GUIDES",len(d["courseGuides"]),"CURRENT_PAGESETS",len(d["coursePages"]))
