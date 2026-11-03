# -*- coding: utf-8 -*-
"""Make the native workspace self-contained with exact FC page images and approved mind maps.
Do not change image bytes or retrieve copyrighted/exam originals from a public endpoint.
Images copied only from user's own existing signed private APK.
"""
from pathlib import Path
from zipfile import ZipFile
import json,hashlib,collections
R=Path(r"D:\AdaptiveStudyRecovery")
A=R/"AdaptiveStudyNative/app/src/main/assets"
D=json.loads((A/"study_data.json").read_text("utf8"))
source=R/"AdaptiveStudy-NATIVE-v3.33.0-INSTALLABLE.apk"
needed=set()
for pages in D["coursePages"].values():
 needed.update("assets/www/"+p for p in pages)
for ch,m in D["mindMaps"].items():
 if not isinstance(m,dict):continue
 if m.get("path"):needed.add("assets/www/"+m["path"])
 for x in m.get("subMaps",[]):
  if x.get("path"):needed.add("assets/www/"+x["path"])
stats=collections.Counter()
size=0
missing=[]
with ZipFile(source) as z:
 existing=set(z.namelist())
 for path in sorted(needed):
  local=A/"www"/path.removeprefix("assets/www/")
  if local.is_file():
   stats["already_present"]+=1
   continue
  if path not in existing:
   missing.append(path)
   continue
  b=z.read(path)
  local.parent.mkdir(parents=True,exist_ok=True)
  local.write_bytes(b)
  assert hashlib.sha256(local.read_bytes()).digest()==hashlib.sha256(b).digest()
  stats["restored"]+=1
  size+=len(b)
assert not missing,("UNRESTORED",len(missing),missing[:15])
assert all((A/"www"/p.removeprefix("assets/www/")).is_file() for p in needed)
print("CANONICAL_OFFLINE_IMAGES",len(needed),"RESTORED",stats["restored"],
      "ALREADY_PRESENT",stats["already_present"],"MB",round(size/1e6,2))
print("ALL_REFERENCES_RESOLVED",not missing)
