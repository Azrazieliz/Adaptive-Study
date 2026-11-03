# -*- coding:utf-8 -*-
"""Make Complet text-first over ALL source-indexed facts across every existing course.
Keep original source pages and page jump as a secondary view. No invented completeness claims.
"""
from pathlib import Path
import re,shutil
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
s=p.read_text("utf8")
backup=Path(r"D:\AdaptiveStudyRecovery\source_transfer\MainActivity_before_text_first_complete_v3330.java")
if not backup.exists():shutil.copy2(p,backup)
def change(a,b):
 global s
 assert a in s,"MISSING: "+a[:150]
 s=s.replace(a,b,1)
anchor='''    private JSONObject essentialSelection,completePageIndex;'''
assert anchor in s
replacement='''    private int completeSectionIndex=0;
    private boolean completeSourceMode=false;
    private void showCompleteStructuredText(JSONObject guide,JSONArray originalPages,String subject){
        JSONArray all=arr(guide,"sections");
        int total=all==null?0:all.length();
        heading(body,"Complet — cours structuré");
        LinearLayout summary=panel(body);
        int facts=0;
        if(all!=null)for(int i=0;i<all.length();i++){
            JSONArray rows=arr(all.optJSONObject(i),"items");
            if(rows!=null)facts+=rows.length();
        }
        info(summary,"Notions disponibles",String.valueOf(facts));
        info(summary,"Sections",String.valueOf(total));
        info(summary,"Pages de FC d’origine",String.valueOf(originalPages==null?0:originalPages.length()));
        sub(summary,"Tous les éléments textuels actuellement indexés sont disponibles ici, sans limite arbitraire de premières pages. Les figures et tableaux d’origine restent accessibles dans Pages. La transcription de toutes les images n’est pas encore certifiée exhaustive.");
        buttons(summary,"Comprendre : mécanismes",()->{guideMode="UNDERSTAND";go("LESSON");},
                "Pages originales",()->{completeSourceMode=true;pageIndex=0;go("LESSON");});
        if(total==0){sub(body,"Aucune section structurée dans ce cours.");return;}
        completeSectionIndex=Math.max(0,Math.min(completeSectionIndex,total-1));
        final int current=completeSectionIndex;
        LinearLayout nav=panel(body);
        heading(nav,"Section "+(current+1)+" / "+total);
        buttons(nav,"◀ Section précédente",()->{
            completeSectionIndex=Math.max(0,current-1);go("LESSON");
        },"Section suivante ▶",()->{
            completeSectionIndex=Math.min(total-1,current+1);go("LESSON");
        });
        LinearLayout selector=horizontal();
        EditText number=new EditText(this);
        number.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        number.setText(String.valueOf(current+1));
        number.setSingleLine(true);
        number.setTextColor(WHITE);
        number.setHint("N° de section");
        number.setPadding(dp(13),dp(9),dp(13),dp(9));
        number.setBackground(bg(PANEL2,0,9));
        selector.addView(number,new LinearLayout.LayoutParams(0,dp(48),1));
        TextView go=button("Atteindre",true,()->{
            int next;try{next=Integer.parseInt(number.getText().toString().trim());}
            catch(Exception e){next=current+1;}
            completeSectionIndex=Math.max(0,Math.min(total-1,next-1));go("LESSON");
        });
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(dp(120),dp(48));
        lp.leftMargin=dp(8);selector.addView(go,lp);add(nav,selector);
        // One full section of unlimited length, not a fixed number of facts.
        JSONObject section=all.optJSONObject(current);
        JSONArray factsArr=arr(section,"items");
        ArrayList<JSONObject> rows=new ArrayList<>();
        int minSourcePage=Integer.MAX_VALUE;
        if(factsArr!=null)for(int i=0;i<factsArr.length();i++){
            JSONObject item=factsArr.optJSONObject(i);
            if(item==null)continue;
            String raw=s(item,"value");
            if(raw.isEmpty())raw=s(item,"text");
            if(raw.isEmpty())continue;
            String lower=raw.toLowerCase(Locale.ROOT);
            if(lower.contains("page pdf")&&lower.contains("remplac"))continue;
            if(lower.contains("tableau à insérer"))continue;
            rows.add(item);
            int page=item.optInt("page",0);
            if(page>0)minSourcePage=Math.min(minSourcePage,page);
        }
        LinearLayout block=panel(body);
        heading(block,s(section,"title"));
        if(minSourcePage!=Integer.MAX_VALUE){
            final int target=Math.max(0,minSourcePage-1);
            sub(block,rows.size()+" notions • première page source "+(target+1));
            add(block,button("Voir la page FC correspondante",false,()->{
                pageIndex=target;go("PAGES");
            }));
        }else sub(block,rows.size()+" notions textuelles");
        if(rows.isEmpty())sub(block,"Aucune notion textuelle validée dans cette section. Voir les pages originales.");
        else subjectBoard(block,subject,section,rows);
        // One-tap table of contents: compact and readable, each chapter section reachable directly.
        LinearLayout toc=panel(body);
        heading(toc,"Sommaire du cours");
        for(int i=0;i<total;i++){
            int index=i;
            JSONObject item=all.optJSONObject(i);if(item==null)continue;
            String label=(i+1)+". "+s(item,"title");
            JSONArray evidence=arr(item,"items");
            int n=evidence==null?0:evidence.length();
            add(toc,button(label+" ("+n+")",index==current,()->{
                completeSectionIndex=index;go("LESSON");
            }));
        }
        LinearLayout footer=panel(body);
        buttons(footer,"◀ Précédente",()->{
            completeSectionIndex=Math.max(0,current-1);go("LESSON");
        },"Suivante ▶",()->{
            completeSectionIndex=Math.min(total-1,current+1);go("LESSON");
        });
    }
    private JSONObject essentialSelection,completePageIndex;'''
