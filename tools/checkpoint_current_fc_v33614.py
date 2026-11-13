#!/usr/bin/env python3
"""Commit the signed-build source and QA of current FCs to their private continuation repo.

The original PDFs, previous release APKs, study progress, and private browser
sessions are not altered or committed.
"""
import hashlib,json,pathlib,shutil,subprocess
R=pathlib.Path(r'D:\AdaptiveStudyRecovery')
W=R/'THREE_MODE_WORKTREE_20261113'
APP=R/'AdaptiveStudyNative'
BRANCH="work/three-mode-visual-allcourses-20261113"
REL=pathlib.Path('checkpoints/2026-11-13/existing-courses-v33614')
def git(*args,check=True,timeout=180):
 p=subprocess.run(['git','-C',str(W),*args],capture_output=True,text=True,errors='replace',timeout=timeout)
 if check and p.returncode:raise RuntimeError(str(args)+" failed: "+p.stderr[-1300:])
 return p
assert (W/'.git').exists() or (W/'.git').is_file()
assert git('rev-parse','--abbrev-ref','HEAD').stdout.strip()==BRANCH
assert not git('status','--porcelain').stdout.strip(),"Other pending repository modifications"
git('fetch','origin',BRANCH,timeout=240)
git('merge','--ff-only','FETCH_HEAD',timeout=120)
git('sparse-checkout','add',REL.as_posix(),timeout=120)
folder=W/REL
folder.mkdir(parents=True,exist_ok=True)
data={
"MainActivity.java":APP/'app/src/main/java/com/azrazieliz/adaptivestudy/MainActivity.java',
"build.gradle":APP/'app/build.gradle',
"V33614_EXISTING_COURSES_SIGNED_APK_QA_20261113.json":
  R/'PRESERVATION_20261112_NO_APK_BUILD/V33614_EXISTING_COURSES_SIGNED_APK_QA_20261113.json',
"V33613_SOURCE_VISUAL_STATIC_QA_20261113.json":
  R/'PRESERVATION_20261112_NO_APK_BUILD/V33613_SOURCE_VISUAL_STATIC_QA_20261113.json',
"EXISTING_70_COURSE_NATIVE_SOURCE_INDEX_AUDIT_20261113.json":
  R/'PRESERVATION_20261112_NO_APK_BUILD/EXISTING_70_COURSE_NATIVE_SOURCE_INDEX_AUDIT_20261113.json"
}
for label,src in data.items():
 assert src.is_file(),str(src)
 shutil.copy2(src,folder/label)
signature=json.loads((folder/'V33614_EXISTING_COURSES_SIGNED_APK_QA_20261113.json').read_text('utf-8'))
assert signature["version"]=="3.36.14-visual-current-fc"
assert signature["signatureVerified"]
assert signature["originalMediaPagesVerified"]==1527
assert signature["NoyauOriginalSourcePages"]==25
report={
 "checkpoint":"ASTERION_ADAPTIVE_STUDY_EXISTING_FC_VISUAL_20261113",
 "state":"SOURCE_AND_SIGNED_APK_VERIFIED__PHONE_INSTALL_NOT_ACCEPTED",
 "version":signature["version"],
 "sourceJavaSHA256":hashlib.sha256((folder/'MainActivity.java').read_bytes()).hexdigest(),
 "apk":signature["signedApk"],
 "apkSHA256":signature["sha256"],
 "sourceDataCheckpoint":"../existing-courses-v33612/study_data.json",
 "originalNoyauCheckpoint":"../existing-courses-v33612/FCactu_Noyau_2026-2027_original.pdf",
 "existingIndependentCourseCount":70,
 "originalSourcePageImages":1527,
 "sourceOnlyNoReviewedText":["biocell_noyau"],
 "newCoursesImported":0,
 "questionAndFlashcardIdsUnmodified":True,
 "oneGeneratedOrAuthoredMapPerAvailableGuide":True,
 "questionPracticeOnlyInQuestionMode":True,
 "sourceAlignedEssentialOnly":True,
 "academicPageCompletenessCertified":False,
 "phoneOnDeviceAcceptanceVerified":False,
 "browserCredentialsPreservedLocally":True,
 "credentialsCommitted":False
}
(folder/'CHECKPOINT_STATUS.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
git('add','--sparse','--',REL.as_posix())
assert 'MainActivity.java' in git('status','--short').stdout
git('commit','-m','Checkpoint signed v3.36.14 original-FC visual reader, essential selection and Questions-only routes')
push=git('push','origin','HEAD:'+BRANCH,check=False,timeout=260)
print(json.dumps({"branch":BRANCH,"commit":git('rev-parse','HEAD').stdout.strip(),
"privatePushVerified":push.returncode==0,"commitFiles":list(data)+["CHECKPOINT_STATUS.json"],
"apkSHA256":signature["sha256"],"stagingOnly":True,"pushError":push.stderr[-1000:] if push.returncode else ""},ensure_ascii=True),flush=True)
if push.returncode:raise SystemExit(push.returncode)
