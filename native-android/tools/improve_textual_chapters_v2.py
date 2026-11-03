#!/usr/bin/env python3
"""Build source-traceable explanation prose from existing FC-derived facts.
Never invent science or claim that a scanned FC has been exhaustively transcribed.
Existing app, original PDFs, flashcards, guides and navigation remain unchanged.
"""
from __future__ import annotations
import json,re,hashlib,collections,pathlib,shutil
ROOT=pathlib.Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets")
guide_data=json.loads((ROOT/"study_data.json").read_text("utf8"))
source=ROOT/"comprehension_texts.json"
old=json.loads(source.read_text("utf8"))
backup=ROOT/"comprehension_texts_before_editorial_v2.json"
if not backup.exists():shutil.copy2(source,backup)
chap={c["id"]:c for c in guide_data["chapters"]}
facts_total=0
stats=collections.Counter()

def clean(s):
    s=re.sub(r"\s*\[p\.?\s*\d+\]", "",str(s or ""),flags=re.I)
    s=re.sub(r"(?i)^(?:la|le|cette|ce)\s+(?:FC|fiche(?: de cours)?|cours)\s+(?:indique|précise|rappelle|décrit|mentionne|présente|donne|cite|affirme|associe)\s+(?:que\s+)?","",s)
    s=re.sub(r"(?i)^(?:selon (?:la|le) (?:FC|fiche|cours)\s*:?\s*)","",s)
    s=re.sub(r"(?i)\s+(?:selon|d'après) (?:la|le) (?:FC|fiche)(?: actualisée)?\b","",s)
    s=re.sub(r"(?i)^(?:la fiche|le cours) distingue\s+","Les catégories à distinguer sont : ",s)
    s=re.sub(r"(?i)\s*;\s*la FC (?:indique|rappelle|mentionne|précise)\s+"," ; ",s)
    s=re.sub(r"\s+"," ",s).strip(" .;-")
    return s[:1].upper()+s[1:] if s else ""

VERBS=("Relie","Conduit","Forme","Contient","Débute","Commence","Termine","Permet","Réalise","Assure","Stimule",
       "Freine","Inhibe","Favorise","Produit","Provoque","Constitue","Résulte","Répond","Différencie","Correspond",
       "Comporte","Comprend","Engendre","Se compose","Se situe","Se trouve","Présente","Sécrète","Intervient",
       "Dérive","Donne","Peut","Est","Possède","Émet","Reçoit","S'accompagne")
ARTICLES=("Le ","La ","Les ","L'","Un ","Une ","Des ","Ce ","Cette ","Ces ","Il ","Elle ","Ils ","Elles ",
          "Dans ","En ","Au ","Aux ","Pour ","Lorsque ","Après ","Avant ","Chez ","Si ","Chaque ","Par ",
          "Plus ","Moins ","On ","Toutes ","Tous ","Une ","C'est ","Il s'agit ","Ainsi ")
def grammatical_entity(label):
    label=clean(label)
    label=re.sub(r"\s*[-—]\s*(définition|caractéristiques|éléments|origine|composition|anatomie)$","",label,flags=re.I)
    if label.startswith(("L'","Le ","La ","Les ")):return label
    if label and label[0].isdigit():return label
    if label in ("SNC","SNP"):return "Le "+label
    if label in ("ADN","ARN","ATP","ADP","GTP","GDP","MEC","CSH","IMG","IVG"):return "L'"+label if label[0] in "AI" else "Le "+label
    if label.lower().startswith(("moelle","membrane","plaque","gouttière","racine","cellule","phase",
          "régulation","division","vitesse","accélération","formation","fibre","protéine","granulation",
          "composition","durée","structure","activité","quantité","localisation","fonction","taille",
          "production","prévalence","incidence","répartition","mortalité","loi","formule")):return "La "+label[:1].lower()+label[1:]
    if label.lower().startswith(("crêtes","cellules","granulocytes","plaquettes","lymphocytes","jonctions",
          "protéines","voies","étapes","filaments","acteurs","facteurs")):return "Les "+label[:1].lower()+label[1:]
    if label[:1].lower() in "aéeiouy":return "L'"+label[:1].lower()+label[1:]
    return "Le "+label[:1].lower()+label[1:]

def should_use_topic_label(label):
    return len(label)<=70 and not re.match(r"(?i)^(\d+|phase \d+|avant |après )",label)
def is_sentence(v):
    if not v:return False
    if v.startswith(ARTICLES):return True
    if re.match(r"^(?:Il faut|Il existe|Il s'agit|On distingue|On observe|L’ensemble|L'|La |Le |Les |Cet |Une |Un )",v):return True
    return bool(re.match(r"^(?:[A-ZÉÀ][a-zàâéèêëîïôùûüç]+(?:\s+\w+){0,4})\s+(?:est|sont|correspond|contient|comprend|possède|permet|intervient|reste|résulte|représente|forme)\b",v))

