#!/usr/bin/env python3
"""Non-destructive, reviewed-source-only three-mode native UI patch.

Does not alter study_data.json, original FCs, question IDs, progress or course list.
Run only on a copy/working tree of the existing signed pilot native source.
"""
from __future__ import annotations
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sys

RECOVERY_IDS = (
    "biocell_noyau", "bio_proteines", "bio_biomol",
    "chim_atoliais", "chim_protons", "phys_energie_elec", "phys_fluides"
)
MARKER = "ALL_COURSE_THREE_MODE_V1_20261113"

VISUAL_METHODS = r'''
    // ALL_COURSE_THREE_MODE_V1_20261113: source-grounded visual presentation.
    // A missing original figure is never substituted with a generated one.
    private JSONObject allCourseReviewedVisuals=null;
    private JSONObject reviewedVisualCatalog(){
        if(allCourseReviewedVisuals==null)try{
            JSONObject root=readJsonAsset("academic_visuals_verified_20261112.json");
            allCourseReviewedVisuals=obj(root,"courses");
        }catch(Exception e){
            android.util.Log.w("AdaptiveStudy","Reviewed FC visuals unavailable",e);
        }
        return allCourseReviewedVisuals;
    }
    private boolean isMisregisteredOriginalCourse(){
        return "biocell_noyau".equals(currentChapter) ||
            "bio_proteines".equals(currentChapter) ||
            "bio_biomol".equals(currentChapter) ||
            "chim_atoliais".equals(currentChapter) ||
            "chim_protons".equals(currentChapter) ||
            "phys_energie_elec".equals(currentChapter) ||
            "phys_fluides".equals(currentChapter);
    }
    private void showIndependentFcRecoveryNotice(){
        LinearLayout notice=panel(body);
        heading(notice,"FC originale : correspondance à restaurer");
        sub(notice,"Ce cours est authentique et conserve son identifiant. " +
            "Des pages d'autres FC lui ont été attribuées par erreur. " +
            "Elles ne sont pas présentées comme son propre cours.");
        sub(notice,"La restitution Essentiel, Complet et Comprendre reprendra " +
            "à partir des véritables pages indépendantes, une fois rapprochées.");
        add(notice,button("Retour aux cours",false,()->go("CATALOG")));
    }
    private boolean reviewedBoardAllows(JSONObject board,String mode){
        if(!"PAGE_IMAGE_REVIEWED".equals(s(board,"reviewStatus")))return false;
        JSONArray modes=arr(board,"modes");
        if(modes==null)return false;
        for(int j=0;j<modes.length();j++)
            if(mode.equals(modes.optString(j)))return true;
        return false;
    }
    private void showSourceVerifiedVisualBoards(String mode){
        JSONArray visuals=arr(reviewedVisualCatalog(),currentChapter);
        if(visuals==null)return;
        int accepted=0;
        LinearLayout gallery=null;
        for(int i=0;i<visuals.length();i++){
            JSONObject board=visuals.optJSONObject(i);
            if(board==null||!reviewedBoardAllows(board,mode))continue;
            // The two neural pilot figures have richer mechanism cards below.
            String visualId=s(board,"id");
            if("UNDERSTAND".equals(mode)&&"histo_nerveux".equals(currentChapter)&&
               (visualId.equals("histo_nerveux_neuron_synapse_original_p06")||
                visualId.equals("histo_nerveux_bouton_synaptique_me_p14")))continue;
            String layout=s(board,"layout");
            if(!"source_figure".equals(layout)&&!"flow".equals(layout))continue;
            if(gallery==null){
                gallery=panel(body);
                heading(gallery,"Schémas et relations du FC");
                sub(gallery,"Figures originales vérifiées et chaînes causales " +
                    "liées à leurs pages sources ; les autres pages restent à auditer.");
            }
            LinearLayout figure=panel(gallery);
            add(figure,text(s(board,"title"),16,BLUE,true));
            String subtitle=s(board,"subtitle");
            if(!subtitle.isEmpty())sub(figure,subtitle);
            if("source_figure".equals(layout)){
                if(!pilotOriginalFigure(figure,board)){
                    sub(figure,"Illustration indisponible. Aucun remplacement non sourcé.");
                }
            }else{
                JSONArray steps=arr(board,"steps");
                if(steps!=null)for(int st=0;st<steps.length();st++){
                    JSONObject step=steps.optJSONObject(st);if(step==null)continue;
                    int sourcePage=step.optInt("page",0);
                    pilotStepCard(figure,s(step,"label"),s(step,"detail"),
                        pilotColor(st),sourcePage);
                    if(st+1<steps.length()){
                        TextView arrow=text("↓",18,GREEN,true);
                        arrow.setGravity(Gravity.CENTER);
                        add(figure,arrow);
                    }
                }
            }
            if("UNDERSTAND".equals(mode)){
                String inference=s(board,"deduction");
                if(!inference.isEmpty()){
                    add(figure,text("DÉDUCTION",12,GREEN,true));
                    add(figure,text(inference,14,WHITE,false));
                }
            }
            JSONArray pages=arr(board,"sourcePages");
            if(pages!=null)sourcePageLinks(figure,pages);
            accepted++;
        }
        if(accepted>0)sub(body,accepted+" visuel(s) issus de pages vérifiées, sans prétention d'exhaustivité.");
    }
    private void showReviewedNeuralMechanisms(){
        JSONObject data=nervePilotData();
        JSONArray modules=arr(data,"modules");
        if(modules==null||modules.length()==0)return;
        LinearLayout introduction=panel(body);
        heading(introduction,"Comprendre — mécanismes illustrés");
        sub(introduction,"Deux modules reliés aux pages originales 6 et 14 " +
            "sur les 53 pages du Tissu nerveux. Les autres pages " +
            "ne sont pas déclarées couvertes.");
        JSONArray boards=arr(reviewedVisualCatalog(),"histo_nerveux");
        for(int i=0;i<modules.length();i++){
            JSONObject module=modules.optJSONObject(i);if(module==null)continue;
            LinearLayout card=panel(body);
            add(card,text("FC p. "+module.optInt("sourcePage",0),12,GREEN,true));
            heading(card,s(module,"title"));
            add(card,text(s(module,"concept"),15,WHITE,false));
            sub(card,s(module,"objective"));
            JSONObject match=null;
            if(boards!=null)for(int j=0;j<boards.length();j++){
                JSONObject b=boards.optJSONObject(j);
                if(b!=null&&s(module,"sourceBoardId").equals(s(b,"id"))){
                    match=b;break;
                }
            }
            if(match!=null&&reviewedBoardAllows(match,"UNDERSTAND"))
                pilotOriginalFigure(card,match);
            else sub(card,"Schéma original non vérifié dans ce module.");
            JSONArray steps=arr(module,"steps");
            if(steps!=null)for(int st=0;st<steps.length();st++){
                JSONObject step=steps.optJSONObject(st);if(step==null)continue;
                pilotStepCard(card,s(step,"title"),s(step,"detail"),
                    pilotColor(st),module.optInt("sourcePage",0));
                if(st+1<steps.length()){
                    TextView arrow=text("↓",18,GREEN,true);
                    arrow.setGravity(Gravity.CENTER);add(card,arrow);
                }
            }
            LinearLayout comparisons=panel(card);
            heading(comparisons,"Repères comparatifs");
            JSONArray rows=arr(module,"keys");
            if(rows!=null)for(int j=0;j<rows.length();j++){
                JSONArray pair=rows.optJSONArray(j);
                if(pair!=null&&pair.length()>=2)
                    boardRow(comparisons,pair.optString(0),pair.optString(1),
                        j%2==0,true,module.optInt("sourcePage",0));
            }
            String deduction=s(module,"deduction");
            if(!deduction.isEmpty()){
                add(card,text("Ce que permet de déduire le mécanisme",13,GREEN,true));
                add(card,text(deduction,15,WHITE,false));
            }
            JSONArray link=new JSONArray();link.put(module.optInt("sourcePage",0));
            sourcePageLinks(card,link);
        }
    }
'''

