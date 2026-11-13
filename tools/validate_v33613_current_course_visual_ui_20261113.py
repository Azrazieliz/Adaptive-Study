#!/usr/bin/env python3
"""Static/read-only regression audit for the current FC source-linked native UI.

Does not certify academic completeness. Never modifies source data or user state.
"""
import collections,hashlib,json,pathlib,re,zipfile
root=pathlib.Path(r'D:\AdaptiveStudyRecovery')
app=root/'AdaptiveStudyNative/app'
a=app/'src/main/assets'
data=json.loads((a/'study_data.json').read_text('utf-8'))
java=(app/'src/main/java/com/azrazieliz/adaptivestudy/MainActivity.java').read_text('utf-8')
gradle=(app/'build.gradle').read_text('utf-8')
inactive={'histo_embryo','biocell_cytosq','biocell_mec_integrine','biocell_dev','biocell_cycle',
'bio_proteines','bio_biomol','chim_atoliais','chim_protons','phys_energie_elec','phys_fluides'}
chapters=[c for c in data['chapters'] if c['id'] not in inactive]
assert len(chapters)==70,(len(chapters),"expected 70 independent existing FCs")
assert len(data['chapters'])==81 and len(set(x['id'] for x in data['chapters']))==81
assert "versionCode 33613" in gradle and "3.36.13-visual-source" in gradle
for anchor in ['NATIVE_SOURCE_GROUNDED_VISUAL_STUDY_V33613','showCurrentSourceVisualOverview("ESSENTIAL")',
    'showCurrentSourceVisualOverview("COMPLETE")','showCurrentSourceVisualOverview("UNDERSTAND")',
    'showFocusedSourceRelationBoard(facts,current)','buildSingleGuideMindMap()',
    'if(generated!=null)','final boolean[] detailLoaded={false}',
    'if(expand&&originalFacts!=null&&!detailLoaded[0])',
    'showReviewedNeuralMechanisms()','showSourceVerifiedVisualBoards("UNDERSTAND")',
    'showSourceVerifiedVisualBoards("COMPLETE")','showSourceVerifiedVisualBoards("ESSENTIAL")']:
 assert anchor in java,anchor
assert java.count('showPreservedMapPlates(mind);')==0
assert java.count('showPreservedMapPlates(original);')==0
assert java.count('showReviewedNeuralMechanisms();')>=1
assert 'private void showFocusedPageStudy()' in java
assert 'private void showPageStudyChooser()' in java
assert 'public void onCreate(' in java
assert 'private void pilotOpenQuiz()' in java
assert "if(!byChapter.containsKey(id)||\"biocell_noyau\".equals(id))continue;" in java
imgs=data['coursePages']['biocell_noyau']
assert len(imgs)==25 and len(set(imgs))==25
for relative in imgs:
 p=a/'www'/relative
 assert p.is_file() and p.stat().st_size>12000
 with p.open('rb') as f:assert f.read(3)==b'\xff\xd8\xff'
mode_active=collections.Counter()
groups=0
facts_count=0
visual_sections=collections.Counter()
for course in chapters:
 cid=course['id']
 guide=data.get('courseGuides',{}).get(cid,{})
 secs=guide.get('sections',[])
 assert isinstance(secs,list)
 if secs:mode_active['coursesWithIndexedGuide']+=1
 else:mode_active['sourcePagesOnly']+=1
 for sec in secs:
  sf=[f for f in sec.get('items',[]) if isinstance(f,dict) and (f.get('value') or f.get('text'))]
  if not sf:continue
  groups+=1;facts_count+=len(sf)
  if len(sf)>1:
   visual_sections[cid]+=1
  if 'question' in (sec.get('title') or '').lower() or 'qroc' in (sec.get('title') or '').lower():
   mode_active['practiceTitleSectionsNeedEditorialQuarantine']+=1
mode_active['coursesWithVisualSourceSection']=len(visual_sections)
mode_active['sourceOnlyOriginalNoyau']=len(data.get('courseGuides',{}).get('biocell_noyau',{}).get('sections',[]))==0
images=sum(len(data['coursePages'][x['id']]) for x in chapters)
assert images==1527
assert mode_active['sourceOnlyOriginalNoyau']
result={
 'kind':'STATIC_NATIVE_REGRESSION_AND_SOURCE_MAP_COVERAGE',
 'version':'3.36.13-visual-source',
 'checksPassed':True,
 'existingIndependentCourses':len(chapters),
 'originalImages':images,
 'NoyauOriginalImages':len(imgs),
 'mindMapPolicy':'ONE_GENERATED_OR_AUTHORED_ACTIVE_MAP_PER_COURSE__ARCHIVAL_PLATES_NOT_SHOWN',
 'oneMapSourceGroups':groups,
 'sourceLinkedFactsAvailable':facts_count,
 'coverage':dict(mode_active),
 'coursesWithSourceComparisonCandidate':len(visual_sections),
 'sectionCountByCourse':dict(visual_sections),
 'sourceDataSha256':hashlib.sha256((a/'study_data.json').read_bytes()).hexdigest(),
 'academicAllOriginalPagesComplete':False,
 'onDeviceAcceptanceVerified':False
}
target=root/'PRESERVATION_20261112_NO_APK_BUILD/V33613_SOURCE_VISUAL_STATIC_QA_20261113.json'
target.write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='sectionCountByCourse'},ensure_ascii=True),flush=True)
