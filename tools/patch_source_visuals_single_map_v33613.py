#!/usr/bin/env python3
"""Native visual-source renderer and ONE interactive mind map for existing FCs.

Everything comes from the retained courseGuide facts and source page numbers.
Never guesses a quantitative comparison or adds a course/assessment.
"""
import argparse,hashlib,json,pathlib,shutil

MARK="NATIVE_SOURCE_GROUNDED_VISUAL_STUDY_V33613"
NEW=r'''
    // NATIVE_SOURCE_GROUNDED_VISUAL_STUDY_V33613
    // These cards are alternate layouts for existing FC facts, NOT extra claims.
    private boolean isComparativeFCSection(String title){
        String n=title.toLowerCase(java.util.Locale.ROOT);
        return n.contains("compar")||n.contains("différen")||n.contains("classification")||
            n.contains("typolog")||n.contains("catégorie")||n.contains("types de ")||
            n.contains("formes de ")||n.contains("familles de ")||n.contains(" versus ")||
            n.contains(" vs ")||n.contains(" vs.");
    }
    private boolean isSequentialFCSection(String title){
        String n=title.toLowerCase(java.util.Locale.ROOT);
        return n.contains("étapes")||n.contains("phases")||n.contains("cascade")||
            n.contains("chronologie")||n.contains("enchaînement")||n.contains("déroulement")||
            n.contains("cycle de ")||n.contains("cycle cellulaire");
    }
    private ArrayList<JSONObject> factualVisualItems(JSONArray items,int pageOnly){
        ArrayList<JSONObject> result=new ArrayList<>();
        if(items==null)return result;
        for(int i=0;i<items.length();i++){
            JSONObject fact=items.optJSONObject(i);
            if(fact==null||fact.optBoolean("isAdministrative",false))continue;
            int page=fact.optInt("page",0);
            if(pageOnly>0&&page!=pageOnly)continue;
            String label=s(fact,"label"),value=s(fact,"value");
            if(value.isEmpty())value=s(fact,"text");
            String low=value.toLowerCase(java.util.Locale.ROOT);
            if(value.trim().isEmpty()||low.contains("tableau à insérer")||
               low.contains("page pdf")&&low.contains("remplac"))continue;
            result.add(fact);
        }
        return result;
    }
    private LinearLayout sourceVisualTile(JSONObject fact,int color){
        LinearLayout tile=vertical();
        tile.setPadding(dp(10),dp(11),dp(10),dp(11));
        tile.setBackground(bg(PANEL2,color,12));
        String label=s(fact,"label"),raw=s(fact,"value");
        if(raw.isEmpty())raw=s(fact,"text");
        String subject=s(byChapter.get(currentChapter),"subjectId");
        if(!label.isEmpty())add(tile,text(label,14,color,true));
        String shown=readableValue(label,raw,subject);
        TextView valueText=text(shown,14,WHITE,false);
        valueText.setTextIsSelectable(true);
        valueText.setLineSpacing(dp(2),1.02f);
        add(tile,valueText);
        int page=fact.optInt("page",fact.optInt("sourcePage",0));
        if(page>0){
            add(tile,text("FC p. "+page,11,MUTED,false));
            JSONArray originals=arr(mediaPages,currentChapter);
            if(originals!=null&&page<=originals.length())
                tile.setOnClickListener(v->{pageIndex=page-1;go("PAGES");});
        }
        return tile;
    }
    private void addSourceRelationBoard(LinearLayout target,ArrayList<JSONObject> facts,
            String title,boolean compare,boolean ordered,int maxFacts){
        if(facts.size()<2)return;
        final LinearLayout holder=panel(target);
        heading(holder,title);
        sub(holder,ordered?"Étapes citées dans la section originale • ouvrir une carte pour voir sa page":
            compare?"Caractéristiques juxtaposées depuis la même section de FC":
            "Repères distincts du même passage de la FC");
        int count=Math.min(maxFacts,facts.size());
        for(int i=0;i<count;){
            if(ordered){
                LinearLayout step=horizontal();
                step.setGravity(Gravity.TOP);
                TextView number=text(String.valueOf(i+1),16,GREEN,true);
                number.setGravity(Gravity.CENTER);
                number.setBackground(bg(PANEL2,GREEN,10));
                step.addView(number,new LinearLayout.LayoutParams(dp(38),dp(40)));
                LinearLayout tile=sourceVisualTile(facts.get(i),i%2==0?GREEN:BLUE);
                LinearLayout.LayoutParams fill=new LinearLayout.LayoutParams(0,-2,1);
                fill.leftMargin=dp(8);
                step.addView(tile,fill);
                add(holder,step);
                if(i+1<count){
                    TextView arrow=text("↓",18,GREEN,true);arrow.setGravity(Gravity.CENTER);
                    add(holder,arrow);
                }
                i++;
            }else{
                LinearLayout pair=horizontal();
                pair.setGravity(Gravity.TOP);
                for(int k=0;k<2&&i<count;k++,i++){
                    LinearLayout card=sourceVisualTile(facts.get(i),k==0?BLUE:GREEN);
                    LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1f);
                    if(k>0)lp.leftMargin=dp(8);
                    pair.addView(card,lp);
                }
                add(holder,pair);
            }
        }
        if(facts.size()>count)
            sub(holder,"+"+(facts.size()-count)+" autre(s) repère(s) dans la leçon complète.");
    }
    private void showCurrentSourceVisualOverview(String mode){
        JSONObject guide=obj(guides,currentChapter);
        JSONArray sections=arr(guide,"sections");
        if(sections==null)return;
        int limit="ESSENTIAL".equals(mode)?2:"COMPLETE".equals(mode)?4:3;
        LinearLayout visuals=null;
        int shown=0;
        for(int i=0;i<sections.length()&&shown<limit;i++){
            JSONObject section=sections.optJSONObject(i);
            if(section==null)continue;
            String title=s(section,"title");
            if(isEpitheliumPracticeSection(title)||
               title.toLowerCase(java.util.Locale.ROOT).contains("qroc")||
               title.toLowerCase(java.util.Locale.ROOT).contains("entraînement")||
               title.toLowerCase(java.util.Locale.ROOT).contains("pièges"))continue;
            ArrayList<JSONObject> facts=factualVisualItems(arr(section,"items"),0);
            if(facts.size()<2)continue;
            boolean compare=isComparativeFCSection(title);
            boolean ordered=isSequentialFCSection(title);
            if(!compare&&!ordered&&shown>0)continue;
            if(visuals==null){
                visuals=panel(body);
                heading(visuals,"Synthèse visuelle • FC originale");
                sub(visuals,"Comparaisons et enchaînements uniquement lorsqu'ils sont indiqués "+
                    "dans les sections existantes. Aucun chiffre ni lien scientifique ajouté.");
            }
            addSourceRelationBoard(visuals,facts,title,compare,ordered,
                "ESSENTIAL".equals(mode)?4:6);
            shown++;
        }
        if(shown==0){
            // A fallback visual is a side-by-side reference board, NOT a comparison.
            for(int i=0;i<sections.length();i++){
                JSONObject section=sections.optJSONObject(i);
                if(section==null||isEpitheliumPracticeSection(s(section,"title")))continue;
                ArrayList<JSONObject> facts=factualVisualItems(arr(section,"items"),0);
                if(facts.size()<2)continue;
                LinearLayout area=panel(body);
                heading(area,"Repères visuels • "+s(section,"title"));
                sub(area,"Présentation condensée des données déjà transcrites dans la FC.");
                addSourceRelationBoard(area,facts,"À parcourir",false,false,
                    "ESSENTIAL".equals(mode)?4:6);
                break;
            }
        }
    }
    private void showFocusedSourceRelationBoard(JSONArray indexedFacts,int page){
        if(indexedFacts==null||indexedFacts.length()<2||"biocell_noyau".equals(currentChapter))return;
        ArrayList<JSONObject> facts=new ArrayList<>();
        boolean flagged=false;
        for(int i=0;i<indexedFacts.length()&&facts.size()<6;i++){
            JSONObject original=indexedFacts.optJSONObject(i);
            if(original==null||original.optBoolean("isAdministrative",false))continue;
            String val=s(original,"value");
            if(val.trim().isEmpty())continue;
            if(original.optBoolean("requiresManualReview",false))flagged=true;
            JSONObject copy=new JSONObject();
            try{
                copy.put("label",s(original,"label"));copy.put("value",val);
                copy.put("page",page);
            }catch(org.json.JSONException ignored){continue;}
            facts.add(copy);
        }
        if(facts.size()<2)return;
        LinearLayout holder=panel(body);
        heading(holder,"Planche des repères • page "+page);
        if(flagged)sub(holder,"Notes indexées à confronter à la FC avant validation scientifique.");
        addSourceRelationBoard(holder,facts,"Éléments extraits de la même page",
            false,false,4);
    }
    private JSONObject buildSingleGuideMindMap(){
        JSONObject guide=obj(guides,currentChapter);
        JSONArray sections=arr(guide,"sections");
        if(sections==null||sections.length()==0)return null;
        JSONObject result=new JSONObject();
        JSONArray branches=new JSONArray();
        for(int i=0;i<sections.length();i++){
            JSONObject section=sections.optJSONObject(i);
            if(section==null)continue;
            String title=s(section,"title");
            if(isEpitheliumPracticeSection(title)||
               title.toLowerCase(java.util.Locale.ROOT).contains("qroc")||
               title.toLowerCase(java.util.Locale.ROOT).contains("entraînement")||
               title.toLowerCase(java.util.Locale.ROOT).contains("pièges"))continue;
            ArrayList<JSONObject> facts=factualVisualItems(arr(section,"items"),0);
            if(facts.isEmpty())continue;
            JSONArray selected=new JSONArray();
            java.util.TreeSet<Integer> pages=new java.util.TreeSet<>();
            for(JSONObject fact:facts){
                selected.put(fact);
                if(fact.optInt("page",0)>0)pages.add(fact.optInt("page",0));
            }
            JSONArray sourcePages=new JSONArray();
            for(int page:pages)sourcePages.put(page);
            JSONObject branch=new JSONObject();
            try{
                branch.put("title",title);
                branch.put("relation",facts.size()+" notions du cours");
                branch.put("items",selected);
                branch.put("pages",sourcePages);
            }catch(org.json.JSONException ignored){continue;}
            branches.put(branch);
        }
        if(branches.length()==0)return null;
        try{
            result.put("title","Carte conceptuelle • "+chapterTitle(currentChapter));
            result.put("kind","concepts");
            result.put("branches",branches);
        }catch(org.json.JSONException e){return null;}
        return result;
    }
'''
def one(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(f"{label}: expected 1 anchor, got {n}: {old[:75]}")
 return s.replace(old,new,1)
def patch(s):
 assert MARK not in s
 s=one(s,'    private boolean isSequenceSection(String title){',
     NEW+'\n    private boolean isSequenceSection(String title){',
     "add source-based diagrams and single course map")
 s=one(s,'            showComprehension();\n            showSourceVerifiedVisualBoards("UNDERSTAND");',
     '            showComprehension();\n            showCurrentSourceVisualOverview("UNDERSTAND");\n            showSourceVerifiedVisualBoards("UNDERSTAND");',
     "visual understanding")
 s=one(s,'            showSourceVerifiedVisualBoards("COMPLETE");\n            showCompleteStructuredText(guide,sourceCount,subject);return;',
     '            showCurrentSourceVisualOverview("COMPLETE");\n            showSourceVerifiedVisualBoards("COMPLETE");\n            showCompleteStructuredText(guide,sourceCount,subject);return;',
     "visual full lesson")
 s=one(s,'        if("ESSENTIAL".equals(guideMode))showSourceVerifiedVisualBoards("ESSENTIAL");',
     '        if("ESSENTIAL".equals(guideMode)){\n'
     '            showCurrentSourceVisualOverview("ESSENTIAL");\n'
     '            showSourceVerifiedVisualBoards("ESSENTIAL");\n'
     '        }',
     "visual essential lesson")
 s=one(s,'        if("ESSENTIAL".equals(guideMode)&&displayed==0)\n            sub(body,"Aucune sélection Essentiel vérifiée sur cette page.");',
     '        showFocusedSourceRelationBoard(facts,current);\n'
     '        if("ESSENTIAL".equals(guideMode)&&displayed==0)\n'
     '            sub(body,"Aucune sélection Essentiel vérifiée sur cette page.");',
     "show source comparison board on source page")
 s=one(s,'        if(s(mind,"path").isEmpty()){\n            heading(body,chapterTitle(currentChapter));',
     '        JSONObject generated=buildSingleGuideMindMap();\n'
     '        if(generated!=null){\n'
     '            showAuthoredMap(generated,arr(generated,"branches"),mind);\n'
     '            return;\n'
     '        }\n'
     '        if(s(mind,"path").isEmpty()){\n'
     '            heading(body,chapterTitle(currentChapter));',
     "one generated mind map from all existing chapter sections")
 s=one(s,'        drawImage(mapPath);\n        showPreservedMapPlates(mind);',
     '        drawImage(mapPath);\n'
     '        // Historical supplementary plates remain stored but are not additional mind maps.',
     "one active mind map without duplicate submaps")
 s=one(s,'        String path=s(original,"path");\n        if(!path.isEmpty())add(body,button("Consulter la planche conservée",false,()->openFullMapReader(path)));\n        showPreservedMapPlates(original);',
     '        String path=s(original,"path");\n'
     '        if(!path.isEmpty())add(body,button("Planche d’archive du cours",false,()->openFullMapReader(path)));\n'
     '        // Supplementary legacy plates are preserved in assets; one map is active.',
     "one active map policy for authored maps")
 s=one(s,'            toggle.setOnClickListener(view->{\n                boolean expand=detail.getVisibility()==View.GONE;',
     '            JSONArray originalFacts=arr(branch,"items");\n'
     '            final boolean[] detailLoaded={false};\n'
     '            toggle.setOnClickListener(view->{\n'
     '                boolean expand=detail.getVisibility()==View.GONE;\n'
     '                if(expand&&originalFacts!=null&&!detailLoaded[0]){\n'
     '                    int shown=0;\n'
     '                    for(int j=0;j<originalFacts.length();j++){\n'
     '                        JSONObject fact=originalFacts.optJSONObject(j);\n'
     '                        if(fact==null)continue;\n'
     '                        boardRow(detail,s(fact,"label"),\n'
     '                            readableValue(s(fact,"label"),s(fact,"value"),\n'
     '                                s(byChapter.get(currentChapter),"subjectId")),\n'
     '                            shown%2==0,true,fact.optInt("page",0));\n'
     '                        shown++;\n'
     '                    }\n'
     '                    detailLoaded[0]=true;\n'
     '                }',
     "populate map branch lazily when user expands")
 return s
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--java",required=True)
 parser.add_argument("--gradle",required=True)
 a=parser.parse_args()
 f=pathlib.Path(a.java)
 old=f.read_text(encoding="utf-8")
 new=patch(old)
 assert MARK in new
 backup=f.with_name(f.name+".before_source_visual_v33613")
 if backup.exists():assert backup.read_text(encoding="utf-8")==old
 else:shutil.copy2(f,backup)
 f.write_text(new,encoding="utf-8")
 g=pathlib.Path(a.gradle)
 before=g.read_text(encoding="utf-8")
 assert before.count("versionCode 33612")==1
 assert before.count("versionName '3.36.12-current-courses'")==1
 gback=g.with_name(g.name+".before_v33613")
 if gback.exists():assert gback.read_text(encoding="utf-8")==before
 else:shutil.copy2(g,gback)
 g.write_text(before.replace("versionCode 33612","versionCode 33613").replace(
     "versionName '3.36.12-current-courses'","versionName '3.36.13-visual-source'"),encoding="utf-8")
 print(json.dumps({"version":"3.36.13-visual-source","nativeSHA256":hashlib.sha256(new.encode("utf-8")).hexdigest(),
 "singleMindMapPerCourse":True,"sourceGroundedComparison":True,"sourceGroundedSequence":True,
 "assessmentLocationUnchanged":True,"sourceDataModified":False},ensure_ascii=True))
