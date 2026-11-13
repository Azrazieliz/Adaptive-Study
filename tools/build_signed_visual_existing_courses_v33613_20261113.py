#!/usr/bin/env python3
"""Compile, sign, and independently check the existing-course-only Android APK."""
import collections,hashlib,json,os,pathlib,subprocess,sys,zipfile
R=pathlib.Path(r'D:\AdaptiveStudyRecovery')
P=R/'AdaptiveStudyNative'
a=P/'app/src/main/assets'
index=json.loads((a/'complete_source_page_index_v3310.json').read_text('utf-8'))
data=json.loads((a/'study_data.json').read_text('utf-8'))
before=json.loads((a/'study_data.before_original_noyau_20261113.json').read_text('utf-8'))
INACTIVE={'histo_embryo','biocell_cytosq','biocell_mec_integrine','biocell_dev','biocell_cycle'}
NON_ORIGINAL={'bio_proteines','bio_biomol','chim_atoliais','chim_protons','phys_energie_elec','phys_fluides'}
current=[x for x in data['chapters'] if x['id'] not in INACTIVE|NON_ORIGINAL]
assert len(current)==70,len(current)
assert [x['id'] for x in data['chapters']]==[x['id'] for x in before['chapters']]
assert data['questions']==before['questions'] and data['flashcards']==before['flashcards']
for c in current:
 cid=c['id']
 if cid=='biocell_noyau':continue
 assert data['coursePages'][cid]==before['coursePages'][cid],('COURSE_PAGES_CHANGED',cid)
 assert data['courseGuides'][cid]==before['courseGuides'][cid],('COURSE_GUIDE_CHANGED',cid)
assert len(data['coursePages']['biocell_noyau'])==25
original=R/'source_transfer/medisup_original_fc_20261113/FCactu_Noyau_2026-2027_original.pdf'
expected='78c3a7f67e1838835f1e12c367398209f8ccfd0f2ff1e309c4c72af31f9ef79d'
def sha_file(p):
 h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(4194304),b''):h.update(b)
 return h.hexdigest()
assert sha_file(original)==expected
assert data['courseMeta']['biocell_noyau']['isComposite'] is False
assert data['courseSourceDocuments']['biocell_noyau'][0]['sha256']==expected
assert len(index['courses']['biocell_noyau']['pages'])==25
page_assets=sum(len(data['coursePages'][x['id']]) for x in current)
assert page_assets==1527,page_assets
missing=[]
for c in current:
 cid=c['id']
 for rel in data['coursePages'][cid]:
  if not (a/'www'/rel).is_file():missing.append((cid,rel))
assert not missing,missing[:10]
source_java=(P/'app/src/main/java/com/azrazieliz/adaptivestudy/MainActivity.java').read_text('utf-8')
for marker in ['NATIVE_SOURCE_GROUNDED_VISUAL_STUDY_V33613','buildSingleGuideMindMap','showCurrentSourceVisualOverview','CURRENT_FC_SOURCE_PAGE_STUDY_20261113','ALL_COURSE_THREE_MODE_V1_20261113',
    'lessonFocusPage','showFocusedPageStudy','showPageStudyChooser','needsManualReview']:
 assert marker in source_java,marker
gradle=(P/'app/build.gradle').read_text('utf-8')
assert "versionCode 33613" in gradle and "versionName '3.36.13-visual-source'" in gradle
gradle_bin=pathlib.Path.home()/'.gradle/wrapper/dists/gradle-8.13-bin/5xuhj0ry160q40clulazy9h7d/gradle-8.13/bin/gradle.bat'
assert gradle_bin.exists()
env=dict(os.environ);env['JAVA_HOME']=r'C:\Program Files\Android\Android Studio1\jbr';env['ANDROID_HOME']=str(pathlib.Path.home()/'AppData/Local/Android/Sdk')
cmd=[str(gradle_bin),'-p',str(P),':app:assembleRelease','--offline','--no-daemon','--console=plain']
print('NATIVE_VISUAL_SOURCE_PREBUILD_QA',json.dumps({'version':33613,'existingCourses':len(current),'sourcePagesVerified':page_assets,
    'questionsUnmodified':True,'originalNoyauPages':25,'sourceIndexPages':len(index['courses']['biocell_noyau']['pages'])}),flush=True)
