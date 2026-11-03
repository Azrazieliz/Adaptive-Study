# -*- coding: utf-8 -*-
"""Authorized removal of original exam PDF/question-image module, leaving new QCM/QROC,
course source pages, original learning maps and all grades/progress intact.
"""
from pathlib import Path
import shutil,re
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
s=p.read_text("utf8")
backup=Path(r"D:\AdaptiveStudyRecovery\source_transfer\MainActivity_before_pdf_exam_removal_v3330.java")
backup.parent.mkdir(parents=True,exist_ok=True)
if not backup.exists():shutil.copy2(p,backup)
def sub(a,b):
 global s
 assert a in s,"MISSING "+a[:160]
 s=s.replace(a,b,1)
sub('''        if("EXAM_PDF".equals(screen))pauseOriginalTimer();
''','')
# Inspect potential original lifecycle hooks
s=re.sub(r'''        if\("EXAM_PDF"\.equals\(screen\).*?pauseOriginalTimer\(\);\s*\n''','',s)
sub('''                loadOriginalExamCatalog();
''','')
sub('''                loadOriginalQuestions();
''','')
start=s.index('    private JSONObject originalExamCatalog;')
end=s.index('    private JSONObject essentialSelection',start)
print("REMOVE_EXAM_PDF_BLOCK_CHARS",end-start)
s=s[:start]+s[end:]
start=s.index('    private final ArrayList<JSONObject> originalQuestionItems=')
end=s.index('    private void indexData(){',start)
print("REMOVE_ORIGINAL_QUESTIONS_BLOCK_CHARS",end-start)
replacement='''    private void showQuestionModes(){
        heading(body,"Questions — entraînement concours");
        sub(body,"QCM A–E et QROC, avec corrections détaillées. Les annales/QE brutes au format PDF ont été retirées de l’application.");
        LinearLayout practice=panel(body);
        heading(practice,"Questions d’entraînement");
        sub(practice,questions.size()+" questions conservées • cinq propositions et explications pour les QCM, grille de correction pour les QROC.");
        add(practice,button("Choisir une matière ou un cours",true,()->go("QUIZ_PICK")));
        LinearLayout learning=panel(body);
        heading(learning,"Réviser les cours");
        sub(learning,"Essentiel, Complet, Comprendre, cartes mentales et flashcards.");
        buttons(learning,"Cours",()->go("CATALOG"),"Flashcards",()->go("CARD_PICK"));
    }
'''
s=s[:start]+replacement+s[end:]
for obsolete in ['''            case "ORIGINAL_Q_PICK":showOriginalQuestionPick();break;\n''',
                 '''            case "ORIGINAL_Q":showOriginalQuestion();break;\n''',
                 '''            case "EXAM_LIBRARY":showExamLibrary();break;\n''',
                 '''            case "EXAM_PDF":showOriginalPaper();break;\n''']:
 sub(obsolete,'')
sub('''                ||((screen.equals("QUIZ")||screen.equals("QUIZ_PICK")||screen.equals("ORIGINAL_Q")||
              screen.equals("ORIGINAL_Q_PICK")||screen.equals("EXAM_PDF")||screen.equals("EXAM_LIBRARY"))&&dest.equals("QUESTION_HOME"))''',
'''                ||((screen.equals("QUIZ")||screen.equals("QUIZ_PICK"))&&dest.equals("QUESTION_HOME"))''')
start=s.index('''        JSONObject docs=obj(originalExamCatalog,"courses");''',s.index('    private void showHome(){'))
end=s.index('''        int attempted=0,correct=0,reviewed=0;''',start)
s=s[:start]+'''        sub(body,chapters.size()+" cours • "+cards.size()+" flashcards • "+questions.size()+" questions d’entraînement");
'''+s[end:]
sub('''        info(overview,"Annales et QE fournis",examCount+" PDF de sujets/corrigés — documents originaux");
''','''        info(overview,"Entraînement concours",questions.size()+" questions A–E et QROC");
''')
sub('''        if(attempted>0)sub(overview,attempted+" anciens exercices dérivés traités (ne comptent pas comme annales authentifiées).");
''','''        if(attempted>0)sub(overview,attempted+" questions effectuées • "+correct+" intégralement correctes.");
''')
sub('''        sub(body,"Première semaine • Deuxième semaine (Partie 1) • Fécondation. Accès direct à chaque cours, aux flashcards, aux QCM A–E et aux originaux corrigés.");''',
'''        sub(body,"Première semaine • Deuxième semaine (Partie 1) • Fécondation. Accès direct aux cours, flashcards et QCM A–E corrigés.");''')
sub('''            buttons(focus,"Flashcards",()->startCards(urgentId),
                    "Annales et corrigés",()->openExamLibrary(urgentId));''',
'''            buttons(focus,"Flashcards",()->startCards(urgentId),
                    "Essentiel / Complet",()->{openLesson(urgentId);guideMode="ESSENTIAL";go("LESSON");});''')
sub('''        buttons(body,"Cours structuré",()->{guideMode="COMPLETE";go("LESSON");},"Annales / QE originaux",()->openExamLibrary(currentChapter));''',
'''        buttons(body,"Cours structuré",()->{guideMode="FULL_FACTS";go("LESSON");},"Flashcards",()->startCards(currentChapter));''')
sub('''        else openExamLibrary(id);''',
'''        else go("QUIZ_PICK");''')
start=s.index('    @Override public void onBackPressed(){')
end=s.index('    private final class ZoomImageView',start)
b=s[start:end]
b=b.replace('''        if(screen.equals("EXAM_PDF")){pauseOriginalTimer();openExamLibrary(currentOriginalCourse);}
        else if(screen.equals("ORIGINAL_Q"))go("ORIGINAL_Q_PICK");
        else if(screen.equals("ORIGINAL_Q_PICK")||screen.equals("QUIZ_PICK")||screen.equals("EXAM_LIBRARY"))go("QUESTION_HOME");
        else if(screen.equals("QUESTION_HOME"))go("HOME");''',
'''        if(screen.equals("QUIZ_PICK"))go("QUESTION_HOME");
        else if(screen.equals("QUESTION_HOME"))go("HOME");''')
s=s[:start]+b+s[end:]
# Original files are private authoring materials only, nothing should refer to the removed UI asset paths.
for verboten in ["originalExamCatalog","originalQuestionItems","originalQuestionIndex",
                 "openExamLibrary","original_assessment_catalog.json","original_question_catalog.json",
                 'case "EXAM_PDF"','case "EXAM_LIBRARY"','case "ORIGINAL_Q"']:
 assert verboten not in s,"Unreachable original UI reference: "+verboten
p.write_text(s,"utf8")
print("JAVA_CLEANED",len(s),"chars",p)
