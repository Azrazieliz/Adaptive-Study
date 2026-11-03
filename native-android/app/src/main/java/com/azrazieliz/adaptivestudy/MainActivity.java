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
    private long questionStarted=0L, questionActiveMs=0L;
    private double quizScore=0.0;
    private boolean questionFinalized=false;
    private TextView questionClock;
    private final android.os.Handler quizHandler=new android.os.Handler(android.os.Looper.getMainLooper());
    private final Runnable clockUpdater=new Runnable(){
        @Override public void run(){
            if(questionClock!=null&&"QUIZ".equals(screen)&&quizIndex<sessionQuestions.size()){
                JSONObject q=questions.get(sessionQuestions.get(quizIndex));
                long elapsed=activeQuestionMs()/1000;
                int target=targetSeconds(q);
                long remaining=target-elapsed;
                String time=fmtSeconds(Math.abs(remaining));
                questionClock.setText((remaining>=0?"Temps restant : ":"Dépassement : +")+time+
                    "   •   cible "+fmtSeconds(target));
                questionClock.setTextColor(remaining>=0?GREEN:RED);
            }
            quizHandler.postDelayed(this,1000);
        }
    };
    private final ArrayList<Integer> sessionQuestions=new ArrayList<>(), sessionCards=new ArrayList<>();
    private final Random random=new Random();

    private String installedVersion(){try{return getPackageManager().getPackageInfo(getPackageName(),0).versionName;}catch(Exception e){return "native";}}
    private long activeQuestionMs(){
        return questionActiveMs+(questionStarted>0?Math.max(0,SystemClock.elapsedRealtime()-questionStarted):0);
    }
    private static String fmtSeconds(long n){
        return String.format(Locale.FRANCE,"%02d:%02d",n/60,n%60);
    }
    private JSONObject subjectMetadata(String id){
        JSONArray a=arr(corpus,"subjects");
        if(a!=null)for(int i=0;i<a.length();i++){
            JSONObject s=a.optJSONObject(i);
            if(s!=null&&id.equals(s.optString("id")))return s;
        }
        return null;
    }
    private int coefficient(String id){
        JSONObject subj=subjectMetadata(id);
        return subj==null?1:subj.optInt("coefficient",1);
    }
    private int targetSeconds(JSONObject q){
        if("QROC".equalsIgnoreCase(s(q,"format")))return 600;
        JSONObject subj=subjectMetadata(s(q,"subjectId"));
        JSONObject exam=obj(subj,"exam");
        if(exam!=null&&exam.optDouble("approxItems",0)>0&&exam.optDouble("durationMin",0)>0)
            return Math.max(10,(int)Math.round(60*exam.optDouble("durationMin")/exam.optDouble("approxItems")));
        return 90;
    }
    @Override protected void onPause(){
        if("QUIZ".equals(screen)&&!questionFinalized&&questionStarted>0){
            questionActiveMs+=Math.max(0,SystemClock.elapsedRealtime()-questionStarted);
            questionStarted=0;
        }
        super.onPause();
    }
    @Override protected void onResume(){
        super.onResume();
        if("QUIZ".equals(screen)&&!questionFinalized&&questionStarted==0&&quizIndex<sessionQuestions.size())
            questionStarted=SystemClock.elapsedRealtime();
    }
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
        quizHandler.post(clockUpdater);
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
                loadComprehensionGuides();
                loadFullLessonIndexes();
                loadExpertComprehension();
                runOnUiThread(this::render);
            }catch(Exception e){
                runOnUiThread(()->{root.removeAllViews();TextView err=text("Impossible de charger les cours hors ligne : "+e,16,RED,false);root.addView(err);});
            }
        },"NativeCorpus").start();
    }
    private int completeSectionIndex=0;
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
    private JSONObject essentialSelection,completePageIndex;
    private void loadFullLessonIndexes()throws Exception{
        essentialSelection=readJsonAsset("essential_study_selection_v3310.json").optJSONObject("courses");
        completePageIndex=readJsonAsset("complete_source_page_index_v3310.json").optJSONObject("courses");
    }
    private JSONObject readJsonAsset(String path)throws Exception{
        try(InputStream in=getAssets().open(path);
            ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] b=new byte[32768];int n;
            while((n=in.read(b))!=-1)out.write(b,0,n);
            return new JSONObject(new String(out.toByteArray(),"UTF-8"));
        }
    }
    private void showCompleteSourceReader(JSONArray originalPages,JSONObject guide,String subject){
        if(!completeSourceMode){
            showCompleteStructuredText(guide,originalPages,subject);
            return;
        }
        heading(body,"Pages FC — contrôle de la source");
        int n=originalPages==null?0:originalPages.length();
        JSONObject entry=completePageIndex==null?null:completePageIndex.optJSONObject(currentChapter);
        JSONObject meta=courseMeta==null?null:courseMeta.optJSONObject(currentChapter);
        LinearLayout summary=panel(body);
        info(summary,"Pages du cours",String.valueOf(n));
        JSONArray all=arr(guide,"sections");
        int count=0;
        if(all!=null)for(int j=0;j<all.length();j++){
            JSONArray items=arr(all.optJSONObject(j),"items");
            if(items!=null)count+=items.length();
        }
        info(summary,"Notions structurées",String.valueOf(count));
        sub(summary,"Le mode Complet contient les images originales de chaque page et les notions déjà transcrites. Les pages non encore textualisées restent consultables dans leur intégralité.");
        if(meta!=null&&meta.optBoolean("isComposite",false)){
            JSONArray related=arr(meta,"compositeParts");
            sub(summary,"Regroupement thématique de FC déjà fournies — chaque page conserve son cours d'origine.");
            if(related!=null)for(int i=0;i<related.length();i++){
                JSONObject part=related.optJSONObject(i);if(part==null)continue;
                String id=s(part,"sourceChapter");
                add(summary,button(s(part,"sourceTitle")+" — "+part.optInt("pages")+" pages",false,()->openLesson(id)));
            }
        }
        buttons(summary,"Revenir au cours structuré",()->{
                completeSourceMode=false;go("LESSON");},
            "Comprendre",()->{guideMode="UNDERSTAND";go("LESSON");});
        if(n<=0){sub(body,"Source complète non disponible dans cette entrée.");return;}
        int perView=2;
        pageIndex=Math.max(0,Math.min(n-1,pageIndex));
        int start=(pageIndex/perView)*perView;
        int end=Math.min(n,start+perView);
        LinearLayout navPanel=panel(body);
        heading(navPanel,"Pages "+(start+1)+" à "+end+" sur "+n);
        buttons(navPanel,"◀ Pages précédentes",()->{
            pageIndex=Math.max(0,start-perView);go("LESSON");
        },"Pages suivantes ▶",()->{
            pageIndex=Math.min(n-1,start+perView);go("LESSON");
        });
        LinearLayout jump=horizontal();
        EditText number=new EditText(this);
        number.setSingleLine(true);
        number.setInputType(android.text.InputType.TYPE_CLASS_NUMBER);
        number.setText(String.valueOf(start+1));
        number.setHint("Page 1–"+n);
        number.setTextColor(WHITE);
        number.setTextSize(16);
        number.setBackground(bg(PANEL2,0,9));
        number.setPadding(dp(13),dp(9),dp(13),dp(9));
        jump.addView(number,new LinearLayout.LayoutParams(0,dp(48),1));
        TextView go=button("Aller à la page",true,()->{
            int next;
            try{next=Integer.parseInt(number.getText().toString().trim());}
            catch(Exception ignored){next=start+1;}
            pageIndex=Math.max(0,Math.min(n-1,next-1));
            go("LESSON");
        });
        LinearLayout.LayoutParams right=new LinearLayout.LayoutParams(dp(135),dp(48));
        right.leftMargin=dp(6);jump.addView(go,right);add(navPanel,jump);
        JSONObject pageEntries=entry==null?null:obj(entry,"pages");
        for(int p=start;p<end;p++){
            int originalPage=p+1;
            JSONObject page=pageEntries==null?null:pageEntries.optJSONObject(String.valueOf(originalPage));
            LinearLayout pageCard=panel(body);
            heading(pageCard,"Page "+originalPage+" / "+n);
            JSONObject part=page==null?null:obj(page,"sourcePart");
            if(part!=null){
                int sourcePage=originalPage-part.optInt("startPage")+1;
                sub(pageCard,"FC source : "+s(part,"sourceTitle")+" • page "+sourcePage+"/"+part.optInt("pages"));
            }
            JSONArray facts=arr(page,"facts");
            if(facts!=null&&facts.length()>0){
                sub(pageCard,"Notions transcrites de cette page : "+facts.length());
                for(int j=0;j<facts.length();j++){
                    JSONObject f=facts.optJSONObject(j);
                    if(f==null||f.optBoolean("isAdministrative",false))continue;
                    String v=s(f,"value");
                    String label=s(f,"label");
                    if(v.isEmpty())continue;
                    info(pageCard,label,readableValue(label,v,subject));
                }
            }else sub(pageCard,"Aucun texte intégral vérifié pour cette page ; l'image source complète suit.");
            drawImageInto(pageCard,originalPages.optString(p));
        }
        LinearLayout footer=panel(body);
        buttons(footer,"◀ Pages précédentes",()->{
            pageIndex=Math.max(0,start-perView);go("LESSON");
        },"Pages suivantes ▶",()->{
            pageIndex=Math.min(n-1,start+perView);go("LESSON");
        });
        add(footer,button("Complet — toutes les sections textuelles",false,()->{
            completeSourceMode=false;go("LESSON");
        }));
    }

    private JSONObject comprehensionGuides;
    private void loadComprehensionGuides()throws Exception{
        try(InputStream in=getAssets().open("comprehension_texts.json");
            ByteArrayOutputStream out=new ByteArrayOutputStream()){
            byte[] b=new byte[16384];int n;
            while((n=in.read(b))!=-1)out.write(b,0,n);
            comprehensionGuides=new JSONObject(new String(out.toByteArray(),"UTF-8")).optJSONObject("chapters");
        }
    }
    private JSONObject expertComprehension;
    private void loadExpertComprehension() throws Exception{
        JSONObject root=readJsonAsset("expert_comprehension_v3311.json");
        expertComprehension=obj(root,"courses");
    }
    private TextView technicalText(String value,int fontSize,int textColor,JSONArray keywords){
        TextView label=text(value,fontSize,textColor,false);
        label.setTextIsSelectable(true);
        label.setLineSpacing(dp(4),1.06f);
        if(keywords==null||keywords.length()==0)return label;
        android.text.SpannableString span=new android.text.SpannableString(value);
        String lower=value.toLowerCase(Locale.ROOT);
        for(int k=0;k<keywords.length();k++){
            String term=keywords.optString(k,"");
            if(term.isEmpty()||term.length()<3)continue;
            String fragment=term.toLowerCase(Locale.ROOT);
            int pos=0;
            while(pos<lower.length()){
                int at=lower.indexOf(fragment,pos);
                if(at<0)break;
                int end=Math.min(at+term.length(),value.length());
                span.setSpan(new android.text.style.StyleSpan(android.graphics.Typeface.BOLD),
                        at,end,android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
                span.setSpan(new android.text.style.ForegroundColorSpan(BLUE),
                        at,end,android.text.Spanned.SPAN_EXCLUSIVE_EXCLUSIVE);
                pos=end;
            }
        }
        label.setText(span);
        return label;
    }
    private void showExpertComprehension(JSONObject course){
        LinearLayout introduction=panel(body);
        heading(introduction,"Comprendre en profondeur — niveau moléculaire");
        sub(introduction,"Faits examinables de la FC 2026–2027, mécanismes explicatifs et approfondissements scientifiques distingués.");
        JSONArray sections=arr(course,"sections");
        if(sections==null)return;
        sub(introduction,sections.length()+" développements • structures, tailles, compartiments, molécules, interactions et conséquences.");
        add(introduction,button("Voir tous les faits structurés de la FC",false,()->{
            guideMode="FULL_FACTS";go("LESSON");
        }));
        final ArrayList<View> positions=new ArrayList<>();
        ArrayList<String> labels=new ArrayList<>();labels.add("Aller directement à une partie…");
        for(int k=0;k<sections.length();k++){
            JSONObject block=sections.optJSONObject(k);
            labels.add(s(block,"title"));
        }
        Spinner navigation=new Spinner(this);
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,labels);
        navigation.setAdapter(adapter);add(body,navigation);
        navigation.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            @Override public void onNothingSelected(android.widget.AdapterView<?> p){}
            @Override public void onItemSelected(android.widget.AdapterView<?> p,View v,int pos,long id){
                if(pos<1||pos>positions.size())return;
                View target=positions.get(pos-1);
                scroll.post(()->scroll.smoothScrollTo(0,Math.max(0,target.getTop())));
            }
        });
        for(int i=0;i<sections.length();i++){
            JSONObject block=sections.optJSONObject(i);
            if(block==null)continue;
            LinearLayout card=panel(body);
            positions.add(card);
            heading(card,s(block,"title"));
            JSONArray sourcePages=arr(block,"sourcePages");
            ArrayList<String> named=new ArrayList<>();
            if(sourcePages!=null)for(int j=0;j<sourcePages.length();j++)named.add(String.valueOf(sourcePages.optInt(j)));
            sub(card,"FC d'origine • page(s) "+android.text.TextUtils.join(", ",named));
            JSONArray keywords=arr(block,"keywords");
            TextView tag=technicalText(s(block,"source"),15,WHITE,keywords);
            tag.setPadding(dp(5),dp(6),dp(5),dp(10));
            add(card,text("FAITS ET DÉTAILS DE LA FC",12,GREEN,true));
            add(card,tag);
            String mechanisms=s(block,"mechanism");
            if(!mechanisms.isEmpty()){
                add(card,text("EXPLICATION MÉCANISTIQUE • LIENS ET DÉDUCTIONS",12,BLUE,true));
                TextView explained=technicalText(mechanisms,16,WHITE,keywords);
                explained.setPadding(dp(5),dp(7),dp(5),dp(12));add(card,explained);
            }
            String advanced=s(block,"advanced");
            if(!advanced.isEmpty()){
                add(card,text("APPROFONDISSEMENT • DISTINCT DU TEXTE EXIGIBLE DE LA FC",12,MUTED,true));
                TextView expanded=technicalText(advanced,14,MUTED,keywords);
                expanded.setPadding(dp(5),dp(5),dp(5),dp(10));add(card,expanded);
            }
            if(sourcePages!=null&&sourcePages.length()>0){
                int first=sourcePages.optInt(0,1);
                add(card,button("Contrôler la page originale "+first,false,()->{
                    pageIndex=Math.max(0,first-1);go("PAGES");
                }));
            }
        }
        LinearLayout end=panel(body);
        sub(end,"Les pages et schémas d'origine restent accessibles : les paragraphes n'effacent ni les données quantitatives, ni les structures, ni les partenaires moléculaires.");
        buttons(end,"Cours complet et tableaux",()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");},
                "Questions du cours",()->startQuiz(currentChapter));
    }
    private void showAllUnderlyingFacts(LinearLayout container,JSONObject section,boolean shs){
        JSONArray evidence=arr(section,"evidence");
        if(evidence==null||evidence.length()==0)return;
        TextView label=text(shs?"INTITULÉS, MOTS-CLÉS ET DÉTAILS DES TABLEAUX":"DONNÉES STRUCTURALES, MOLÉCULAIRES ET QUANTITATIVES",12,BLUE,true);
        label.setPadding(dp(3),dp(8),dp(3),dp(8));add(container,label);
        for(int j=0;j<evidence.length();j++){
            JSONObject row=evidence.optJSONObject(j);
            if(row==null)continue;
            String raw=s(row,"value");
            if(raw.isEmpty())continue;
            String title=s(row,"label");
            if(title.isEmpty())title="Notion "+(j+1);
            if(raw.toLowerCase(Locale.ROOT).contains("page pdf")&&raw.toLowerCase(Locale.ROOT).contains("remplac"))continue;
            int page=row.optInt("sourcePage",0);
            String provenance=page>0?" • FC p. "+page:"";
            // SHS labels are bold and emphasized; source PDF typography is preserved in the image.
            LinearLayout statement=vertical();
            statement.setPadding(dp(11),dp(8),dp(11),dp(10));
            statement.setBackground(bg(PANEL2,0,10));
            TextView name=text(title+provenance,shs?14:13,BLUE,true);
            add(statement,name);
            TextView detail=text(raw,15,WHITE,false);
            detail.setTextIsSelectable(true);
            detail.setLineSpacing(dp(3),1.05f);
            add(statement,detail);
            add(container,statement);
        }
    }

    private void showComprehension(){
        JSONObject entry=comprehensionGuides==null?null:comprehensionGuides.optJSONObject(currentChapter);
        if(entry==null){
            LinearLayout empty=panel(body);
            heading(empty,"Texte explicatif indisponible");
            sub(empty,"Aucun texte vérifié pour ce chapitre.");
            add(empty,button("Consulter les sources",true,()->{pageIndex=0;go("PAGES");}));
            return;
        }
        JSONObject expert=expertComprehension==null?null:expertComprehension.optJSONObject(currentChapter);
        if(expert!=null){
            showExpertComprehension(expert);
            return;
        }
        String status=s(entry,"coverageStatus");
        int sourceFacts=entry.optInt("sourceFacts",0);
        int sourcePages=entry.optInt("sourcePageTotal",0);
        boolean linked=status.startsWith("RELATED_CONTENT_ONLY");
        boolean composite=status.startsWith("COMPOSITE_EXISTING_SOURCE_COURSES");
        boolean incomplete=status.startsWith("SOURCE_GUIDE_INCOMPLETE");
        LinearLayout intro=panel(body);
        heading(intro,"Comprendre et relier les notions");
        if(linked){
            sub(intro,"Ce chapitre ne possède pas de cours source propre dans les fichiers intégrés. Les explications ci-dessous réunissent uniquement des passages de cours voisins et ne remplacent pas la FC manquante.");
        }else if(composite){
            sub(intro,"Chapitre composé à partir des FC des sous-chapitres existants. Aucun PDF autonome portant ce titre n'a été fourni. Les faits et les pages restent liés à chaque sous-chapitre.");
            JSONArray parts=arr(entry,"compositeParts");
            if(parts!=null)for(int ci=0;ci<parts.length();ci++){
                JSONObject part=parts.optJSONObject(ci);
                if(part==null)continue;
                String id=s(part,"sourceChapter");
                String title=s(part,"sourceTitle");
                add(intro,button(title,false,()->openLesson(id)));
            }
        }else if(incomplete){
            sub(intro,"Couverture partielle. Le texte reprend les repères actuellement structurés, mais ne contient pas tous les éléments du PDF original.");
        }else{
            sub(intro,"Synthèse textuelle fondée sur les données structurées du cours. L'exhaustivité page par page reste à contrôler.");
        }
        sub(intro,entry.optJSONArray("sections")==null?"":entry.optJSONArray("sections").length()+" parties");
        sub(intro,entry.optInt("paragraphCount")+" paragraphes • "+sourceFacts+
              " faits structurés"+(sourcePages>0?" • "+sourcePages+" pages sources":""));
        add(intro,button("Cours original intégral — toutes les pages",true,()->{
            pageIndex=0;guideMode="COMPLETE";go("LESSON");
        }));
        TextView reasoning=text(s(entry,"readingStrategy"),14,BLUE,false);
        reasoning.setPadding(dp(8),dp(11),dp(8),dp(11));
        reasoning.setLineSpacing(dp(4),1.08f);
        add(intro,reasoning);
        JSONArray sections=arr(entry,"sections");
        if(sections==null||sections.length()==0){
            sub(body,"Aucune section disponible dans ce chapitre.");
            return;
        }
        ArrayList<View> locations=new ArrayList<>();
        Spinner topics=new Spinner(this);
        ArrayList<String> names=new ArrayList<>();
        names.add("Aller à une partie…");
        for(int i=0;i<sections.length();i++){
            JSONObject section=sections.optJSONObject(i);
            names.add((i+1)+". "+s(section,"heading"));
        }
        ArrayAdapter<String> adapter=new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,names);
        topics.setAdapter(adapter);
        add(body,topics);
        topics.setOnItemSelectedListener(new android.widget.AdapterView.OnItemSelectedListener(){
            public void onNothingSelected(android.widget.AdapterView<?> p){}
            public void onItemSelected(android.widget.AdapterView<?> p,View v,int pos,long id){
                if(pos<=0||pos>locations.size())return;
                View target=locations.get(pos-1);
                scroll.post(()->scroll.smoothScrollTo(0,Math.max(0,target.getTop())));
            }
        });
        for(int i=0;i<sections.length();i++){
            JSONObject section=sections.optJSONObject(i);
            if(section==null)continue;
            LinearLayout container=vertical();
            container.setPadding(dp(5),dp(16),dp(5),dp(9));
            locations.add(container);
            add(body,container);
            View line=new View(this);line.setBackgroundColor(Color.rgb(56,83,116));
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(1));
            lp.bottomMargin=dp(14);container.addView(line,lp);
            heading(container,s(section,"heading"));
            if(linked){
                String related=s(section,"relatedCourseTitle");
                if(!related.isEmpty())sub(container,"Notions issues de : "+related);
            }
            JSONArray paras=arr(section,"paragraphs");
            if(paras!=null)for(int j=0;j<paras.length();j++){
                String paragraph=paras.optString(j);
                if(paragraph.isEmpty())continue;
                TextView t=text(paragraph,16,WHITE,false);
                t.setTextIsSelectable(true);
                t.setGravity(Gravity.TOP);
                t.setLineSpacing(dp(5),1.1f);
                t.setPadding(dp(4),dp(3),dp(4),dp(11));
                add(container,t);
            }
            showAllUnderlyingFacts(container,section,"shs".equals(s(byChapter.get(currentChapter),"subjectId")));
            JSONArray pg=arr(section,"sourcePages");
            if(!linked&&pg!=null&&pg.length()>0){
                int first=pg.optInt(0,0);
                if(first>0)add(container,button("Consulter la source de cette partie",false,()->{
                    pageIndex=first-1;go("PAGES");
                }));
            }
            String related=s(section,"relatedChapter");
            if(linked&&!related.isEmpty()&&byChapter.containsKey(related)){
                add(container,button("Ouvrir le cours source : "+chapterTitle(related),false,()->openLesson(related)));
            }
        }
        LinearLayout close=panel(body);
        sub(close,"Les paragraphes sont complétés par les données détaillées structurées de la FC. Les termes en gras des sources SHS sont préservés dans les pages originales, et les intitulés sont mis en valeur ici.");
        buttons(close,"Complet (sources et textes)",()->{pageIndex=0;guideMode="COMPLETE";go("LESSON");},
                "Toutes les notions",()->{guideMode="FULL_FACTS";go("LESSON");});
    }

    private void showQuestionModes(){
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
            case "MAP_BOARD":showStructuredMap();break;
            case "MAP_IMAGE_DETAIL":showOriginalMapDetail();break;
            case "MAP_DETAIL":showConceptBranch();break;
            case "QUESTION_HOME":showQuestionModes();break;
            case "QUIZ_PICK":showPick(true);break;
            case "CARD_PICK":showPick(false);break;
            case "QUIZ":showQuiz();break;
            case "CARDS":showCard();break;
            default:showHome();
        }
        nav=horizontal();nav.setBackground(bg(PANEL,0,0));nav.setPadding(dp(6),dp(7),dp(6),dp(7));
        addNav("Accueil","HOME");addNav("Questions","QUESTION_HOME");addNav("Flashcards","CARD_PICK");addNav("Cours","CATALOG");
        root.addView(nav,new LinearLayout.LayoutParams(-1,-2));
    }
    private void addNav(String name,String dest){
        boolean active=screen.equals(dest)||((screen.equals("LESSON")||screen.equals("PAGES")||screen.equals("MAP")||screen.equals("MAP_BOARD")||screen.equals("MAP_IMAGE_DETAIL")||screen.equals("MAP_DETAIL")||screen.equals("BOARDS"))&&dest.equals("CATALOG"))
                ||((screen.equals("QUIZ")||screen.equals("QUIZ_PICK"))&&dest.equals("QUESTION_HOME"))||(screen.equals("CARDS")&&dest.equals("CARD_PICK"));
        TextView t=text(name,11,active?BLUE:MUTED,active);t.setGravity(Gravity.CENTER);
        t.setMinHeight(dp(46));t.setBackground(bg(active?PANEL2:PANEL,0,9));t.setOnClickListener(v->go(dest));
        nav.addView(t,new LinearLayout.LayoutParams(0,dp(47),1));
    }
    private int attempts(String questionId){return prefs.getInt("qa/"+questionId,0);}
    private boolean lastCorrect(String questionId){return prefs.getBoolean("qc/"+questionId,false);}
    private void recordAnswer(JSONObject question,double score,long durationMs){
        String id=s(question,"id");SharedPreferences.Editor e=prefs.edit();
        e.putInt("qa/"+id,attempts(id)+1);
        e.putBoolean("qc/"+id,score>=0.999);
        e.putFloat("qs/"+id,(float)score);
        if(score<0.999)e.putInt("qe/"+id,prefs.getInt("qe/"+id,0)+1);
        e.putLong("qt/"+id,Math.max(0,durationMs));
        e.putInt("qt_target/"+id,targetSeconds(question));
        e.putLong("qt_accumulated/"+id,prefs.getLong("qt_accumulated/"+id,0)+durationMs);
        e.apply();
    }
    private void showHome(){
        heading(body,"Réviser. S'entraîner. Progresser.");
        sub(body,chapters.size()+" cours • "+cards.size()+" flashcards • "+questions.size()+" questions d’entraînement");
        int attempted=0,correct=0,reviewed=0;
        for(JSONObject q:questions){String id=s(q,"id");if(attempts(id)>0){attempted++;if(lastCorrect(id))correct++;}}
        for(JSONObject c:cards)if(prefs.getInt("cr/"+s(c,"id"),0)>0)reviewed++;
        LinearLayout overview=panel(body);
        heading(overview,"Votre progression");
        info(overview,"Entraînement concours",questions.size()+" questions A–E et QROC");
        if(attempted>0)sub(overview,attempted+" questions effectuées • "+correct+" intégralement correctes.");
        info(overview,"Flashcards révisées",reviewed+" / "+cards.size());
        buttons(overview,"Questions concours",()->go("QUESTION_HOME"),"Réviser les cartes",()->go("CARD_PICK"));
        heading(body,"EXAMEN DU 4 NOVEMBRE — TROIS PRIORITÉS");
        sub(body,"Première semaine • Deuxième semaine (Partie 1) • Fécondation. Accès direct aux cours, flashcards et QCM A–E corrigés.");
        String[] urgentIds={"histo_semaine1","histo_semaine2","histo_fecondation"};
        for(String urgentId:urgentIds){
            JSONObject chapter=byChapter.get(urgentId);
            if(chapter==null)continue;
            LinearLayout focus=panel(body);
            heading(focus,s(chapter,"title"));
            JSONArray sourcePages=mediaPages==null?null:mediaPages.optJSONArray(urgentId);
            int pageCount=sourcePages==null?0:sourcePages.length();
            int cardCount=cardsByChapter.containsKey(urgentId)?cardsByChapter.get(urgentId).size():0;
            int qCount=questionsByChapter.containsKey(urgentId)?questionsByChapter.get(urgentId).size():0;
            sub(focus,pageCount+" pages FC • "+cardCount+" flashcards • "+qCount+" QCM/QROC d'entraînement");
            buttons(focus,"Comprendre / Cours",()->openLesson(urgentId),
                    "QCM A–E",()->startQuiz(urgentId));
            buttons(focus,"Flashcards",()->startCards(urgentId),
                    "Essentiel / Complet",()->{openLesson(urgentId);guideMode="ESSENTIAL";go("LESSON");});
        }
        heading(body,"Révisions — cours existants");
        ArrayList<JSONObject> rank=new ArrayList<>(chapters);
        rank.sort((a,b)->Integer.compare(priorityScore(b),priorityScore(a)));
        int shown=0;
        for(JSONObject c:rank){
            String id=s(c,"id");if(!questionsByChapter.containsKey(id)&&!cardsByChapter.containsKey(id))continue;
            LinearLayout item=panel(body);
            item.addView(text(subjectName(s(c,"subjectId"))+" • "+s(c,"title"),15,WHITE,true));
            int fc=cardsByChapter.containsKey(id)?cardsByChapter.get(id).size():0;
            JSONArray examPapers=docs==null?null:docs.optJSONArray(id);
            int paperCount=examPapers==null?0:examPapers.length();
            sub(item,fc+" cartes de révision • "+paperCount+" PDF annales/QE fournis");
            buttons(item,"Annales / QE",()->startQuiz(id),"Cours",()->openLesson(id));
            if(++shown>=5)break;
        }
        heading(body,"Matières");
        for(Map.Entry<String,String> sb:subjects.entrySet()){
            String sid=sb.getKey();int courseCount=0,paperCount=0;
            for(JSONObject c:chapters)if(s(c,"subjectId").equals(sid)){
                courseCount++;
                JSONArray a=docs==null?null:docs.optJSONArray(s(c,"id"));
                if(a!=null)paperCount+=a.length();
            }
            LinearLayout p=panel(body);p.addView(text(sb.getValue(),16,WHITE,true));sub(p,courseCount+" cours • "+paperCount+" PDF annales/QE");
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
                sub(p,subjectName(sid)+" • "+nf+" cartes de révision • "+(guide?"Fiche structurée : couverture variable":"Leçon absente — source à intégrer"));
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
    private void openLesson(String id){
        currentChapter=id;guideMode="UNDERSTAND";boardIndex=0;boardRevealed=true;
        boardAnswerDraft="";completeSectionIndex=0;completeSourceMode=false;go("LESSON");
    }
    private boolean isFormulaSubject(String subject){
        return "phys".equals(subject)||"chimie".equals(subject);
    }
    private View fractionFormula(String formula){
        String formatted=formula.replace("m1","m₁").replace("m2","m₂").replace("q1","q₁")
                .replace("q2","q₂").replace("epsilon0","ε₀");
        int eq=formatted.indexOf('=');
        int slash=formatted.lastIndexOf('/');
        if(eq<0||slash<eq)return text(formatted,22,WHITE,true);
        String leading=formatted.substring(0,eq+1).trim();
        String numerator=formatted.substring(eq+1,slash).trim();
        String denominator=formatted.substring(slash+1).trim();
        if(numerator.length()==0||denominator.length()==0||denominator.length()>22
          ||numerator.length()>45)return text(formatted,22,WHITE,true);
        LinearLayout result=horizontal();
        result.setGravity(Gravity.CENTER_VERTICAL|Gravity.LEFT);
        TextView lhs=text(leading,22,WHITE,true);
        LinearLayout.LayoutParams lhsLp=new LinearLayout.LayoutParams(-2,-2);
        lhsLp.rightMargin=dp(10);result.addView(lhs,lhsLp);
        LinearLayout frac=vertical();
        frac.setGravity(Gravity.CENTER);
        TextView top=text(numerator,21,WHITE,true);
        top.setGravity(Gravity.CENTER);top.setPadding(dp(5),0,dp(5),dp(5));
        frac.addView(top,new LinearLayout.LayoutParams(-1,-2));
        View line=new View(this);line.setBackgroundColor(WHITE);
        frac.addView(line,new LinearLayout.LayoutParams(-1,dp(2)));
        TextView bottom=text(denominator,21,WHITE,true);
        bottom.setGravity(Gravity.CENTER);bottom.setPadding(dp(5),dp(5),dp(5),0);
        frac.addView(bottom,new LinearLayout.LayoutParams(-1,-2));
        result.addView(frac,new LinearLayout.LayoutParams(-2,-2));
        return result;
    }
    private String formulaNotes(String raw,String formula){
        String val=raw==null?"":raw;
        int before=val.indexOf(" ; ");
        if(before>=0&&val.substring(0,before).indexOf('=')<0){
            String note=val.substring(0,before).trim();
            if(note.length()>4&&note.length()<85)return note;
        }
        if(val.startsWith("Toujours attractive"))return "Toujours attractive • portée infinie";
        return "";
    }

    private String compactFormula(String label,String value,String subject){
        String key=label.toLowerCase(java.util.Locale.ROOT);
        String raw=value==null?"":value;
        if("phys".equals(subject)){
            if(key.contains("gravitation")&&raw.contains("/r²"))return "|F| = G m₁m₂/r²";
            if(key.contains("électrostatique")&&key.contains("norme"))
                return "|F| = |q₁q₂|/(4πε₀r²)";
            if(key.contains("charge élémentaire")&&raw.contains("1,602"))return "e = 1,602 × 10⁻¹⁹ C";
            if(key.contains("nombre d’avogadro")||key.contains("nombre d'avogadro"))return "Nₐ = 6,022 × 10²³";
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
        String lhs=eq.substring(0,eq.indexOf('=')).trim();
        if(lhs.length()>18||lhs.contains(" " )&&!lhs.startsWith("|F|")&&!lhs.startsWith("ΣF"))
            return "";
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
                    add(formulaBox,fractionFormula(formula));
                    String note=formulaNotes(raw,formula);
                    if(!note.isEmpty())add(formulaBox,text(note,13,MUTED,false));
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
                    add(f,fractionFormula(formula));
                    String note=formulaNotes(val,formula);
                    if(!note.isEmpty())add(f,text(note,13,MUTED,false));
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
        boolean understanding="UNDERSTAND".equals(guideMode);
        add(body,button(understanding?"Comprendre — lecture détaillée":"Comprendre — explications détaillées",
                understanding,()->{guideMode="UNDERSTAND";go("LESSON");}));
        LinearLayout menu=horizontal();
        String[] names={"Essentiel","Complet","Pages","Carte"};
        for(int i=0;i<names.length;i++){
            final int choice=i;
            boolean active=i==0&&"ESSENTIAL".equals(guideMode)||i==1&&"COMPLETE".equals(guideMode);
            TextView tab=button(names[i],active,()->{
                if(choice==2){pageIndex=0;go("PAGES");}
                else if(choice==3){go("MAP");}
                else{
                    guideMode=choice==0?"ESSENTIAL":"COMPLETE";
                    completeSourceMode=false;completeSectionIndex=0;go("LESSON");
                }
            });
            LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(0,dp(47),1);
            if(i<names.length-1)lp.rightMargin=dp(6);
            menu.addView(tab,lp);
        }
        add(body,menu);
        if("UNDERSTAND".equals(guideMode)){showComprehension();return;}
        JSONObject guide=guides==null?null:guides.optJSONObject(currentChapter);
        JSONArray sections=arr(guide,"sections");
        if(sections==null||sections.length()==0){
            LinearLayout missing=panel(body);
            sub(missing,"Fiche structurée indisponible. Les pages originales restent accessibles.");
            add(missing,button("Lire la source",true,()->{pageIndex=0;go("PAGES");}));
            return;
        }
        int sourceCount=0;JSONArray originalPages=mediaPages==null?null:mediaPages.optJSONArray(currentChapter);
        if(originalPages!=null)sourceCount=originalPages.length();
        int available=0;
        for(int ii=0;ii<sections.length();ii++){
            JSONObject ss=sections.optJSONObject(ii);
            JSONArray list=arr(ss,"items");if(list!=null)available+=list.length();
        }
        if(sourceCount>0&&available<sourceCount*3&&!"COMPLETE".equals(guideMode)){
            LinearLayout warning=panel(body);
            heading(warning,"Texte structuré et document source");
            sub(warning,available+" notions transcrites • "+sourceCount+" pages sources intégralement consultables dans Complet.");
            add(warning,button("Lire les pages sources",true,()->{pageIndex=0;go("PAGES");}));
        }
        int displayed=0,total=0;
        if("COMPLETE".equals(guideMode)){
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
        if(!essential)heading(body,"Toutes les notions structurées");
        for(int j=0;j<sections.length();j++){
            JSONObject section=sections.optJSONObject(j);if(section==null)continue;
            JSONArray items=arr(section,"items");if(items==null)continue;
            ArrayList<JSONObject> selected=new ArrayList<>();
            for(int k=0;k<items.length();k++){
                JSONObject item=items.optJSONObject(k);if(item==null)continue;
                String value=s(item,"value");if(value.isEmpty())value=s(item,"text");
                if(value.isEmpty())continue;
                total++;
                if(essential&&!selectedKeys.contains(j+":"+k))continue;
                String memo=s(item,"value");
                if(memo.isEmpty())memo=s(item,"text");
                if(memo.matches("(?is).*(?:page\\s+PDF\\s*\\d+\\s+(?:est\\s+)?(?:à remplacer|remplacée)|tableau\\s+à\\s+insérer).*"))continue;
                selected.add(item);displayed++;
            }
            if(!selected.isEmpty())subjectBoard(body,subject,section,selected);
        }
        if(displayed==0)sub(body,"Aucun repère sélectionné. Consulter le mode Complet ou les pages.");
        if(essential)
            sub(body,"Essentiel : "+displayed+" repères sélectionnés dans toutes les parties du cours, parmi "+total+" notions actuellement structurées. Le mode Complet contient également les pages intégrales.");
        else{
            sub(body,"Toutes les notions structurées : "+displayed+" repères. Le mode Complet affiche aussi les "+sourceCount+" pages de cours, y compris celles dont le texte n'a pas encore été transcrit.");
            if(sourceCount>0){
                LinearLayout sourceLink=panel(body);
                heading(sourceLink,"Pages intégrales du cours");
                sub(sourceLink,"La synthèse textuelle ne remplace pas les figures, tableaux et pages non encore transcrites.");
                add(sourceLink,button("Ouvrir les pages de FC ("+sourceCount+")",true,()->{pageIndex=0;go("PAGES");}));
            }
        }
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
        buttons(body,"Cours structuré",()->{guideMode="FULL_FACTS";go("LESSON");},"Flashcards",()->startCards(currentChapter));
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
            ArrayList<Integer> activeIndexes=new ArrayList<>();
            for(int i=0;i<pages.length();i++){
                int actualPage=i+1;
                if("biocell_intro".equals(currentChapter)&&
                    (actualPage==9||actualPage==14||actualPage==17))continue;
                activeIndexes.add(i);
            }
            if(activeIndexes.size()==0){sub(body,"Pages sources indisponibles.");return;}
            int position=activeIndexes.indexOf(pageIndex);
            if(position<0){
                position=0;
                while(position+1<activeIndexes.size()&&activeIndexes.get(position)<pageIndex)position++;
                pageIndex=activeIndexes.get(position);
            }
            final int where=position;
            sub(body,"Pages actives du cours : "+activeIndexes.size()+" • pinch zoom");
            buttons(body,"◀ Précédente",()->{
                pageIndex=activeIndexes.get(Math.max(0,where-1));go("PAGES");
            },"Suivante ▶",()->{
                pageIndex=activeIndexes.get(Math.min(activeIndexes.size()-1,where+1));go("PAGES");
            });
            sub(body,(where+1)+" / "+activeIndexes.size());
            if(meta!=null&&meta.optBoolean("isComposite",false)){
                JSONArray parts=arr(meta,"compositeParts");
                if(parts!=null)for(int j=0;j<parts.length();j++){
                    JSONObject part=parts.optJSONObject(j);
                    if(part==null)continue;
                    int p=pageIndex+1;
                    if(p>=part.optInt("startPage",999999)&&p<=part.optInt("endPage",0)){
                        sub(body,"FC source : "+s(part,"sourceTitle")+" — page "+(p-part.optInt("startPage")+1)+" / "+part.optInt("pages"));
                        break;
                    }
                }
            }
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
    private final class ConnectedConceptMap extends FrameLayout {
        private View centerNode;
        private final ArrayList<View> satelliteNodes=new ArrayList<>();
        private final ArrayList<Integer> satelliteColors=new ArrayList<>();
        ConnectedConceptMap(Context ctx){super(ctx);setWillNotDraw(false);}
        void center(View v){centerNode=v;}
        void satellite(View v,int color){satelliteNodes.add(v);satelliteColors.add(color);}
        @Override protected void dispatchDraw(android.graphics.Canvas canvas){
            if(centerNode!=null&&getWidth()>0){
                int[] frame=new int[2],hub=new int[2],node=new int[2];
                getLocationOnScreen(frame);centerNode.getLocationOnScreen(hub);
                float cx=hub[0]-frame[0]+centerNode.getWidth()/2f;
                float cy=hub[1]-frame[1]+centerNode.getHeight();
                android.graphics.Paint paint=new android.graphics.Paint(android.graphics.Paint.ANTI_ALIAS_FLAG);
                paint.setStyle(android.graphics.Paint.Style.STROKE);
                paint.setStrokeWidth(dp(2.5f));
                for(int i=0;i<satelliteNodes.size();i++){
                    View card=satelliteNodes.get(i);
                    if(card.getWidth()==0)continue;
                    card.getLocationOnScreen(node);
                    float nx=node[0]-frame[0]+card.getWidth()/2f,ny=node[1]-frame[1];
                    paint.setColor(satelliteColors.get(i));
                    android.graphics.Path route=new android.graphics.Path();
                    route.moveTo(cx,cy);
                    float halfway=cy+(ny-cy)*0.5f;
                    route.cubicTo(cx,halfway,nx,halfway,nx,ny);
                    canvas.drawPath(route,paint);
                    paint.setStyle(android.graphics.Paint.Style.FILL);
                    canvas.drawCircle(nx,ny,dp(4),paint);
                    paint.setStyle(android.graphics.Paint.Style.STROKE);
                }
            }
            super.dispatchDraw(canvas);
        }
    }

    private int mindMapDetailIndex=0;
    private void showConceptMap(){
        JSONObject mind=mindmaps==null?null:mindmaps.optJSONObject(currentChapter);
        if(mind==null||s(mind,"path").isEmpty()){
            showStructuredMap();
            return;
        }
        heading(body,"Carte mentale originale — "+chapterTitle(currentChapter));
        sub(body,"Cartes originales restaurées depuis le projet antérieur, sans remplacement graphique.");
        add(body,button("Voir les tableaux et relations lisibles",false,()->go("MAP_BOARD")));
        drawImage(s(mind,"path"));
        JSONArray branches=arr(mind,"subMaps");
        if(branches!=null&&branches.length()>0){
            heading(body,"Cartes détaillées");
            for(int i=0;i<branches.length();i++){
                JSONObject branch=branches.optJSONObject(i);if(branch==null)continue;
                int ix=i;
                add(body,button((i+1)+". "+s(branch,"title"),false,()->{
                    mindMapDetailIndex=ix;go("MAP_IMAGE_DETAIL");
                }));
            }
        }
        add(body,button("Revenir au cours",true,()->go("LESSON")));
    }
    private void showOriginalMapDetail(){
        JSONObject mind=mindmaps==null?null:mindmaps.optJSONObject(currentChapter);
        JSONArray branches=arr(mind,"subMaps");
        if(branches==null||branches.length()==0){go("MAP");return;}
        mindMapDetailIndex=Math.max(0,Math.min(branches.length()-1,mindMapDetailIndex));
        JSONObject page=branches.optJSONObject(mindMapDetailIndex);
        heading(body,s(page,"title"));
        sub(body,"Carte "+(mindMapDetailIndex+1)+" / "+branches.length()+" — image originale");
        buttons(body,"◀ Précédente",()->{
            mindMapDetailIndex=Math.max(0,mindMapDetailIndex-1);go("MAP_IMAGE_DETAIL");
        },"Suivante ▶",()->{
            mindMapDetailIndex=Math.min(branches.length()-1,mindMapDetailIndex+1);go("MAP_IMAGE_DETAIL");
        });
        drawImage(s(page,"path"));
        buttons(body,"Toutes les cartes",()->go("MAP"),"Liste textuelle",()->go("MAP_BOARD"));
    }

    private void showStructuredMap(){
        String courseName=chapterTitle(currentChapter);
        JSONObject chapter=byChapter.get(currentChapter);
        String subject=s(chapter,"subjectId");
        ArrayList<JSONObject> branches=mapBranches();
        heading(body,"Carte des notions");
        ConnectedConceptMap graph=new ConnectedConceptMap(this);
        LinearLayout graphContent=vertical();
        graphContent.setPadding(dp(1),dp(4),dp(1),dp(6));
        graph.addView(graphContent,new FrameLayout.LayoutParams(-1,-2));
        add(body,graph);
        LinearLayout center=panel(graphContent);
        TextView hub=text(courseName,19,WHITE,true);
        hub.setGravity(Gravity.CENTER);
        hub.setTextAlignment(View.TEXT_ALIGNMENT_CENTER);
        hub.setPadding(dp(12),dp(15),dp(12),dp(15));
        hub.setBackground(bg(PANEL2,BLUE,17));
        add(center,hub);
        graph.center(hub);
        TextView caption=text(branches.size()+" branches — sélectionnez un domaine",13,MUTED,false);
        caption.setGravity(Gravity.CENTER);add(center,caption);
        gap(graphContent,18);
        if(isMemorySubject(currentChapter)){
            JSONObject pack=boardCatalog==null?null:boardCatalog.optJSONObject(currentChapter);
            JSONArray units=arr(pack,"items");
            if(units!=null&&units.length()>0){
                add(graphContent,button("Tableaux / planches sources : "+units.length(),true,()->{
                    boardIndex=0;boardRevealed=true;go("BOARDS");
                }));
            }
        }
        if(branches.size()==0){
            LinearLayout unavailable=panel(graphContent);
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
                int[] palette={Color.rgb(0,213,229),Color.rgb(253,89,183),Color.rgb(250,197,48),Color.rgb(115,239,153),
                               Color.rgb(171,122,255),Color.rgb(255,147,91),Color.rgb(89,165,255),Color.rgb(230,108,151)};
                int branchColor=palette[idx%palette.length];
                box.setBackground(bg(PANEL,branchColor,14));
                graph.satellite(box,branchColor);
                TextView ordinal=text(String.format(Locale.ROOT,"%02d",idx+1),13,branchColor,true);
                add(box,ordinal);
                TextView name=text(s(sec,"title"),15,branchColor,true);add(box,name);
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
            add(graphContent,row);
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
    private void drawImage(String path){drawImageInto(body,path);}
    private void drawImageInto(LinearLayout target,String path){
        final ZoomImageView image=new ZoomImageView(this);
        image.setBackground(bg(PANEL,Color.rgb(45,67,94),12));
        LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(-1,dp(560));target.addView(image,lp);
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
            }catch(Exception e){runOnUiThread(()->sub(target,"Image indisponible : "+path));}
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
        sub(body,quiz?"Exercices reconstruits depuis les guides — NON issus d’annales authentifiées.":"Cartes de rappel issues des notes, pas des questions originales d’examen.");
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
        ArrayList<Integer> list=questionsByChapter.get(id);
        if(list!=null&&!list.isEmpty())launchQuiz(list);
        else go("QUIZ_PICK");
    }
    private void launchQuiz(List<Integer> ids){
        sessionQuestions.clear();sessionQuestions.addAll(ids);
        if(sessionQuestions.size()>20){
            int offset=prefs.getInt("quizoffset/"+ids.hashCode(),0)%sessionQuestions.size();
            Collections.rotate(sessionQuestions,-offset);
            sessionQuestions.subList(20,sessionQuestions.size()).clear();
            prefs.edit().putInt("quizoffset/"+ids.hashCode(),offset+20).apply();
        }
        quizIndex=0;quizCorrect=0;quizAnswered=0;quizScore=0;questionFinalized=false;questionActiveMs=0;questionStarted=SystemClock.elapsedRealtime();
        go("QUIZ");
    }
    private void showQuiz(){
        if(quizIndex>=sessionQuestions.size()){
            heading(body,"Session terminée");
            info(body,"Barème du concours",String.format(Locale.FRANCE,"%.1f / %d points",quizScore,quizAnswered));
            info(body,"Réponses totalement exactes",quizCorrect+" / "+quizAnswered);
            sub(body,"QCM : 0 erreur = 1 ; 1 erreur = 0,7 ; 2 erreurs = 0,1 ; 3+ = 0.");
            long elapsed=0;for(int i=0;i<quizAnswered&&i<sessionQuestions.size();i++){
                JSONObject old=questions.get(sessionQuestions.get(i));
                elapsed+=prefs.getLong("qt/"+s(old,"id"),0);
            }
            sub(body,"Temps de réponse cumulé : "+fmtSeconds(elapsed/1000));
            buttons(body,"Nouvelle session",()->go("QUIZ_PICK"),"Cours",()->go("CATALOG"));return;
        }
        JSONObject q=questions.get(sessionQuestions.get(quizIndex));
        String chap=s(q,"chapterId");boolean qroc="QROC".equalsIgnoreCase(s(q,"format"));
        sub(body,subjectName(s(q,"subjectId"))+" • "+chapterTitle(chap));
        sub(body,"Coefficient "+coefficient(s(q,"subjectId"))+" • barème concours");
        questionClock=text("",15,GREEN,true);add(body,questionClock);
        int target=targetSeconds(q);long elapsed=activeQuestionMs()/1000;
        questionClock.setText((elapsed<=target?"Temps restant : ":"Dépassement : +")+fmtSeconds(Math.abs(target-elapsed))+" • cible "+fmtSeconds(target));
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
                if(questionStarted>0){questionActiveMs+=SystemClock.elapsedRealtime()-questionStarted;questionStarted=0;}
                questionFinalized=true;
                JSONArray pts=arr(q,"expectedPoints");heading(feedback,"Correction : grille exhaustive");
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
                }));
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
                int errors=0;
                for(int i=0;i<5;i++)if(boxes[i].isChecked()!=keys[i])errors++;
                double points=errors==0?1.0:errors==1?0.7:errors==2?0.1:0.0;
                final double result=points;
                for(CheckBox box:boxes)box.setEnabled(false);
                heading(feedback,String.format(Locale.FRANCE,"Barème : %.1f / 1 — %d erreur(s)",points,errors));
                if(questionStarted>0){questionActiveMs+=SystemClock.elapsedRealtime()-questionStarted;questionStarted=0;}
                questionFinalized=true;
                sub(feedback,"Temps actif : "+fmtSeconds(questionActiveMs/1000)+" • cible "+fmtSeconds(targetSeconds(q)));
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
        buttons(body,"Revenir aux questions",()->go("QUESTION_HOME"),"Ouvrir ce cours",()->openLesson(chap));
    }
    private void finishQuizQuestion(JSONObject q,double points){
        long duration=activeQuestionMs();
        recordAnswer(q,points,duration);
        quizAnswered++;quizScore+=points;if(points>=0.999)quizCorrect++;
        quizIndex++;questionFinalized=false;questionActiveMs=0;questionStarted=SystemClock.elapsedRealtime();
        go("QUIZ");
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
        long days=choice==0?1:choice==1?2:choice==2?4:7;
        long due=System.currentTimeMillis()+days*86400000L;
        SharedPreferences.Editor e=prefs.edit();e.putInt("cr/"+id,n);e.putLong("cd/"+id,due);e.putInt("cg/"+id,choice);e.apply();
        cardReviewed++;cardIndex++;go("CARDS");
    }
    @Override public void onBackPressed(){
        if(screen.equals("QUIZ_PICK"))go("QUESTION_HOME");
        else if(screen.equals("QUESTION_HOME"))go("HOME");
        else if(screen.equals("MAP_IMAGE_DETAIL")||screen.equals("MAP_BOARD"))go("MAP");
        else if(screen.equals("LESSON")||screen.equals("BOARDS")||screen.equals("QUIZ_PICK")||screen.equals("CARD_PICK")||screen.equals("CATALOG"))go("HOME");
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
