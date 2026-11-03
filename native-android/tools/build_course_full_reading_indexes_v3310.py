from pathlib import Path
import json,re,collections,math,hashlib,statistics
R=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets")
data=json.loads((R/"study_data.json").read_text("utf8"))
essentials={}
pagecatalog={}
control=re.compile(r"(?i)(?:page\s+(?:PDF\s*)?\d+\s+(?:est\s+)?(?:à remplacer|explicitement marquée|remplacée)|(?:tableau|page)\s+à\s+insérer|erreur\s+(?:de|dans)\s+(?:PDF|FC)|note\s+à\s+(?:l'auteur|corriger)|contenu\s+barré|la\s+FC\s+(?:indique|présente|associe)\s+que\s+la\s+page)")
stats=collections.Counter()
for ch in data["chapters"]:
 cid=ch["id"];guide=data["courseGuides"][cid];page_count=len(data["coursePages"][cid])
 candidates=[];allfacts=[];by_page=collections.defaultdict(list);by_section=collections.defaultdict(list)
 for si,section in enumerate(guide.get("sections",[])):
  for ii,it in enumerate(section.get("items",[])):
   v=str(it.get("value") or it.get("text") or "").strip()
   if not v:continue
   label=str(it.get("label","")).strip()
   pg=it.get("page");page=pg if isinstance(pg,int) and 1<=pg<=page_count else 0
   rec={"section":si,"item":ii,"page":page,"priority":it.get("priority",1),
        "label":label,"value":v,"topic":section.get("title",""),"originalChapter":it.get("sourceChapter",cid)}
   allfacts.append(rec)
   if page:by_page[page].append(rec)
   if control.search(v) or control.search(label):
    stats["administrative_notes"]+=1
    continue
   if re.search(r"(?i)^Pièges attestés|questions? et annales|remarques sur le document",section.get("title","")):rec["priority"]=min(int(rec["priority"] or 1),1)
   candidates.append(rec);by_section[si].append(rec)
 target=min(len(candidates),min(70,max(16,round(math.sqrt(max(1,len(candidates)))*3))))
 selected=[];keys=set();per_section=collections.Counter();per_page=collections.Counter()
 def add(x):
  key=(x["section"],x["item"])
  if key in keys:return False
  selected.append(x);keys.add(key);per_section[x["section"]]+=1;per_page[x["page"]]+=1
  return True
 # Step one: a representative fact from as many sections as feasible, across the whole syllabus.
 sections=list(by_section)
 if len(sections)>target:
  # Stratified selection rather than just the first chapters.
  sections=list(dict.fromkeys(sections[min(len(sections)-1,round(i*(len(sections)-1)/max(1,target-1)))] for i in range(target)))
 for si in sections:
  vals=by_section[si]
  vals=sorted(vals,key=lambda it:(-int(it["priority"] or 1),it["page"],it["item"]))
  if vals:add(vals[0])
 # Step two: ensure late source pages are not systematically omitted.
 quartiles=14
 allpg=[x for x in candidates if x["page"]>0]
 if allpg:
  for binidx in range(quartiles):
   low=binidx*page_count/quartiles; high=(binidx+1)*page_count/quartiles
   group=[x for x in allpg if low<x["page"]<=high]
   group.sort(key=lambda it:(-int(it["priority"] or 1),per_section[it["section"]],it["page"]))
   if group and len(selected)<target and not any(low<x["page"]<=high for x in selected):add(group[0])
 # Step three: fill with priorities, penalising duplicate sections, pages, and identical answers.
 seenvalue={x["value"].lower() for x in selected}
 while len(selected)<target:
  remaining=[x for x in candidates if (x["section"],x["item"]) not in keys]
  if not remaining:break
  chosen=max(remaining,key=lambda x:(
    int(x["priority"] or 1)*3.0
    -per_section[x["section"]]*1.2-per_page[x["page"]]*1.0
    - (3.0 if x["value"].lower() in seenvalue else 0)
    + (0.25 if x["page"]>=page_count*.75 else 0)
  ))
  add(chosen);seenvalue.add(chosen["value"].lower())
 selected.sort(key=lambda x:(x["section"],x["item"]))
 essentials[cid]={"indices":[[x["section"],x["item"]] for x in selected],
     "sourcePages":page_count,"available":len(allfacts),
     "selected":len(selected),"coveredSourcePages":len({x["page"] for x in selected if x["page"]}),
     "coveredSections":len({x["section"] for x in selected}),
     "totalSections":len(guide["sections"])}
 # Per-page original-source facts. Keep all data, identify administrative notes as non-study.
 pagecatalog[cid]={
  "pageCount":page_count,
  "pages":{str(pg):{
      "sourcePart":next((part for part in guide.get("compositeParts",[]) if part["startPage"]<=pg<=part["endPage"]),None),
      "facts":[{"section":x["section"],"item":x["item"],"label":x["label"],
                "value":x["value"],"topic":x["topic"],"originalChapter":x["originalChapter"],
                "isAdministrative":bool(control.search(x["value"]) or control.search(x["label"]))}
                for x in by_page.get(pg,[])],
  } for pg in range(1,page_count+1)}
 }
 stats["courses"]+=1;stats["total_facts"]+=len(allfacts);stats["selected"]+=len(selected)
 stats["source_pages"]+=page_count;stats["pages_with_structured_notes"]+=len(by_page)
(R/"essential_study_selection_v3310.json").write_text(json.dumps({"schema":"essential_selection_v3310","courses":essentials},ensure_ascii=False,separators=(",",":")),encoding="utf8")
(R/"complete_source_page_index_v3310.json").write_text(json.dumps({"schema":"complete_source_page_index_v3310","courses":pagecatalog},ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("INDEX",dict(stats))
for cid in ("shs_rnd","histo_nerveux","biocell_intro","biocell_noyau","biocell_cycle","histo_methodes"):
 print(cid,essentials[cid])