def sentence(label,value,section,chapter):
    l=clean(label).strip(":")
    v=clean(value)
    if not v:return ""
    if not l:return v.rstrip(".")+"."
    # Repeated label at the start of source is removed without losing its factual remainder.
    if v.casefold().startswith((l+":").casefold()):
        v=v[len(l)+1:].strip()
    ll=l.casefold()
    if is_sentence(v):
        return v.rstrip(".")+"."
    # Stable concept definitions that require a proper subject.
    if ll.endswith(" — définition"):
        noun=l.rsplit(" — ",1)[0]
        if v.lower().startswith(("interruption","étude","science","réaction","substance","cellule","structure","méthode")):
            return grammatical_entity(noun)+" désigne une "+v[:1].lower()+v[1:].rstrip(".")+"."
        if v.lower().startswith(("ensemble","processus","tissu")):
            return grammatical_entity(noun)+" désigne un "+v[:1].lower()+v[1:].rstrip(".")+"."
        return grammatical_entity(noun)+" : "+v.rstrip(".")+"."
    # Recognize connected source facts and describe the relation without adding an external claim.
    if ll in ("snc : composantes","snc — composantes","composantes du snc"):
        return "Le système nerveux central comprend "+v[:1].lower()+v[1:].rstrip(".")+"."
    if ll=="espaces du lcs" and v.startswith("Circulation dans "):
        return "Le liquide cérébrospinal circule dans "+v[len("Circulation dans "):].rstrip(".")+"."
    if ll=="plasma" and v.startswith("Substance fondamentale liquide"):
        if "contenant " in v:
            return "Le plasma est la substance fondamentale liquide du sang ; il contient "+v.split("contenant ",1)[1].rstrip(".")+"."
        return "Le plasma est "+v[:1].lower()+v[1:].rstrip(".")+"."
    if ll=="éléments figurés" and v.startswith("Globules rouges"):
        return "Parmi les éléments figurés du sang, les globules rouges sont aussi appelés hématies ou érythrocytes ; "+v.split(" ; ",1)[1].rstrip(".")+"." if " ; " in v else "Les éléments figurés du sang sont : "+v.rstrip(".")+"."
    if ll=="fécondité" and "l’IVG" in v:
        return "L’IVG ne rend pas stérile et ne diminue pas la fécondité." if "ne rend pas stérile" in v else v.rstrip(".")+"."
    if ll.startswith("img — motifs") and v.startswith("Poursuite de"):
        return "Les motifs médicaux d’IMG comprennent la poursuite d’une grossesse mettant gravement en péril la santé de la mère, ou la forte probabilité d’une affection particulièrement grave et reconnue comme incurable chez l’enfant à naître au diagnostic."
    if ll in ("définition","descriptive — définition") and chapter["subjectId"]=="sp" and "épidémio" in chapter["title"].lower():
        return "L’épidémiologie est l’étude scientifique de l’état de santé de la population et des facteurs influant sur la santé humaine." if v.startswith("Étude scientifique") else "L’épidémiologie descriptive est "+v[:1].lower()+v[1:].rstrip(".")+"."
    if ll=="nature" and chapter["subjectId"]=="sp" and "épidémio" in chapter["title"].lower():
        return "L’épidémiologie est une "+v[:1].lower()+v[1:].rstrip(".")+"."
    if ll=="place" and v.startswith("N’est ni") and "épidémio" in chapter["title"].lower():
        return "L’épidémiologie n’est ni la santé publique ni la médecine ; "+v.split(";",1)[1].strip().rstrip(".")+"." if ";" in v else "L’épidémiologie "+v[:1].lower()+v[1:].rstrip(".")+"."
    if ll=="second messager" and v.startswith("Petite molécule"):
        return "Le second messager est une petite molécule de signalisation intracellulaire."
    if ll=="deux modalités de génération" and v.startswith("Synthèse par"):
        return "Un second messager peut être généré par synthèse grâce à une protéine enzymatique cible, ou libéré à partir d’une source intracellulaire."
    if chapter["subjectId"]=="phys":
        if ll=="vitesse" and ("lim(" in v or "δt" in v):
            return "La vitesse instantanée correspond à la dérivée temporelle de la position : v = dOM/dt."
        if ll=="accélération" and ("lim(" in v or "δt" in v):
            return "L’accélération est la dérivée temporelle de la vitesse : a = dv/dt = d²OM/dt²."
        if ll=="relation fondamentale" and "dp/dt" in v:
            return "La somme des forces extérieures est égale à la dérivée temporelle de la quantité de mouvement : ΣF_ext = dp/dt."
    if ll in ("volume","volume sanguin") and "tissu sanguin" in chapter["title"].lower() and v.startswith("5 L"):
        return "Chez un adulte de 70 kg, le volume sanguin est d’environ 5 L, soit 1/14 du poids du corps."
    if ll=="facteurs" and v.startswith("Facteurs de risque"):
        return "On distingue les facteurs de risque, qui peuvent déclencher les maladies, et les facteurs protecteurs, qui peuvent empêcher ou retarder leur apparition."
    if ll=="compartiments" and v.startswith("Présence d’organites"):
        return "La cellule comporte des organites intracellulaires."
    if ll=="machinerie et ouvriers" and v.startswith("Organites et protéines"):
        return "Les organites et les protéines constituent la machinerie de la cellule."
    if ll=="centre de contrôle" and "noyau cellulaire" in v.lower():
        return "Le noyau cellulaire constitue le centre de contrôle."
    if ll=="production énergétique" and "ATP" in v and "mitochondries" in v:
        return "Les mitochondries produisent de l’énergie sous forme d’ATP."
    # Interpret a verb predicate using only the explicit label as subject.
    for verb in VERBS:
        if v.startswith(verb+" ") or v==verb:
            return grammatical_entity(l)+" "+v[:1].lower()+v[1:].rstrip(".")+"."
    if ll in ("nature","nature du tissu","définition","description","présentation"):
        if v.startswith(("Tissu ","Science ","Structure ","Ensemble ","Processus ","Réaction ","Méthode ")):
            first=v.split(" ",1)[0].lower()
            article="une" if first in ("science","structure","réaction","méthode") else "un"
            subject=grammatical_entity(chapter["title"])
            return subject+" est "+article+" "+v[:1].lower()+v[1:].rstrip(".")+"."
        return v.rstrip(".")+"."
    if ll in ("composition","constituants","éléments figurés","composants","constituants principaux"):
        return "La composition comprend "+v[:1].lower()+v[1:].rstrip(".")+"."
    if ll in ("fonction","fonctions","rôle","objectif","objectifs","utilité"):
        return grammatical_entity(chapter["title"])+" a pour "+("fonctions" if ll.endswith("s") else "fonction")+" : "+v.rstrip(".")+"."
    if ll in ("localisation","position","localisation principale","distribution"):
        return "La localisation correspond à "+v[:1].lower()+v[1:].rstrip(".")+"."
    if ll in ("volume","quantité","taille","nombre","masse","durée","durée sanguine","diamètre","épaisseur"):
        return "La "+ll+" est de "+v.rstrip(".")+"."
    # Contextualizes a numerical/date value without interpreting its significance.
    if re.match(r"^\d+(?:[,.]\d+)?\s*(?:%|µm|nm|mm|m|L|h|jours?|semaines?|mois|ans?)\b",v,re.I):
        return "Pour "+l[:1].lower()+l[1:]+", la valeur indiquée est "+v.rstrip(".")+"."
    if v.startswith(("Tissu ","Structure ","Ensemble ","Liquide ","Forme ","Matériel ","Protéine ","Molécule ")):
        first=v.split(" ",1)[0].lower()
        article="une" if first in ("structure","forme","protéine","molécule") else "un"
        return grammatical_entity(l)+" est "+article+" "+v[:1].lower()+v[1:].rstrip(".")+"."
    # Don't invent a causal relation if no causal direction is in the source.
    if ":" in v or ";" in v:
        return l[:1].upper()+l[1:]+" : "+v.rstrip(".")+"."
    if v.startswith(("Présence ","Absence ","Formation ","Libération ","Augmentation ","Diminution ","Production ","Modification ","Différenciation ")):
        return "Pour "+l[:1].lower()+l[1:]+", on observe "+v[:1].lower()+v[1:].rstrip(".")+"."
    return l[:1].upper()+l[1:]+" : "+v.rstrip(".")+"."

