#!/usr/bin/env python3
"""Restore accurate current FC catalog and source-anchored per-page study views.

Does not create courses, modify question IDs, or mark unreviewed academic text
as complete. Historical study data and profile remain intact.
"""
import argparse,hashlib,json,pathlib,shutil
MARK="CURRENT_FC_SOURCE_PAGE_STUDY_20261113"
HIDDEN={"bio_proteines","bio_biomol","chim_atoliais","chim_protons","phys_energie_elec","phys_fluides"}
SOURCE= r'''
    // CURRENT_FC_SOURCE_PAGE_STUDY_20261113: source-linked per-page study.
    // A page without verified explanatory text remains a page of the original FC.
    private int lessonFocusPage=0;
    private boolean sourcePagesContain(JSONArray pages,int number){
        if(pages==null)return false;
        for(int i=0;i<pages.length();i++)if(pages.optInt(i)==number)return true;
        return false;
    }
    private boolean factChosenEssential(JSONObject indexed,HashSet<String> selected){
        int sidx=indexed.optInt("section",-1),iidx=indexed.optInt("item",-1);
        return selected.contains(sidx+":"+iidx);
    }
    private void showPageStudyChooser(){
        JSONArray originals=arr(mediaPages,currentChapter);
        if(originals==null||originals.length()<1)return;
        add(body,button(lessonFocusPage>0?
            "Page "+lessonFocusPage+" / "+originals.length()+" • changer de page":
            "Étudier par page • "+originals.length()+" pages de FC",false,()->{
            int size=originals.length();
            String[] labels=new String[size];
            for(int i=0;i<size;i++)labels[i]="FC originale • page "+(i+1);
            new android.app.AlertDialog.Builder(this)
                .setTitle("Choisir une page de "+chapterTitle(currentChapter))
                .setItems(labels,(dialog,which)->{
                    lessonFocusPage=which+1;pageIndex=which;go("LESSON");
                }).setNegativeButton("Fermer",null).show();
        }));
    }
    private void showFocusedPageStudy(){
        JSONArray originals=arr(mediaPages,currentChapter);
        if(originals==null||originals.length()==0){
            sub(body,"Aucune page originale disponible.");return;
        }
        final int count=originals.length();
        final int current=Math.min(count,Math.max(1,lessonFocusPage));
        lessonFocusPage=current;
        pageIndex=current-1;
        LinearLayout actions=panel(body);
        String modeTitle="UNDERSTAND".equals(guideMode)?"Comprendre":
            "COMPLETE".equals(guideMode)?"Complet":"Essentiel";
        heading(actions,modeTitle+" • page "+current+" / "+count);
        sub(actions,"Page originale et notes reliées à cette page uniquement.");
        LinearLayout toolbar=horizontal();
        TextView previous=button("‹",false,()->{
            lessonFocusPage=Math.max(1,current-1);go("LESSON");
        });
        previous.setEnabled(current>1);previous.setAlpha(current>1?1f:0.45f);
        TextView next=button("›",false,()->{
            lessonFocusPage=Math.min(count,current+1);go("LESSON");
        });
        next.setEnabled(current<count);next.setAlpha(current<count?1f:0.45f);
        toolbar.addView(previous,new LinearLayout.LayoutParams(dp(52),-2));
        TextView overview=button("Toute la FC",false,()->{
            lessonFocusPage=0;go("LESSON");
        });
        LinearLayout.LayoutParams stretch=new LinearLayout.LayoutParams(0,-2,1f);
        stretch.setMargins(dp(6),0,dp(6),0);
        toolbar.addView(overview,stretch);
        toolbar.addView(next,new LinearLayout.LayoutParams(dp(52),-2));
        add(actions,toolbar);
        add(actions,button("Ouvrir dans Pages",false,()->{
            pageIndex=current-1;go("PAGES");
        }));
        // Original source first, not a diagram invented from a title or OCR.
        drawImage(originals.optString(current-1));
        if("biocell_noyau".equals(currentChapter)){
            LinearLayout notice=panel(body);
            heading(notice,"Noyau — FC originale retrouvée");
            sub(notice,"Les 25 pages proviennent du véritable cours Noyau. " +
                "Les anciennes 50 pages de FC voisines ont été séparées. " +
                "Aucun texte non revu n’est présenté comme une leçon validée.");
            return;
        }
        if("shs_sante_environnement".equals(currentChapter)){
            sub(body,"Cette FC est consultable intégralement. Les transcriptions OCR "+
                "automatiques ne constituent pas un cours validé.");
            return;
        }
        int explained=0;
        if("UNDERSTAND".equals(guideMode)){
            JSONObject expert=obj(expertComprehension,currentChapter);
            JSONArray exp=arr(expert,"sections");
            if(exp!=null)for(int i=0;i<exp.length();i++){
                JSONObject sec=exp.optJSONObject(i);
                if(sec==null||!sourcePagesContain(arr(sec,"sourcePages"),current))continue;
                LinearLayout block=panel(body);
                heading(block,s(sec,"title"));
                String source=s(sec,"source");
                String mechanism=s(sec,"mechanism");
                String advanced=s(sec,"advanced");
                if(!source.isEmpty()){
                    add(block,text("ÉLÉMENTS DU FC",12,GREEN,true));
                    add(block,technicalText(source,15,WHITE,arr(sec,"keywords")));
                }
                if(!mechanism.isEmpty()){
                    add(block,text("MÉCANISME ET RELATIONS",12,BLUE,true));
                    add(block,technicalText(mechanism,16,WHITE,arr(sec,"keywords")));
                }
                if(!advanced.isEmpty()){
                    add(block,text("APPROFONDISSEMENT — HORS DU TEXTE EXIGIBLE",12,MUTED,true));
                    add(block,technicalText(advanced,14,MUTED,arr(sec,"keywords")));
                }
                explained++;
            }
            JSONArray reviewed=reviewedCourseMode("understand");
            if(reviewed!=null)for(int i=0;i<reviewed.length();i++){
                JSONObject sec=reviewed.optJSONObject(i);
                if(sec==null||!sourcePagesContain(arr(sec,"sourcePages"),current))continue;
                LinearLayout block=panel(body);
                heading(block,s(sec,"title"));
                String mechanism=s(sec,"mechanism");
                if(!mechanism.isEmpty())add(block,technicalText(mechanism,16,WHITE,arr(sec,"keywords")));
                explained++;
            }
        }
        JSONObject record=obj(obj(obj(completePageIndex,currentChapter),"pages"),
            String.valueOf(current));
        JSONArray facts=arr(record,"facts");
        boolean showFacts=!"UNDERSTAND".equals(guideMode)||explained==0;
        int displayed=0;
        if(showFacts&&facts!=null){
            LinearLayout board=panel(body);
            heading(board,"UNDERSTAND".equals(guideMode)?
                "Repères de cette page":"ESSENTIAL".equals(guideMode)?
                "À retenir — page "+current:"Toutes les notions indexées — page "+current);
            HashSet<String> selection=new HashSet<>();
            JSONObject selections=obj(essentialSelection,currentChapter);
            JSONArray indices=arr(selections,"indices");
            if(indices!=null)for(int i=0;i<indices.length();i++){
                JSONArray pair=indices.optJSONArray(i);
                if(pair!=null&&pair.length()>=2)
                    selection.add(pair.optInt(0)+":"+pair.optInt(1));
            }
            for(int i=0;i<facts.length();i++){
                JSONObject f=facts.optJSONObject(i);
                if(f==null||f.optBoolean("isAdministrative",false))continue;
                if("ESSENTIAL".equals(guideMode)&&!factChosenEssential(f,selection))continue;
                String label=s(f,"label"),value=s(f,"value");
                if(value.isEmpty()||isEpitheliumPracticeSection(s(f,"topic")))continue;
                if(value.toLowerCase(Locale.ROOT).contains("tableau à insérer"))continue;
                boardRow(board,label,
                    readableValue(label,value,s(byChapter.get(currentChapter),"subjectId")),
                    displayed%2==0,true,current);
                displayed++;
            }
            if(displayed==0)sub(board,"Aucun repère validé associé à cette page.");
        }
        if("UNDERSTAND".equals(guideMode)&&explained==0){
            LinearLayout gap=panel(body);
            heading(gap,"Explication page par page à compléter");
            sub(gap,"La FC originale est disponible, mais aucune explication de "+
                "mécanisme correctement rattachée à cette page n’a encore été validée.");
        }
        if("ESSENTIAL".equals(guideMode)&&displayed==0)
            sub(body,"Aucune sélection Essentiel vérifiée sur cette page.");
    }
'''
def once(s,old,new,label):
 n=s.count(old)
 if n!=1:raise AssertionError(f"{label}: expected one exact anchor; got {n}")
 return s.replace(old,new,1)
