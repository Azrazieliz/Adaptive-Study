import re,json,pathlib,collections,shutil
p=pathlib.Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets\study_data.json")
d=json.loads(p.read_text("utf8"))
backup=p.with_name("flashcards_before_direct_questions_v3301.json")
if backup.exists():d["flashcards"]=json.loads(backup.read_text("utf8"))
b=backup
if not b.exists():b.write_text(json.dumps(d["flashcards"],ensure_ascii=False,separators=(",",":")),encoding="utf8")
stats=collections.Counter();problem=[];cards=[]
def clean(s):
 s=re.sub(r"\s*\[p\.?\s*\d+\]","",s)
 s=re.sub(r"\s+"," ",s).strip(" .;")
 return s
def answer_cleanup(a):
 a=clean(a)
 a=re.sub(r"(?i)\b(?:la|le)\s+FC\s+donne (?:comme )?","",a)
 a=re.sub(r"(?i)\b(?:la|le)\s+FC\s+indique\s+(?:que )?","",a)
 a=re.sub(r"(?i)\b(?:la|le)\s+FC\s+précise\s+(?:que )?","",a)
 a=re.sub(r"(?i)\b(?:la|le)\s+FC\s+(?:mentionne|rappelle)\s+(?:que )?","",a)
 a=re.sub(r"(?i)\b(?:selon|d'après) (?:la|le) FC\b","",a)
 a=re.sub(r"\s+"," ",a).strip(" .;")
 if a and a[0].islower():a=a[0].upper()+a[1:]
 return a