res=subprocess.run(cmd,capture_output=True,text=True,errors='replace',timeout=900,env=env)
print('GRADLE',json.dumps({'exit':res.returncode,'stdoutTail':res.stdout[-3000:],'stderrTail':res.stderr[-1500:]},ensure_ascii=True),flush=True)
if res.returncode:sys.exit(res.returncode)
unsigned=P/'app/build/outputs/apk/release/app-release-unsigned.apk'
assert unsigned.is_file() and unsigned.stat().st_size>200000000
sdk=pathlib.Path.home()/'AppData/Local/Android/Sdk/build-tools/35.0.1'
signer=sdk/'apksigner.bat';key=pathlib.Path.home()/'.android/debug.keystore'
assert signer.is_file() and key.is_file()
target=R/'AdaptiveStudy-NATIVE-v3.36.12-EXISTING-COURSES-PREVIEW.apk'
if target.exists():raise RuntimeError('TARGET_ALREADY_EXISTS_DO_NOT_OVERWRITE')
args=[str(signer),'sign','--ks',str(key),'--ks-key-alias','androiddebugkey',
      '--ks-pass','pass:android','--key-pass','pass:android','--out',str(target),str(unsigned)]
sign=subprocess.run(args,capture_output=True,text=True,errors='replace',timeout=300,env=env)
print('SIGN',sign.returncode,sign.stderr[-1200:],flush=True)
assert sign.returncode==0
verified=subprocess.run([str(signer),'verify','--verbose',str(target)],
        capture_output=True,text=True,errors='replace',timeout=150,env=env)
assert verified.returncode==0,(verified.stdout[-900:],verified.stderr[-900:])
with zipfile.ZipFile(target) as zip:
 names=set(zip.namelist())
 required=['assets/study_data.json','assets/complete_source_page_index_v3310.json',
   'assets/www/assets/new-course-source/biocell_noyau/fc-1.pdf',
   'assets/www/assets/new-course-pages/biocell_noyau/fc-1/0001.jpg',
   'assets/www/assets/new-course-pages/biocell_noyau/fc-1/0025.jpg',
   'assets/pilot_histo_nerveux_v1.json']
 assert all(p in names for p in required),[p for p in required if p not in names]
 assert hashlib.sha256(zip.read('assets/www/assets/new-course-source/biocell_noyau/fc-1.pdf')).hexdigest()==expected
 packaged=json.loads(zip.read('assets/study_data.json'))
 assert len(packaged['coursePages']['biocell_noyau'])==25
 assert len(packaged['chapters'])==81
 assert packaged['questions']==data['questions'] and packaged['flashcards']==data['flashcards']
 assert zip.read('assets/complete_source_page_index_v3310.json')==(a/'complete_source_page_index_v3310.json').read_bytes()
 actual_files=[f"assets/www/{page}" for page in packaged['coursePages']['biocell_noyau']]
 assert all(p in names for p in actual_files)
report={
 'status':'SIGNED_BUILD_FILE_VERIFIED_NO_DEVICE_ACCEPTANCE_YET','version':'3.36.13-visual-source',
 'package':'com.azrazieliz.adaptivestudy.preview','existingGenuineCourses':len(current),
 'hiddenDerivedNonStandalone':sorted(NON_ORIGINAL),'originalMediaPagesVerified':page_assets,
 'NoyauOriginalSourcePages':25,'NoyauOriginalSourceHash':expected,
 'preservedPriorQuestionIds':True,'preservedPriorFlashcardIds':True,
 'signedApk':str(target),'sizeBytes':target.stat().st_size,'sha256':sha_file(target),
 'signatureVerified':True,'academicallyCompleteAllPages':False,
 'priorStudyHistoryExpectedToRemainSeparatePackage':True
}
out=R/'PRESERVATION_20261112_NO_APK_BUILD/V33613_EXISTING_COURSES_SIGNED_APK_QA_20261113.json'
out.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print('SIGNED_BUILD_QA',json.dumps(report,ensure_ascii=True),flush=True)
