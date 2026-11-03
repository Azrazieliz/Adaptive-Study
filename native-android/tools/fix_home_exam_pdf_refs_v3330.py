from pathlib import Path
p=Path(r"D:\AdaptiveStudyRecovery\AdaptiveStudyNative\app\src\main\java\com\azrazieliz\adaptivestudy\MainActivity.java")
s=p.read_text("utf8")
a='''            JSONArray examPapers=docs==null?null:docs.optJSONArray(id);
            int paperCount=examPapers==null?0:examPapers.length();
            sub(item,fc+" cartes de révision • "+paperCount+" PDF annales/QE fournis");
            buttons(item,"Annales / QE",()->startQuiz(id),"Cours",()->openLesson(id));'''
b='''            int practice=questionsByChapter.containsKey(id)?questionsByChapter.get(id).size():0;
            sub(item,fc+" flashcards • "+practice+" questions d’entraînement");
            buttons(item,"Questions",()->startQuiz(id),"Cours",()->openLesson(id));'''
assert a in s
s=s.replace(a,b,1)
a='''        for(Map.Entry<String,String> sb:subjects.entrySet()){
            String sid=sb.getKey();int courseCount=0,paperCount=0;
            for(JSONObject c:chapters)if(s(c,"subjectId").equals(sid)){
                courseCount++;
                JSONArray a=docs==null?null:docs.optJSONArray(s(c,"id"));
                if(a!=null)paperCount+=a.length();
            }
            LinearLayout p=panel(body);p.addView(text(sb.getValue(),16,WHITE,true));sub(p,courseCount+" cours • "+paperCount+" PDF annales/QE");
            p.setOnClickListener(v->{activeSubject=sid;go("CATALOG");});
        }'''
b='''        for(Map.Entry<String,String> sb:subjects.entrySet()){
            String sid=sb.getKey();int courseCount=0,practiceCount=0;
            for(JSONObject c:chapters)if(s(c,"subjectId").equals(sid)){
                courseCount++;
                ArrayList<Integer> entries=questionsByChapter.get(s(c,"id"));
                if(entries!=null)practiceCount+=entries.size();
            }
            LinearLayout p=panel(body);
            p.addView(text(sb.getValue(),16,WHITE,true));
            sub(p,courseCount+" cours • "+practiceCount+" questions d’entraînement");
            p.setOnClickListener(v->{activeSubject=sid;go("CATALOG");});
        }'''
assert a in s
s=s.replace(a,b,1)
assert "docs==" not in s and "Annales / QE" not in s
p.write_text(s,"utf8")
print("HOME_EXAM_REFERENCES_REMOVED")
