from pathlib import Path
import json
r=Path(r"D:\AdaptiveStudyRecovery")
gradle=r/"AdaptiveStudyNative/app/build.gradle"
s=gradle.read_text("utf8")
assert "versionCode 3320" in s and "3.32.0-native-exam" in s
gradle.write_text(s.replace("versionCode 3320","versionCode 3330").replace("3.32.0-native-exam","3.33.0-native-content"),encoding="utf8")
data=r/"AdaptiveStudyNative/app/src/main/assets/study_data.json"
d=json.loads(data.read_text("utf8"))
if isinstance(d.get("pack"),dict):d["pack"]["version"]="3.33.0-native-content"
data.write_text(json.dumps(d,ensure_ascii=False,separators=(",",":")),encoding="utf8")
old=r/"build_native_v3320.py";script=old.read_text("utf8")
assert 'v3.32.0' in script and "if inf.filename.startswith(\"assets/www/assets/\") and inf.filename not in names:" in script
script=script.replace("v3.32.0","v3.33.0")
script=script.replace(
'if inf.filename.startswith("assets/www/assets/") and inf.filename not in names:',
'''if (inf.filename.startswith("assets/www/assets/")
            and inf.filename not in names
            and not any(excluded in inf.filename.lower() for excluded in (
                "/original_questions/", "/new-course-preview/", "/original_assessments/",
                "/annale_sujet", "/annale_correction", "/qe_sujet", "/qe_correction",
                "/acc_sujet", "/acc_correction", "/qcm_sujet", "/qcm_correction"))
            ):
'''.rstrip())
assert '"/original_questions/"' in script
(r/"build_native_v3330.py").write_text(script,encoding="utf8")
print("PREPARED_ANDROID_3330","CHAPTERS",len(d["chapters"]),"ACTIVE_CARDS",len(d["flashcards"]),
"AUTHORED_PRACTICE",len(d["questions"]))
