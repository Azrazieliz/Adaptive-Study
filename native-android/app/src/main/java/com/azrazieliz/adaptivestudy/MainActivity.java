package com.azrazieliz.adaptivestudy;

import android.app.Activity;
import android.os.Bundle;
import android.os.Build;
import android.os.SystemClock;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.AssetManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.graphics.Color;
import android.graphics.Matrix;
import android.graphics.PointF;
import android.graphics.drawable.GradientDrawable;
import android.graphics.pdf.PdfRenderer;
import android.os.ParcelFileDescriptor;
import android.text.Editable;
import android.text.TextWatcher;
import android.view.Gravity;
import android.view.MotionEvent;
import android.view.ScaleGestureDetector;
import android.view.View;
import android.view.ViewGroup;
import android.view.WindowInsets;
import android.widget.*;
import org.json.JSONArray;
import org.json.JSONObject;
import java.io.*;
import java.util.*;

public class MainActivity extends Activity {
    static final int BG=Color.rgb(10,18,31), PANEL=Color.rgb(19,34,54), PANEL2=Color.rgb(25,45,71);
    static final int WHITE=Color.rgb(240,247,255), MUTED=Color.rgb(162,180,204);
    static final int BLUE=Color.rgb(145,176,255), GREEN=Color.rgb(99,224,180), RED=Color.rgb(255,139,151), GOLD=Color.rgb(246,194,111);
    private LinearLayout root, body, nav, titleBar;
    private ScrollView scroll;
    private SharedPreferences prefs;
    private JSONObject corpus, guides, mediaPages, mindmaps, courseAssets, courseMeta, boardCatalog;
    private final ArrayList<JSONObject> chapters=new ArrayList<>(), questions=new ArrayList<>(), cards=new ArrayList<>();
    private final LinkedHashMap<String,String> subjects=new LinkedHashMap<>();
    private final HashMap<String,JSONObject> byChapter=new HashMap<>();
    private final HashMap<String,ArrayList<Integer>> questionsByChapter=new HashMap<>(), cardsByChapter=new HashMap<>();
    private String screen="HOME", currentChapter="", activeSubject="ALL", guideMode="ESSENTIAL";
    private int pageIndex=0, cardIndex=0, quizIndex=0, quizCorrect=0, quizAnswered=0, cardReviewed=0, boardIndex=0;
    private boolean boardRevealed=true;
    private String boardAnswerDraft="";
    private long questionStarted=0L;
    private final ArrayList<Integer> sessionQuestions=new ArrayList<>(), sessionCards=new ArrayList<>();
    private final Random random=new Random();

    private String installedVersion(){try{return getPackageManager().getPackageInfo(getPackageName(),0).versionName;}catch(Exception e){return "native";}}
    private int dp(float n){return (int)(getResources().getDisplayMetrics().density*n+0.5f);}
    private static String s(JSONObject j,String k){return j==null?"":j.optString(k,"");}
    private static JSONArray arr(JSONObject j,String k){return j==null?null:j.optJSONArray(k);}
    private static JSONObject obj(JSONObject j,String k){return j==null?null:j.optJSONObject(k);}
    private static String value(Object o){return o==null||o==JSONObject.NULL?"":String.valueOf(o);}
    private String chapterTitle(String id){JSONObject c=byChapter.get(id);return c==null?id:s(c,"title");}
    private String subjectName(String id){String z=subjects.get(id);return z==null?id:z;}

