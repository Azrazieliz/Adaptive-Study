import json,pathlib,re,collections
p=pathlib.Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets\study_data.json")
d=json.loads(p.read_text("utf8"))
count=collections.Counter();clean=[]
for c in d["flashcards"]:
 q=c["question"];a=c["answer"]
 original=q
 q=q.replace("Quelle est la limite de résolution de œil nu ?","Quelle est la limite de résolution de l'œil nu ?")
 q=q.replace("Quelle est la limite de résolution de microscope optique ?","Quelle est la limite de résolution du microscope optique ?")
 q=q.replace("Quelle est la limite de résolution de microscope électronique ?","Quelle est la limite de résolution du microscope électronique ?")
 q=q.replace("Quel est le rôle de Microscopie optique et contraste de phase ?","Quel grossissement maximal est mentionné pour la microscopie optique ?")
 q=q.replace("Que se produit-il pendant contraste de phase — principe ?","Sur quel principe repose la microscopie à contraste de phase ?")
 q=q.replace("Que se produit-il pendant contraste de phase — intérêt ?","Pourquoi utiliser la microscopie à contraste de phase ?")
 q=q.replace("Comment s’effectue formation de l’image ?","Comment se forme l’image en microscopie électronique à transmission ?")
 q=q.replace("Quelle valeur caractérise résolution ?","De quoi dépend l'amélioration de la résolution en microscopie électronique ?")
 q=q.replace("Quelle valeur est associée à — Coupe ultrafine ?","Quelle est l'épaisseur d'une coupe ultrafine destinée à la MET ?")
 q=q.replace("Quelle valeur est associée à — Coupe ?","Quelle est l'épaisseur habituelle des coupes en microscopie optique ?")
 q=q.replace("Quel est le rôle de Microscopie électronique à balayage (MEB) ?","Quel est l'intérêt de la microscopie électronique à balayage ?")
 q=q.replace("Quelle présence ou absence caractérise peroxydase des éosinophiles ?","Quelle réaction catalyse une peroxydase en présence de DAB et de H₂O₂ ?")
 q=q.replace("Quelle valeur est associée à fITC ?","Quelles longueurs d'onde caractérisent le FITC ?")
 q=q.replace("Quelle valeur est associée à phycoérythrine (PE) ?","Quelles longueurs d'onde caractérisent la phycoérythrine ?")
 q=q.replace("Quelle est la méthode de fixation de Microscopie électronique à balayage (MEB) ?","Quel agent est utilisé pour la fixation en microscopie électronique à balayage ?")
 q=q.replace("Quel support est utilisé pour MET — préparation du prélèvement ?","Sur quel support est déposé un prélèvement pour la MET ?")
 q=q.replace("Quel est le principe de Immunohistologie — cible et anticorps ?","Comment l'immunohistologie permet-elle de localiser une molécule ?")
 q=q.replace("Quel est le rôle de ","Quel est le rôle de ") # reserved stable
 if q!=original:count["manual_front_fixes"]+=1
 # Remove document-control voice from answers without losing facts.
 if re.search(r"\bLa FC\b",a,re.I):
  a=re.sub(r"(?i)\bLa FC relie la meilleure résolution à la longueur d’onde plus courte des électrons",
           "Une longueur d'onde électronique plus courte améliore la résolution",a)
  a=re.sub(r"(?i)\bLa FC attribue au (\w[^;,.]*) (.+)",r"\1 : \2",a)
  a=re.sub(r"(?i)\bLa FC (?:donne|indique|mentionne|précise|rappelle) (?:comme )?","",a)
  a=re.sub(r"(?i)\bselon la FC\b","",a)
  a=re.sub(r"(?i)\bLa FC (?:associe|relie) ","Association : ",a)
  a=re.sub(r"\s+"," ",a).strip(" ;")
  count["clean_answers"]+=1
 c["question"]=q;c["answer"]=a
 if len(a)>140 or len(q)>155 or re.search(r"(?i)quels éléments essentiels|que retenir de|page pdf|tableau à insérer",q+" "+a):
  count["quality_quarantine"]+=1;continue
 clean.append(c)
d["flashcards"]=clean
p.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("CARD_POST_QA",dict(count),"ACTIVE",len(clean))
for x in [c for c in clean if c["chapterId"]=="histo_methodes"][:12]:print(x["question"],"=>",x["answer"][:100])
