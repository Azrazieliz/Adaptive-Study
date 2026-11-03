# -*- coding:utf-8 -*-
"""Repair empirically observed malformed/ambiguous flashcards while retaining stable IDs.
Quarantine unrepairable same-front/different-answer items outside Android, never erase the source.
"""
from pathlib import Path
import json,re,collections,shutil,hashlib
ROOT=Path(r"D:\AdaptiveStudyRecovery")
ASSETS=ROOT/"AdaptiveStudyNative/app/src/main/assets"
P=ASSETS/"study_data.json"
VAULT=ROOT/"source_transfer/private_exam_assets_removed_from_app_v3330"
VAULT.mkdir(parents=True,exist_ok=True)
D=json.loads(P.read_text("utf8"))
B=VAULT/"flashcards_before_quality_repair_v3330.json"
if not B.exists():B.write_text(json.dumps(D["flashcards"],ensure_ascii=False,indent=1),encoding="utf8")
source_cards=json.loads(B.read_text("utf8"))
guides=D["courseGuides"]
def norm(s):
 return re.sub(r"\s+"," ",str(s).strip().lower()).rstrip(". ;")
def source_match(c):
 cid=c["chapterId"]
 guide=guides.get(cid,{})
 matches=[]
 for sec in guide.get("sections",[]):
  for fact in sec.get("items",[]):
   if norm(fact.get("value",fact.get("text","")))==norm(c["answer"]):
    matches.append((fact.get("label",""),sec.get("title",""),fact.get("page",0)))
 if not matches:return (None,None,None)
 page=c.get("source",{}).get("page")
 return next((x for x in matches if x[2]==page),matches[0])
manual={
"guide-fact29:60f8922c83d7":"Quelle relation donne la différence de potentiel d’un condensateur plan ?",
"guide-fact29:bf459adfd45b":"Que signifie un potentiel standard positif par rapport au couple H⁺/H₂ ?",
"guide-fact29:8f3793e4c5ff":"Quelle différence distingue l’ovogenèse de la folliculogenèse ?",
"guide-fact29:7c7da3b6c00c":"Quelle différence distingue SN et élimination dans les dérivés halogénés ?",
"fc-products-visual:07:00":"Comment définit-on un événement indésirable (EI) ?",
"fc-products-visual:07:02":"Comment définit-on un événement sanitaire indésirable (ESI) ?",
"fc-products-visual:07:03":"Quels exemples d’ESI sans lien avec les soins sont cités ?",
"fc-products-visual:07:04":"Que signifie EIAS et quelles situations recouvre-t-il ?",
"fc-products-visual:07:05":"Quels types de soins peuvent être à l’origine d’un EIAS ?",
"fc-products-visual:07:06":"Quel rôle les conditions d’utilisation d’un produit de santé jouent-elles dans un EI ?",
"fc-products-visual:07:07":"Quels dysfonctionnements de prescription ou délivrance favorisent les EIAS ?",
"micro-20261030:fa75f92849a0129c8651":"Quelle différence distingue l’ovogenèse de la folliculogenèse ?",
"micro-20261030:8b2f06c478c361f65203":"Quelle différence distingue SN et élimination sur un dérivé halogéné ?",
"micro-20261030:4d187102e971db2c7bc2":"Quelle relation donne la différence de potentiel d’un condensateur plan ?",
"micro-20261030:c703c3d3efc1fe81f2ae":"Que signifie un potentiel standard positif par rapport au couple H⁺/H₂ ?",
"micro-20261030:29c147dc49c5f821a4f0":"Quels événements ne constituent pas une IVG ?",
"v3312:related:95614a068be0cf53c96a5d":"Quelle différence distingue l’ovogenèse de la folliculogenèse ?",
"v3312:related:ed7e2539eae9ae6ebcebb6":"Quelle différence distingue l’ovogenèse de la folliculogenèse ?",
"v3312:related:4ad0a80a667184edf5ab77":"Quelle différence distingue l’ovogenèse de la folliculogenèse ?",
"v3312:related:6bbb92b914101b5e4e2c56":"Quelle différence distingue l’ovogenèse de la folliculogenèse ?"
}
quarantine=[];corrected=[];changes=collections.Counter()
for c in source_cards:
 c=dict(c)
 id=c["id"];q=c["question"]
 if id in manual:
  c["question"]=manual[id];changes["manual_rewrite"]+=1
  if "ovogenèse" in c["question"].lower():
   c["answer"]="L’ovogenèse forme l’ovocyte ; la folliculogenèse développe le follicule."
 if id=="micro-20261030:3b9a57af7cd5986b2da3":
  quarantine.append({"reason":"UNHELPFUL_COMPARATIVE_ANALOGY","card":c})
  changes["quarantine_analogy"]+=1;continue
 if q.startswith("Quelle différence existe entre les éléments de") and id not in manual:
  quarantine.append({"reason":"GENERIC_UNANSWERABLE_COMPARISON","card":c})
  changes["quarantine_generic_comparison"]+=1;continue
 # Fixed front-reference mismatch: generic old questions cannot reliably point to a unique source target.
 badfront=bool(re.search(r"(?i)^(?:quelle forme d.énergie intervient dans énergie|quelle forme présente cytosquelette|comment définit-on.*:\s*couleur)",c["question"]))
 if badfront:
  label,sec,page=source_match(c)
  if label=="Couleur" and "hémoglobine" in c["answer"].lower() and c["chapterId"]=="histo_sanguin":
   c["question"]="À quoi le sang doit-il sa couleur rouge ?"
   changes["contextual_rewrite"]+=1
  elif c["chapterId"]=="biocell_intro" and "cytosquelette" in c["question"].lower():
   c["question"]="Quel rôle le cytosquelette joue-t-il dans la forme de la cellule ?"
   changes["contextual_rewrite"]+=1
  else:
   quarantine.append({"reason":"MISLEADING_GENERIC_FRONT","card":c});changes["quarantine_misleading"]+=1;continue
 # Prefer direct material rather than "la FC indique": remove it from the FRONT when not needed.
 if "la FC" in c["question"] and c["chapterId"]=="histo_fecondation":
  before=c["question"]
  c["question"]=re.sub(r"(?:\s+selon la FC|\s+dans la FC)", "",c["question"],flags=re.I)
  c["question"]=c["question"].replace("indique la FC","indique le cours").replace("la FC indique-t-elle","est indiquée")
  if before!=c["question"]:changes["removed_fc_front"]+=1
 corrected.append(c)
