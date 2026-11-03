import pathlib,json,shutil
r=pathlib.Path(r"D:\AdaptiveStudyRecovery")
src=r/"Adaptive-Study/local_instance/private_app/app"
dst=r/"AdaptiveStudyNative/app/src/main/assets/www"
d=json.loads((r/"AdaptiveStudyNative/app/src/main/assets/study_data.json").read_text("utf8"))
missing=[];n=0;size=0
for cid,obj in d["mindMaps"].items():
 for path in [obj.get("path")]+[x.get("path") for x in obj.get("subMaps",[])]:
  if not path:continue
  s=src/path;t=dst/path
  if not s.is_file():missing.append((cid,path));continue
  t.parent.mkdir(parents=True,exist_ok=True)
  if not t.exists() or t.stat().st_size!=s.stat().st_size:shutil.copy2(s,t)
  n+=1;size+=t.stat().st_size
print("RESTORED",n,"MAP_FILES",round(size/1e6,1),"MB","MISSING",len(missing),missing[:10])
assert not missing