def replace_once(data: str, old: str, new: str, label: str) -> str:
    num=data.count(old)
    if num!=1:
        raise AssertionError(f"{label}: expected one anchor, got {num}")
    return data.replace(old,new,1)

def patch(text: str) -> str:
    if MARKER in text:
        raise AssertionError("Already patched: no duplicate alterations")
    text=replace_once(text,
        '        if("histo_nerveux".equals(id)){openNeuralPilot();return;}\n        go("LESSON");',
        '        go("LESSON");',
        "retain three modes for the neural course")
    text=replace_once(text,
        '        JSONArray files=arr(mediaPages,"histo_nerveux");',
        '        JSONArray files=arr(mediaPages,currentChapter);',
        "generalize original-image crop renderer")
    text=replace_once(text,
        '    private boolean isFormulaSubject(String subject){',
        VISUAL_METHODS+'\n    private boolean isFormulaSubject(String subject){',
        "install shared source-verified visual boards")
    text=replace_once(text,
        '        add(practice,button("Choisir une matière ou un cours",true,()->go("QUIZ_PICK")));',
        '        add(practice,button("Choisir une matière ou un cours",true,()->go("QUIZ_PICK")));\n'
        '        if(nervePilotData()!=null)\n'
        '            add(practice,button("Tissu nerveux — 3 QCM du pilote",false,this::pilotOpenQuiz));',
        "move neural pilot QCM into Questions")
    text=replace_once(text,
        '        JSONArray corrections=shsEntries(currentChapter,true);\n'
        '        if(corrections!=null&&corrections.length()>0)\n'
        '            add(body,button("QROC du cours",false,()->openShsCorrections(true)));',
        '        // QROC exercises live in Questions, never in the lesson reader.',
        "remove in-lesson QROC shortcut")
    text=replace_once(text,
        '        if(isMemorySubject(currentChapter)){\n'
        '            LinearLayout notice=panel(body);\n'
        '            sub(notice,"SHS, histologie et biologie cellulaire : toutes les données des tableaux originaux doivent être mémorisées.");\n'
        '            add(notice,button("Réviser les tableaux originaux",true,()->{boardIndex=0;boardRevealed=true;go("BOARDS");}));\n'
        '        }',
        '        // Source boards remain in the lessons; graded recall is in Questions.',
        "remove in-lesson board quiz")
    text=replace_once(text,
        '        buttons(learning,"SHS — entraînement QROC",()->openShsCorrections(true),',
        '        if(byChapter.containsKey(currentChapter)&&isMemorySubject(currentChapter)){\n'
        '            JSONObject bc=boardCatalog==null?null:boardCatalog.optJSONObject(currentChapter);\n'
        '            JSONArray units=arr(bc,"items");\n'
        '            if(units!=null&&units.length()>0)\n'
        '                add(practice,button("Tableaux à restituer — "+chapterTitle(currentChapter),false,()->{\n'
        '                    boardIndex=0;boardRevealed=true;go("BOARDS");\n'
        '                }));\n'
        '        }\n'
        '        buttons(learning,"SHS — entraînement QROC",()->openShsCorrections(true),',
        "move graded board recall into Questions")
    text=replace_once(text,
        '        if(!"COMPLETE".equals(guideMode))showCourseReferenceLinks();\n'
        '        if("shs_sante_environnement".equals(currentChapter)',
        '        if(!"COMPLETE".equals(guideMode))showCourseReferenceLinks();\n'
        '        if(isMisregisteredOriginalCourse()){\n'
        '            showIndependentFcRecoveryNotice();return;\n'
        '        }\n'
        '        if("shs_sante_environnement".equals(currentChapter)',
        "avoid presenting borrowed pages as original FC")
    text=replace_once(text,
        '        if("UNDERSTAND".equals(guideMode)){showComprehension();return;}',
        '        if("UNDERSTAND".equals(guideMode)){\n'
        '            showComprehension();\n'
        '            showSourceVerifiedVisualBoards("UNDERSTAND");\n'
        '            if("histo_nerveux".equals(currentChapter))showReviewedNeuralMechanisms();\n'
        '            return;\n'
        '        }',
        "understand mechanisms integrated in regular mode")
    text=replace_once(text,
        '        if("COMPLETE".equals(guideMode)){\n'
        '            showCompleteStructuredText(guide,sourceCount,subject);return;\n'
        '        }',
        '        if("COMPLETE".equals(guideMode)){\n'
        '            showSourceVerifiedVisualBoards("COMPLETE");\n'
        '            showCompleteStructuredText(guide,sourceCount,subject);return;\n'
        '        }\n'
        '        if("ESSENTIAL".equals(guideMode))showSourceVerifiedVisualBoards("ESSENTIAL");',
        "add original diagrams to essentiel and complet")
    text=replace_once(text,
        '            add(finish,button("Revenir au parcours",true,()->{\n'
        '                pilotModuleIndex=-1;go("NEURAL_PILOT");\n'
        '            }));',
        '            add(finish,button("Revenir aux Questions",true,()->{\n'
        '                pilotModuleIndex=-1;go("QUESTION_HOME");\n'
        '            }));',
        "return diagnostic to questions")
    text=replace_once(text,
        '        add(body,button("‹ Quitter le diagnostic",false,()->{pilotModuleIndex=-1;go("NEURAL_PILOT");}));',
        '        add(body,button("‹ Questions",false,()->{pilotModuleIndex=-1;go("QUESTION_HOME");}));',
        "pilot QCM back button")
    text=replace_once(text,
        '||((screen.equals("QUIZ")||screen.equals("QUIZ_PICK")||screen.equals("SHS_CORRECTIONS"))&&dest.equals("QUESTION_HOME"))',
        '||((screen.equals("QUIZ")||screen.equals("QUIZ_PICK")||screen.equals("SHS_CORRECTIONS")||screen.equals("NEURAL_PILOT_QUIZ")||screen.equals("BOARDS"))&&dest.equals("QUESTION_HOME"))',
        "questions navigation indicator")
    text=replace_once(text,
        '||screen.equals("BOARDS"))&&dest.equals("CATALOG"))',
        ')&&dest.equals("CATALOG"))',
        "board recall is now a Questions screen")
    return text

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--java",required=True)
    ap.add_argument("--check",action="store_true")
    args=ap.parse_args()
    original=Path(args.java)
    old=original.read_text(encoding="utf-8")
    new=patch(old)
    assert 'if("histo_nerveux".equals(id)){openNeuralPilot();return;}' not in new
    assert MARKER in new and 'showReviewedNeuralMechanisms();' in new
    report={"patched":True,"checkOnly":args.check,
            "previousSha256":hashlib.sha256(old.encode()).hexdigest(),
            "newSha256":hashlib.sha256(new.encode()).hexdigest(),
            "bytesAfter":len(new.encode("utf-8")),
            "courseDataUntouched":True,
            "allCourseModes":["ESSENTIAL","COMPLETE","UNDERSTAND"],
            "sourceVerifiedVisualAssetsShared":True,
            "practiceOnlyInQuestions":True,
            "independentSevenRetained":list(RECOVERY_IDS)}
    if not args.check:
        backup=original.with_name(original.name+".before_three_modes_20261113")
        if backup.exists():
            assert backup.read_bytes()==old.encode("utf-8"),"Backup collision: preserve both versions"
        else:shutil.copy2(original,backup)
        staged=original.with_name(original.name+".three_modes_tmp")
        staged.write_text(new,encoding="utf-8")
        staged.replace(original)
        report["backup"]=str(backup)
    print(json.dumps(report,ensure_ascii=True))
    return 0

if __name__=="__main__":
    sys.exit(main())
