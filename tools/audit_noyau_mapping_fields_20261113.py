import json,pathlib
A=pathlib.Path(r'D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets')
d=json.loads((A/'study_data.json').read_text('utf-8'))
for cid in ['biocell_noyau','chim_atoms','histo_nerveux','histo_muscles1','shs_sante_environnement']:
 print('\nCOURSE',cid)
 for key in ['courseMeta','courseAssets','courseSourceDocuments','sourceVerifiedLessonCoverage','mindMaps']:
  x=d.get(key,{}).get(cid,None)
  print(key,json.dumps(x,ensure_ascii=True)[:2200])
 qs=[q for q in d['questions'] if q.get('chapterId')==cid]
 fs=[x for x in d['flashcards'] if x.get('chapterId')==cid]
 print('QUESTIONS',len(qs),[(x.get('id'),x.get('format')) for x in qs[:4]])
 print('CARDS',len(fs),[(x.get('id'),x.get('studyCardStatus')) for x in fs[:3]])
for name in ['essential_study_selection_v3310.json','complete_source_page_index_v3310.json','board_catalog.json']:
 x=json.loads((A/name).read_text('utf-8'))
 print('ASSET',name,list(x),[(k,type(v).__name__) for k,v in x.items()][:4])
 if 'biocell_noyau' in x.get('courses',{}):print('NOYAU',json.dumps(x['courses']['biocell_noyau'],ensure_ascii=True)[:950])
 if 'biocell_noyau' in x.get('chapters',{}):print('NOYAU_CHAPTERS',json.dumps(x['chapters']['biocell_noyau'],ensure_ascii=True)[:500])
