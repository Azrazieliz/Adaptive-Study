#!/usr/bin/env python3
"""Final truthful coverage indicators for the existing native course reader."""
import argparse,pathlib,shutil,hashlib,json
p=argparse.ArgumentParser();p.add_argument("--java",required=True);p.add_argument("--gradle",required=True)
a=p.parse_args()
java=pathlib.Path(a.java);s=java.read_text(encoding="utf-8")
def once(old,new,name):
 global s
 n=s.count(old)
 if n!=1:raise AssertionError((name,n,old[:100]))
 s=s.replace(old,new,1)
once('            LinearLayout board=panel(body);\n            heading(board,"UNDERSTAND".equals(guideMode)?',
    '            LinearLayout board=panel(body);\n'
    '            boolean needsManualReview=false;\n'
    '            for(int idx=0;idx<facts.length();idx++){\n'
    '                JSONObject recorded=facts.optJSONObject(idx);\n'
    '                if(recorded!=null&&recorded.optBoolean("requiresManualReview",false)){\n'
    '                    needsManualReview=true;break;\n'
    '                }\n'
    '            }\n'
    '            if(needsManualReview)sub(board,"Notes rattachées aux pages originales, mais vérification scientifique détaillée non terminée.");\n'
    '            heading(board,"UNDERSTAND".equals(guideMode)?',
    'show unreviewed page provenance')
once('                boolean guide=guides!=null&&guides.optJSONObject(id)!=null;\n'
     '                sub(p,subjectName(sid)+" • "+nf+" cartes de révision • "+(guide?"Fiche structurée : couverture variable":"Leçon absente — source à intégrer"));',
    '                JSONObject sourceGuide=obj(guides,id);\n'
    '                JSONArray sourceSections=arr(sourceGuide,"sections");\n'
    '                boolean guide=sourceSections!=null&&sourceSections.length()>0;\n'
    '                sub(p,subjectName(sid)+" • "+nf+" cartes de révision • "+\n'
    '                    (guide?"Leçon et pages originales disponibles":"FC originale consultable • texte pédagogique à compléter"));',
    'avoid claiming Noyau teaching complete')
backup=java.with_name(java.name+".before_coverage_truth_20261113")
if backup.exists():assert backup.read_text(encoding="utf-8")==java.read_text(encoding="utf-8")
else:shutil.copy2(java,backup)
java.write_text(s,encoding="utf-8")
gradle=pathlib.Path(a.gradle);before=gradle.read_text(encoding="utf-8")
assert before.count("versionCode 33611")==1 and before.count("versionName '3.36.11-histo-pilot'")==1
graded=before.replace("versionCode 33611","versionCode 33612").replace("versionName '3.36.11-histo-pilot'","versionName '3.36.12-current-courses'")
gb=gradle.with_name(gradle.name+".before_33612_20261113")
if gb.exists():assert gb.read_text(encoding="utf-8")==before
else:shutil.copy2(gradle,gb)
gradle.write_text(graded,encoding="utf-8")
print(json.dumps({"javaSha256":hashlib.sha256(s.encode("utf-8")).hexdigest(),"versionCode":33612,"versionName":"3.36.12-current-courses","javaWarningForUnreviewedFacts":True,"originalQuestionHistoryRetained":True},ensure_ascii=True))
