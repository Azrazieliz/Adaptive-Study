import json,re,pathlib
root=pathlib.Path("D:/AdaptiveStudyRecovery/AdaptiveStudyNative/app/src/main/assets")
data=json.loads((root/"study_data.json").read_text("utf8"))
path=root/"comprehension_texts.json"
obj=json.loads(path.read_text("utf8"))
strategies={
"shs":"Pour raisonner, commencez par définir les notions, puis replacez les idées dans leur contexte historique ou social. Distinguez faits, interprétations, enjeux et conséquences.",
"sp":"Pour comprendre les indicateurs de santé publique, reliez chaque donnée à sa population, sa période, sa définition et ses limites d’interprétation.",
"histo":"Pour reconnaître un tissu, reliez sa localisation, la forme de ses cellules, la matrice, l’organisation et les fonctions qu’il assure.",
"biocell":"Pour comprendre un mécanisme cellulaire, identifiez les éléments impliqués, leur localisation, l’ordre des événements et la conséquence d’une activation ou d’une inhibition.",
"bio":"Reliez structure moléculaire, interactions, conditions, propriétés et conséquences fonctionnelles. Les méthodes décrivent ce qui est réellement observable.",
"chimie":"Reliez les espèces, les charges, les liaisons et les conditions aux propriétés observées. Les règles et équations s’appliquent dans leur domaine de validité.",
"phys":"Identifiez les grandeurs, leurs unités et les conditions des lois. Pour comprendre une situation, sélectionnez la relation qui lie les variables sans apprendre de calcul arbitraire."
}
for cid,chapter in obj["chapters"].items():
 chapter["readingStrategy"]=strategies.get(chapter["subjectId"],"Reliez chaque notion à ses caractéristiques, ses conditions et ses conséquences.")
 if chapter["provenance"]=="SOURCE_GUIDE_DERIVED":
  src=data["courseGuides"].get(cid,{})
  for a,b in zip(chapter["sections"],src.get("sections",[])):
   a["sourcePages"]=sorted({x["page"] for x in b.get("items",[]) if isinstance(x.get("page"),int) and x["page"]>0})
 else:
  for section in chapter["sections"]:section["sourcePages"]=[]
 chapter["courseSourcePresent"]=bool(data["coursePages"].get(cid))
path.write_text(json.dumps(obj,ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("AUGMENTED",path.stat().st_size,"COURSES",len(obj["chapters"]))
