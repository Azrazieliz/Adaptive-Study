import pathlib,json,collections,re,copy,hashlib
r=pathlib.Path(r"D:\AdaptiveStudyRecovery")
root=r/"AdaptiveStudyNative/app/src/main/assets"
p=root/"study_data.json"
d=json.loads(p.read_text("utf8"))
assert len(d["questions"])==0,"Do not overwrite an active exam bank"
old=json.loads((r/"generated_questions_quarantined_20261030.json").read_text("utf8"))
allow={
"MANUAL_FC_IMAGE_VERIFIED",
"SOURCE_FORMULA_LINKED_DERIVED",
"FC_FORMULA_LINKED_NEW_EXAM_MODEL",
"EDITORIAL_VISUALLY_VERIFIED_FC",
"EDITORIAL_AE_EXAM_STYLE",
"EDITORIAL_AE_SOURCE_LINKED",
"PDF_TOPIC_AE_EDITORIAL",
"MANUAL_SOURCE_SHS_BOARD",
"SHS_COMPLETE_BOARD_VISUALLY_VERIFIED",
}
good=[];quarantine=[];reasons=collections.Counter()
for item in old:
 if item.get("provenance") not in allow:continue
 q=copy.deepcopy(item)
 f=q.get("format","")
 if f=="QCM":
  opts=q.get("options",[]);key=q.get("correct",[])
  if len(opts)!=5 or not key or len(set(key))!=len(key) or any(not isinstance(i,int) or i<0 or i>=5 for i in key):
   reasons["INVALID_KEY"]+=1;quarantine.append(q);continue
  if any(len(v)<12 for v in opts) or any(len(v)>240 for v in opts):
   reasons["OPTION_LENGTH"]+=1;quarantine.append(q);continue
  if re.search(r"(0[.,]2 mm (?:correspond|équivaut)|conversion|le cours (?:indique|précise)|la FC)",q.get("stem",""),re.I):
   reasons["TRIVIAL_OR_EDITORIAL"]+=1;quarantine.append(q);continue
  q["stem"]=re.sub(r"(?i)dans la FC|selon la FC|du cours","",q["stem"]).strip()
  # Explanation and per-proposition feedback already in authored datasets.
  if len(q.get("optionRationales",[]))!=5:
   reasons["MISSING_OPTION_RATIONALES"]+=1;quarantine.append(q);continue
 elif f=="QROC":
  if len(q.get("expectedPoints",[]))<3:
   reasons["SHORT_QROC"]+=1;quarantine.append(q);continue
  q["strictAll"]=True
 else:
  reasons["BAD_FORMAT"]+=1;quarantine.append(q);continue
 q["provenanceCategory"]="NEW_EXAM_STYLE_PRACTICE_FROM_SOURCE__NOT_ORIGINAL_QE"
 q["assessmentStatus"]="EDITORIALLY_SELECTED_FROM_PRIOR_SOURCE_GUIDE_BANK__NOT_COMPLETE_ANNAL_CERTIFIED"
 q["displaySourceMark"]=False
 good.append(q)
d["questions"]=good
p.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":")),encoding="utf8")
(root/"practice_source_provenance.json").write_text(json.dumps({"status":"CURATED_NEW_PRACTICE__NOT_AUTHENTIC_ANNAL","activeCount":len(good),
  "excludedCounts":dict(reasons),"selectedProvenance":sorted(allow),"questions":[{"id":x["id"],"provenance":x["provenance"],
    "source":x.get("source"),"assessmentStatus":x.get("assessmentStatus")} for x in good]},ensure_ascii=False,separators=(",",":")),encoding="utf8")
print("NEW_PRACTICE",len(good),"SUBJECT",dict(collections.Counter(x["subjectId"] for x in good)),"FORMATS",dict(collections.Counter(x["format"] for x in good)),"SKIPPED",dict(reasons))
for x in good[:2]:print("EX",x["stem"][:140])
