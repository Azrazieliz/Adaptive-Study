#!/usr/bin/env python3
"""Fix Essential's visual selection and make original-page links explicit.

Existing source, question and progress identities remain byte-identical.
"""
import argparse,hashlib,json,pathlib,shutil
MARK="ESSENTIAL_VISUAL_SELECTION_SOURCE_LINK_FIX_V33614"
NEW=r'''
    // ESSENTIAL_VISUAL_SELECTION_SOURCE_LINK_FIX_V33614
    private ArrayList<JSONObject> factualVisualItemsForMode(
            JSONArray items,int sectionIndex,String mode){
        if(!"ESSENTIAL".equals(mode))return factualVisualItems(items,0);
        ArrayList<JSONObject> selected=new ArrayList<>();
        if(items==null)return selected;
        JSONObject courseSelection=obj(essentialSelection,currentChapter);
        JSONArray indices=arr(courseSelection,"indices");
        if(indices==null)return selected;
        HashSet<Integer> keep=new HashSet<>();
        for(int i=0;i<indices.length();i++){
            JSONArray pair=indices.optJSONArray(i);
            if(pair!=null&&pair.length()>=2&&pair.optInt(0,-1)==sectionIndex)
                keep.add(pair.optInt(1,-1));
        }
        JSONArray picked=new JSONArray();
        for(int j=0;j<items.length();j++)
            if(keep.contains(j))picked.put(items.optJSONObject(j));
        return factualVisualItems(picked,0);
    }
'''
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(f"{label}: expected exactly one anchor but found {n}")
 return s.replace(old,new,1)
def patch(s):
 assert MARK not in s
 s=one(s,
 '    private void showCurrentSourceVisualOverview(String mode){',
 NEW+'\n    private void showCurrentSourceVisualOverview(String mode){',
 "essential visual filter helper")
 start=s.index('    private void showCurrentSourceVisualOverview(String mode){')
 end=s.index('    private void showFocusedSourceRelationBoard(',start)
 sec=s[start:end]
 old='ArrayList<JSONObject> facts=factualVisualItems(arr(section,"items"),0);'
 assert sec.count(old)==2,("Visual overview occurrences",sec.count(old))
 sec=sec.replace(old,'ArrayList<JSONObject> facts=factualVisualItemsForMode(arr(section,"items"),i,mode);')
 s=s[:start]+sec+s[end:]
 s=one(s,
 '        for(int i=0;i<indexedFacts.length()&&facts.size()<6;i++){\n'
 '            JSONObject original=indexedFacts.optJSONObject(i);\n'
 '            if(original==null||original.optBoolean("isAdministrative",false))continue;',
 '        HashSet<String> selectedKeys=new HashSet<>();\n'
 '        if("ESSENTIAL".equals(guideMode)){\n'
 '            JSONArray indices=arr(obj(essentialSelection,currentChapter),"indices");\n'
 '            if(indices!=null)for(int i=0;i<indices.length();i++){\n'
 '                JSONArray pair=indices.optJSONArray(i);\n'
 '                if(pair!=null&&pair.length()>=2)\n'
 '                    selectedKeys.add(pair.optInt(0)+":"+pair.optInt(1));\n'
 '            }\n'
 '        }\n'
 '        for(int i=0;i<indexedFacts.length()&&facts.size()<6;i++){\n'
 '            JSONObject original=indexedFacts.optJSONObject(i);\n'
 '            if(original==null||original.optBoolean("isAdministrative",false))continue;\n'
 '            if("ESSENTIAL".equals(guideMode)&&!factChosenEssential(original,selectedKeys))continue;',
 "focused Essential visual cards use Essential selection only")
 s=one(s,
 '        if(page>0){\n'
 '            add(tile,text("FC p. "+page,11,MUTED,false));\n'
 '            JSONArray originals=arr(mediaPages,currentChapter);\n'
 '            if(originals!=null&&page<=originals.length())\n'
 '                tile.setOnClickListener(v->{pageIndex=page-1;go("PAGES");});\n'
 '        }',
 '        if(page>0){\n'
 '            TextView sourceLink=text("FC p. "+page+"  ›",12,BLUE,true);\n'
 '            sourceLink.setPadding(0,dp(8),0,dp(4));\n'
 '            JSONArray originals=arr(mediaPages,currentChapter);\n'
 '            if(originals!=null&&page<=originals.length()){\n'
 '                sourceLink.setOnClickListener(v->{pageIndex=page-1;go("PAGES");});\n'
 '                tile.setOnClickListener(v->{pageIndex=page-1;go("PAGES");});\n'
 '            }\n'
 '            add(tile,sourceLink);\n'
 '        }',
 "explicit tap target for source links")
 return s
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--java",required=True)
 parser.add_argument("--gradle",required=True)
 args=parser.parse_args()
 p=pathlib.Path(args.java);old=p.read_text(encoding="utf-8");new=patch(old)
 backup=p.with_name(p.name+".before_v33614_essential_fix")
 if backup.exists():assert backup.read_text(encoding="utf-8")==old
 else:shutil.copy2(p,backup)
 p.write_text(new,encoding="utf-8")
 g=pathlib.Path(args.gradle)
 orig=g.read_text(encoding="utf-8")
 assert orig.count("versionCode 33613")==1 and orig.count("versionName '3.36.13-visual-source'")==1
 gb=g.with_name(g.name+".before_v33614")
 if gb.exists():assert gb.read_text(encoding="utf-8")==orig
 else:shutil.copy2(g,gb)
 g.write_text(orig.replace("versionCode 33613","versionCode 33614").replace(
   "versionName '3.36.13-visual-source'","versionName '3.36.14-visual-current-fc'"),encoding="utf-8")
 print(json.dumps({"version":"3.36.14-visual-current-fc",
  "sourceSHA256":hashlib.sha256(new.encode("utf-8")).hexdigest(),
  "essentialVisualFiltering":True,"explicitFCPageLinks":True,
  "originalCourseDataUnchanged":True,"questionIdsUnchanged":True},ensure_ascii=True))
