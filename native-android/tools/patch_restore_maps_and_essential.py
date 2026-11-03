from pathlib import Path
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
s=p.read_text("utf8")
def change(a,b):
 global s
 assert a in s,a[:120]
 s=s.replace(a,b,1)
change('''    private void showConceptMap(){
        String courseName=chapterTitle(currentChapter);''',
'''    private void showStructuredMap(){
        String courseName=chapterTitle(currentChapter);''')
change('''    private void showStructuredMap(){''',
Path(r"D:\AdaptiveStudyRecovery\native_original_mindmaps.javafrag").read_text("utf8")+'\n    private void showStructuredMap(){')
change('''            case "MAP":showConceptMap();break;''',
'''            case "MAP":showConceptMap();break;
            case "MAP_BOARD":showStructuredMap();break;
            case "MAP_IMAGE_DETAIL":showOriginalMapDetail();break;''')
change('''screen.equals("MAP")||screen.equals("MAP_DETAIL")||screen.equals("BOARDS")''',
'''screen.equals("MAP")||screen.equals("MAP_BOARD")||screen.equals("MAP_IMAGE_DETAIL")||screen.equals("MAP_DETAIL")||screen.equals("BOARDS")''')
# Source page count warning remains; improve full/essential difference.
change('''        int maxPerSection=Math.max(2,56/Math.max(1,sections.length()));''',
'''        int maxPerSection=Math.max(1,Math.min(3,30/Math.max(1,sections.length())));''')
change('''                if(essential&&item.optInt("priority",1)<2)continue;
                if(essential&&selected.size()>=maxPerSection)continue;''',
'''                if(essential&&item.optInt("priority",1)<2)continue;
                if(essential&&selected.size()>=maxPerSection)continue;
                if(essential&&displayed>=30)continue;''')
change('''        if(essential)
            sub(body,"Essentiel : "+displayed+" repères sélectionnés. Le mode Complet contient les "+total+" repères structurés actuellement disponibles.");
        else
            sub(body,""+displayed+" repères structurés disponibles. La fidélité et l'exhaustivité doivent être vérifiées contre le cours original.");''',
'''        if(essential)
            sub(body,"Essentiel : "+displayed+" repères prioritaires sur "+total+" actuellement structurés. Le mode Complet inclut tous les repères disponibles.");
        else{
            sub(body,"Complet : "+displayed+" repères structurés, plus les "+sourceCount+" pages du cours source. Les passages non transcrits doivent être étudiés sur les pages.");
            if(sourceCount>0){
                LinearLayout sourceLink=panel(body);
                heading(sourceLink,"Pages intégrales du cours");
                sub(sourceLink,"La synthèse textuelle ne remplace pas les figures, tableaux et pages non encore transcrites.");
                add(sourceLink,button("Lire le cours original, page par page ("+sourceCount+")",true,()->{pageIndex=0;go("PAGES");}));
            }
        }''')
p.write_text(s,"utf8")
print("RESTORED_ORIGINAL_MINDMAP",p.stat().st_size)
