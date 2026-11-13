import pathlib,subprocess,shutil,hashlib,json
R=pathlib.Path(r'D:\AdaptiveStudyRecovery')
origin=R/'PRIVATE_GITHUB_BACKUP_20261113'
work=R/'THREE_MODE_WORKTREE_20261113'
branch='work/three-mode-visual-allcourses-20261113'
rel=pathlib.Path('checkpoints/2026-11-13/three-mode-all-courses')
source=R/'AdaptiveStudyNative/app/src/main/java/com/azrazieliz/adaptivestudy/MainActivity.java'
manifest=R/'PRESERVATION_20261112_NO_APK_BUILD/THREE_MODE_ALL_COURSES_COVERAGE_20261113.json'
assert source.is_file() and manifest.is_file()
def git(*args,timeout=100,check=True,folder=origin):
 p=subprocess.run(['git','-C',str(folder),*args],capture_output=True,text=True,encoding='utf-8',errors='replace',timeout=timeout)
 if check and p.returncode:raise RuntimeError('git '+str(args)+' failed '+p.stderr[-1000:])
 return p
git('fetch','origin','backup/academic-recovery-20261113',timeout=150)
if not work.exists():
 p=git('worktree','add','--no-checkout','-b',branch,str(work),'FETCH_HEAD',timeout=120)
else:
 assert work.is_dir()
 assert git('rev-parse','--abbrev-ref','HEAD',folder=work).stdout.strip()==branch
git('sparse-checkout','init','--cone',folder=work)
git('sparse-checkout','set',str(rel).replace('\\','/'),folder=work)
folder=work/rel
folder.mkdir(parents=True,exist_ok=True)
shutil.copy2(source,folder/'MainActivity.java')
shutil.copy2(manifest,folder/'THREE_MODE_ALL_COURSES_COVERAGE_20261113.json')
for filename in ['patch_native_three_modes_visual_review_20261113.py','patch_three_mode_navigation_polish_20261113.py','audit_three_mode_source_coverage_20261113.py']:
 p=R/filename
 if p.exists():shutil.copy2(p,folder/filename)
sha=hashlib.sha256(source.read_bytes()).hexdigest()
report=json.loads(manifest.read_text('utf-8'))
checkpoint={'state':'COMPILED_NOT_BUILT_OR_INSTALLED','sourceSHA256':sha,
 'datasetUnchangedSHA256':'02f4ffb2c53cc2a42c6bd7f2cbfddfc85a4ec6a9d430c6131fdff9af6876807a',
 'courses':report['summary']['activeOriginalCoursesPreserved'],
 'visualBoardsReviewed':report['summary']['verifiedVisualBoards'],
 'visualBoardCourseCoverage':report['summary']['coursesWithSourceVerifiedVisualBoards'],
 'originalIndependentFCMappingPending':report['summary']['originalCourseIdsRequiringSourceRecovery'],
 'editorialAllPagesComplete':False,
 'notes':'Native routing, page-verified visuals and separation of assessment from lessons compiled. Existing source PDFs and private study JSON untouched. Requires comprehensive page authoring and device acceptance.'}
(folder/'NATIVE_THREE_MODE_CHECKPOINT.json').write_text(json.dumps(checkpoint,ensure_ascii=False,indent=2),encoding='utf-8')
git('add','--',str(rel).replace('\\','/'),folder=work)
status=git('status','--short',folder=work).stdout
assert 'MainActivity.java' in status and 'THREE_MODE_ALL_COURSES_COVERAGE' in status
commit=git('commit','-m','Checkpoint source-verified three-mode native reader and per-course academic gaps',folder=work,timeout=90)
push=git('push','--set-upstream','origin',branch,folder=work,timeout=150,check=False)
print(json.dumps({'branch':branch,'commit':git('rev-parse','HEAD',folder=work).stdout.strip(),
'pushSucceeded':push.returncode==0,'pushErrorTail':push.stderr[-800:] if push.returncode else '',
'javaSha256':sha,'manifests':1,'sourceIntegrityPreserved':True,'checkpointPath':str(folder)},ensure_ascii=True),flush=True)
if push.returncode:raise SystemExit(push.returncode)