def context_question(label,section,answer):
 label=clean(label).rstrip("?")
 lower=label.lower()
 val=answer.lower()
 topic=re.sub(r"^(\d+[\s.-]*)","",label)
 if lower=="cellules" and ("5 à 20" in val or "visible" in val):return "Quelle est la taille habituelle des cellules et sont-elles visibles à l’œil nu ?"
 if "résolution indiquée" in val or ("limite de résolution" in val):
  return "Quelle est la limite de résolution de "+topic[:1].lower()+topic[1:]+" ?"
 if lower.startswith("choix de la technique"):return "Quels éléments déterminent le choix d’une technique histologique ?"
 if "composantes" in lower or lower in ("composition","principaux constituants","éléments figurés","éléments"):
  return "Quels éléments composent "+section.strip(" .;")+" ?"
 if "phase " in lower or lower.startswith(("étape","temps ")):
  return "Que se produit-il pendant "+topic[:1].lower()+topic[1:]+" ?"
 if lower.startswith(("rôle","fonction","action","but","objectif","utilité")):
  return "Quel est le rôle de "+section.strip(" .;")+" ?"
 if lower.startswith(("localisation","situation","site")):return "Où se situe "+section.strip(" .;")+" ?"
 if lower.startswith(("origine",)):return "Quelle est l'origine de "+topic[:1].lower()+topic[1:]+" ?"
 if lower.startswith(("mécanisme",)):return "Quel est le mécanisme de "+section.strip(" .;")+" ?"
 if lower.startswith(("définition",)):return "Comment définit-on "+section.strip(" .;")+" ?"
 if lower.startswith(("types","classification","catégories")):return "Quelles sont les catégories de "+section.strip(" .;")+" ?"
 if lower.startswith(("propriétés","caractéristiques",)):return "Quelles sont les propriétés de "+section.strip(" .;")+" ?"
 if lower.startswith(("avantages","inconvénients","limites")):return "Quels sont les "+topic.lower()+" de "+section.strip(" .;")+" ?"
 if lower.startswith(("taille","diamètre","résolution","épaisseur","volume","durée","nombre","taux","pourcentage","longueur","masse","fréquence","distance","température")):
  return "Quelle valeur caractérise "+topic[:1].lower()+topic[1:]+" ?"
 if lower.startswith(("transport","diffusion","exocytose","endocytose","division","croissance","formation","maturation","ossification","différenciation","migration","glycolyse")):
  return "Comment s’effectue "+topic[:1].lower()+topic[1:]+" ?"
 if "présente chez" in val or "retrouve chez" in val:return "Chez quels organismes trouve-t-on "+topic[:1].lower()+topic[1:]+" ?"
 if val.startswith(("composé","composée","formé","formée","constitué","constituée","ester ")) or " est formé" in val or " est constitué" in val:
  return "De quoi se compose "+topic[:1].lower()+topic[1:]+" ?"
 if val.startswith(("permet","assure","favorise","inhibe","stimule","déclenche","régule")):
  return "Quelle fonction assure "+topic[:1].lower()+topic[1:]+" ?"
 if "action" in val and (lower.startswith("inhibition") or lower.startswith("activation")):
  return "Quels sont les effets de "+topic[:1].lower()+topic[1:]+" ?"
 if val.startswith(("correspond","désigne","est un ","est une ","ensemble","substance")):
  return "Comment définit-on "+topic[:1].lower()+topic[1:]+" ?"
 if lower.startswith(("protéine","enzyme","membrane","cartilage","microtubule","chondroblaste","plasma","hydroxyapatite","triade","nucléole")):
  return "Quelle caractéristique définit "+topic[:1].lower()+topic[1:]+" ?"
 if val.startswith(("se situe","est situé","est localisé","présent dans","présente dans")):
  return "Où se trouve "+topic[:1].lower()+topic[1:]+" ?"
 if val.startswith(("le ","la ","les ","l’","l'","un ","une ","des ")):
  if "absence" in val or "présence" in val:return "Quelle présence ou absence caractérise "+topic[:1].lower()+topic[1:]+" ?"
  if any(x in val for x in ("permet","assure","favorise","inhibe","stimule","empêche","résulte","provoque")):
   return "Quelle est la conséquence fonctionnelle de "+topic[:1].lower()+topic[1:]+" ?"
 if re.search(r"\d",val) and any(x in val for x in (" µm"," nm"," %"," mm"," cm"," an"," mol"," jours"," kda"," °c")):
  return "Quelle valeur est associée à "+topic[:1].lower()+topic[1:]+" ?"
 if lower.startswith(("évolution","historique","chronologie","loi","date","période")):
  return "Quel repère chronologique correspond à "+topic[:1].lower()+topic[1:]+" ?"
 if lower.startswith(("différence","comparaison","distinction")):
  return "Quelle différence existe entre les éléments de "+section.strip(" .;")+" ?"
 # Explicitly described properties make better single-recall prompts than category labels.
 simple={"principe":"Quel est le principe de ","nature":"Quelle est la nature de ",
   "structure":"Quelle est la structure de ","exemple":"Quel exemple illustre ",
   "orientation":"Quelle est l'orientation de ","effet":"Quel effet produit ",
   "dégradation":"Comment se déroule la dégradation de ",
   "cible":"Quelle est la cible de ","cibles":"Quelles sont les cibles de ",
   "récepteur":"Quel récepteur intervient dans ","conséquence":"Quelle est la conséquence de ",
   "résultat":"Quel résultat observe-t-on pour ","activation":"Comment s'active ",
   "inactivation":"Comment s'inactive ","intérêt":"Quel est l'intérêt de ",
   "dissociation":"Comment se produit la dissociation de ",
   "séparation":"Comment s'effectue la séparation lors de ",
   "organisation":"Comment s'organise ","fixation":"Comment s'effectue la fixation de ",
   "support":"Quel support est utilisé pour ","dynamique":"Quelle dynamique caractérise ",
   "mobilité":"Quelle mobilité présente ","forme":"Quelle forme présente ",
   "conservation":"Quel phénomène de conservation caractérise ",
   "risque":"Quel risque est associé à ","énergie":"Quelle forme d'énergie intervient dans ",
   "rôles":"Quels rôles assure ","fonction":"Quelle est la fonction de ",
   "distribution":"Comment se répartit ","circulation":"Comment circule ",
   "solubilité":"Quelle solubilité caractérise ","seuil":"Quel est le seuil de ",
   "vitesse":"Comment évolue la vitesse dans ","comparaison":"Quelle comparaison faut-il faire pour ",
   "interprétation":"Comment interpréter ","lecture":"Comment lire ",
   "affinité":"Quelle est l'affinité de ","maturation":"Comment mûrit ",
   "sécrétion":"Comment se fait la sécrétion de ","fixation":"Quelle est la méthode de fixation de ",
   "synthèse":"Comment se réalise la synthèse de ",
   "phagocytose":"Comment se déroule la phagocytose dans ",
   "révélation":"Comment est réalisée la révélation pour ",
   "hybridation":"Comment fonctionne l'hybridation dans ",
   "cumul":"Comment le cumul des facteurs affecte-t-il ",
   "norme":"Quelle est la norme pour "}
 if lower in simple and section:
  return simple[lower]+section.strip(" .;")+" ?"
 if lower.startswith(("propriétés ","principe ","rôle ","effet ","résultat ","étape ")):
  if lower.startswith("étape "):return "Que se passe-t-il durant "+topic.lower()+" ?"
  return "Que précise "+topic.lower()+" dans "+section.strip(" .;")+" ?"
 if val.startswith(("un ","une ","des ","les ","la ","le ","l'","l’")) and re.search(r"\b(est|sont|désigne|correspond|constitue|représente|contient|comporte)\b",val):
  return "Comment définit-on "+topic[:1].lower()+topic[1:]+" ?"
 return None
