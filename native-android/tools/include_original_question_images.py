import json,pathlib,shutil,os,collections
r=pathlib.Path(r"D:\AdaptiveStudyRecovery")
d=json.loads((r/"AdaptiveStudyNative/app/src/main/assets/original_question_catalog.json").read_text("utf8"))
source=r/"Adaptive-Study/local_instance/private_app/app"
dest=r/"AdaptiveStudyNative/app/src/main/assets/www"
paths={v for q in d["items"] for v in q["questionImages"]+q["correctionImages"]}
missing=[];total=0
for path in sorted(paths):
 sp=source/path
 dp=dest/path
 if not sp.is_file():missing.append(str(sp));continue
 dp.parent.mkdir(parents=True,exist_ok=True)
 if not dp.exists() or dp.stat().st_size!=sp.stat().st_size:shutil.copy2(sp,dp)
 total+=dp.stat().st_size
print("SOURCE_QUESTION_IMAGES",len(paths),"MISSING",len(missing),"TOTAL_MB",round(total/1e6,1),"FIRST_MISSING",missing[:7])
assert not missing
