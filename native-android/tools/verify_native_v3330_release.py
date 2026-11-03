# -*- coding:utf-8 -*-
from pathlib import Path
from zipfile import ZipFile
import json,collections,hashlib
R=Path(r"D:\AdaptiveStudyRecovery")
APK=R/"AdaptiveStudy-NATIVE-v3.33.0-INSTALLABLE.apk"
assert APK.exists(),str(APK)
with ZipFile(APK) as z:
 names=set(z.namelist())
 needed=["assets/study_data.json","assets/board_catalog.json","assets/comprehension_texts.json",
   "assets/essential_study_selection_v3310.json","assets/complete_source_page_index_v3310.json",
   "assets/expert_comprehension_v3311.json"]
 assert all(n in names for n in needed),[n for n in needed if n not in names]
 d=json.loads(z.read("assets/study_data.json"))
 chapters=d["chapters"];questions=d["questions"];cards=d["flashcards"]
 assert len(chapters)==75 and len(questions)==341 and len(cards)==1904,(len(chapters),len(questions),len(cards))
 sources=set(x for ps in d["coursePages"].values() for x in ps)
 missing_pages=[p for p in sources if "assets/www/"+p not in names]
 maps=d["mindMaps"]
 mp=[p for m in maps.values() for p in ([m.get("path")]+[q.get("path") for q in m.get("subMaps",[])]) if p]
 missing_maps=[p for p in mp if "assets/www/"+p not in names]
 banned=[
 n for n in names if any(x in n.lower() for x in (
 "original_assessment_catalog","original_question_catalog","/original_questions/",
 "/original_assessments/","/new-course-preview/"))
 ]
 # Scans from legacy fallback must not reappear under the source directory either.
 embedded_exam=[
 n for n in names if n.startswith("assets/www/assets/new-course-source/")
 and any(x in n.lower() for x in (
 "/annale","/qe_","/acc_","/qcm_","correction"))
 ]
 bad_q=[q.get("id") for q in questions if q.get("format")=="QCM" and
   (len(q.get("options",[]))!=5 or len(q.get("optionRationales",[]))!=5 or not q.get("correct"))]
 malformed=[c["id"] for c in cards if "Quelle différence existe entre les éléments" in c.get("question","")]
 comp=json.loads(z.read("comprehension_texts.json".join(["assets/",""])))["chapters"]
 assert len(comp)==75
 assert not missing_pages,("MISSING_COURSE_PAGE",missing_pages[:10],len(missing_pages))
 assert not missing_maps,("MISSING_MAP",missing_maps[:10],len(missing_maps))
 assert not banned,("EXAMS_REINTRODUCED",banned[:20],len(banned))
 assert not embedded_exam,("EXAM_PDF_FALLBACK",embedded_exam[:10])
 assert not bad_q,("BAD_AE",bad_q[:20])
 assert not malformed,("MALFORMED_CARDS",malformed)
 print("PASS APK_PACKAGE",APK.name,round(APK.stat().st_size/1e6,2),"MB")
 print("CHAPTERS",len(chapters),"COMP_EXPLANATIONS",len(comp),"CARDS",len(cards),"NEW_PRACTICE",len(questions))
 print("SOURCE_COURSE_IMAGE_REFERENCES",len(sources),"MISSING",len(missing_pages))
 print("ORIGINAL_LEARNING_MAP_IMAGES",len(mp),"MISSING",len(missing_maps))
 print("ORIGINAL_EXAM_PDF_OR_IMAGES_EMBEDDED",len(banned)+len(embedded_exam))
 print("CORRECTION_RATIONALE_ERRORS",len(bad_q),"MALFORMED_LEGACY_PROMPTS",len(malformed))
 print("SHA256",hashlib.sha256(APK.read_bytes()).hexdigest())
