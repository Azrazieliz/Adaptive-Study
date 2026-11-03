import json,pathlib,collections,zipfile
r=pathlib.Path(r"D:\AdaptiveStudyRecovery")
s=(r/"Adaptive-Study/local_instance/private_app/app/original_corpus.js").read_text("utf8")
a=s.index("window.ORIGINAL_CORPUS = ")+len("window.ORIGINAL_CORPUS = ")
d=json.loads(s[a:].strip().rstrip(";"))
z=zipfile.ZipFile(r/"AdaptiveStudy-NATIVE-v3.30.0-INSTALLABLE.apk");names=set(z.namelist())
needed={i for q in d for i in q.get("questionImages",[])+q.get("correctionImages",[])}
miss=[i for i in needed if "assets/www/"+i not in names]
print("CATALOG",len(d),"COURSES",len({x["chapterId"] for x in d}),"IMAGE_PATHS",len(needed),"MISSING_ASSETS",len(miss),"EX",miss[:5])
keep=[]
for x in d:
 if not x.get("questionImages") or not x.get("correctionImages"):continue
 keep.append({k:x.get(k) for k in ("id","chapterId","subjectType","number","sourceType","subjectName","subjectPages","correctionPages","questionImages","correctionImages","pagePairing","rawPdfSubject","rawPdfCorrection")})
out=r/"AdaptiveStudyNative/app/src/main/assets/original_question_catalog.json"
out.write_text(json.dumps({"schema":"original_image_questions_v1","items":keep},ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("OUTPUT",out.stat().st_size)
