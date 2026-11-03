import json,pathlib,re,collections,shutil
r=pathlib.Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets")
p=r/"comprehension_texts.json"
data=json.loads(p.read_text("utf8"))
backup=r/"comprehension_texts_v2_before_polish.json"
if not backup.exists():shutil.copy2(p,backup)
stats=collections.Counter()
# Explicit rewrite of known source-expressed relationships; does not add teaching facts.
fixed={
("histo_sanguin","Tissu sanguin : nature, composition et volume"):(
 "Le sang est un tissu conjonctif spécialisé qui circule dans l'appareil cardiovasculaire, à l'intérieur des vaisseaux. "
 "Sa partie liquide est le plasma, contenant l'albumine, les globulines, des enzymes, des lipides, des glucides, des ions, "
 "des sels minéraux, des vitamines, des gaz dissous et de l'eau. "
 "Les éléments figurés comprennent les globules rouges (hématies ou érythrocytes), les globules blancs (leucocytes), "
 "les plaquettes (thrombocytes) ainsi que les réticulocytes, décrits comme des globules rouges immatures dans des conditions pathologiques. "
 "Chez un adulte de 70 kg, le volume sanguin indiqué est de 5 L, soit environ un quatorzième du poids du corps."),
("biocell_signal2","Transduction par second messager"):(
 "Le signal extracellulaire constitue le premier messager : il s'agit du ligand du récepteur. "
 "La transduction commence lorsque ce ligand interagit avec son récepteur, déclenchant l'activation d'un commutateur moléculaire. "
 "Après cette activation apparaît un second messager, petite molécule intracellulaire qui propage et amplifie la stimulation. "
 "Ce second messager peut être synthétisé par une protéine enzymatique cible ou libéré depuis une réserve intracellulaire."),
("biocell_noyau","Machinerie cellulaire et composition"):(
 "La membrane plasmique délimite la cellule, laquelle contient différents organites remplissant des fonctions particulières. "
 "Dans cette organisation générale, le noyau joue le rôle de centre de contrôle. "
 "Les organites et les protéines constituent la machinerie de la cellule, tandis que les mitochondries produisent de l'énergie sous forme d'ATP. "
 "Les protéines sont citées parmi les principaux produits finis de l'activité cellulaire. "
 "Pour fonctionner, la cellule absorbe des matières premières, recycle une partie importante de ses constituants et utilise de l'énergie, "
 "ce qui s'accompagne de la production de déchets."),
}
# Do not replace if we cannot account for the number of facts preserved.
coverage_requirements={
 ("histo_sanguin","Tissu sanguin : nature, composition et volume"):4,
 ("biocell_signal2","Transduction par second messager"):6,
 ("biocell_noyau","Machinerie cellulaire et composition"):8,
}
for cid,entry in data["chapters"].items():
 for sec in entry.get("sections",[]):
  key=(cid,sec["heading"])
  if key in fixed and len(sec["evidence"])==coverage_requirements[key]:
   sec["paragraphs"]=[fixed[key]]
   stats["hand_reviewed_source_paragraphs"]+=1
  for i,paragraph in enumerate(sec["paragraphs"]):
   original=paragraph
   paragraph=re.sub(r"(?i)\bLa FC (?:montre|schématise|illustre)\s+","L'illustration représente ",paragraph)
   paragraph=re.sub(r"(?i)\bLa FC (?:indique|précise|rappelle|mentionne|affirme|signale)\s+que\s+","",paragraph)
   paragraph=re.sub(r"(?i)\bLa FC (?:distingue|compare)\s+","On distingue ",paragraph)
   paragraph=re.sub(r"(?i)\bLa FC (?:donne|indique|cite|mentionne|rappelle)\s+","On relève ",paragraph)
   paragraph=re.sub(r"(?i)\bLa FC (?:l'associe|les associe)\s+à\s+","les associe à ",paragraph)
   paragraph=re.sub(r"(?i)\bLa FC (?:le décrit|la décrit|les décrit)\s+comme\s+","Il est décrit comme ",paragraph)
   paragraph=re.sub(r"(?i)\b(?:selon|d'après) (?:le schéma|la photo) de la FC\b","d'après l'illustration",paragraph)
   paragraph=re.sub(r"(?i)\b(?:selon|d'après) la FC\b","",paragraph)
   paragraph=re.sub(r"(?i)\bla FC\b","les données de référence",paragraph)
   paragraph=paragraph.replace("Fécondité : L’IVG","L’IVG").replace("Le noyau cellulaire comme centre de contrôle.","Le noyau cellulaire joue le rôle de centre de contrôle.")
   paragraph=paragraph.replace("Le système nerveux central comprend cerveau","Le système nerveux central comprend le cerveau")
   paragraph=paragraph.replace("cerveau à deux hémisphères, tronc cérébral, cervelet et moelle épinière",
                               "cerveau à deux hémisphères, le tronc cérébral, le cervelet et la moelle épinière")
   paragraph=paragraph.replace("il contient albumine et globulines, ainsi que enzymes","il contient de l'albumine, des globulines et des enzymes")
   paragraph=paragraph.replace("Pour sNC","Pour le SNC").replace("Pour iMG","Pour l'IMG")
   paragraph=re.sub(r"\s{2,}"," ",paragraph).strip()
   if paragraph!=original:stats["polished_paragraphs"]+=1
   sec["paragraphs"][i]=paragraph
entry_count=sum(len(x["sections"]) for x in data["chapters"].values())
data["schema"]="native_comprehension_v2_editorial_proof"
data["description"]="Source-linked explanatory prose; all source guide facts retained in evidence. Missing original course PDFs and incomplete source verification remain explicitly identified."
for entry in data["chapters"].values():
 entry["paragraphCount"]=sum(len(sec["paragraphs"]) for sec in entry["sections"])
p.write_text(json.dumps(data,ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("POLISH",dict(stats),"SECTIONS",entry_count,"PARAS",sum(x["paragraphCount"] for x in data["chapters"].values()))
for cid in ("histo_sanguin","histo_nerveux","shs_ivg","biocell_signal2","biocell_noyau"):
 e=data["chapters"][cid];print("SAMPLE",cid,e["sections"][0]["paragraphs"][0][:650])
