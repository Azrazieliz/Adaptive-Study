from pathlib import Path
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
s=p.read_text("utf8")
def change(a,b):
 global s
 assert a in s,a[:150]
 s=s.replace(a,b,1)
change('''        if(sourceCount>0&&available<sourceCount*3){
            LinearLayout warning=panel(body);
            heading(warning,"Couverture insuffisante");
            sub(warning,available+" points structurés pour "+sourceCount+" pages sources. Cette leçon ne peut pas être considérée comme complète.");
            add(warning,button("Consulter les pages sources",true,()->{pageIndex=0;go("PAGES");}));
        }''',
'''        if(sourceCount>0&&available<sourceCount*3&&!"COMPLETE".equals(guideMode)){
            LinearLayout warning=panel(body);
            heading(warning,"Texte structuré et document source");
            sub(warning,available+" notions transcrites • "+sourceCount+" pages sources intégralement consultables dans Complet.");
            add(warning,button("Lire toutes les pages sources",true,()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");}));
        }''')
change('''        sub(intro,entry.optInt("paragraphCount")+" paragraphes • "+sourceFacts+
              " faits réintégrés"+(sourcePages>0?" • "+sourcePages+" pages sources":""));''',
'''        sub(intro,entry.optInt("paragraphCount")+" paragraphes • "+sourceFacts+
              " faits structurés"+(sourcePages>0?" • "+sourcePages+" pages sources":""));
        add(intro,button("Cours original intégral — toutes les pages",true,()->{
            pageIndex=0;guideMode="COMPLETE";go("LESSON");
        }));''')
change('''        buttons(close,"Complet (tableaux)",()->{guideMode="COMPLETE";go("LESSON");},
                "Pages sources",()->{pageIndex=0;go("PAGES");});''',
'''        buttons(close,"Complet (sources et textes)",()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");},
                "Toutes les notions",()->{guideMode="FULL_FACTS";go("LESSON");});''')
# Ensure the source-fragment does not change on future Gradle builds.
p.write_text(s,"utf8")
print("READER_UI_PATCHED",p.stat().st_size)
