from pathlib import Path
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
frag=Path(r"D:\AdaptiveStudyRecovery\native_original_question_sessions.javafrag").read_text("utf8")
s=p.read_text("utf8")
def replace(a,b):
 global s
 assert a in s,a[:100]
 s=s.replace(a,b,1)
replace('    private void indexData(){',frag+'\n    private void indexData(){')
replace('''                loadOriginalExamCatalog();
                loadComprehensionGuides();
                runOnUiThread(this::render);''',
'''                loadOriginalExamCatalog();
                loadComprehensionGuides();
                loadOriginalQuestions();
                runOnUiThread(this::render);''')
replace('''            case "EXAM_LIBRARY":showExamLibrary();break;''',
'''            case "QUESTION_HOME":showQuestionModes();break;
            case "ORIGINAL_Q_PICK":showOriginalQuestionPick();break;
            case "ORIGINAL_Q":showOriginalQuestion();break;
            case "EXAM_LIBRARY":showExamLibrary();break;''')
replace('''            case "QUIZ_PICK":showExamLibrary();break;''',
'''            case "QUIZ_PICK":showPick(true);break;''')
replace('''addNav("Accueil","HOME");addNav("Questions","EXAM_LIBRARY");addNav("Flashcards","CARD_PICK");''',
'''addNav("Accueil","HOME");addNav("Questions","QUESTION_HOME");addNav("Flashcards","CARD_PICK");''')
replace('''(screen.equals("QUIZ")&&dest.equals("EXAM_LIBRARY"))||
            (screen.equals("EXAM_PDF")&&dest.equals("EXAM_LIBRARY"))''',
'''((screen.equals("QUIZ")||screen.equals("QUIZ_PICK")||screen.equals("ORIGINAL_Q")||
              screen.equals("ORIGINAL_Q_PICK")||screen.equals("EXAM_PDF")||screen.equals("EXAM_LIBRARY"))&&dest.equals("QUESTION_HOME"))''')
replace('''buttons(overview,"Annales et QE originaux",()->openExamLibrary(""),"Réviser les cartes",()->go("CARD_PICK"));''',
'''buttons(overview,"Questions concours",()->go("QUESTION_HOME"),"Réviser les cartes",()->go("CARD_PICK"));''')
replace('''    private void startQuiz(String id){openExamLibrary(id);}''',
'''    private void startQuiz(String id){
        ArrayList<Integer> list=questionsByChapter.get(id);
        if(list!=null&&!list.isEmpty())launchQuiz(list);
        else openExamLibrary(id);
    }''')
replace('''buttons(body,"Revenir aux questions",()->go("QUIZ_PICK"),"Ouvrir ce cours",()->openLesson(chap));''',
'''buttons(body,"Revenir aux questions",()->go("QUESTION_HOME"),"Ouvrir ce cours",()->openLesson(chap));''')
replace('''            buttons(body,"Nouvelle session",()->go("QUIZ_PICK"),"Cours",()->go("CATALOG"));return;''',
'''            buttons(body,"Nouvelle session",()->go("QUIZ_PICK"),"Cours",()->go("CATALOG"));return;''')
replace('''    private void drawImage(String path){
        final ZoomImageView image=new ZoomImageView(this);''',
'''    private void drawImage(String path){drawImageInto(body,path);}
    private void drawImageInto(LinearLayout target,String path){
        final ZoomImageView image=new ZoomImageView(this);''')
replace('''        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(560));body.addView(image,lp);''',
'''        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(560));target.addView(image,lp);''')
replace('''            }catch(Exception e){runOnUiThread(()->sub(body,"Image indisponible : "+path));}''',
'''            }catch(Exception e){runOnUiThread(()->sub(target,"Image indisponible : "+path));}''')
replace('''            if(corrected!=null)for(int i=0;i<corrected.length();i++)drawImage(corrected.optString(i));''',
'''            if(corrected!=null)for(int i=0;i<corrected.length();i++)drawImageInto(correction,corrected.optString(i));''')
replace('''    private int originalQuestionIndex=0;''',
'''    private int originalQuestionIndex=0;
    private String originalSelected="";''')
replace('''        originalQuestionIndex=0;originalAnswerVisible=false;originalItemStart=SystemClock.elapsedRealtime();''',
'''        originalQuestionIndex=0;originalAnswerVisible=false;originalSelected="";originalItemStart=SystemClock.elapsedRealtime();''')
replace('''        originalAnswerVisible=false;originalItemStart=SystemClock.elapsedRealtime();
        go("ORIGINAL_Q");''',
'''        originalAnswerVisible=false;originalSelected="";originalItemStart=SystemClock.elapsedRealtime();
        go("ORIGINAL_Q");''')
replace('''            if(shs){
                EditText draft=new EditText(this);''',
'''            final ArrayList<CheckBox> answers=new ArrayList<>();
            if(shs){
                EditText draft=new EditText(this);''')
replace('''                    add(response,check);
                }
            }
            add(response,button("Afficher le corrigé original",true,()->{
                originalAnswerVisible=true;go("ORIGINAL_Q");''',
'''                    add(response,check);answers.add(check);
                }
            }
            add(response,button("Afficher le corrigé original",true,()->{
                StringBuilder selected=new StringBuilder();
                for(CheckBox box:answers)if(box.isChecked()){
                    if(selected.length()>0)selected.append(", ");
                    selected.append(box.getText());
                }
                originalSelected=selected.length()>0?selected.toString():"Aucune proposition cochée";
                originalAnswerVisible=true;go("ORIGINAL_Q");''')
replace('''            heading(correction,"Corrigé fourni");
            String status=''',
'''            heading(correction,"Corrigé fourni");
            if(!shs)sub(correction,"Votre sélection : "+originalSelected);
            String status=''')
# QROC checkbox self scoring will be handled separately.
p.write_text(s,encoding="utf8")
print("PATCHED_QUESTION_HOME",p.stat().st_size,"MAPPING",s.count('case "QUESTION_HOME"'))
