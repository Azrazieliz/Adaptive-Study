import re,json,collections,pathlib,textwrap
root=pathlib.Path("D:/AdaptiveStudyRecovery/AdaptiveStudyNative/app/src/main/assets")
d=json.loads((root/"study_data.json").read_text("utf8"))
chapters={c["id"]:c for c in d["chapters"]}
aliases={
"histo_embryo":["histo_fecondation","histo_nerveux"],
"biocell_noyau":["biocell_intro","biocell_adn"],
"biocell_cytosq":["biocell_intro","histo_nerveux"],
"biocell_mec_integrine":["biocell_membrane","histo_conjonctifs"],
"biocell_dev":["histo_fecondation","histo_nerveux"],
"biocell_cycle":["biocell_methodes1","biocell_methodes2","biocell_apoptose"],
"bio_proteines":["bio_structure","bio_repliement","bio_aa"],
"bio_biomol":["biocell_intro","biocell_adn","bio_methodes"],
"chim_atoliais":["chim_atoms","chim_liaison"],
"chim_protons":["chim_acide_base","chim_redox"],
"phys_energie_elec":["phys_energies","phys_electro"],
"phys_fluides":["phys_fluides_parfaits","phys_fluides_visqueux"]}
focus={
"histo_embryo":("fécond","embryon","neurulation","développement"),
"biocell_noyau":("noyau","nuclé","expression","adn","chromat","transcription"),
"biocell_cytosq":("cytosquelette","microtub","actine","filament","dynamique"),
"biocell_mec_integrine":("intégrine","matrice","collagène","adhésion","laminine"),
"biocell_dev":("développement","fécond","neurulation","embryon"),
"biocell_cycle":("cycle","mitos","apoptos","prolif","cytométr","phase"),
"bio_proteines":("protéine","liaison","repliement","structure","acide aminé"),
"bio_biomol":("expression","adn","arn","gène","réplication","transcription","moléculaire"),
"chim_atoliais":("atome","orbital","liaison","lewis","structure","vsepr"),
"chim_protons":("acide","base","proton","redox","oxyd","équilibre"),
"phys_energie_elec":("énergie","travail","puissance","électrostat","force","champ"),
"phys_fluides":("fluide","écoulement","viscos","débit","pression","bernoulli")
}
def clean(t):
 t=re.sub(r"\s*\[p\.?\s*\d+\]","",str(t or ""),flags=re.I)
 t=re.sub(r"(?i)^(?:la|le) (?:FC|fiche de cours) (?:indique|précise|décrit|mentionne|rappelle|présente|place|donne) (?:que )?","",t)
 t=re.sub(r"\s+"," ",t).strip(" .")
 if not t:return ""
 return t[0].upper()+t[1:]
def fact_sentence(item):
 label=clean(item.get("label","")).rstrip(":")
 value=clean(item.get("value") or item.get("text"))
 if not value:return ""
 if value.lower().startswith(label.lower()) and label:return value.rstrip(".")+"."
 if value[0].isupper() and len(value)>30:
  if label.lower() in value.lower()[:38]:return value.rstrip(".")+"."
 return f"{label} : {value.rstrip('.')}."
def group_paragraphs(items):
 sentences=[fact_sentence(x) for x in items if fact_sentence(x)]
 pars=[]
 for i in range(0,len(sentences),4):
  unit=sentences[i:i+4]
  pars.append(" ".join(unit))
 return pars
def get_sections(cid):
 g=d["courseGuides"].get(cid)
 if g and g.get("sections"):return g["sections"],"SOURCE_GUIDE_DERIVED",[]
 related=aliases.get(cid,[]);keywords=focus.get(cid,())
 selected=[]
 for src in related:
  for sec in d["courseGuides"].get(src,{}).get("sections",[]):
   hay=(sec.get("title","")+" "+" ".join(str(x.get("label","")) for x in sec.get("items",[]))).lower()
   score=sum(1 for word in keywords if word in hay)
   if score>=1:
    selected.append({"title":sec.get("title",""),"items":sec.get("items",[]),"relatedCourse":src,"sourceTitle":chapters[src]["title"]})
 if not selected:
  for src in related:
   for sec in d["courseGuides"].get(src,{}).get("sections",[])[:2]:
    selected.append({"title":sec.get("title",""),"items":sec.get("items",[]),"relatedCourse":src,"sourceTitle":chapters[src]["title"]})
 return selected,"RELATED_CHAPTER_SYNTHESIS_NOT_ORIGINAL_COURSE",related
results={}
for cid,ch in chapters.items():
 sections,kind,related=get_sections(cid)
 contents=[];facts=0;pages=set()
 for sec in sections:
  items=[x for x in sec.get("items",[]) if clean(x.get("value") or x.get("text"))]
  if not items:continue
  facts+=len(items)
  for it in items:
   pg=it.get("page")
   if isinstance(pg,int) and pg>0 and kind=="SOURCE_GUIDE_DERIVED":pages.add(pg)
  contents.append({"heading":clean(sec.get("title","")),
     "paragraphs":group_paragraphs(items),"sourceFacts":len(items),
     "relatedChapter":sec.get("relatedCourse",""),"relatedCourseTitle":sec.get("sourceTitle","")})
 sourcePageCount=len(d["coursePages"].get(cid,[]))
 missing=(kind!="SOURCE_GUIDE_DERIVED")
 coverage="SOURCE_GUIDE_INCOMPLETE_REVIEW_REQUIRED" if sourcePageCount and (len(pages)<max(3,round(sourcePageCount*.6)) or facts<sourcePageCount*3) else "SOURCE_GUIDE_NOT_EXHAUSTIVENESS_VERIFIED"
 if missing:coverage="RELATED_CONTENT_ONLY__ORIGINAL_COURSE_NOT_PROVIDED"
 results[cid]={"title":ch["title"],"subjectId":ch["subjectId"],
   "sections":contents,"paragraphCount":sum(len(x["paragraphs"]) for x in contents),
   "sourceFacts":facts,"sourcePages":sorted(pages),"sourcePageTotal":sourcePageCount,
   "provenance":kind,"relatedChapters":related,"coverageStatus":coverage,
   "requiresPageByPageReview":True}
result={"schema":"native_comprehension_v1","description":"Textualised source guide, not a verified full-page transcription. Missing originals are explicitly marked related only.","chapters":results}
out=root/"comprehension_texts.json"
out.write_text(json.dumps(result,ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("OUTPUT",out,out.stat().st_size,"CHAPTERS",len(results))
print("SECTION_TOTAL",sum(len(x["sections"]) for x in results.values()),"PARAGRAPHS",sum(x["paragraphCount"] for x in results.values()),"FACT_REFERENCES",sum(x["sourceFacts"] for x in results.values()))
print("STATES",dict(collections.Counter(x["coverageStatus"] for x in results.values())))
for cid in ["shs_ivg","biocell_intro","histo_nerveux","phys_energies","biocell_noyau"]:
 x=results[cid];print("SAMPLE",cid,x["coverageStatus"],x["sourceFacts"],x["paragraphCount"])
 print("TEXT",[(s["heading"],s["paragraphs"][0][:280]) for s in x["sections"][:2]])
