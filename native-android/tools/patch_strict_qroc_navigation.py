from pathlib import Path
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
s=p.read_text("utf8")
a='''                JSONArray pts=arr(q,"expectedPoints");heading(feedback,"Correction : éléments attendus");
                if(pts!=null)for(int i=0;i<pts.length();i++)info(feedback,"Point "+(i+1),pts.optString(i));
                String extra=s(q,"explanation");if(!extra.isEmpty())sub(feedback,extra);
                buttons(feedback,"À revoir (0)",()->finishQuizQuestion(q,0.0),"Tous les points (1)",()->finishQuizQuestion(q,1.0));'''
b='''                JSONArray pts=arr(q,"expectedPoints");heading(feedback,"Correction : grille exhaustive");
                ArrayList<CheckBox> mandatory=new ArrayList<>();
                if(pts!=null)for(int i=0;i<pts.length();i++){
                    CheckBox check=new CheckBox(this);
                    check.setText((i+1)+". "+pts.optString(i));check.setTextColor(WHITE);
                    check.setTextSize(15);check.setPadding(dp(4),dp(8),dp(4),dp(8));
                    check.setButtonTintList(android.content.res.ColorStateList.valueOf(BLUE));
                    add(feedback,check);mandatory.add(check);
                }
                sub(feedback,"Cochez uniquement les éléments réellement restitués : si un élément exigé manque, la QROC n'est pas intégralement correcte.");
                String extra=s(q,"explanation");if(!extra.isEmpty())sub(feedback,extra);
                add(feedback,button("Valider la restitution intégrale",true,()->{
                    boolean complete=!mandatory.isEmpty();
                    for(CheckBox check:mandatory)if(!check.isChecked())complete=false;
                    finishQuizQuestion(q,complete?1.0:0.0);
                }));'''
assert a in s
s=s.replace(a,b,1)
a='''        if(screen.equals("EXAM_PDF")){pauseOriginalTimer();openExamLibrary(currentOriginalCourse);}
        else if(screen.equals("EXAM_LIBRARY"))go("HOME");'''
b='''        if(screen.equals("EXAM_PDF")){pauseOriginalTimer();openExamLibrary(currentOriginalCourse);}
        else if(screen.equals("ORIGINAL_Q"))go("ORIGINAL_Q_PICK");
        else if(screen.equals("ORIGINAL_Q_PICK")||screen.equals("QUIZ_PICK")||screen.equals("EXAM_LIBRARY"))go("QUESTION_HOME");
        else if(screen.equals("QUESTION_HOME"))go("HOME");
        else if(screen.equals("MAP_IMAGE_DETAIL")||screen.equals("MAP_BOARD"))go("MAP");'''
assert a in s
s=s.replace(a,b,1)
p.write_text(s,"utf8")
print("RESTORED_STRICT_SHS_AND_BACK")