for card in d["flashcards"]:
 q=clean(card["question"]);ans=answer_cleanup(card["answer"])
 if not ans:stats["empty"]+=1;problem.append(card);continue
 if re.match(r"^(Quels?|Quelles?|Comment|Pourquoi|Où|Quand|Citez|Définissez|De quoi|Par quoi|Quelle est|Quel est|Que signifie|Combien|Chez quels|À quoi|En quoi)\b",q,re.I):
  refined=q
 else:
  m=re.fullmatch(r"(.+?)\s*:\s*quels éléments essentiels\s*\?",q,re.I)
  if m:
   label=m.group(1);section=""
  else:
   m=re.fullmatch(r"(.+?)\s*:\s*(.+?)\s*\?",q)
   if m:section=m.group(1);label=m.group(2)
   else:
    bits=re.split(r"\s+[—–]\s+",q.rstrip(" ?"))
    if len(bits)>=2:label=bits[-1];section=bits[-2]
    else:label=q.rstrip("?");section=""
  if not section:section=label
  refined=context_question(label,section,ans)
  if refined is None:
   stats["unresolved"]+=1
   problem.append(card)
   continue
  stats["rewritten"]+=1
 refined=refined.rstrip(" ?")+" ?"
 if re.search(r"(?i)quels éléments essentiels|que retenir de|la FC|à propos de «",refined) or len(refined)>155:
  stats["poor_front"]+=1;problem.append(card);continue
 if len(ans)>140:
  stats["long_answer"]+=1;problem.append(card);continue
 card["question"]=refined;card["answer"]=ans
 card["assessmentStatus"]="CONCISE_FACT_REWRITTEN__SOURCE_GUIDE_REVIEW_PENDING"
 cards.append(card)
d["flashcards"]=cards
p.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":")),encoding="utf8")
(p.parent/"flashcards_unresolved_style_v3301.json").write_text(json.dumps(problem,ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("RESULT",dict(stats),"ACTIVE",len(cards),"UNRESOLVED",len(problem))
for x in [y for y in cards if y["chapterId"]=="histo_methodes"][:17]:
 print("CARD",repr(x["question"]),"=>",repr(x["answer"][:145]))