    @Override public void onCreate(Bundle state){
        super.onCreate(state);
        prefs=getSharedPreferences("native_study_v1",MODE_PRIVATE);
        getWindow().setStatusBarColor(BG);
        getWindow().setNavigationBarColor(BG);
        if(Build.VERSION.SDK_INT>=30) getWindow().setDecorFitsSystemWindows(false);
        root=new LinearLayout(this);root.setOrientation(LinearLayout.VERTICAL);root.setBackgroundColor(BG);
        setContentView(root);
        root.setOnApplyWindowInsetsListener((v,insets)->{
            if(Build.VERSION.SDK_INT>=30){
                android.graphics.Insets b=insets.getInsets(WindowInsets.Type.systemBars()|WindowInsets.Type.displayCutout());
                root.setPadding(b.left,b.top,b.right,b.bottom);
            }else root.setPadding(0,insets.getSystemWindowInsetTop(),0,insets.getSystemWindowInsetBottom());
            return insets;
        });
        TextView loading=text("Chargement du programme hors ligne…",18,WHITE,true);
        loading.setPadding(dp(24),dp(36),dp(24),dp(24));root.addView(loading);
        new Thread(()->{
            try{
                byte[] input;try(InputStream is=getAssets().open("study_data.json");ByteArrayOutputStream b=new ByteArrayOutputStream()){
                    byte[] buf=new byte[32768];int n;while((n=is.read(buf))!=-1)b.write(buf,0,n);input=b.toByteArray();
                }
                corpus=new JSONObject(new String(input,"UTF-8"));indexData();
                try(InputStream ins=getAssets().open("board_catalog.json");ByteArrayOutputStream out=new ByteArrayOutputStream()){byte[] tmp=new byte[16384];int n;while((n=ins.read(tmp))!=-1)out.write(tmp,0,n);boardCatalog=new JSONObject(new String(out.toByteArray(),"UTF-8"));}
                runOnUiThread(this::render);
            }catch(Exception e){
                runOnUiThread(()->{root.removeAllViews();TextView err=text("Impossible de charger les cours hors ligne : "+e,16,RED,false);root.addView(err);});
            }
        },"NativeCorpus").start();
    }
    private void indexData(){
        guides=obj(corpus,"courseGuides");mediaPages=obj(corpus,"coursePages");
        mindmaps=obj(corpus,"mindMaps");courseAssets=obj(corpus,"courseAssets");courseMeta=obj(corpus,"courseMeta");
        JSONArray subj=arr(corpus,"subjects");
        if(subj!=null)for(int i=0;i<subj.length();i++){JSONObject x=subj.optJSONObject(i);if(x!=null)subjects.put(s(x,"id"),s(x,"name"));}
        JSONArray ch=arr(corpus,"chapters");
        if(ch!=null)for(int i=0;i<ch.length();i++){JSONObject c=ch.optJSONObject(i);if(c!=null){chapters.add(c);byChapter.put(s(c,"id"),c);}}
        JSONArray qs=arr(corpus,"questions");
        if(qs!=null)for(int i=0;i<qs.length();i++){
            JSONObject q=qs.optJSONObject(i);if(q==null)continue;
            int pos=questions.size();questions.add(q);
            String id=s(q,"chapterId");questionsByChapter.computeIfAbsent(id,k->new ArrayList<>()).add(pos);
        }
        JSONArray cs=arr(corpus,"flashcards");
        if(cs!=null)for(int i=0;i<cs.length();i++){
            JSONObject c=cs.optJSONObject(i);if(c==null)continue;
            int pos=cards.size();cards.add(c);
            String id=s(c,"chapterId");cardsByChapter.computeIfAbsent(id,k->new ArrayList<>()).add(pos);
        }
    }
    private GradientDrawable bg(int color,int stroke,int rad){
        GradientDrawable g=new GradientDrawable();g.setColor(color);g.setCornerRadius(dp(rad));
        if(stroke!=0)g.setStroke(dp(1),stroke);return g;
    }
    private TextView text(String str,int size,int color,boolean bold){
        TextView t=new TextView(this);t.setText(str);t.setTextSize(size);t.setTextColor(color);
        t.setIncludeFontPadding(true);if(bold)t.setTypeface(null,1);t.setGravity(Gravity.CENTER_VERTICAL);
        t.setLineSpacing(dp(2),1.0f);return t;
    }
    private void gap(LinearLayout target,int h){View v=new View(this);target.addView(v,new LinearLayout.LayoutParams(1,dp(h)));}
    private void add(LinearLayout target,View view){
        LinearLayout.LayoutParams l=new LinearLayout.LayoutParams(-1,-2);l.bottomMargin=dp(9);
        target.addView(view,l);
    }
    private LinearLayout vertical(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.VERTICAL);return l;}
    private LinearLayout horizontal(){LinearLayout l=new LinearLayout(this);l.setOrientation(LinearLayout.HORIZONTAL);l.setGravity(Gravity.CENTER_VERTICAL);return l;}
    private LinearLayout panel(LinearLayout parent){
        LinearLayout l=vertical();l.setPadding(dp(13),dp(13),dp(13),dp(12));l.setBackground(bg(PANEL,Color.rgb(42,63,90),15));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,-2);lp.bottomMargin=dp(11);parent.addView(l,lp);return l;
    }
    private TextView button(String label,boolean primary,Runnable click){
        TextView b=text(label,14,primary?BG:WHITE,true);
        b.setGravity(Gravity.CENTER);b.setMinHeight(dp(47));b.setPadding(dp(10),dp(10),dp(10),dp(10));
        b.setBackground(bg(primary?BLUE:PANEL2,primary?0:Color.rgb(53,80,116),12));
        b.setOnClickListener(v->click.run());return b;
    }
    private void buttons(LinearLayout parent,String a,Runnable ac,String b,Runnable bc){
        LinearLayout row=horizontal(); TextView left=button(a,true,ac),right=button(b,false,bc);
        LinearLayout.LayoutParams p1=new LinearLayout.LayoutParams(0,-2,1);p1.rightMargin=dp(7);row.addView(left,p1);
        row.addView(right,new LinearLayout.LayoutParams(0,-2,1));add(parent,row);
    }
    private void heading(LinearLayout parent,String title){
        TextView h=text(title,20,WHITE,true);h.setPadding(0,dp(8),0,dp(9));add(parent,h);
    }
    private void sub(LinearLayout parent,String str){TextView t=text(str,13,MUTED,false);add(parent,t);}
    private void info(LinearLayout parent,String label,String val){
        LinearLayout row=vertical();row.setPadding(dp(9),dp(8),dp(9),dp(8));row.setBackground(bg(PANEL2,0,9));
        TextView l=text(label,13,BLUE,true);row.addView(l);TextView v=text(val,14,WHITE,false);row.addView(v);add(parent,row);
    }
    private void go(String next){screen=next;render();}
    private void render(){
        if(corpus==null)return;
        root.removeAllViews();
        titleBar=horizontal();titleBar.setPadding(dp(14),dp(11),dp(14),dp(11));titleBar.setBackgroundColor(BG);
        LinearLayout tt=vertical();tt.addView(text("Concours — Adaptive Study",16,WHITE,true));tt.addView(text("NATIF • 100 % hors ligne • v"+installedVersion(),11,GREEN,true));
        titleBar.addView(tt,new LinearLayout.LayoutParams(0,-2,1));
        TextView menu=button("≡",false,()->go("CATALOG"));titleBar.addView(menu,new LinearLayout.LayoutParams(dp(44),dp(42)));
        root.addView(titleBar);
        scroll=new ScrollView(this);scroll.setFillViewport(true);scroll.setVerticalScrollBarEnabled(false);
        body=vertical();body.setPadding(dp(13),dp(3),dp(13),dp(22));
        scroll.addView(body);root.addView(scroll,new LinearLayout.LayoutParams(-1,0,1));
        switch(screen){
            case "HOME":showHome();break;
            case "CATALOG":showCatalog();break;
            case "LESSON":subjectLesson();break;
            case "BOARDS":showBoards();break;
            case "PAGES":showPages(false);break;
            case "MAP":showConceptMap();break;
            case "MAP_DETAIL":showConceptBranch();break;
            case "QUIZ_PICK":showPick(true);break;
            case "CARD_PICK":showPick(false);break;
            case "QUIZ":showQuiz();break;
            case "CARDS":showCard();break;
            default:showHome();
        }
        nav=horizontal();nav.setBackground(bg(PANEL,0,0));nav.setPadding(dp(6),dp(7),dp(6),dp(7));
        addNav("Accueil","HOME");addNav("Questions","QUIZ_PICK");addNav("Flashcards","CARD_PICK");addNav("Cours","CATALOG");
        root.addView(nav,new LinearLayout.LayoutParams(-1,-2));
    }
    private void addNav(String name,String dest){
        boolean active=screen.equals(dest)||((screen.equals("LESSON")||screen.equals("PAGES")||screen.equals("MAP")||screen.equals("MAP_DETAIL")||screen.equals("BOARDS"))&&dest.equals("CATALOG"))
                ||(screen.equals("QUIZ")&&dest.equals("QUIZ_PICK"))||(screen.equals("CARDS")&&dest.equals("CARD_PICK"));
        TextView t=text(name,11,active?BLUE:MUTED,active);t.setGravity(Gravity.CENTER);
        t.setMinHeight(dp(46));t.setBackground(bg(active?PANEL2:PANEL,0,9));t.setOnClickListener(v->go(dest));
        nav.addView(t,new LinearLayout.LayoutParams(0,dp(47),1));
    }
    private int attempts(String questionId){return prefs.getInt("qa/"+questionId,0);}
    private boolean lastCorrect(String questionId){return prefs.getBoolean("qc/"+questionId,false);}
    private void recordAnswer(JSONObject question,boolean correct,long durationMs){
        String id=s(question,"id");SharedPreferences.Editor e=prefs.edit();
        e.putInt("qa/"+id,attempts(id)+1);
        e.putBoolean("qc/"+id,correct);
        if(!correct)e.putInt("qe/"+id,prefs.getInt("qe/"+id,0)+1);
        e.putLong("qt/"+id,Math.max(0,durationMs));e.apply();
    }
    private void showHome(){
        heading(body,"Réviser. S'entraîner. Progresser.");
        sub(body,chapters.size()+" cours • "+questions.size()+" questions • "+cards.size()+" flashcards");
        int attempted=0,correct=0,reviewed=0;
        for(JSONObject q:questions){String id=s(q,"id");if(attempts(id)>0){attempted++;if(lastCorrect(id))correct++;}}
        for(JSONObject c:cards)if(prefs.getInt("cr/"+s(c,"id"),0)>0)reviewed++;
        LinearLayout overview=panel(body);
        heading(overview,"Votre progression");
        info(overview,"Questions travaillées",attempted+" / "+questions.size()+" • "+(attempted==0?"aucun résultat":(100*correct/attempted)+" % correctes à la dernière tentative"));
        info(overview,"Flashcards révisées",reviewed+" / "+cards.size());
        buttons(overview,"Faire des questions",()->go("QUIZ_PICK"),"Réviser les cartes",()->go("CARD_PICK"));
        heading(body,"Priorités adaptatives");
        ArrayList<JSONObject> rank=new ArrayList<>(chapters);
        rank.sort((a,b)->Integer.compare(priorityScore(b),priorityScore(a)));
        int shown=0;
        for(JSONObject c:rank){
            String id=s(c,"id");if(!questionsByChapter.containsKey(id)&&!cardsByChapter.containsKey(id))continue;
            LinearLayout item=panel(body);
            item.addView(text(subjectName(s(c,"subjectId"))+" • "+s(c,"title"),15,WHITE,true));
            int n=questionsByChapter.containsKey(id)?questionsByChapter.get(id).size():0;
            int fc=cardsByChapter.containsKey(id)?cardsByChapter.get(id).size():0;
            sub(item,n+" questions • "+fc+" flashcards • "+(priorityScore(c)>100?"Revoir les erreurs":"Travail conseillé"));
            buttons(item,"Questions",()->startQuiz(id),"Cours",()->openLesson(id));
            if(++shown>=5)break;
        }
        heading(body,"Matières");
        for(Map.Entry<String,String> sb:subjects.entrySet()){
            String sid=sb.getKey();int courseCount=0,qCount=0;
            for(JSONObject c:chapters)if(s(c,"subjectId").equals(sid)){courseCount++;ArrayList<Integer> a=questionsByChapter.get(s(c,"id"));if(a!=null)qCount+=a.size();}
            LinearLayout p=panel(body);p.addView(text(sb.getValue(),16,WHITE,true));sub(p,courseCount+" cours • "+qCount+" questions");
            p.setOnClickListener(v->{activeSubject=sid;go("CATALOG");});
        }
    }
    private int priorityScore(JSONObject chapter){
        String id=s(chapter,"id");ArrayList<Integer> a=questionsByChapter.get(id);
        if(a==null||a.size()==0)return cardsByChapter.containsKey(id)?20:0;
        int bad=0,done=0;
        for(int x:a){String qid=s(questions.get(x),"id");if(attempts(qid)>0){done++;if(!lastCorrect(qid))bad++;}}
        return bad*25+Math.max(0,40-done)+(done==0?25:0);
    }
    private void subjectFilters(LinearLayout target,Runnable onSelect){
        HorizontalScrollView hsv=new HorizontalScrollView(this);hsv.setHorizontalScrollBarEnabled(false);
        LinearLayout row=horizontal();row.setPadding(0,dp(2),0,dp(9));hsv.addView(row);
        ArrayList<String> names=new ArrayList<>();names.add("Toutes");names.addAll(subjects.values());
        ArrayList<String> ids=new ArrayList<>();ids.add("ALL");ids.addAll(subjects.keySet());
        for(int i=0;i<ids.size();i++){
            final String id=ids.get(i);boolean on=activeSubject.equals(id);
            TextView t=button(names.get(i),on,()->{activeSubject=id;onSelect.run();});
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-2,dp(43));lp.rightMargin=dp(7);row.addView(t,lp);
        }
        add(target,hsv);
    }
    private void showCatalog(){
        heading(body,"Bibliothèque de cours");
        subjectFilters(body,()->go("CATALOG"));
        EditText search=new EditText(this);search.setTextSize(15);search.setSingleLine(true);
        search.setTextColor(WHITE);search.setHintTextColor(MUTED);search.setHint("Rechercher un cours…");
        search.setPadding(dp(13),dp(8),dp(13),dp(8));search.setBackground(bg(PANEL2,0,12));
        add(body,search);
        LinearLayout list=vertical();body.addView(list);
        Runnable update=()->{
            list.removeAllViews();String needle=search.getText().toString().toLowerCase(Locale.ROOT).trim();
            int count=0;
            for(JSONObject c:chapters){
                final String id=s(c,"id"),title=s(c,"title"),sid=s(c,"subjectId");
                if(!activeSubject.equals("ALL")&&!activeSubject.equals(sid))continue;
                if(!needle.isEmpty()&&!(title+" "+subjectName(sid)).toLowerCase(Locale.ROOT).contains(needle))continue;
                LinearLayout p=panel(list);p.addView(text(title,15,WHITE,true));
                int nq=questionsByChapter.containsKey(id)?questionsByChapter.get(id).size():0;
                int nf=cardsByChapter.containsKey(id)?cardsByChapter.get(id).size():0;
                boolean guide=guides!=null&&guides.optJSONObject(id)!=null;
                sub(p,subjectName(sid)+" • "+nq+" Q • "+nf+" cartes • "+(guide?"Fiche structurée (couverture variable)":"Guide non disponible"));
                p.setOnClickListener(v->openLesson(id));count++;
            }
            if(count==0)sub(list,"Aucun cours correspondant.");
        };
        search.addTextChangedListener(new TextWatcher(){
            @Override public void beforeTextChanged(CharSequence t,int s,int c,int a){}
            @Override public void onTextChanged(CharSequence t,int s,int b,int c){update.run();}
            @Override public void afterTextChanged(Editable e){}
        });
        update.run();
    }
    private void openLesson(String id){currentChapter=id;guideMode="ESSENTIAL";boardIndex=0;boardRevealed=true;boardAnswerDraft="";go("LESSON");}
    private boolean isFormulaSubject(String subject){
        return "phys".equals(subject)||"chimie".equals(subject);
    }
    private String compactFormula(String label,String value,String subject){
        String key=label.toLowerCase(java.util.Locale.ROOT);
        String raw=value==null?"":value;
        if("phys".equals(subject)){
            if(key.equals("vitesse")&&raw.contains("lim("))return "v = dx/dt";
            if(key.equals("accélération")&&raw.contains("lim("))return "a = dv/dt";
            if(key.contains("relation fondamentale")&&raw.contains("dp/dt"))return "ΣF = dp/dt";
            if(key.contains("masse constante")&&raw.contains("m·a"))return "ΣF = m × a";
            if(key.equals("quantité de mouvement")&&raw.contains("m·v"))return "p = m × v";
            if(key.contains("système isolé")&&raw.contains("m·v"))return "p = constante";
        }
        String cleaned=raw.replace("ΣF_ext","ΣF").replace("||F||","|F|")
            .replace("×10^","×10").replace("dOM/dt","dx/dt");
        if(cleaned.contains("lim(")||cleaned.contains("δt→0"))return "";
        int equal=cleaned.indexOf(" = ");
        if(equal<0)equal=cleaned.indexOf('=');
        if(equal<0)return "";
        int start=cleaned.lastIndexOf(':',equal);
        if(start>=0)start++;
        else{
            start=Math.max(0,cleaned.lastIndexOf(';',equal)+1);
            int open=cleaned.lastIndexOf('(',equal);
            if(open>=0&&equal-open<18)start=Math.max(start,open+1);
        }
        String eq=cleaned.substring(start).trim();
        int end=eq.indexOf(';');if(end>=0)eq=eq.substring(0,end);
        int avec=eq.indexOf(" avec ");if(avec>0)eq=eq.substring(0,avec);
        int ifrom=eq.indexOf(" où ");if(ifrom>0)eq=eq.substring(0,ifrom);
        int and=eq.indexOf(" et ",eq.indexOf('=')+1);if(and>0)eq=eq.substring(0,and);
        eq=eq.trim();
        if(eq.length()>80||eq.indexOf('=')<0)return "";
        if(eq.indexOf('.')>=0&&eq.indexOf('.')<eq.length()-8)return "";
        return eq;
    }
    private String readableValue(String label,String value,String subject){
        String raw=value==null?"":value.trim();
        if("phys".equals(subject)){
            String low=label.toLowerCase(java.util.Locale.ROOT);
            if(low.equals("vitesse")&&raw.contains("lim("))return "Vitesse instantanée : variation de la position par rapport au temps.";
            if(low.equals("accélération")&&raw.contains("lim("))return "Accélération instantanée : variation de la vitesse par rapport au temps.";
        }
        return raw.replaceAll("\\s*\\[p\\.?\\s*\\d+\\]","").trim();
    }
    private boolean isSequenceSection(String title){
        String n=title.toLowerCase(java.util.Locale.ROOT);
        return n.contains("étape")||n.contains("cycle")||n.contains("processus")||
             n.contains("neurulation")||n.contains("biosynthèse")||n.contains("cascade")||
             n.contains("historique")||n.contains("chronologie")||n.contains("mécanisme");
    }
    private boolean isChronologySection(String title){
        String n=title.toLowerCase(java.util.Locale.ROOT);
        return n.contains("histoire")||n.contains("chronolog")||n.contains("législat")||
               n.contains("évolution")||n.contains("années")||n.contains("historique");
    }
    private void boardRow(LinearLayout parent,String label,String value,boolean alternate){
        boolean longExplanation=value.length()>105||getResources().getConfiguration().fontScale>1.2f;
        LinearLayout row=longExplanation?vertical():horizontal();
        row.setGravity(Gravity.TOP);
        row.setPadding(dp(10),dp(10),dp(10),dp(10));
        row.setBackground(bg(alternate?PANEL2:Color.rgb(21,39,61),0,9));
        TextView left=text(label,14,BLUE,true);
        left.setGravity(Gravity.TOP);
        left.setPadding(0,0,dp(9),longExplanation?dp(5):0);
        if(longExplanation)row.addView(left,new LinearLayout.LayoutParams(-1,-2));
        else row.addView(left,new LinearLayout.LayoutParams(0,-2,0.37f));
        TextView right=text(value,15,WHITE,false);
        right.setGravity(Gravity.TOP);right.setTextIsSelectable(true);
        if(longExplanation)row.addView(right,new LinearLayout.LayoutParams(-1,-2));
        else row.addView(right,new LinearLayout.LayoutParams(0,-2,0.63f));
        add(parent,row);
    }
    private void subjectBoard(LinearLayout parent,String subject,JSONObject section,ArrayList<JSONObject> chosen){
        String title=s(section,"title");
        LinearLayout board=panel(parent);
        heading(board,title);
        if("phys".equals(subject)){
            sub(board,"LOIS ET FORMULES");
            int index=0;
            for(JSONObject item:chosen){
                String label=s(item,"label"),raw=s(item,"value");
                if(raw.isEmpty())raw=s(item,"text");
                String formula=compactFormula(label,raw,subject);
                String infoText=readableValue(label,raw,subject);
                if(!formula.isEmpty()){
                    LinearLayout formulaBox=vertical();
                    formulaBox.setPadding(dp(14),dp(10),dp(14),dp(10));
                    formulaBox.setBackground(bg(PANEL2,0,12));
                    add(formulaBox,text(label,14,BLUE,true));
                    TextView math=text(formula,22,WHITE,true);
                    math.setTextIsSelectable(true);add(formulaBox,math);
                    if(!infoText.equals(formula)&&!infoText.contains("lim(")){
                        if(infoText.length()<155&&!infoText.contains(formula))
                            add(formulaBox,text(infoText,13,MUTED,false));
                    }
                    add(board,formulaBox);
                }else{
                    boardRow(board,label,infoText,index%2==0);
                }
                index++;
            }
            return;
        }
        if("chimie".equals(subject)){
            sub(board,"RÉACTIONS, CONDITIONS ET RÈGLES");
            int index=0;
            for(JSONObject item:chosen){
                String label=s(item,"label"),val=readableValue(label,s(item,"value"),subject);
                if(val.isEmpty())val=readableValue(label,s(item,"text"),subject);
                String formula=compactFormula(label,val,subject);
                if(!formula.isEmpty()){
                    LinearLayout f=vertical();f.setPadding(dp(12),dp(10),dp(12),dp(10));
                    f.setBackground(bg(PANEL2,0,10));
                    add(f,text(label,14,BLUE,true));
                    add(f,text(formula,21,WHITE,true));
                    if(!val.equals(formula)&&val.length()<155)
                        add(f,text(val,13,MUTED,false));
                    add(board,f);
                }else boardRow(board,label,val,index%2==0);
                index++;
            }
            return;
        }
        boolean sequence=isSequenceSection(title);
        boolean chronology=isChronologySection(title)&&"shs".equals(subject);
        String headingType=sequence?"ÉTAPES ET MÉCANISMES":chronology?"REPÈRES CHRONOLOGIQUES":
            "sp".equals(subject)?"DONNÉES ET COMPARAISONS":
            "shs".equals(subject)?"TABLEAU DE MÉMORISATION":
            "histo".equals(subject)?"STRUCTURES ET CARACTÉRISTIQUES":
            "biocell".equals(subject)?"COMPOSANTS ET FONCTIONS":"NOTIONS ET DÉFINITIONS";
        sub(board,headingType);
        for(int i=0;i<chosen.size();i++){
            JSONObject item=chosen.get(i);
            String label=s(item,"label"),val=s(item,"value");
            if(val.isEmpty())val=s(item,"text");
            val=readableValue(label,val,subject);
            if(sequence){
                LinearLayout line=horizontal();
                line.setGravity(Gravity.TOP);
                line.setPadding(dp(10),dp(10),dp(10),dp(10));
                line.setBackground(bg(i%2==0?PANEL2:Color.rgb(21,39,61),0,9));
                TextView num=text(String.format(java.util.Locale.ROOT,"%02d",i+1),16,GREEN,true);
                line.addView(num,new LinearLayout.LayoutParams(dp(38),-2));
                LinearLayout details=vertical();
                add(details,text(label,14,BLUE,true));
                TextView v=text(val,15,WHITE,false);v.setTextIsSelectable(true);add(details,v);
                line.addView(details,new LinearLayout.LayoutParams(0,-2,1f));
                add(board,line);
            }else boardRow(board,label,val,i%2==0);
        }
    }
    private void subjectLesson(){
        JSONObject chapter=byChapter.get(currentChapter);
        if(chapter==null){showCatalog();return;}
        String subject=s(chapter,"subjectId");
        heading(body,s(chapter,"title"));
        if(isMemorySubject(currentChapter)){
            LinearLayout notice=panel(body);
            sub(notice,"SHS, histologie et biologie cellulaire : toutes les données des tableaux originaux doivent être mémorisées.");
            add(notice,button("Réviser les tableaux originaux",true,()->{boardIndex=0;boardRevealed=true;go("BOARDS");}));
        }
        LinearLayout menu=horizontal();
        String[] names={"Essentiel","Complet","Pages","Carte"};
        for(int i=0;i<names.length;i++){
            final int choice=i;
            boolean active=i==0&&"ESSENTIAL".equals(guideMode)||i==1&&"COMPLETE".equals(guideMode);
            TextView tab=button(names[i],active,()->{
                if(choice==2){pageIndex=0;go("PAGES");}
                else if(choice==3){go("MAP");}
                else{guideMode=choice==0?"ESSENTIAL":"COMPLETE";go("LESSON");}
            });
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(47),1);
            if(i<names.length-1)lp.rightMargin=dp(6);
            menu.addView(tab,lp);
        }
        add(body,menu);
        JSONObject guide=guides==null?null:guides.optJSONObject(currentChapter);
        JSONArray sections=arr(guide,"sections");
        if(sections==null||sections.length()==0){
            LinearLayout missing=panel(body);
            sub(missing,"Fiche structurée indisponible. Les pages originales restent accessibles.");
            add(missing,button("Lire la source",true,()->{pageIndex=0;go("PAGES");}));
            return;
        }
        int displayed=0,total=0;
        boolean essential="ESSENTIAL".equals(guideMode);
        int maxPerSection=Math.max(2,56/Math.max(1,sections.length()));
        for(int j=0;j<sections.length();j++){
            JSONObject section=sections.optJSONObject(j);if(section==null)continue;
            JSONArray items=arr(section,"items");if(items==null)continue;
            ArrayList<JSONObject> selected=new ArrayList<>();
            for(int k=0;k<items.length();k++){
                JSONObject item=items.optJSONObject(k);if(item==null)continue;
                String value=s(item,"value");if(value.isEmpty())value=s(item,"text");
                if(value.isEmpty())continue;
                total++;
                if(essential&&item.optInt("priority",1)<2)continue;
                if(essential&&selected.size()>=maxPerSection)continue;
                selected.add(item);displayed++;
            }
            if(!selected.isEmpty())subjectBoard(body,subject,section,selected);
        }
        if(displayed==0)sub(body,"Aucun repère sélectionné. Consulter le mode Complet ou les pages.");
        if(essential)
            sub(body,"Essentiel : "+displayed+" repères sélectionnés. Le mode Complet contient les "+total+" repères structurés actuellement disponibles.");
        else
            sub(body,""+displayed+" repères structurés disponibles. La fidélité et l'exhaustivité doivent être vérifiées contre le cours original.");
    }

    private boolean isMemorySubject(String id){
        JSONObject chapter=byChapter.get(id);
        String subject=s(chapter,"subjectId");
        return subject.equals("shs")||subject.equals("biocell")||subject.equals("histo");
    }
    private void selectBoard(int position,int total){
        if(position<0||position>=total)return;
        boardIndex=position;boardRevealed=true;boardAnswerDraft="";go("BOARDS");
    }
    private void gradeBoard(JSONObject unit,boolean allKnown,int total){
        String id=s(unit,"id");
        int count=prefs.getInt("board/count/"+id,0)+1;
        int streak=allKnown?Math.min(10,prefs.getInt("board/streak/"+id,0)+1):0;
        long days=allKnown?Math.min(45,(long)Math.pow(2,Math.min(5,streak-1))):0;
        prefs.edit().putInt("board/count/"+id,count)
            .putInt("board/streak/"+id,streak)
            .putBoolean("board/known/"+id,allKnown)
            .putLong("board/due/"+id,System.currentTimeMillis()+days*86400000L)
            .apply();
        if(boardIndex+1<total)selectBoard(boardIndex+1,total);
        else{boardRevealed=true;go("BOARDS");}
    }
    private void showBoards(){
        JSONObject course=boardCatalog==null?null:boardCatalog.optJSONObject(currentChapter);
        JSONArray units=arr(course,"items");
        if(units==null||units.length()==0){
            heading(body,chapterTitle(currentChapter));
            sub(body,"Catalogue de tableaux indisponible pour ce chapitre.");
            add(body,button("Source originale",true,()->{pageIndex=0;go("PAGES");}));
            return;
        }
        int total=units.length();
        boardIndex=Math.max(0,Math.min(boardIndex,total-1));
        JSONObject unit=units.optJSONObject(boardIndex);
        if(unit==null){sub(body,"Entree absente.");return;}
        heading(body,chapterTitle(currentChapter));
        sub(body,subjectName(s(byChapter.get(currentChapter),"subjectId"))+" - MEMORISATION EXHAUSTIVE");
        int done=0,due=0;
        for(int j=0;j<total;j++){
            JSONObject u=units.optJSONObject(j);
            if(u==null)continue;
            String id=s(u,"id");
            if(prefs.getBoolean("board/known/"+id,false))done++;
            if(prefs.getLong("board/due/"+id,0L)<=System.currentTimeMillis())due++;
        }
        LinearLayout overview=panel(body);
        info(overview,"Couverture source",total+" unites de memorisation, "+done+" auto-evaluees comme connues, "+due+" a reviser");
        sub(overview,"Tous les details du tableau source comptent. Les reperes d'autocontrole ne remplacent jamais l'image originale.");
        ArrayList<String> names=new ArrayList<>();
        for(int i=0;i<total;i++){
            JSONObject u=units.optJSONObject(i);
            names.add((i+1)+". "+s(u,"title")+(prefs.getBoolean("board/known/"+s(u,"id"),false)?" [revu]":""));
        }
        Spinner spinner=new Spinner(this);
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,names);
        spinner.setAdapter(adapter);
        spinner.setSelection(boardIndex,false);
        spinner.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            @Override public void onItemSelected(android.widget.AdapterView<?> parent,View view,int pos,long id){
                if(pos!=boardIndex)selectBoard(pos,total);
            }
            @Override public void onNothingSelected(android.widget.AdapterView<?> parent){}
        });
        add(body,spinner);
        buttons(body,"Precedent",()->selectBoard(boardIndex-1,total),"Suivant",()->selectBoard(boardIndex+1,total));
        LinearLayout plan=panel(body);
        heading(plan,(s(unit,"scope").equals("source_board")?"Tableau ":"Planche source ")+(boardIndex+1)+" / "+total);
        info(plan,"Intitule et emplacement",s(unit,"title")+" | page originale "+unit.optInt("sourcePage"));
        sub(plan,"Rendre toutes les informations avec leur organisation dans le bon tableau.");
        if(!boardRevealed){
            sub(plan,"Exercice a blanc : sans ouvrir la source, restituez toutes les lignes, colonnes, defininitions, dates, noms, exemples, conditions et exceptions.");
            EditText recall=new EditText(this);recall.setTextColor(WHITE);recall.setHintTextColor(MUTED);
            recall.setTextSize(15);recall.setHint("Restitution de memoire (integrale)...");
            recall.setGravity(Gravity.TOP);recall.setMinLines(5);recall.setText(boardAnswerDraft);
            recall.setPadding(dp(12),dp(12),dp(12),dp(12));recall.setBackground(bg(PANEL2,0,10));
            add(plan,recall);
            add(plan,button("Reveler la source pour correction",true,()->{
                boardAnswerDraft=recall.getText().toString();
                boardRevealed=true;go("BOARDS");
            }));
        }else{
            add(plan,button("MASQUER LA SOURCE ET RECITER",true,()->{boardRevealed=false;go("BOARDS");}));
            sub(body,"SOURCE ORIGINALE : toutes les cases et l'ordre d'origine. Zoom par pincement.");
            String crop=s(unit,"crop"),original=s(unit,"source");
            if(!crop.isEmpty())drawImage(crop);
            else if(!original.isEmpty())drawImage(original);
            else sub(body,"Image source absente.");
            int originalPage=unit.optInt("sourcePage",1);
            add(body,button("Afficher la page integrale du cours",false,()->{pageIndex=originalPage-1;go("PAGES");}));
            LinearLayout review=panel(body);
            heading(review,"Correction exhaustive - liste de controle");
            sub(review,"Une case cochee signifie que vous avez restitue sans regarder la source. Ne cochez pas si un element est absent.");
            ArrayList<CheckBox> checks=new ArrayList<>();
            JSONArray cues=arr(unit,"checkpoints");
            if(cues!=null)for(int j=0;j<cues.length();j++){
                String cue=cues.optString(j);
                if(cue.isEmpty())continue;
                CheckBox c=new CheckBox(this);c.setText(cue);c.setTextSize(14);c.setTextColor(WHITE);
                c.setButtonTintList(android.content.res.ColorStateList.valueOf(BLUE));
                add(review,c);checks.add(c);
            }
            String[] required={
                "Toutes les lignes, colonnes, rubriques et leurs positions",
                "Chaque information de chaque case du tableau",
                "Dates, noms, chiffres, definitions et comparaisons",
                "Toutes les nuances, conditions, exceptions et exemples",
                "Restitution sans aucune omission et avec le bon tableau"
            };
            for(String label:required){
                CheckBox c=new CheckBox(this);c.setText(label);c.setTextSize(14);c.setTextColor(WHITE);
                c.setButtonTintList(android.content.res.ColorStateList.valueOf(BLUE));
                add(review,c);checks.add(c);
            }
            if(!boardAnswerDraft.isEmpty())info(review,"Votre restitution avant correction",boardAnswerDraft);
            TextView pass=button("J'AI TOUT RESTITUE : REVISION ESPACEE",true,()->gradeBoard(unit,true,total));
            pass.setEnabled(false);pass.setAlpha(.42f);
            for(CheckBox c:checks)c.setOnCheckedChangeListener((v,checked)->{
                boolean all=true;
                for(CheckBox box:checks){if(!box.isChecked()){all=false;break;}}
                pass.setEnabled(all);pass.setAlpha(all?1f:.42f);
            });
            add(review,pass);
            add(review,button("OUBLI OU ERREUR - RECOMMENCER",false,()->gradeBoard(unit,false,total)));
            sub(review,"Score = declaration personnelle apres comparaison. Aucune notation automatique de votre restitution n'est pretendue.");
        }
        buttons(body,"Cours structuré (tous les détails saisis)",()->{guideMode="COMPLETE";go("LESSON");},"Questions du cours",()->startQuiz(currentChapter));
    }

    private InputStream media(String rel)throws IOException {
        if(rel==null||rel.isEmpty())throw new FileNotFoundException("Media absent");
        String name=rel.startsWith("www/")?rel:"www/"+rel;
        return getAssets().open(name,AssetManager.ACCESS_STREAMING);
    }
    private void showPages(boolean map){
        heading(body,chapterTitle(currentChapter));
        if(map){showConceptMap();return;}
        JSONArray pages=mediaPages==null?null:mediaPages.optJSONArray(currentChapter);
        JSONObject meta=courseMeta==null?null:courseMeta.optJSONObject(currentChapter);
        String pdf=courseAssets==null?"":courseAssets.optString(currentChapter,"");
        if(pdf.isEmpty()&&meta!=null){JSONObject imp=meta.optJSONObject("importedFullFC");if(imp!=null)pdf=s(imp,"pdf");}
        if(pages!=null&&pages.length()>0){
            if(pageIndex>=pages.length())pageIndex=pages.length()-1;
            sub(body,"Pages du cours original : "+pages.length()+" • pincez pour agrandir");
            showPager(body,pages.length(),false);
            drawImage(pages.optString(pageIndex));
        }else if(!pdf.isEmpty()){
            sub(body,"PDF original • rendu Android PdfRenderer");
            String pdfPath=pdf;drawPdf(pdfPath);
        }else{
            sub(body,"Les pages originales de ce cours ne sont pas présentes dans le paquet récupéré.");
        }
    }
    private int mapSectionIndex=0;
    private ArrayList<JSONObject> mapBranches(){
        ArrayList<JSONObject> out=new ArrayList<>();
        JSONObject guide=guides==null?null:guides.optJSONObject(currentChapter);
        JSONArray sections=arr(guide,"sections");
        if(sections!=null)for(int i=0;i<sections.length();i++){
            JSONObject sec=sections.optJSONObject(i);
            if(sec!=null&&arr(sec,"items")!=null&&arr(sec,"items").length()>0)out.add(sec);
        }
        return out;
    }
    private void showConceptMap(){
        String courseName=chapterTitle(currentChapter);
        JSONObject chapter=byChapter.get(currentChapter);
        String subject=s(chapter,"subjectId");
        ArrayList<JSONObject> branches=mapBranches();
        heading(body,"Carte des notions");
        LinearLayout center=panel(body);
        TextView hub=text(courseName,19,WHITE,true);
        hub.setGravity(Gravity.CENTER);
        hub.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        hub.setPadding(dp(12),dp(15),dp(12),dp(15));
        hub.setBackground(bg(PANEL2,BLUE,17));
        add(center,hub);
        TextView caption=text(branches.size()+" branches — sélectionnez un domaine",13,MUTED,false);
        caption.setGravity(Gravity.CENTER);add(center,caption);
        View connector=new View(this);connector.setBackgroundColor(BLUE);
        LinearLayout.LayoutParams conn=new LinearLayout.LayoutParams(dp(3),dp(17));
        conn.gravity=Gravity.CENTER_HORIZONTAL;body.addView(connector,conn);
        if(isMemorySubject(currentChapter)){
            JSONObject pack=boardCatalog==null?null:boardCatalog.optJSONObject(currentChapter);
            JSONArray units=arr(pack,"items");
            if(units!=null&&units.length()>0){
                add(body,button("Tableaux / planches sources : "+units.length(),true,()->{
                    boardIndex=0;boardRevealed=true;go("BOARDS");
                }));
            }
        }
        if(branches.size()==0){
            LinearLayout unavailable=panel(body);
            sub(unavailable,"Pas de branches structurées disponibles : consultez la source originale.");
            add(unavailable,button("Pages originales",true,()->{pageIndex=0;go("PAGES");}));
            return;
        }
        for(int i=0;i<branches.size();i+=2){
            LinearLayout row=horizontal();row.setGravity(Gravity.TOP);
            for(int col=0;col<2;col++){
                int idx=i+col;
                if(idx>=branches.size()){
                    row.addView(new View(this),new LinearLayout.LayoutParams(0,dp(8),1));continue;
                }
                JSONObject sec=branches.get(idx);
                JSONArray items=arr(sec,"items");
                LinearLayout box=vertical();
                box.setPadding(dp(12),dp(12),dp(12),dp(12));
                box.setBackground(bg(PANEL,Color.rgb(58,84,119),14));
                TextView ordinal=text(String.format(Locale.ROOT,"%02d",idx+1),13,GREEN,true);
                add(box,ordinal);
                TextView name=text(s(sec,"title"),15,WHITE,true);add(box,name);
                StringBuilder shortList=new StringBuilder();
                if(items!=null){
                    for(int j=0;j<Math.min(3,items.length());j++){
                        JSONObject item=items.optJSONObject(j);
                        if(item==null)continue;
                        if(shortList.length()>0)shortList.append("\n");
                        shortList.append("• ").append(s(item,"label"));
                    }
                }
                TextView sample=text(shortList.toString(),12,MUTED,false);
                sample.setMaxLines(6);add(box,sample);
                add(box,button("Ouvrir",false,()->{mapSectionIndex=idx;go("MAP_DETAIL");}));
                LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,-2,1);
                if(col==0)lp.rightMargin=dp(9);
                row.addView(box,lp);
            }
            add(body,row);
        }
        sub(body,"Chaque branche s'ouvre en tableau lisible, sans image à agrandir.");
        add(body,button("Lire les pages originales",false,()->{pageIndex=0;go("PAGES");}));
    }
    private void showConceptBranch(){
        ArrayList<JSONObject> branches=mapBranches();
        if(branches.isEmpty()){go("MAP");return;}
        mapSectionIndex=Math.min(branches.size()-1,Math.max(0,mapSectionIndex));
        JSONObject section=branches.get(mapSectionIndex);
        JSONObject chapter=byChapter.get(currentChapter);
        String subject=s(chapter,"subjectId");
        heading(body,chapterTitle(currentChapter));
        sub(body,"Notion "+(mapSectionIndex+1)+" / "+branches.size());
        buttons(body,"← Carte",()->go("MAP"),"Pages originales",()->{pageIndex=0;go("PAGES");});
        JSONArray items=arr(section,"items");
        ArrayList<JSONObject> content=new ArrayList<>();
        if(items!=null)for(int j=0;j<items.length();j++){
            JSONObject it=items.optJSONObject(j);if(it!=null)content.add(it);
        }
        subjectBoard(body,subject,section,content);
        buttons(body,"← Précédent",()->{mapSectionIndex=Math.max(0,mapSectionIndex-1);go("MAP_DETAIL");},
                "Suivant →",()->{mapSectionIndex=Math.min(branches.size()-1,mapSectionIndex+1);go("MAP_DETAIL");});
        if(isMemorySubject(currentChapter))
            add(body,button("Mémorisation des tableaux originaux",true,()->{boardIndex=0;boardRevealed=true;go("BOARDS");}));
    }

    private void showPager(LinearLayout target,int n,boolean map){
        buttons(target,"◀ Page précédente",()->{if(pageIndex>0){pageIndex--;go(map?"MAP":"PAGES");}},
                "Page suivante ▶",()->{if(pageIndex<n-1){pageIndex++;go(map?"MAP":"PAGES");}});
        sub(target,(pageIndex+1)+" / "+n);
    }
    private void drawImage(String path){
        final ZoomImageView image=new ZoomImageView(this);
        image.setBackground(bg(PANEL,Color.rgb(45,67,94),12));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(560));body.addView(image,lp);
        image.setTag(path);
        new Thread(()->{
            try(InputStream in=media(path)){
                BitmapFactory.Options o=new BitmapFactory.Options();o.inJustDecodeBounds=true;
                try(InputStream dims=media(path)){BitmapFactory.decodeStream(dims,null,o);}
                int sample=1;while(o.outWidth/sample>2400||o.outHeight/sample>3400)sample*=2;
                BitmapFactory.Options opts=new BitmapFactory.Options();opts.inSampleSize=sample;
                Bitmap b=BitmapFactory.decodeStream(in,null,opts);
                if(b==null)throw new IOException("Image absente");
                runOnUiThread(()->{if(path.equals(image.getTag()))image.load(b);else b.recycle();});
            }catch(Exception e){runOnUiThread(()->sub(body,"Image indisponible : "+path));}
        },"NativeImage").start();
    }
    private void drawPdf(String path){
        LinearLayout status=panel(body);status.addView(text("Ouverture du PDF original…",14,MUTED,false));
        new Thread(()->{
            try {
                File target=new File(getCacheDir(),"course_"+currentChapter.replaceAll("[^a-zA-Z0-9]","")+".pdf");
                if(!target.exists()||target.length()==0)try(InputStream in=media(path);OutputStream out=new FileOutputStream(target)){
                    byte[] buf=new byte[32768];int n;while((n=in.read(buf))!=-1)out.write(buf,0,n);
                }
                try(ParcelFileDescriptor fd=ParcelFileDescriptor.open(target,ParcelFileDescriptor.MODE_READ_ONLY);
                    PdfRenderer pdf=new PdfRenderer(fd)){
                    int count=pdf.getPageCount();int pos=Math.min(Math.max(0,pageIndex),count-1);
                    try(PdfRenderer.Page page=pdf.openPage(pos)){
                        float ratio=(float)page.getHeight()/Math.max(1,page.getWidth());
                        int w=1200,h=Math.min(2600,Math.max(1,(int)(w*ratio)));
                        Bitmap b=Bitmap.createBitmap(w,h,Bitmap.Config.ARGB_8888);
                        b.eraseColor(Color.WHITE);page.render(b,null,null,PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY);
                        runOnUiThread(()->{
                            status.removeAllViews();sub(status,"PDF page "+(pos+1)+" / "+count);
                            buttons(status,"◀",()->{pageIndex=Math.max(0,pageIndex-1);go("PAGES");}, "▶",()->{pageIndex=Math.min(count-1,pageIndex+1);go("PAGES");});
                            ZoomImageView im=new ZoomImageView(this);status.addView(im,new LinearLayout.LayoutParams(-1,dp(560)));im.load(b);
                        });
                    }
                }
            }catch(Exception e){runOnUiThread(()->info(status,"PDF non disponible",e.toString()));}
        },"NativePdf").start();
    }
    private void showPick(boolean quiz){
        heading(body,quiz?"Choisir les questions":"Choisir les flashcards");
        sub(body,quiz?"QCM A–E avec corrections par proposition ; QROC SHS exhaustives.":"Cartes à rappel actif, échéances locales et autoévaluation.");
        subjectFilters(body,()->go(quiz?"QUIZ_PICK":"CARD_PICK"));
        ArrayList<Integer> together=new ArrayList<>();
        for(JSONObject ch:chapters)if(activeSubject.equals("ALL")||activeSubject.equals(s(ch,"subjectId"))){
            ArrayList<Integer> list=(quiz?questionsByChapter:cardsByChapter).get(s(ch,"id"));if(list!=null)together.addAll(list);
        }
        if(!together.isEmpty()){
            LinearLayout all=panel(body);
            all.addView(text("Session multi-cours",17,WHITE,true));
            sub(all,together.size()+(quiz?" questions":" flashcards")+" dans les matières sélectionnées.");
            add(all,button("Commencer • sélection complète",true,()->{if(quiz)launchQuiz(together);else launchCards(together);}));
        }
        for(JSONObject c:chapters){
            String id=s(c,"id"),sid=s(c,"subjectId");
            if(!activeSubject.equals("ALL")&&!activeSubject.equals(sid))continue;
            ArrayList<Integer> list=(quiz?questionsByChapter:cardsByChapter).get(id);
            if(list==null||list.isEmpty())continue;
            LinearLayout pp=panel(body);pp.addView(text(s(c,"title"),15,WHITE,true));
            sub(pp,subjectName(sid)+" • "+list.size()+(quiz?" questions":" cartes"));
            pp.setOnClickListener(v->{if(quiz)startQuiz(id);else startCards(id);});
        }
    }
    private void startQuiz(String id){
        ArrayList<Integer> items=questionsByChapter.get(id);
        if(items==null||items.isEmpty()){currentChapter=id;go("QUIZ_PICK");return;}
        launchQuiz(items);
    }
    private void launchQuiz(List<Integer> ids){
        sessionQuestions.clear();sessionQuestions.addAll(ids);
        if(sessionQuestions.size()>20){
            int offset=prefs.getInt("quizoffset/"+ids.hashCode(),0)%sessionQuestions.size();
            Collections.rotate(sessionQuestions,-offset);
            sessionQuestions.subList(20,sessionQuestions.size()).clear();
            prefs.edit().putInt("quizoffset/"+ids.hashCode(),offset+20).apply();
        }
        quizIndex=0;quizCorrect=0;quizAnswered=0;questionStarted=SystemClock.elapsedRealtime();
        go("QUIZ");
    }
    private void showQuiz(){
        if(quizIndex>=sessionQuestions.size()){
            heading(body,"Session terminée");
            info(body,"Résultat",quizCorrect+" / "+quizAnswered+" questions évaluées");
            buttons(body,"Nouvelle session",()->go("QUIZ_PICK"),"Cours",()->go("CATALOG"));return;
        }
        JSONObject q=questions.get(sessionQuestions.get(quizIndex));
        String chap=s(q,"chapterId");boolean qroc="QROC".equalsIgnoreCase(s(q,"format"));
        sub(body,subjectName(s(q,"subjectId"))+" • "+chapterTitle(chap));
        heading(body,"Question "+(quizIndex+1)+" / "+sessionQuestions.size()+(qroc?" • QROC":" • A–E"));
        LinearLayout p=panel(body);
        TextView stem=text(s(q,"stem"),17,WHITE,true);add(p,stem);
        LinearLayout feedback=vertical();
        if(qroc){
            EditText answer=new EditText(this);answer.setTextColor(WHITE);answer.setTextSize(15);
            answer.setHintTextColor(MUTED);answer.setHint("Écrire votre réponse ici…");
            answer.setMinLines(5);answer.setGravity(Gravity.TOP);answer.setBackground(bg(PANEL2,0,10));answer.setPadding(dp(12),dp(12),dp(12),dp(12));add(p,answer);
            add(p,button("Afficher les éléments attendus",true,()->{
                if(feedback.getChildCount()>0)return;
                JSONArray pts=arr(q,"expectedPoints");heading(feedback,"Correction : éléments attendus");
                if(pts!=null)for(int i=0;i<pts.length();i++)info(feedback,"Point "+(i+1),pts.optString(i));
                String extra=s(q,"explanation");if(!extra.isEmpty())sub(feedback,extra);
                buttons(feedback,"À revoir",()->finishQuizQuestion(q,false),"Réponse conforme",()->finishQuizQuestion(q,true));
            }));
        }else{
            CheckBox[] boxes=new CheckBox[5];JSONArray options=arr(q,"options");
            for(int i=0;i<5;i++){
                CheckBox box=new CheckBox(this);boxes[i]=box;
                box.setText((char)('A'+i)+". "+(options!=null?options.optString(i):""));
                box.setTextSize(15);box.setTextColor(WHITE);box.setButtonTintList(android.content.res.ColorStateList.valueOf(BLUE));
                box.setPadding(dp(6),dp(9),dp(5),dp(9));box.setBackground(bg(PANEL2,0,9));add(p,box);
            }
            add(p,button("Valider les réponses",true,()->{
                if(feedback.getChildCount()>0)return;
                JSONArray correct=arr(q,"correct");boolean[] keys=new boolean[5];
                if(correct!=null)for(int i=0;i<correct.length();i++){int idx=correct.optInt(i,-1);if(idx>=0&&idx<5)keys[idx]=true;}
                boolean okay=true;for(int i=0;i<5;i++)if(boxes[i].isChecked()!=keys[i])okay=false;
                final boolean result=okay;
                for(CheckBox box:boxes)box.setEnabled(false);
                heading(feedback,okay?"Réponse correcte":"À revoir");
                JSONArray rationales=arr(q,"optionRationales");
                for(int i=0;i<5;i++){
                    String label=(char)('A'+i)+(keys[i]?" ✓ Vrai":" ✗ Faux");
                    String rationale=rationales!=null?rationales.optString(i):"";
                    info(feedback,label,rationale.isEmpty()?"Voir la correction.":rationale);
                }
                String exp=s(q,"explanation");if(!exp.isEmpty())info(feedback,"Explication",exp);
                JSONObject source=obj(q,"source");if(source!=null){String pg=source.has("page")?" • p. "+source.optInt("page"):"";sub(feedback,"Source : "+s(source,"kind")+pg);}
                add(feedback,button("Question suivante",true,()->finishQuizQuestion(q,result)));
            }));
        }
        add(p,feedback);
        buttons(body,"Revenir aux questions",()->go("QUIZ_PICK"),"Ouvrir ce cours",()->openLesson(chap));
    }
    private void finishQuizQuestion(JSONObject q,boolean correct){
        recordAnswer(q,correct,SystemClock.elapsedRealtime()-questionStarted);
        quizAnswered++;if(correct)quizCorrect++;quizIndex++;questionStarted=SystemClock.elapsedRealtime();go("QUIZ");
    }
    private void startCards(String id){
        ArrayList<Integer> items=cardsByChapter.get(id);
        if(items==null||items.isEmpty()){go("CARD_PICK");return;}launchCards(items);
    }
    private void launchCards(List<Integer> ids){
        sessionCards.clear();sessionCards.addAll(ids);
        long now=System.currentTimeMillis();
        sessionCards.sort((a,b)->{
            long x=prefs.getLong("cd/"+s(cards.get(a),"id"),0L),y=prefs.getLong("cd/"+s(cards.get(b),"id"),0L);
            return Long.compare(x,y);
        });
        if(sessionCards.size()>50)sessionCards.subList(50,sessionCards.size()).clear();
        cardIndex=0;cardReviewed=0;go("CARDS");
    }
    private TextView gradeFlashButton(String label,int fill,int outline,int ink,JSONObject card,int grade){
        TextView b=text(label,17,ink,true);
        b.setGravity(Gravity.CENTER);
        b.setPadding(dp(8),dp(12),dp(8),dp(12));
        b.setMinHeight(dp(57));
        b.setBackground(bg(fill,outline,12));
        b.setOnClickListener(v->gradeCard(card,grade));
        return b;
    }
    private void showCard(){
        if(cardIndex>=sessionCards.size()){
            LinearLayout done=panel(body);
            heading(done,"Session terminee");
            info(done,"Flashcards revisees",String.valueOf(cardReviewed));
            buttons(done,"Nouvelle session",()->go("CARD_PICK"),"Cours",()->go("CATALOG"));
            return;
        }
        JSONObject card=cards.get(sessionCards.get(cardIndex));
        String chapter=s(card,"chapterId");
        String q=s(card,"question"),a=s(card,"answer");
        LinearLayout status=horizontal();
        TextView topic=text(subjectName(s(card,"subjectId")),13,BLUE,true);
        topic.setPadding(dp(9),dp(7),dp(9),dp(7));
        topic.setBackground(bg(PANEL2,0,15));
        status.addView(topic,new LinearLayout.LayoutParams(0,-2,1));
        TextView count=text((cardIndex+1)+" / "+sessionCards.size(),14,MUTED,true);
        count.setGravity(Gravity.RIGHT|Gravity.CENTER_VERTICAL);
        status.addView(count,new LinearLayout.LayoutParams(0,-2,1));
        add(body,status);
        TextView course=text(chapterTitle(chapter),13,MUTED,false);add(body,course);
        LinearLayout outer=panel(body);
        LinearLayout face=vertical();
        face.setPadding(dp(17),dp(20),dp(17),dp(13));
        face.setBackground(bg(PANEL,Color.rgb(67,92,126),22));
        face.setMinimumHeight(dp(302));
        face.setGravity(Gravity.CENTER);
        TextView fact=text(q,21,WHITE,true);
        fact.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        fact.setGravity(Gravity.CENTER);
        LinearLayout.LayoutParams factLp=new LinearLayout.LayoutParams(-1,dp(242));
        face.addView(fact,factLp);
        TextView hint=text("Touchez pour voir la reponse",13,MUTED,false);
        hint.setGravity(Gravity.CENTER);
        face.addView(hint,new LinearLayout.LayoutParams(-1,dp(35)));
        final boolean[] flipped={false};
        face.setOnClickListener(v->{
            flipped[0]=!flipped[0];
            fact.setText(flipped[0]?a:q);
            fact.setTextSize(flipped[0]?20:21);
            fact.setTypeface(null,flipped[0]?0:1);
            hint.setText(flipped[0]?"Touchez pour revoir la question":"Touchez pour voir la reponse");
        });
        add(outer,face);
        LinearLayout grades=vertical();
        String[] labs={"A revoir","Difficile","Bien","Facile"};
        int[] fills={Color.rgb(67,30,39),Color.rgb(68,53,32),Color.rgb(28,69,51),Color.rgb(145,176,255)};
        int[] outlines={Color.rgb(137,67,78),Color.rgb(138,110,64),Color.rgb(65,138,99),BLUE};
        int[] inks={WHITE,WHITE,WHITE,BG};
        for(int row=0;row<2;row++){
            LinearLayout line=horizontal();
            for(int col=0;col<2;col++){
                int grade=row*2+col;
                TextView b=gradeFlashButton(labs[grade],fills[grade],outlines[grade],inks[grade],card,grade);
                LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(59),1);
                if(col==0)lp.rightMargin=dp(8);
                line.addView(b,lp);
            }
            LinearLayout.LayoutParams rowLp=new LinearLayout.LayoutParams(-1,dp(59));
            if(row==0)rowLp.bottomMargin=dp(8);
            grades.addView(line,rowLp);
        }
        add(outer,grades);
        sub(body,"Une question, un fait, une reponse courte. Noter selon la memoire.");
    }
    private void gradeCard(JSONObject c,int choice){
        String id=s(c,"id");int n=prefs.getInt("cr/"+id,0)+1;
        long days=choice==0?0:choice==1?1:choice==2?Math.min(30,Math.max(2,n*3)):Math.min(90,Math.max(4,n*7));
        long due=System.currentTimeMillis()+days*86400000L;
        SharedPreferences.Editor e=prefs.edit();e.putInt("cr/"+id,n);e.putLong("cd/"+id,due);e.putInt("cg/"+id,choice);e.apply();
        cardReviewed++;cardIndex++;go("CARDS");
    }
    @Override public void onBackPressed(){
        if(screen.equals("LESSON")||screen.equals("BOARDS")||screen.equals("QUIZ_PICK")||screen.equals("CARD_PICK")||screen.equals("CATALOG"))go("HOME");
        else if(screen.equals("PAGES")||screen.equals("MAP"))go("LESSON");
        else if(screen.equals("MAP_DETAIL"))go("MAP");
        else if(screen.equals("QUIZ"))go("QUIZ_PICK");
        else if(screen.equals("CARDS"))go("CARD_PICK");
        else super.onBackPressed();
    }
    private final class ZoomImageView extends androidxPlaceholderImageView {
        private final Matrix matrix=new Matrix();
        private final ScaleGestureDetector detector;
        private float scale=1f,min=1f,max=5f;
        private float lastX,lastY;
        private boolean dragging=false;
        private Bitmap bitmap;
        ZoomImageView(Context ctx){
            super(ctx);setScaleType(ScaleType.MATRIX);
            detector=new ScaleGestureDetector(ctx,new ScaleGestureDetector.SimpleOnScaleGestureListener(){
                @Override public boolean onScale(ScaleGestureDetector d){
                    float f=Math.min(max/scale,Math.max(min/scale,d.getScaleFactor()));
                    scale*=f;matrix.postScale(f,f,d.getFocusX(),d.getFocusY());setImageMatrix(matrix);return true;
                }
            });
        }
        void load(Bitmap b){
            Bitmap old=bitmap;bitmap=b;setImageBitmap(b);
            if(old!=null&&old!=b&&!old.isRecycled())old.recycle();
            post(()->{
                if(bitmap!=b||getWidth()==0)return;
                matrix.reset();float fit=Math.min((float)getWidth()/b.getWidth(),(float)getHeight()/b.getHeight());
                float tx=(getWidth()-fit*b.getWidth())/2f,ty=(getHeight()-fit*b.getHeight())/2f;
                matrix.postScale(fit,fit);matrix.postTranslate(tx,ty);scale=1f;setImageMatrix(matrix);
            });
        }
        @Override public boolean onTouchEvent(MotionEvent ev){
            detector.onTouchEvent(ev);
            switch(ev.getActionMasked()){
                case MotionEvent.ACTION_DOWN:lastX=ev.getX();lastY=ev.getY();dragging=true;getParent().requestDisallowInterceptTouchEvent(true);return true;
                case MotionEvent.ACTION_MOVE:
                    if(dragging&&!detector.isInProgress()&&ev.getPointerCount()==1){
                        float dx=ev.getX()-lastX,dy=ev.getY()-lastY;
                        if(scale>1.01f){matrix.postTranslate(dx,dy);setImageMatrix(matrix);}
                        lastX=ev.getX();lastY=ev.getY();
                    }return true;
                case MotionEvent.ACTION_UP:
                    dragging=false;performClick();return true;
                case MotionEvent.ACTION_CANCEL:dragging=false;return true;
            }
            return true;
        }
        @Override public boolean performClick(){super.performClick();return true;}
    }
    private static class androidxPlaceholderImageView extends ImageView {
        androidxPlaceholderImageView(Context c){super(c);}
    }
}