# For identical question but conflicting answers, resolve by source label where verified and specific,
# otherwise quarantine ambiguous unanswerable cards (archives preserved).
groups=collections.defaultdict(list)
for c in corrected:groups[(c["chapterId"],norm(c["question"]))].append(c)
kept=[];dup_count=0
usedfronts=set()
for c in corrected:
 key=(c["chapterId"],norm(c["question"]))
 siblings=groups[key]
 if len(set(norm(x["answer"]) for x in siblings))<2:
  # Preserve existing stable IDs and progress unless truly ambiguous.
  kept.append(c);continue
 label,sec,pg=source_match(c)
 base=norm(label or "")
 if label and sec and len(base)>=3 and base not in ("étape 1","étape 2","étape 3","rôle","taille","principe","structure","définition","origine","localisation"):
  if base in ("réception","intégration","stockage","transmission","excitabilité","conductibilité"):
   revised=f"Quelle fonction du neurone est liée à « {label.lower()} » ?"
  elif c["chapterId"]=="sp_produits_sante" and label not in ("Risque","Produits de santé"):
   revised=f"Comment caractérise-t-on « {label} » dans le risque iatrogène ?"
  elif len(sec)<65 and len(label)<65:
   # Domain named, technical concept identified, no course-title-only question.
   revised=f"Que caractérise « {label} » dans « {sec} » ?"
  else:revised=None
  if revised and (c["chapterId"],norm(revised)) not in usedfronts:
   c["question"]=revised;changes["disambiguated_with_original_source_label"]+=1
   usedfronts.add((c["chapterId"],norm(revised)))
   kept.append(c);continue
 quarantine.append({"reason":"MULTIPLE_DIFFERENT_ANSWERS_SAME_FRONT","card":c,
  "source_match":None if label is None else {"label":label,"section":sec,"page":pg}})
 changes["quarantine_same_front"]+=1
# One last cross-course same-front ambiguity check is intentionally not applied: the chapter is on screen.
for c in kept:
 assert "Quelle différence existe entre les éléments" not in c["question"]
assert len({x["id"] for x in kept})==len(kept)
D["flashcards"]=kept
P.write_text(json.dumps(D,ensure_ascii=False,separators=(",",":")),encoding="utf8")
(VAULT/"flashcards_quarantined_v3330.json").write_text(json.dumps(quarantine,ensure_ascii=False,indent=1),encoding="utf8")
report={"active":len(kept),"original":len(source_cards),"changes":dict(changes),
 "quarantined":len(quarantine),"archived_outside_apk":str(VAULT),
 "chapters_with_active_cards":len(set(c["chapterId"] for c in kept)),
 "protected_question_ids":len(D["questions"])}
(ASSETS/"flashcard_qc_report_v3330.json").write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding="utf8")
print("FLASHCARD_REPAIR",report)
for c in [c for c in kept if c["chapterId"]=="histo_fecondation" and "ovogenèse" in c["question"].lower()][:6]:
 print("FECONDATION_CARD",c["id"],c["question"],"=>",c["answer"])