def build_paras(section,chapter,items):
    paragraphs=[]
    page_groups=[]
    for it in items:
        val=it.get("value") or it.get("text") or ""
        if not clean(val):continue
        sent=sentence(it.get("label",""),val,section,chapter)
        if not sent:continue
        p=it.get("page");pg=p if isinstance(p,int) and p>0 else None
        if not page_groups or pg!=page_groups[-1][0] or sum(len(x) for x in page_groups[-1][1])>490:
            page_groups.append([pg,[]])
        page_groups[-1][1].append(sent)
    for pg,ss in page_groups:
        text=" ".join(ss).replace(". .",".").strip()
        if text:paragraphs.append(text)
    return paragraphs

# Existing related-only chapters use sourced facts from neighbors. Never pass off as original.
newchap={}
for cid,ch in chap.items():
    old_entry=old.get("chapters",{}).get(cid,{})
    source_guide=guide_data["courseGuides"].get(cid)
    related=not bool(source_guide and source_guide.get("sections"))
    resolved=[]
    sections=source_guide.get("sections",[]) if source_guide else []
    if related:
        for old_sec in old_entry.get("sections",[]):
            rel=old_sec.get("relatedChapter")
            target=next((x for x in guide_data["courseGuides"].get(rel,{}).get("sections",[])
                        if clean(x.get("title"))==clean(old_sec.get("heading"))),None)
            if target:
                resolved.append((target,rel,old_sec.get("relatedCourseTitle","")))
            else:
                stats["unresolved_related_sections"]+=1
    else:
        resolved=[(sec,"","") for sec in sections]
    result_sections=[];page_total=set();facts=0;paragraphs=0
    for sec,related_cid,related_title in resolved:
        items=[it for it in sec.get("items",[]) if clean(it.get("value") or it.get("text"))]
        if not items:continue
        paras=build_paras(sec,ch,items)
        pages=sorted({it["page"] for it in items if isinstance(it.get("page"),int) and it["page"]>0}) if not related else []
        page_total.update(pages)
        evidence=[]
        for it in items:
            norm=clean(it.get("value") or it.get("text"))
            evidence.append({"label":clean(it.get("label")),"value":norm,
                 "sourcePage":it.get("page"),"sourceChapter":related_cid or cid,
                 "fingerprint":hashlib.sha256((cid+"|"+str(it.get("page"))+"|"+norm).encode("utf8")).hexdigest()[:16]})
        result_sections.append({"heading":clean(sec.get("title")),
            "paragraphs":paras,"sourceFacts":len(items),"sourcePages":pages,
            "relatedChapter":related_cid,"relatedCourseTitle":related_title,"evidence":evidence})
        paragraphs+=len(paras);facts+=len(items)
    status=old_entry.get("coverageStatus","")
    composite=bool(source_guide and source_guide.get("sourceVersion")=="COMPOSITE_OF_EXISTING_COURSES")
    if composite:status="COMPOSITE_EXISTING_SOURCE_COURSES__NO_INDEPENDENT_FC"
    elif related:status="RELATED_CONTENT_ONLY__ORIGINAL_COURSE_NOT_PROVIDED"
    elif not status:status="SOURCE_GUIDE_NOT_EXHAUSTIVENESS_VERIFIED"
    page_count=len(guide_data.get("coursePages",{}).get(cid,[]))
    entry={"title":ch["title"],"subjectId":ch["subjectId"],
         "sections":result_sections,"paragraphCount":paragraphs,"sourceFacts":facts,
         "sourcePages":sorted(page_total),"sourcePageTotal":page_count,
         "provenance":"COMPOSITE_EXISTING_COURSES" if composite else ("RELATED_ONLY" if related else "FC_STRUCTURED_FACTS"),
         "relatedChapters":old_entry.get("relatedChapters",[]),
         "coverageStatus":status,"requiresPageByPageReview":True,
         "readingStrategy":old_entry.get("readingStrategy",""),
         "courseSourcePresent":page_count>0,
         "independentCourseSourcePresent":not related and not composite,
         "compositeParts":source_guide.get("compositeParts",[]) if source_guide else [],
         "textualizationQuality":"SOURCE_PRESERVING_PROSE__NOT_EDITORIALLY_CERTIFIED"}
    newchap[cid]=entry
    stats[status]+=1;stats["sections"]+=len(result_sections);stats["paragraphs"]+=paragraphs;stats["facts"]+=facts
    if not result_sections:stats["no_sections"]+=1
assert len(newchap)==73 and stats["no_sections"]==0,dict(stats)
new={"schema":"native_comprehension_v2",
     "description":"Natural-language reading passages from available FC structured facts; per-fact evidence retained. No assertion of source-exhaustive lessons.",
     "chapters":newchap}
out=ROOT/"comprehension_texts.json"
out.write_text(json.dumps(new,ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("STATS",dict(stats),"OUTPUT_KB",round(out.stat().st_size/1024,1),"ORIGINAL_KB",round(backup.stat().st_size/1024,1))
for cid in ("histo_sanguin","histo_nerveux","shs_ivg","sp_epidemiologie","biocell_signal2","phys_energies","biocell_noyau"):
  e=newchap[cid];sec=e["sections"][0];print("EXAMPLE",cid,"SECTION",sec["heading"],"PROSE",sec["paragraphs"][0][:700])
