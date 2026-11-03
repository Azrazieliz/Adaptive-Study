from pathlib import Path
import json,copy,collections,shutil
R=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets")
p=R/"study_data.json"
d=json.loads(p.read_text("utf8"))
backup=R/"study_data_before_related_source_assembly_v3310.json"
if not backup.exists():shutil.copy2(p,backup)
chap={c["id"]:c for c in d["chapters"]}
# Strict original-source map: no invented FCs, no material external to the supplied documents.
relations={
 "histo_embryo":[("histo_fecondation",[0,1,2]),("histo_nerveux",[1]),("histo_osseux",[1,15,16])],
 "biocell_noyau":[("biocell_intro",[4,8,9,11]),("biocell_adn",[0,1,2]),("biocell_apoptose",[1,4,5])],
 "biocell_cytosq":[("biocell_intro",[11,13]),("histo_nerveux",[5]),("histo_epitheliaux",[5,7,8,9,10,11,18]),("biocell_membrane",[15])],
 "biocell_mec_integrine":[("histo_conjonctifs",[0,1,2,3,10,11,12]),("histo_epitheliaux",[1,5,7,8,9,11]),("biocell_membrane",[7,10,12,13])],
 "biocell_dev":[("histo_fecondation",[0,1,2]),("histo_nerveux",[1]),("histo_osseux",[1,15,16]),("biocell_signal1",[12,14])],
 "biocell_cycle":[("biocell_intro",[14,15]),("biocell_adn",[0,1,2]),("biocell_apoptose",[0,1,4,5,6,7,8]),("biocell_methodes1",[0,1,2,3])],
 "bio_biomol":[("biocell_intro",[8,9]),("biocell_adn",[0,1,2]),("bio_methodes",[0,6,7,8,9,11,12]),("bio_structure",[0,2,7,12])]
}
stats=collections.Counter();source_index={}
for cid, related in relations.items():
 assert cid in chap
 if cid in d["courseGuides"]:raise RuntimeError("Refusing overwrite existing source course "+cid)
 guide_sections=[];pages=[];parts=[];offset=0;source_chapters=[]
 for srcid,indices in related:
  if srcid not in d["courseGuides"] or srcid not in d["coursePages"]:raise RuntimeError("Missing original source for "+srcid)
  orig=d["courseGuides"][srcid]
  original_pages=d["coursePages"][srcid]
  # All pages are retained for full reading; selected sections do NOT misrepresent those pages as exclusively about the target topic.
  parts.append({"sourceChapter":srcid,"sourceTitle":chap[srcid]["title"],"startPage":offset+1,
      "endPage":offset+len(original_pages),"pages":len(original_pages),"sourceVersion":orig.get("sourceVersion","")})
  source_chapters.append(srcid)
  pages+=original_pages
  for idx in indices:
   if idx<0 or idx>=len(orig["sections"]):raise RuntimeError("Section selection outside guide "+srcid+" "+str(idx))
   sec=copy.deepcopy(orig["sections"][idx])
   if not sec.get("items"):continue
   sec["title"]=chap[srcid]["title"]+" — "+sec["title"]
   sec["originChapter"]=srcid
   sec["originSectionIndex"]=idx
   for it in sec["items"]:
    pg=it.get("page")
    it["sourceChapter"]=srcid;it["sourceDocument"]=orig.get("sourceFile","")
    if isinstance(pg,int) and pg>0:
     if pg>len(original_pages):raise RuntimeError("Invalid source page "+srcid+" "+str(pg))
     it["originalSourcePage"]=pg
     it["page"]=offset+pg
   guide_sections.append(sec)
  offset+=len(original_pages)
 if not guide_sections or not pages:raise RuntimeError("Empty recovered source-link chapter "+cid)
 d["courseGuides"][cid]={"sourceVersion":"COMPOSITE_OF_EXISTING_COURSES",
     "sourceFile":"Sources FC existantes rapprochées par thème; aucune FC autonome fournie sous ce titre",
     "guideCoverage":"RELATED_SOURCES_ONLY__NOT_INDEPENDENT_FC",
     "independentSourceFilePresent":False,
     "compositeParts":parts,"sections":guide_sections}
 d["coursePages"][cid]=pages
 d["courseMeta"][cid]={"pages":len(pages),"isComposite":True,
   "compositeParts":parts,"independentSourceFilePresent":False,
   "relationship":"RELATED_COURSE_REFERENCE_NOT_SAME_AS_ORIGINAL_FC"}
 d["courseSourceDocuments"][cid]={"kind":"RELATED_COMPOSITE",
   "chapters":source_chapters,"independentOriginalFC":False,
   "relatedSourcePages":len(pages)}
 chap[cid]["available"]=True
 chap[cid]["auditStatus"]="RELATED_SOURCE_COURSES_ASSEMBLED"
 chap[cid]["auditNote"]="Contenu provenant des FC existantes voisines et référencé par chapitre/page ; ne prétend pas être la transcription d'une FC autonome portant ce titre."
 source_index[cid]={"chapters":source_chapters,"sourcePages":len(pages),
   "sections":len(guide_sections),"facts":sum(len(s["items"]) for s in guide_sections)}
 stats["chapters"]+=1;stats["pages"]+=len(pages);stats["sections"]+=len(guide_sections)
 stats["facts"]+=sum(len(s["items"]) for s in guide_sections)
d["pack"]["notes"]="Original 31 FC syllabus preserved. Additional umbrella chapters use labeled existing source course references, never fabricated independent FCs."
p.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":")),encoding="utf8")
(R/"related_source_recovery_v3310.json").write_text(json.dumps({
"method":"Strict references to already provided FC guides and original pages; no fabricated FC source",
"topics":source_index},ensure_ascii=False,indent=2),encoding="utf8")
print("RECOVERED_SEVEN_REFERENCED_TOPICS",dict(stats))
for k,v in source_index.items():print(k,v)
print("STRUCTURED",len(d["courseGuides"]),"SOURCE_PAGE_SETS",len(d["coursePages"]))
