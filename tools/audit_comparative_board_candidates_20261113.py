import json,pathlib,collections,re
a=pathlib.Path(r'D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\assets')
d=json.loads((a/'study_data.json').read_text(encoding='utf-8'))
ids={'histo_nerveux','histo_muscles1','bio_repliement','chim_liaison','phys_electro','sp_financement','shs_ethique_hist','biocell_membrane'}
tot=collections.Counter();interesting=[]
for c in d['chapters']:
 cid=c['id'];guide=d['courseGuides'].get(cid,{})
 for s in guide.get('sections',[]):
  labels=collections.Counter(str(f.get('label','')).lower().strip() for f in s.get('items',[]))
  repeat=[(k,v) for k,v in labels.items() if k and v>=2]
  if len(repeat)>=1:tot['groups_with_repeated_facts']+=1;interesting.append({'cid':cid,'title':s.get('title'),'repeat':repeat[:4]})
  if re.search('étape|phase|cascade|chronolog|processus|mécanisme|cycle|transformation|états|voies',s.get('title',''),re.I):tot['mechanism_groups']+=1
  for f in s.get('items',[]):
   val=str(f.get('value') or f.get('text') or '')
   if re.match(r'^\s*[+-]?\d+(?:[.,]\d+)?\s*(?:%|mm|µm|nm|kg|mL|L|ms|s|h|ans|m/s|g)\s*$',val):tot['simple_numeric']+=1
 if cid in ids:
  print('SAMPLE',cid,[{'title':s.get('title'),'items':[(f.get('label'),str(f.get('value') or f.get('text'))[:155]) for f in s.get('items',[])[:4]]} for s in guide.get('sections',[])[:3]])
print('COUNTS',dict(tot))
print('REPEATS',interesting[:30])
