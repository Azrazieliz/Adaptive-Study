#!/usr/bin/env python3
"""Checkpoint source-only repair of existing Adaptive Study FCs to private corpus branch.

Do not commit credentials, browser cookies, session tokens, or APK binaries.
"""
import hashlib,json,pathlib,shutil,subprocess,sys
R=pathlib.Path(r'D:\AdaptiveStudyRecovery')
P=R/'AdaptiveStudyNative'
A=P/'app/src/main/assets'
W=R/'THREE_MODE_WORKTREE_20261113'
BRANCH='work/three-mode-visual-allcourses-20261113'
REL=pathlib.Path('checkpoints/2026-11-13/existing-courses-v33612')
def git(*args,check=True,timeout=150):
 p=subprocess.run(['git','-C',str(W),*args],capture_output=True,text=True,errors='replace',timeout=timeout)
 if check and p.returncode:raise RuntimeError("git "+str(args)+" exit "+str(p.returncode)+" "+p.stderr[-1400:])
 return p
assert (W/'.git').exists() or (W/'.git').is_file(),'Private source worktree missing'
assert git('rev-parse','--abbrev-ref','HEAD').stdout.strip()==BRANCH,'Unexpected branch'
st=git('status','--porcelain').stdout
assert st.strip()=='',"Preserve uncommitted existing work, not overwriting: "+st[:800]
git('fetch','origin',BRANCH,timeout=200)
git('merge','--ff-only','FETCH_HEAD',timeout=120)
dest=W/REL
dest.mkdir(parents=True,exist_ok=True)
files={
 "MainActivity.java":P/'app/src/main/java/com/azrazieliz/adaptivestudy/MainActivity.java',
 "build.gradle":P/'app/build.gradle',
 "study_data.json":A/'study_data.json',
 "complete_source_page_index_v3310.json":A/'complete_source_page_index_v3310.json',
 "essential_study_selection_v3310.json":A/'essential_study_selection_v3310.json',
 "expert_comprehension_v3311.json":A/'expert_comprehension_v3311.json',
 "comprehension_texts.json":A/'comprehension_texts.json',
 "board_catalog.json":A/'board_catalog.json',
 "EXISTING_70_COURSE_NATIVE_SOURCE_INDEX_AUDIT_20261113.json":
    R/'PRESERVATION_20261112_NO_APK_BUILD/EXISTING_70_COURSE_NATIVE_SOURCE_INDEX_AUDIT_20261113.json',
 "FCactu_Noyau_2026-2027_original.pdf":
    R/'source_transfer/medisup_original_fc_20261113/FCactu_Noyau_2026-2027_original.pdf',
}
for name,source in files.items():
 assert source.is_file(),str(source)
 shutil.copy2(source,dest/name)
page_root=A/'www/assets/new-course-pages/biocell_noyau/fc-1'
copy_root=dest/'original-noyau-25-pages'
copy_root.mkdir(parents=True,exist_ok=True)
images=sorted(page_root.glob('*.jpg'))
assert len(images)==25
for file in images:shutil.copy2(file,copy_root/file.name)
meta={
 "courseScope":"ONLY EXISTING COURSES",
 "compiledVersion":"3.36.12-current-courses",
 "independentActiveCourseCount":70,
 "sourceImageCount":1527,
 "currentOriginalNoyauPages":25,
 "originalNoyauPdfSha256":"78c3a7f67e1838835f1e12c367398209f8ccfd0f2ff1e309c4c72af31f9ef79d",
 "sourceFactsReindexedWithoutNewAuthoring":763,
 "questionIdsAndFlashcardsPreserved":True,
 "academicAllPagesCompleted":False,
 "sourceDocsPrivate":True,
 "credentialsStored":False,
 "APKNotCommittedBecauseLarge":True
}
(dest/'CURRENT_COURSE_CHECKPOINT_STATUS.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
git('add','--',REL.as_posix(),timeout=180)
status=git('status','--short').stdout
assert 'study_data.json' in status and 'FCactu_Noyau' in status,status[-1000:]
git('commit','-m','Checkpoint current original FCs: Noyau 25 pages and 70-course study reader v3.36.12',timeout=180)
push=git('push','origin','HEAD:'+BRANCH,check=False,timeout=300)
print(json.dumps({'commitSha':git('rev-parse','HEAD').stdout.strip(),
'branch':BRANCH,'pushSucceeded':push.returncode==0,
'pushStderrTail':push.stderr[-1200:] if push.returncode else '',
'trackedFiles':len(files)+len(images)+1,
'originalNoyauImages':len(images),'credentialsExcluded':True},ensure_ascii=True),flush=True)
if push.returncode:sys.exit(push.returncode)
