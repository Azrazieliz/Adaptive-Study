#!/usr/bin/env python3
"""Move all legacy exercise/QROC-labelled guide sections out of lessons.

Keep original FC images, historical course/quiz IDs, and explanations unchanged.
"""
import argparse,hashlib,json,pathlib,shutil
MARK="QUESTIONS_ONLY_LEGACY_PRACTICE_ROUTING_V33613"
def one(s,old,new,name):
 n=s.count(old)
 if n!=1:raise AssertionError(f"{name} anchor count={n} expected=1")
 return s.replace(old,new,1)
def patch(s):
 assert MARK not in s
 s=one(s,
   '    private boolean isEpitheliumPracticeSection(String title){\n'
   '        if(!"histo_epitheliaux".equals(currentChapter))return false;\n'
   '        String key=title.toLowerCase(Locale.ROOT);\n'
   '        return key.startsWith("pièges attestés")||key.startsWith("questions et annales");\n'
   '    }',
   '    // QUESTIONS_ONLY_LEGACY_PRACTICE_ROUTING_V33613\n'
   '    private boolean isEpitheliumPracticeSection(String title){\n'
   '        String key=(title==null?"":title).trim().toLowerCase(Locale.ROOT);\n'
   '        return key.startsWith("pièges attestés")||key.startsWith("pièges et")||\n'
   '            key.startsWith("questions et annales")||key.startsWith("questions d’entraînement")||\n'
   '            key.startsWith("questions d\\u0027entraînement")||key.startsWith("préparation qroc")||\n'
   '            key.contains("préparation qroc")||key.startsWith("qroc ")||\n'
   '            key.startsWith("qcm ")||key.startsWith("annales")||\n'
   '            key.startsWith("exercices");\n'
   '    }\n'
   '    private void openPracticeNotesPicker(){\n'
   '        ArrayList<String> courseIds=new ArrayList<>();\n'
   '        ArrayList<String> courseLabels=new ArrayList<>();\n'
   '        for(JSONObject course:chapters){\n'
   '            String id=s(course,"id");\n'
   '            JSONArray sections=arr(obj(guides,id),"sections");\n'
   '            if(sections==null)continue;\n'
   '            boolean found=false;\n'
   '            for(int i=0;i<sections.length();i++){\n'
   '                JSONObject item=sections.optJSONObject(i);\n'
   '                if(item!=null&&isEpitheliumPracticeSection(s(item,"title"))){found=true;break;}\n'
   '            }\n'
   '            if(found){courseIds.add(id);courseLabels.add(chapterTitle(id));}\n'
   '        }\n'
   '        if(courseIds.isEmpty()){\n'
   '            new android.app.AlertDialog.Builder(this).setTitle("Notes de pratique")\n'
   '                .setMessage("Aucune section de pratique conservée.").setPositiveButton("OK",null).show();\n'
   '            return;\n'
   '        }\n'
   '        new android.app.AlertDialog.Builder(this).setTitle("Choisir les notes d’entraînement")\n'
   '            .setItems(courseLabels.toArray(new String[0]),(dialog,index)->{\n'
   '                currentChapter=courseIds.get(index);go("PRACTICE_NOTES");\n'
   '            }).setNegativeButton("Fermer",null).show();\n'
   '    }',
   "generalize legacy practice separation")
 s=one(s,
   '                if(section==null)continue;\n'
   '                JSONArray facts=arr(section,"items");',
   '                if(section==null||isEpitheliumPracticeSection(s(section,"title")))continue;\n'
   '                JSONArray facts=arr(section,"items");',
   "remove practice sections from SHS Complet")
 s=one(s,
   '            if(hasPracticeNotes){\n'
   '                LinearLayout.LayoutParams practiceLayout=new LinearLayout.LayoutParams(-2,-2);\n'
   '                practiceLayout.leftMargin=dp(6);\n'
   '                row.addView(button("Pièges",false,()->go("PRACTICE_NOTES")),practiceLayout);\n'
   '            }',
   '            // Existing QROC and pièges are reachable exclusively from Questions.',
   "remove practice button from Complet")
 s=one(s,
   '        heading(body,"Pièges d’entraînement");\n'
   '        JSONArray sections=arr(obj(guides,currentChapter),"sections");',
   '        heading(body,"Notes d’entraînement et pièges du cours");\n'
   '        sub(body,"Ces notes sont classées dans Questions, pas dans Essentiel, Complet ou Comprendre.");\n'
   '        JSONArray sections=arr(obj(guides,currentChapter),"sections");',
   "practice page labeling")
 s=one(s,
   '                if(!rows.isEmpty())subjectBoard(body,"histo",rows,s(section,"title"),true);',
   '                if(!rows.isEmpty())subjectBoard(body,s(byChapter.get(currentChapter),"subjectId"),rows,s(section,"title"),true);',
   "practice notes by genuine course subject")
 s=one(s,
   '        add(body,button("Revenir à Complet",false,()->go("LESSON")));',
   '        add(body,button("Revenir aux Questions",false,()->go("QUESTION_HOME")));',
   "practice page back to Questions")
 s=one(s,
   '        if(nervePilotData()!=null)\n'
   '            add(practice,button("Tissu nerveux — 3 QCM du pilote",false,this::pilotOpenQuiz));',
   '        if(nervePilotData()!=null)\n'
   '            add(practice,button("Tissu nerveux — 3 QCM du pilote",false,this::pilotOpenQuiz));\n'
   '        add(practice,button("Pièges, annales et préparation QROC des FC",false,this::openPracticeNotesPicker));',
   "practice picker added to Questions")
 s=one(s,
   '(screen.equals("LESSON")||screen.equals("PAGES")||screen.equals("PRACTICE_NOTES")||screen.equals("MAP")',
   '(screen.equals("LESSON")||screen.equals("PAGES")||screen.equals("MAP")',
   "practice no longer Catalog tab")
 s=one(s,
   'screen.equals("NEURAL_PILOT_QUIZ")||screen.equals("BOARDS"))&&dest.equals("QUESTION_HOME"))',
   'screen.equals("NEURAL_PILOT_QUIZ")||screen.equals("BOARDS")||screen.equals("PRACTICE_NOTES"))&&dest.equals("QUESTION_HOME"))',
   "practice now Questions tab")
 s=one(s,
   '        else if(screen.equals("PAGES")||screen.equals("PRACTICE_NOTES")||screen.equals("MAP"))go("LESSON");',
   '        else if(screen.equals("PRACTICE_NOTES"))go("QUESTION_HOME");\n'
   '        else if(screen.equals("PAGES")||screen.equals("MAP"))go("LESSON");',
   "practice back route")
 s=one(s,
   '            for(int i=0;i<reviewed.length();i++){\n'
   '                JSONObject section=reviewed.optJSONObject(i);\n'
   '                if(section==null)continue;',
   '            for(int i=0;i<reviewed.length();i++){\n'
   '                JSONObject section=reviewed.optJSONObject(i);\n'
   '                if(section==null||isEpitheliumPracticeSection(s(section,"title")))continue;',
   "filter practice from Comprendre reviewed sections")
 s=one(s,
   '            labels.add(s(block,"title"));\n'
   '        }\n'
   '        Spinner navigation=new Spinner(this);',
   '            if(block!=null&&!isEpitheliumPracticeSection(s(block,"title")))\n'
   '                labels.add(s(block,"title"));\n'
   '        }\n'
   '        Spinner navigation=new Spinner(this);',
   "filter expert section selector")
 s=one(s,
   '            JSONObject block=sections.optJSONObject(i);\n'
   '            if(block==null)continue;\n'
   '            LinearLayout card=panel(body);',
   '            JSONObject block=sections.optJSONObject(i);\n'
   '            if(block==null||isEpitheliumPracticeSection(s(block,"title")))continue;\n'
   '            LinearLayout card=panel(body);',
   "filter expert practice sections")
 s=one(s,
   '            names.add((i+1)+". "+s(section,"heading"));\n'
   '        }\n'
   '        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,names);',
   '            if(section!=null&&!isEpitheliumPracticeSection(s(section,"heading")))\n'
   '                names.add((i+1)+". "+s(section,"heading"));\n'
   '        }\n'
   '        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,names);',
   "filter comprehension paragraph selector")
 s=one(s,
   '            JSONObject section=sections.optJSONObject(i);\n'
   '            if(section==null)continue;\n'
   '            LinearLayout container=vertical();',
   '            JSONObject section=sections.optJSONObject(i);\n'
   '            if(section==null||isEpitheliumPracticeSection(s(section,"heading")))continue;\n'
   '            LinearLayout container=vertical();',
   "filter paragraph practice sections")
 s=one(s,
   '            showComprehension();\n'
   '            showCurrentSourceVisualOverview("UNDERSTAND");',
   '            showCurrentSourceVisualOverview("UNDERSTAND");\n'
   '            showComprehension();',
   "visual first in Comprendre")
 return s

if __name__=="__main__":
 parser=argparse.ArgumentParser();parser.add_argument("--java",required=True)
 a=parser.parse_args()
 p=pathlib.Path(a.java);old=p.read_text(encoding="utf-8");new=patch(old)
 backup=p.with_name(p.name+".before_questions_only_v33613")
 if backup.exists():assert backup.read_text(encoding="utf-8")==old
 else:shutil.copy2(p,backup)
 p.write_text(new,encoding="utf-8")
 print(json.dumps({"questionsOnlyNavigation":True,"noCourseDataChanged":True,
 "nativeSHA":hashlib.sha256(new.encode("utf-8")).hexdigest(),
 "feature":MARK,"sourcePreserved":True},ensure_ascii=True))
