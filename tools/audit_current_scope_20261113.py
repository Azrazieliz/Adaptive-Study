import pathlib,json
R=pathlib.Path(r'D:\AdaptiveStudyRecovery')
base=R/'AdaptiveStudyNative/app/src/main/assets'
names=['study_data.json','source_repairs_20261108.json','expert_comprehension_v3311.json','comprehension_texts.json','academic_visuals_verified_20261112.json','pilot_histo_nerveux_v1.json']
def view(v,depth=0):
 if isinstance(v,dict):return {'kind':'object','size':len(v),'keys':list(v)[:32],'examples':{k:view(v[k],depth+1) for k in list(v)[:3]}} if depth<2 else {'kind':'object','keys':list(v)[:14]}
 if isinstance(v,list):return {'kind':'array','len':len(v),'sample':view(v[0],depth+1) if v and depth<2 else None}
 return {'type':type(v).__name__,'sample':str(v)[:125]}
print('FILES')
for n in names:
 p=base/n
 if p.exists():
  d=json.loads(p.read_text('utf-8'))
  print(n,p.stat().st_size,json.dumps(view(d),ensure_ascii=True)[:1500])
d=json.loads((base/'study_data.json').read_text('utf-8'))
chs=d.get('chapters',[])
print('DATA_COUNTS',json.dumps({k:(len(v) if hasattr(v,'__len__') else 'n') for k,v in d.items()},ensure_ascii=True)[:5000])
for cid in ['histo_nerveux','histo_muscles1','biocell_noyau','shs_ethique_hist','phys_energies','chim_atoms','bio_aa','shs_sante_environnement']:
 c=next((c for c in chs if c['id']==cid),{})
 print('COURSE',cid,'record',json.dumps(c,ensure_ascii=True)[:500],'guide',json.dumps(d.get('courseGuides',{}).get(cid,{}),ensure_ascii=True)[:1600],'pages',json.dumps(d.get('coursePages',{}).get(cid,[])[:2],ensure_ascii=True)[:600])
print('ASSETS_COUNT',len(list(base.iterdir())))
for x in sorted(base.iterdir()):
 if x.is_file() and (x.name.endswith('.json') or 'course' in x.name.lower()):print('ASSET',x.name,x.stat().st_size)
root=R/'source_transfer'
print('SOURCES_DIRS')
for p in [root,root/'salvaged_pdfs',R/'PRIVATE_ACADEMIC_VISUALS_20261112',R/'PRESERVATION_20261112_NO_APK_BUILD']:
 if p.is_dir():
  fs=list(p.iterdir());print(str(p),len(fs),[x.name for x in fs[:18]])
