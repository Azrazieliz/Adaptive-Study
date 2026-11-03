from pathlib import Path
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
s=p.read_text("utf8")
a='''        if("EXAM_PDF".equals(screen)&&currentOriginalDocument!=null&&
            "SUJET".equals(s(currentOriginalDocument,"part"))&&originalRunning&&originalStart==0){
            originalStart=SystemClock.elapsedRealtime();
        }
'''
assert a in s
s=s.replace(a,"",1)
for bad in ("EXAM_PDF","original_assessment_catalog.json","original_question_catalog.json",
            "originalExamCatalog","currentOriginalDocument","originalRunning","openExamLibrary"):
 assert bad not in s,bad
p.write_text(s,"utf8")
print("EXAM_PDF_JAVA_REFERENCES_REMOVED")
