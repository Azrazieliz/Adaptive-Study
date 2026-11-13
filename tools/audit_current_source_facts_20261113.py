import pathlib,json,collections,statistics,re,sys,hashlib,subprocess
R=pathlib.Path(r'D:\AdaptiveStudyRecovery');A=R/'AdaptiveStudyNative/app/src/main/assets';d=json.loads((A/'study_data.json').read_text('utf-8'))
chap=d['chapters'];ids=[c['id'] for c in chap];ex=json.loads((A/'expert_comprehension_v3311.json').read_text('utf-8'))['courses'];texts=json.loads((A/'comprehension_texts.json').read_text('utf-8'))['chapters']
rows=[]
for c in chap:
 id=c['id'];guide=d['courseGuides'].get(id,{});pages=d['coursePages'].get(id,[]);items=[i for sec in guide.get('sections',[]) for i in sec.get('items',[])];fpages=set(i.get('page') for i in items if isinstance(i.get('page'),int));adv=ex.get(id,{});tt=texts.get(id,{})
 rows.append({'id':id,'n':len(pages),'facts':len(items),'fact_pages':len(fpages),'page_num_missing':len(set(range(2,len(pages)+1))-fpages),'expert_sections':len(adv.get('sections',[])),'expert_fields':list(adv),'comprehension_sections':len(tt.get('sections',[])),'source_present':bool(d.get('courseSourceDocuments',{}).get(id)),'source_verified':bool(d.get('sourceVerifiedLessonCoverage',{}).get(id)),'course_pages_blank':not pages,'audit':c.get('auditStatus')})
print('SUMMARY',json.dumps({'chapters':len(rows),'facts':sum(r['facts'] for r in rows),'pages':sum(r['n'] for r in rows),'fact_pages':sum(r['fact_pages'] for r in rows),'courses_no_facts':[r['id'] for r in rows if not r['facts']],'courses_facts_lt_half_pages':[r for r in rows if r['n']>0 and r['fact_pages']<(r['n']/2)][:18],'total_missing_pages':sum(r['page_num_missing'] for r in rows)},ensure_ascii=True)[:9500])
print('ALL_COURSE_ROWS',json.dumps(rows,ensure_ascii=True)[:11000])
for id in ['histo_nerveux','biocell_noyau','histo_muscles1','shs_ethique_hist']:
 print('EXPERT_SAMPLE',id,json.dumps(ex.get(id,{}),ensure_ascii=True)[:2500])
 print('COMPR_SAMPLE',id,json.dumps(texts.get(id,{}),ensure_ascii=True)[:2500])
print('PYTHON_TOOLS',subprocess.run(['where','python'],capture_output=True,text=True).stdout[:800])
print('PDF_MODULES',[(name,__import__('importlib').util.find_spec(name) is not None) for name in ('fitz','pypdf','PyPDF2')])