def patch(s):
 assert MARK not in s
 s=once(s,
   '        "histo_embryo","biocell_cytosq","biocell_mec_integrine","biocell_dev","biocell_cycle"));',
   '        "histo_embryo","biocell_cytosq","biocell_mec_integrine","biocell_dev","biocell_cycle",\n'
   '        "bio_proteines","bio_biomol","chim_atoliais","chim_protons",\n'
   '        "phys_energie_elec","phys_fluides"));',
   "hide only six documented non-standalone courses")
 s=once(s,'    private void subjectLesson(){',SOURCE+'\n    private void subjectLesson(){',"install per-page source-linked lesson reader")
 s=once(s,'        return "biocell_noyau".equals(currentChapter) ||\n            "bio_proteines".equals(currentChapter) ||',
            '        return "bio_proteines".equals(currentChapter) ||',"independent Noyau restored")
 s=once(s,'        currentChapter=id;guideMode="UNDERSTAND";boardIndex=0;boardRevealed=true;',
        '        currentChapter=id;guideMode="UNDERSTAND";lessonFocusPage=0;pageIndex=0;boardIndex=0;boardRevealed=true;',
        "reset prior course focus")
 s=once(s,
        '        if(!"COMPLETE".equals(guideMode))showCourseReferenceLinks();\n        if(isMisregisteredOriginalCourse()){',
        '        if(!"COMPLETE".equals(guideMode))showCourseReferenceLinks();\n'
        '        showPageStudyChooser();\n'
        '        if(lessonFocusPage>0){showFocusedPageStudy();return;}\n'
        '        if(isMisregisteredOriginalCourse()){',
        "show accessible page-by-page study for every retained course")
 s=once(s,
        '                if("PAGES".equals(mode)){pageIndex=0;go("PAGES");}',
        '                if("PAGES".equals(mode)){pageIndex=lessonFocusPage>0?lessonFocusPage-1:0;go("PAGES");}',
        "retain current original page when toggling modes")
 s=once(s,
        '            drawImage(pages.optString(pageIndex));\n            showIndexedPageNotes();',
        '            drawImage(pages.optString(pageIndex));\n'
        '            add(body,button("Étudier cette page • Essentiel / Complet / Comprendre",true,()->{\n'
        '                lessonFocusPage=pageIndex+1;guideMode="UNDERSTAND";go("LESSON");\n'
        '            }));\n            showIndexedPageNotes();',
        "access per-page study from original PDF viewer")
 s=once(s,
        '        boolean hasQuestions=questionsByChapter.containsKey(currentChapter)&&\n'
        '            !questionsByChapter.get(currentChapter).isEmpty();\n'
        '        buttons(end,"Cours complet et tableaux",()->{\n'
        '                    pageIndex=0;guideMode="COMPLETE";go("LESSON");\n'
        '                },\n'
        '                hasQuestions?"Questions du cours":"Pages originales",\n'
        '                ()->{if(hasQuestions)startQuiz(currentChapter);else {pageIndex=0;go("PAGES");}});',
        '        buttons(end,"Cours complet et tableaux",()->{\n'
        '                    pageIndex=0;guideMode="COMPLETE";go("LESSON");\n'
        '                },\n'
        '                "Pages originales",()->{pageIndex=0;go("PAGES");});',
        "remove in-lesson questions link")
 s=once(s,
        '            if(id.isEmpty()||INACTIVE_COURSES.contains(id))continue;',
        '            if(id.isEmpty()||INACTIVE_COURSES.contains(id))continue;',
        "ensure unchanged existing catalog gate") if False else s
 s=once(s,
        '            String id=s(q,"chapterId");\n            if(!byChapter.containsKey(id))continue;',
        '            String id=s(q,"chapterId");\n            if(!byChapter.containsKey(id)||"biocell_noyau".equals(id))continue;',
        "suppress unverified Noyau practice")
 s=once(s,
        '            String id=s(c,"chapterId");\n            if(!byChapter.containsKey(id))continue;',
        '            String id=s(c,"chapterId");\n            if(!byChapter.containsKey(id)||"biocell_noyau".equals(id))continue;',
        "suppress unverified Noyau flashcard hints")
 return s
if __name__=="__main__":
 parser=argparse.ArgumentParser()
 parser.add_argument("--java",required=True)
 args=parser.parse_args()
 path=pathlib.Path(args.java);before=path.read_text(encoding="utf-8")
 after=patch(before)
 backup=path.with_name(path.name+".before_current_fc_source_page_20261113")
 if backup.exists():assert backup.read_text(encoding="utf-8")==before
 else:shutil.copy2(path,backup)
 path.write_text(after,encoding="utf-8")
 print(json.dumps({"sourcePageStudyInstalled":True,"bytes":len(after.encode("utf-8")),
    "sha256":hashlib.sha256(after.encode("utf-8")).hexdigest(),
    "currentCatalogDocumentedNonstandaloneHidden":sorted(HIDDEN),
    "originalNoyauVisible":True,"questionsSeparate":True,
    "allSourcePagesSelectable":True,"backup":str(backup)},ensure_ascii=True))
