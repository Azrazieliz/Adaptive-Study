import pathlib,json,collections,statistics,hashlib,sys,re
R=pathlib.Path(r'D:\AdaptiveStudyRecovery');A=R/'AdaptiveStudyNative/app/src/main/assets'
d=json.loads((A/'study_data.json').read_text(encoding='utf-8'))
cover=json.loads((A/'complete_source_page_index_v3310.json').read_text(encoding='utf-8'))
essen=json.loads((A/'essential_study_selection_v3310.json').read_text(encoding='utf-8'))
ex=json.loads((A/'expert_comprehension_v3311.json').read_text(encoding='utf-8'))['courses']
rows=[]
for c in d['chapters']:
 id=c['id'];pg=d['coursePages'].get(id,[]);g=d['courseGuides'].get(id,{});facts=[x for s in g.get('sections',[]) for x in s.get('items',[])];fp={x.get('page') for x in facts if isinstance(x.get('page'),int)}
 entry=cover.get('courses',{}).get(id,{})
 epages=entry.get('pages',{})
 cnt=sum(len(v.get('facts',[])) for v in epages.values() if isinstance(v,dict))
 sec=ex.get(id,{}).get('sections',[]);expert_pages={p for s in sec for p in s.get('sourcePages',[]) if isinstance(p,int)}
 rows.append({'id':id,'pages':len(pg),'facts':len(facts),'guidePages':len(fp),'indexedPages':sum(bool(v.get('facts')) for v in epages.values() if isinstance(v,dict)),'indexedFacts':cnt,'expertSections':len(sec),'expertPages':len(expert_pages),'essentialIndices':len(essen.get('courses',{}).get(id,{}).get('indices',[]))})
print('SCHEMA',json.dumps({'complete':{k:str(type(v).__name__)+':'+str(len(v)) for k,v in cover.items()},'essential':{k:str(type(v).__name__)+':'+str(len(v)) for k,v in essen.items()}},ensure_ascii=True))
print('SUMMARY',json.dumps({'courseRecords':len(rows),'pages':sum(v['pages'] for v in rows),'facts':sum(v['facts'] for v in rows),'indexedPages':sum(v['indexedPages'] for v in rows),'indexedFacts':sum(v['indexedFacts'] for v in rows),'expertSections':sum(v['expertSections'] for v in rows),'coursesWithMissingSource':[r['id'] for r in rows if not r['pages']],'coursesWithLessThanHalfIndexed':[r for r in rows if r['pages']>0 and r['indexedPages']*2<r['pages']]},ensure_ascii=True)[:12000])
print('SELECTED',json.dumps([r for r in rows if r['id'] in ['histo_nerveux','biocell_noyau','histo_muscles1','shs_sante_environnement','chim_atoms','bio_aa','bio_proteines','bio_biomol','chim_protons']],ensure_ascii=True))
for id in ['histo_nerveux','biocell_noyau','histo_muscles1']:
 print('PAGE_INDEX_SAMPLE',id,json.dumps(cover.get('courses',{}).get(id,{}),ensure_ascii=True)[:1800])
print('FITZ_ATTEMPT')
try:
 import fitz
 print('FITZ_VERSION',fitz.version)
 for name in ['FCactu_Noyau_2026-2027_original.pdf','FC_Actu_13_Secret_professionnel_2026-2027_original.pdf']:
  p=R/'source_transfer/medisup_original_fc_20261113'/name
  pdf=fitz.open(str(p))
  lengths=[len(page.get_text().strip()) for page in pdf]
  print('PDF',name,'pages',pdf.page_count,'textPageCount',sum(x>30 for x in lengths),'lengths',lengths[:45],'sha',hashlib.sha256(p.read_bytes()).hexdigest())
except Exception as e:print('FITZ_ERROR',type(e).__name__,str(e)[:800])