change(anchor,replacement)
change('''    private void showCompleteSourceReader(JSONArray originalPages,JSONObject guide,String subject){
        heading(body,"Cours intégral — sources et explications");''',
'''    private void showCompleteSourceReader(JSONArray originalPages,JSONObject guide,String subject){
        if(!completeSourceMode){
            showCompleteStructuredText(guide,originalPages,subject);
            return;
        }
        heading(body,"Pages FC — contrôle de la source");''')
change('''        buttons(summary,"Texte pour comprendre",()->{guideMode="UNDERSTAND";go("LESSON");},
            "Toutes les notions structurées",()->{guideMode="FULL_FACTS";go("LESSON");});''',
'''        buttons(summary,"Revenir au cours structuré",()->{
                completeSourceMode=false;go("LESSON");},
            "Comprendre",()->{guideMode="UNDERSTAND";go("LESSON");});''')
change('''        add(footer,button("Lire le cours comme un texte",false,()->{guideMode="UNDERSTAND";go("LESSON");}));''',
'''        add(footer,button("Complet — toutes les sections textuelles",false,()->{
            completeSourceMode=false;go("LESSON");
        }));''')
# Switching into Complet always starts with the text, unless explicit Pages button is selected.
change('''                else{guideMode=choice==0?"ESSENTIAL":"COMPLETE";go("LESSON");}''',
'''                else{
                    guideMode=choice==0?"ESSENTIAL":"COMPLETE";
                    completeSourceMode=false;completeSectionIndex=0;go("LESSON");
                }''')
# When opening a different chapter, avoid inheriting another chapter's section position.
change('''    private void openLesson(String id){currentChapter=id;guideMode="UNDERSTAND";boardIndex=0;boardRevealed=true;boardAnswerDraft="";go("LESSON");}''',
'''    private void openLesson(String id){
        currentChapter=id;guideMode="UNDERSTAND";boardIndex=0;boardRevealed=true;
        boardAnswerDraft="";completeSectionIndex=0;completeSourceMode=false;go("LESSON");
    }''')
# Old page warning should route to original page or text; don't imply complete = page images only.
change('''            add(warning,button("Lire toutes les pages sources",true,()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");}));''',
'''            add(warning,button("Lire les pages sources",true,()->{pageIndex=0;go("PAGES");}));''')
change('''                add(sourceLink,button("Cours complet avec les pages ("+sourceCount+")",true,()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");}));''',
'''                add(sourceLink,button("Ouvrir les pages de FC ("+sourceCount+")",true,()->{pageIndex=0;go("PAGES");}));''')
p.write_text(s,"utf8")
print("ALL_CHAPTERS_TEXT_FIRST_COMPLETE",p.stat().st_size,"BYTES")
