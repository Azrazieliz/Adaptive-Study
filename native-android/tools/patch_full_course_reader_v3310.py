from pathlib import Path
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
s=p.read_text("utf8")
def repl(a,b):
 global s
 assert a in s,"NOT FOUND "+a[:160]
 s=s.replace(a,b,1)
repl('''                loadOriginalQuestions();
                runOnUiThread(this::render);''',
'''                loadOriginalQuestions();
                loadFullLessonIndexes();
                runOnUiThread(this::render);''')
repl('''    private JSONObject comprehensionGuides;''',
Path(r"D:\AdaptiveStudyRecovery\native_complete_course_reader_v3310.javafrag").read_text("utf8")+
'\n    private JSONObject comprehensionGuides;')
repl('''        boolean essential="ESSENTIAL".equals(guideMode);
        int maxPerSection=Math.max(1,Math.min(3,30/Math.max(1,sections.length())));''',
'''        if("COMPLETE".equals(guideMode)){
            showCompleteSourceReader(originalPages,guide,subject);return;
        }
        boolean essential="ESSENTIAL".equals(guideMode);
        JSONObject selection=essentialSelection==null?null:essentialSelection.optJSONObject(currentChapter);
        JSONArray chosen=arr(selection,"indices");
        HashSet<String> selectedKeys=new HashSet<>();
        if(chosen!=null)for(int i=0;i<chosen.length();i++){
            JSONArray pair=chosen.optJSONArray(i);
            if(pair!=null&&pair.length()>=2)selectedKeys.add(pair.optInt(0)+":"+pair.optInt(1));
        }
        if(!essential)heading(body,"Toutes les notions structurées");''')
repl('''                if(essential&&item.optInt("priority",1)<2)continue;
                if(essential&&selected.size()>=maxPerSection)continue;
                if(essential&&displayed>=30)continue;''',
'''                if(essential&&!selectedKeys.contains(j+":"+k))continue;
                String memo=s(item,"value");
                if(memo.isEmpty())memo=s(item,"text");
                if(memo.matches("(?is).*(?:page\\\\s+PDF\\\\s*\\\\d+\\\\s+(?:est\\\\s+)?(?:à remplacer|remplacée)|tableau\\\\s+à\\\\s+insérer).*"))continue;''')
repl('''            sub(body,"Complet : "+displayed+" repères structurés, plus les "+sourceCount+" pages du cours source. Les passages non transcrits doivent être étudiés sur les pages.");''',
'''            sub(body,"Toutes les notions structurées : "+displayed+" repères. Le mode Complet affiche aussi les "+sourceCount+" pages de cours, y compris celles dont le texte n'a pas encore été transcrit.");''')
repl('''                add(sourceLink,button("Lire le cours original, page par page ("+sourceCount+")",true,()->{pageIndex=0;go("PAGES");}));''',
'''                add(sourceLink,button("Cours complet avec les pages ("+sourceCount+")",true,()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");}));''')
repl('''        if(essential)
            sub(body,"Essentiel : "+displayed+" repères prioritaires sur "+total+" actuellement structurés. Le mode Complet inclut tous les repères disponibles.");''',
'''        if(essential)
            sub(body,"Essentiel : "+displayed+" repères sélectionnés dans toutes les parties du cours, parmi "+total+" notions actuellement structurées. Le mode Complet contient également les pages intégrales.");''')
# New option retained in bottom: current "complete" links pages anyway
p.write_text(s,"utf8")
print("PATCHED",p.stat().st_size)
