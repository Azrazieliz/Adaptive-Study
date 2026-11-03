import json,pathlib
p=pathlib.Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets\study_data.json")
d=json.loads(p.read_text("utf8"))
fixed=[]
for c in d["chapters"]:
 cid=c["id"]
 if c.get("auditStatus")=="NOT_RECEIVED" and cid in d["courseGuides"] and len(d["coursePages"].get(cid,[]))>0:
  c["auditStatus"]="SOURCE_PRESENT_REINDEXED"
  c["auditNote"]="FC source et pages retrouvées ; l'état NOT_RECEIVED historique ne correspond plus à l'inventaire actuel."
  fixed.append(cid)
p.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("FIXED_STALE_MISSING_STATUSES",fixed)
