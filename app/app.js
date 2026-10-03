window.__ADAPTIVE_BUILD='3.25.1-standalone-autonomous';

(()=>{
const C=window.APP_CONTENT||window.STUDY_CONTENT,KEY='adaptive-study-v22-state',DAY=86400000;
// STATE_SCHEMA below is intentionally independent from the app release so existing user progress is preserved.
if(!C||!Array.isArray(C.subjects)||!Array.isArray(C.chapters)||!Array.isArray(C.questions)){throw new Error('Contenu original non chargé ou incomplet. Recharge la page après remplacement du dossier.')}
window.APP_CONTENT=C;
const $=id=>document.getElementById(id),now=()=>Date.now(),today=()=>new Date().toISOString().slice(0,10);
const clamp=(x,a,b)=>Math.max(a,Math.min(b,x)),shuffle=a=>{a=[...a];for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]]}return a};
const median=a=>{if(!a.length)return 0;const b=[...a].sort((x,y)=>x-y),m=Math.floor(b.length/2);return b.length%2?b[m]:(b[m-1]+b[m])/2};
const esc=s=>String(s??'').replace(/[&<>"']/g,m=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[m]));
const subs=Object.fromEntries(C.subjects.map(x=>[x.id,x])),chs=Object.fromEntries(C.chapters.map(x=>[x.id,x]));
const base=()=>({version:'3.20.0-original-pdfs',created:new Date().toISOString(),daily:{date:today(),attempts:0},settings:{goal:30},concepts:{},cards:{},errors:{},sessions:[],seenGenerated:[]});
let S=load(),session=null,review=null,currentMain='home',currentMore='errors',questionTimer=null,readerState=null;
function legacyBadText(t){const z=String(t||'');return /Le raisonnement porte notamment|Les propositions croisent notamment|Une attention particulière est requise|Association proposée —|À quelle notion \/ structure cela correspond-il|Quelle notion \/ règle correspond à/i.test(z)||/;\s*(?:À propos de|Pour «|Association proposée —)/i.test(z)}
function migrateState(x){
 x=Object.assign(base(),x||{});x.cards=x.cards||{};x.errors=x.errors||{};
 Object.keys(x.cards).forEach(k=>{const c=x.cards[k];if(c?.custom&&legacyBadText((c.front||'')+' '+(c.back||'')))delete x.cards[k]});
 Object.keys(x.errors).forEach(k=>{const e=x.errors[k];if(legacyBadText((e?.question||'')+' '+(e?.correction||'')))delete x.errors[k]});
 if(x.version!=='3.20.0-original-pdfs'){x.concepts={};x.cards={};x.errors={};x.sessions=[];x.seenGenerated=[]}x.version='3.20.0-original-pdfs';return x;
}
function load(){try{let x=JSON.parse(localStorage.getItem(KEY)||'null')||base();if(!x.daily||x.daily.date!==today())x.daily={date:today(),attempts:0};return migrateState(x)}catch(e){return base()}}
function save(){localStorage.setItem(KEY,JSON.stringify(S));if(currentMain==='home')renderHome()}
function toast(m){$('toast').textContent=m;$('toast').classList.remove('hidden');setTimeout(()=>$('toast').classList.add('hidden'),2000)}
function sourceText(s){return s?[s.kind,s.title,s.year,s.page?'p.'+s.page:null].filter(Boolean).join(' · '):''}
function fmtSec(sec){
 sec=Math.max(0,Math.round(sec||0));const m=Math.floor(sec/60),s=sec%60;
 return `${m}:${String(s).padStart(2,'0')}`;
}
function examTargetSec(sid){
 const e=subs[sid]?.exam;
 if(!e||!e.durationMin||!e.approxItems)return 0;
 return (e.durationMin*60)/e.approxItems;
}
function questionTargetSec(q){
 if(q?.format==='QROC')return 600;
 return examTargetSec(q?.subjectId);
}
function targetContextForQuestion(q){
 if(q?.format==='QROC')return 'QROC : objectif 10 min';
 const e=subs[q?.subjectId]?.exam;if(!e)return'';
 return `${e.durationMin} min / ≈${e.approxItems} questions`;
}
function timingStatus(sec,target){
 if(!target)return'';
 const r=sec/target;
 if(r<=1)return'ok';
 if(r<=1.25)return'warn';
 return'bad';
}
function timingText(sec,target){
 if(!target)return `${fmtSec(sec)} écoulé`;
 const remain=Math.round(target-sec);
 return remain>=0?`${fmtSec(remain)} restantes`:`+${fmtSec(-remain)} au-delà`;
}
function activeElapsedMs(){
 if(!session)return 0;
 let ms=session.qActiveMs||0;
 if(session.qActiveStart&&!document.hidden)ms+=now()-session.qActiveStart;
 return ms;
}
function pauseActiveTimer(){
 if(!session||!session.qActiveStart)return;
 session.qActiveMs=(session.qActiveMs||0)+(now()-session.qActiveStart);
 session.qActiveStart=null;
}
function resumeActiveTimer(){
 if(!session||session.answered||document.hidden||session.qActiveStart)return;
 session.qActiveStart=now();
}
document.addEventListener('visibilitychange',()=>{
 if(document.hidden)pauseActiveTimer();else resumeActiveTimer();
});
window.addEventListener('pagehide',()=>pauseActiveTimer());
function stopQuestionTimer(){
 if(questionTimer){clearInterval(questionTimer);questionTimer=null}
 pauseActiveTimer();
}
function initQuestionTiming(q){
 stopQuestionTimer();
 session.qActiveMs=0;session.qActiveStart=document.hidden?null:now();
 startQuestionTimer(q);
}
function startQuestionTimer(q){
 if(questionTimer)clearInterval(questionTimer);
 const target=questionTargetSec(q);
 const tick=()=>{
   if(!session||session.answered)return;
   const sec=Math.max(0,Math.floor(activeElapsedMs()/1000));
   const el=$('questionClock'); if(!el)return;
   const st=timingStatus(sec,target);
   el.className=`question-clock ${st}`;
   el.innerHTML=`<div class="clock-main">${timingText(sec,target)}</div><div class="clock-sub">${target?`repère ${fmtSec(target)} · ${targetContextForQuestion(q)}`:'temps indicatif indisponible'} · temps actif</div>`;
 };
 tick();questionTimer=setInterval(tick,1000);
}
function sessionTimingSummary(items){
 if(!items||!items.length)return null;
 const valid=items.filter(x=>x.sec>0&&x.targetSec>0&&x.valid!==false);
 if(!valid.length)return null;
 const avg=valid.reduce((a,x)=>a+x.sec,0)/valid.length;
 const avgTarget=valid.reduce((a,x)=>a+x.targetSec,0)/valid.length;
 const onTime=valid.filter(x=>x.sec<=x.targetSec).length;
 const ratio=avg/avgTarget;
 return{avg,avgTarget,onTime,total:valid.length,ratio,median:median(valid.map(x=>x.sec))};
}
function normTxt(s){return String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase().replace(/[^a-z0-9]+/g,' ').trim()}
function uniqueFacts(fs){
 const seenTerm=new Set(),seenAnswer=new Set(),seenPair=new Set(),out=[];
 const sorted=[...fs].sort((a,b)=>{
   const ak=(a.source?.kind==='Cours'?2:a.source?.kind==='Annale'?1:0),bk=(b.source?.kind==='Cours'?2:b.source?.kind==='Annale'?1:0);
   return bk-ak+(b.importance||1)-(a.importance||1);
 });
 for(const f of sorted){
   const t=normTxt(f.term),a=normTxt(f.answer),pair=t+'|'+a;
   if(seenPair.has(pair))continue;
   if(t&&seenTerm.has(t))continue;
   if(a&&a.length>24&&seenAnswer.has(a))continue;
   seenPair.add(pair);if(t)seenTerm.add(t);if(a&&a.length>24)seenAnswer.add(a);out.push(f);
 }
 return out
}
const STOP=new Set('quelle quelles quels quel que quoi pour avec dans des les une un du de la le et est sont sera etre être comment pourquoi concernant cours parmi selon cette celui celle aux au par sur entre peut peuvent doit doivent plus moins'.split(/\s+/));
function flashcardSource(c){
 if(c?.source)return c.source;
 return {kind:'Cours',title:c?.sourceFile||'',year:c?.sourceVersion||'',page:c?.sourcePage||null};
}
function knowledgeItems(sid='all',chid='all'){
 if((C.flashcards||[]).length){
  return C.flashcards.filter(c=>(sid==='all'||c.subjectId===sid)&&(chid==='all'||c.chapterId===chid)).map(c=>({
   id:c.id,subjectId:c.subjectId,chapterId:c.chapterId,conceptId:c.conceptId||c.id,
   term:c.question,answer:c.answer,source:flashcardSource(c),category:c.category||'flashcard',
   importance:c.priority===2?1.3:1,cardLevel:c.cardLevel||'detail'
  }));
 }
 return (C.facts||[]).filter(f=>(sid==='all'||f.subjectId===sid)&&(chid==='all'||f.chapterId===chid));
}
function tokens(s){return new Set(normTxt(s).split(/\s+/).filter(x=>x.length>=4&&!STOP.has(x)))}
function courseSupportFor(q,answer){
 const correctText=(q.correct||[]).map(i=>q.options?.[i]||'').join(' ');
 const selectedText=Array.isArray(answer)?answer.map(i=>q.options?.[i]||'').join(' '):'';
 const target=tokens([q.stem,correctText,selectedText,q.explanation||''].join(' '));
 const fs=uniqueFacts(knowledgeItems(q.subjectId,q.chapterId));
 const scored=fs.map(f=>{
   const tt=tokens(f.term+' '+f.answer);let overlap=0;target.forEach(w=>{if(tt.has(w))overlap++});
   let score=overlap;
   if(q.conceptId&&f.conceptId===q.conceptId)score+=12;
   if(q.conceptId&&f.id===q.conceptId)score+=8;
   if((f.importance||1)>=1.2)score+=.5;
   return{f,score};
 }).filter(x=>x.score>0).sort((a,b)=>b.score-a.score);
 const out=[];const seen=new Set();
 for(const x of scored){
   const k=normTxt(x.f.term)+'|'+normTxt(x.f.answer);if(seen.has(k))continue;
   seen.add(k);out.push(x.f);if(out.length>=4)break;
 }
 if(!out.length){
   const fall=fs.slice().sort((a,b)=>(b.importance||1)-(a.importance||1)).slice(0,2);
   return fall;
 }
 return out;
}
function supportHtml(q,answer){
 const fs=courseSupportFor(q,answer);
 if(!fs.length)return'';
 return `<div class="course-support"><div class="support-title">Point${fs.length>1?'s':''} du cours à retenir</div>${fs.map(f=>`<div class="support-item"><b>${esc(f.term)}</b><div>${esc(f.answer)}</div><div class="source">${esc(sourceText(f.source))}</div></div>`).join('')}</div>`;
}
function rationaleHtml(q){
 if(!q.optionRationales||!q.optionRationales.length)return'';
 return `<details class="rationales" open><summary>Pourquoi les propositions sont vraies / fausses</summary><div>${q.optionRationales.map((r,i)=>`<div class="rationale-row"><span class="choice-letter mini">${String.fromCharCode(65+i)}</span><span>${esc(r)}</span></div>`).join('')}</div></details>`;
}
function oneMediaHtml(m){
 if(!m)return'';
 if(m.html)return `<div class="question-media generated-media">${m.html}${m.caption?`<div class="media-caption">${esc(m.caption)}</div>`:''}</div>`;
 if(m.src)return `<figure class="question-media" data-media-box><div class="media-loading">Chargement du document…</div><img class="question-media-img" src="./${m.src}" data-media-src="./${m.src}" alt="${esc(m.alt||'Document visuel')}" decoding="async">${m.caption?`<figcaption>${esc(m.caption)}</figcaption>`:''}</figure>`;
 return'';
}
function mediaHtml(q){
 const list=(q?.mediaGallery?.length?q.mediaGallery:(q?.media?[q.media]:[]));
 if(!list.length)return'';
 const seen=new Set(),uniq=list.filter(m=>{const k=m?.src||m?.html;if(!k||seen.has(k))return false;seen.add(k);return true});
 return `<div class="question-media-gallery">${uniq.map(oneMediaHtml).join('')}</div>`;
}
function correctionMediaHtml(q){
 const list=(q?.correctionMediaGallery?.length?q.correctionMediaGallery:(q?.correctionMedia?[q.correctionMedia]:[]));
 if(!list.length)return'';
 const seen=new Set(),uniq=list.filter(m=>{const k=m?.src||m?.html;if(!k||seen.has(k))return false;seen.add(k);return true});
 return `<details class="rationales correction-document"><summary>Corrigé original</summary><div class="question-media-gallery">${uniq.map(oneMediaHtml).join('')}</div></details>`;
}
function bindQuestionMedia(){
 document.querySelectorAll('.question-media-img').forEach(img=>{
   const box=img.closest('[data-media-box]'),loading=box?.querySelector('.media-loading');
   const ok=()=>{if(loading)loading.remove();img.classList.add('loaded')};
   const fail=()=>{
     if(loading)loading.innerHTML=`Document indisponible. <button class="btn compact" data-retry-media>Réessayer</button>`;
     const b=loading?.querySelector('[data-retry-media]');
     if(b)b.onclick=()=>{loading.textContent='Nouvel essai…';img.src=img.dataset.mediaSrc+'?r='+Date.now()};
   };
   if(img.complete&&img.naturalWidth)ok();else{img.addEventListener('load',ok,{once:true});img.addEventListener('error',fail,{once:true})}
 });
}
function preloadNextMedia(){
 const q=session?.list?.[session.i+1],src=q?.media?.src;if(!src)return;
 const im=new Image();im.src='./'+src;
}

function visualPool(sid,chid){
 return C.questions.filter(q=>q.media&&q.subjectId===sid&&(chid==='all'||q.chapterId===chid));
}
function runtimeRecovery(err){
 console.error(err);
 try{localStorage.setItem('adaptive-study-last-crash',JSON.stringify({date:new Date().toISOString(),message:String(err?.message||err)}))}catch(_){}
 let x=document.getElementById('runtimeRecovery');
 if(!x){x=document.createElement('div');x.id='runtimeRecovery';x.className='runtime-recovery';document.body.appendChild(x)}
 x.innerHTML=`<b>Adaptive Study a rencontré une erreur.</b><div class="small">${esc(err?.message||String(err))}</div><div class="row" style="margin-top:8px"><button class="btn primary" id="recoverReload">Recharger</button><button class="btn" id="recoverHome">Revenir à l’accueil</button></div>`;
 document.getElementById('recoverReload').onclick=()=>location.reload();
 document.getElementById('recoverHome').onclick=()=>{session=null;stopQuestionTimer();x.remove();try{renderHome();document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id==='home'));}catch(_){location.reload()}};
}
window.addEventListener('unhandledrejection',e=>runtimeRecovery(e.reason||new Error('Promesse rejetée')));
function nav(main){
 try{
   currentMain=main;
   document.querySelectorAll('.bottom-nav button').forEach(b=>b.classList.toggle('active',b.dataset.main===main));
   document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id===main));
   if(main==='quiz')return renderQuizSetup();
   if(main==='cards')return renderCards();
   if(main==='course')return renderCourse();
   if(main==='more')return renderMore();
   return renderHome();
 }catch(e){runtimeRecovery(e)}
}
document.querySelectorAll('.bottom-nav button').forEach(b=>b.onclick=()=>nav(b.dataset.main));

function leaveQuizSession(ask=true,fromHistory=false){
 if(!session)return false;
 if(ask&&!confirm('Revenir au choix du quiz ? Les réponses déjà validées restent enregistrées.'))return false;
 stopQuestionTimer();session=null;review=null;currentMain='quiz';
 document.querySelectorAll('.bottom-nav button').forEach(b=>b.classList.toggle('active',b.dataset.main==='quiz'));
 document.querySelectorAll('.view').forEach(v=>v.classList.toggle('active',v.id==='quiz'));
 renderQuizSetup();
 if(!fromHistory&&history.state?.adaptiveQuizSession){try{history.back()}catch(_){}}
 return true;
}
function pushQuizHistory(){
 try{history.pushState({adaptiveQuizSession:true},'',location.pathname+location.search+'#quiz-session')}catch(_){}
}
window.addEventListener('popstate',()=>{if(session)leaveQuizSession(false,true);else if(document.getElementById('mindMapOverlay'))closeMindMap()});

function cs(sid,cid){
 const k=sid+':'+cid;
 const st=S.concepts[k]||(S.concepts[k]={a:1.5,b:1.5,n:0,c:0,last:0,times:[],wrongStreak:0,highWrong:0});
 if(st.timeRatioEMA==null)st.timeRatioEMA=1;
 if(st.slowCount==null)st.slowCount=0;
 if(st.lowScoreCount==null)st.lowScoreCount=0;
 return st;
}
function mastery(st){if(!st)return .5;return clamp(st.a/(st.a+st.b),0,1)}
function chapterFacts(chid){return uniqueFacts(knowledgeItems('all',chid))}
function chapterPracticeStats(chid){
 const xs=allPracticeItems().filter(x=>x.chapterId===chid),sid=chs[chid]?.subjectId;
 const score=xs.length?xs.reduce((a,x)=>a+Number(x.score||0),0)/xs.length:null;
 const tx=xs.filter(x=>x.targetSec>0&&x.sec>0),timeRatio=tx.length?tx.reduce((a,x)=>a+x.sec/x.targetSec,0)/tx.length:null;
 const concepts=[...new Set(xs.map(x=>x.conceptId).filter(Boolean))].map(cid=>S.concepts[(sid||'')+':'+cid]).filter(Boolean);
 const concept=concepts.length?concepts.reduce((a,st)=>a+mastery(st),0)/concepts.length:null;
 return{n:xs.length,score,timeRatio,concept};
}
function chMastery(chid){
 const p=chapterPracticeStats(chid);
 if(!p.n)return .5;
 const concept=p.concept==null?p.score:p.concept,timePerf=p.timeRatio==null?1:clamp(1-(p.timeRatio-1)*.22,.65,1);
 return clamp(.62*p.score+.28*concept+.10*timePerf,0,1);
}
function subMastery(sid){
 const arr=C.chapters.filter(c=>c.subjectId===sid&&c.available&&(bankPool(sid,c.id).length||cardPool(sid,c.id).length));
 if(!arr.length)return .5;
 const practiced=arr.filter(c=>chapterPracticeStats(c.id).n>0);
 const use=practiced.length?practiced:arr;
 return use.reduce((a,c)=>a+chMastery(c.id),0)/use.length;
}

function allPracticeItems(){
 return (S.sessions||[]).flatMap(se=>(se.results&&se.results.length?se.results:(se.timing||[]))).filter(x=>x&&x.subjectId&&x.score!=null);
}
function subjectPracticeStats(sid){
 const xs=allPracticeItems().filter(x=>x.subjectId===sid),ex=xs.filter(x=>x.kind==='exercise'||String(x.questionId||'').startsWith('ex35_')||String(x.questionId||'').startsWith('ex_'));
 const score=xs.length?xs.reduce((a,x)=>a+Number(x.score||0),0)/xs.length:null;
 const exScore=ex.length?ex.reduce((a,x)=>a+Number(x.score||0),0)/ex.length:null;
 const tx=xs.filter(x=>x.targetSec>0&&x.sec>0),ratio=tx.length?tx.reduce((a,x)=>a+x.sec/x.targetSec,0)/tx.length:null;
 return{n:xs.length,score,exerciseN:ex.length,exerciseScore:exScore,timeRatio:ratio};
}
function subjectMasteryComposite(sid){
 const concept=subMastery(sid),p=subjectPracticeStats(sid);
 if(!p.n)return concept;
 const timePerf=p.timeRatio==null?concept:clamp(1-(p.timeRatio-1)*.22,.65,1);
 if(p.exerciseN>=2)return clamp(.45*concept+.32*p.score+.15*p.exerciseScore+.08*timePerf,0,1);
 return clamp(.58*concept+.34*p.score+.08*timePerf,0,1);
}
const METHOD_TIPS={
 shs:"QROC : 10 min. Liste d’abord les éléments indispensables, puis rédige dense et sans dépasser la limite de lignes.",
 histo:"Avant les propositions, identifie 2–3 critères morphologiques discriminants puis seulement le nom de la structure.",
 sp:"Graphique : axes → population → période → unité → comparaison → conclusion minimale. Ne transforme pas une association en causalité.",
 biocell:"Technique → contrôle → observable → conclusion autorisée. Distingue toujours présence, quantité, localisation et interaction.",
 bio:"Compresse l’exercice en Donnée → Règle → Conclusion. Pour les méthodes, demande ce que la technique mesure et ce qu’elle ne peut pas prouver.",
 chimie:"Pars de la structure : Lewis → VSEPR/hybridation → géométrie/propriété. Fais les relations symboliques avant le calcul mental.",
 phys:"Écris données + unités + schéma, choisis la loi, écris-la symboliquement puis calcule. Vérifie signe, unité et ordre de grandeur."
};
function personalizedAdvice(){
 const stats=C.subjects.map(s=>({s,p:subjectPracticeStats(s.id),m:subjectMasteryComposite(s.id)}));
 const practiced=stats.filter(x=>x.p.n>=2);
 const weak=(practiced.length?practiced:stats).slice().sort((a,b)=>a.m-b.m)[0];
 const slow=practiced.filter(x=>x.p.timeRatio!=null).slice().sort((a,b)=>(b.p.timeRatio||0)-(a.p.timeRatio||0))[0];
 const open=Object.values(S.errors||{}).filter(e=>e.open).sort((a,b)=>(b.count||0)-(a.count||0))[0];
 const highWrong=Object.entries(S.concepts||{}).map(([k,v])=>({k,v})).filter(x=>(x.v.highWrong||0)>0).sort((a,b)=>(b.v.highWrong||0)-(a.v.highWrong||0))[0];
 const arr=[];
 if(weak)arr.push({tone:'green',title:`Priorité : ${weak.s.name}`,body:`Maîtrise estimée ${Math.round(100*weak.m)} %${weak.p.score!=null?` · score global ${Math.round(100*weak.p.score)} %`:''}. ${METHOD_TIPS[weak.s.id]}`});
 if(slow&&slow.p.timeRatio>1.05)arr.push({tone:'cyan',title:`Temps : ${slow.s.name}`,body:`Tu utilises en moyenne ${Math.round(100*slow.p.timeRatio)} % du budget moyen par question. ${METHOD_TIPS[slow.s.id]}`});
 if(open)arr.push({tone:'red',title:`Erreur récurrente : ${subs[open.subjectId]?.name||''}`,body:`Cette notion a généré ${open.count||1} erreur(s). Revois d’abord le point du cours associé puis refais une question sans regarder la correction.`});
 if(highWrong)arr.push({tone:'pink',title:'Confiance à recalibrer',body:`Au moins une notion a été ratée avec une confiance élevée. Sur ces items, impose un contrôle final : donnée → règle → conclusion avant validation.`});
 return arr.slice(0,4);
}
function dueCount(sid='all',chid='all'){return cardPool(sid,chid).filter(c=>{const x=S.cards[c.id];return !!(x&&x.reps>0&&x.due&&x.due<=now())}).length}
function newCardCount(sid='all',chid='all'){return cardPool(sid,chid).filter(c=>!S.cards[c.id]||!(S.cards[c.id].reps>0)).length}
function priorities(){
 return C.chapters.filter(c=>c.available&&(bankPool(c.subjectId,c.id).length||cardPool(c.subjectId,c.id).length)).map(c=>{
   const subj=subs[c.subjectId],m=chMastery(c.id),pstat=chapterPracticeStats(c.id),items=allPracticeItems().filter(x=>x.chapterId===c.id),
   last=Math.max(0,...items.map(x=>Number(x.date||0)),...Object.values(S.errors||{}).filter(e=>e.chapterId===c.id).map(e=>Date.parse(e.last||0)||0)),
   days=last?(now()-last)/DAY:30,forget=clamp(days/9,.35,1),
   open=Object.values(S.errors||{}).filter(e=>e.chapterId===c.id&&e.open).reduce((a,e)=>a+Math.min(3,e.count||1),0),
   slow=pstat.timeRatio==null?0:Math.max(0,pstat.timeRatio-1),unseen=pstat.n?0:1,
   p=subj.coefficient*(c.examWeight||1)*(.26+.50*(1-m)+.12*clamp(slow/.5,0,1)+.12*unseen)*forget*(1+Math.min(.8,open*.08));
   return{c,m,p,stats:pstat,open};
 }).sort((a,b)=>b.p-a.p)
}
function renderHome(){
 const active=C.questions.length,orig=(window.ORIGINAL_CORPUS||[]).length,qroc=C.questions.filter(q=>q.format==='QROC').length,qcm=C.questions.filter(q=>q.format==='QCM').length,
 due=dueCount(),openErr=Object.values(S.errors||{}).filter(e=>e.open).length,prio=priorities(),top=prio[0],advice=personalizedAdvice();
 const subjectCards=C.subjects.map(sub=>{const ps=subjectPracticeStats(sub.id),m=subjectMasteryComposite(sub.id),pct=ps.n?Math.round(100*m):null;return `<button class="mastery-card" data-home-sub="${sub.id}"><span class="mastery-name">${esc(sub.name)}</span><span class="mastery-value">${pct==null?'—':pct+'%'}</span><span class="mastery-meta">${ps.n?`${ps.n} réponses${ps.timeRatio?` · temps ${Math.round(ps.timeRatio*100)}%`:''}`:'pas encore mesurée'}</span>${pct!=null?`<span class="mastery-bar"><i style="width:${pct}%"></i></span>`:''}</button>`}).join('');
 const topBlock=top?`<div class="focus-card"><div class="row"><span class="badge accent">Priorité adaptative</span><span class="badge">${Math.round(top.m*100)}% maîtrise</span><span class="right small">${top.open?top.open+' erreur(s) ouvertes':''}</span></div><h2>${esc(subs[top.c.subjectId]?.name||'')} · ${esc(top.c.title)}</h2><div class="small">Priorité calculée à partir du score, des erreurs répétées, du temps actif et de la récence.</div><div class="quick-actions"><button class="btn primary" id="focusQuiz">20 questions ciblées</button><button class="btn soft" id="focusCards">Flashcards ciblées</button><button class="btn" id="focusCourse">Cours</button></div></div>`:'';
 $('homeContent').innerHTML=`<div class="home-kpis"><div><b>${active}</b><span>questions actives</span></div><div><b>${(C.flashcards||[]).length}</b><span>flashcards</span></div><div><b>${due}</b><span>cartes dues</span></div><div><b>${openErr}</b><span>erreurs ouvertes</span></div></div>${topBlock}<div class="card compact-card"><div class="section-title"><h2 class="grow">Maîtrise par matière</h2><span class="small">score + erreurs + temps</span></div><div class="mastery-grid">${subjectCards}</div></div>${advice.length?`<div class="advice-grid">${advice.slice(0,3).map(a=>`<div class="mini-advice tone-${a.tone}"><b>${esc(a.title)}</b><span>${esc(a.body)}</span></div>`).join('')}</div>`:''}<div class="bank-strip"><button class="bank-mini" id="homePractice"><b>${qcm} QCM + ${qroc} QROC</b><span>Banque active</span></button><button class="bank-mini" id="homeOriginals"><b>${orig}</b><span>originaux PDF</span></button></div><div class="callout compact-note"><b>SHS</b> : les QROC sont entraînables. Aucun commentaire de texte n’est fabriqué sans sujet/corrigé source explicitement exploitable dans le corpus.</div>`;
 $('homePractice').onclick=()=>nav('quiz');$('homeOriginals').onclick=()=>{nav('quiz');setTimeout(()=>toast('Choisis une matière et un cours puis ouvre les originaux PDF.'),50)};
 document.querySelectorAll('[data-home-sub]').forEach(b=>b.onclick=()=>openQuizFor(b.dataset.homeSub,'all'));
 if(top){$('focusQuiz').onclick=()=>openQuizFor(top.c.subjectId,top.c.id);$('focusCards').onclick=()=>startChapterCards(top.c.id,50);$('focusCourse').onclick=()=>openCourseFor(top.c.id)}
}
function subOpts(){return C.subjects.map(s=>`<option value="${s.id}">${esc(s.name)}</option>`).join('')}
function chapterOpts(sid,all=true){return (all?'<option value="all">Tous les chapitres actifs</option>':'')+C.chapters.filter(c=>c.subjectId===sid&&c.available).map(c=>`<option value="${c.id}">${c.id==='histo_conjonctifs'?'★ ':''}${esc(c.title)}${c.id==='histo_conjonctifs'?' — nouveau':''}</option>`).join('')}
function renderQuizSetup(){
 if(session)return renderQuestion();
 $('quizContent').innerHTML=`<div class="card quiz-setup-card"><div class="section-title"><h2 class="grow">Entraînement</h2><span class="badge accent">adaptatif</span></div><div class="quiz-setup-grid"><label><span class="lbl">Matière</span><select id="qSub" class="field">${subOpts()}</select></label><label><span class="lbl">Cours</span><select id="qCh" class="field"></select></label><label><span class="lbl">Nombre</span><select id="qCount" class="field"><option>10</option><option selected>20</option><option>30</option><option>50</option></select></label></div><div id="qStats" class="callout compact-note" style="margin-top:10px"></div><div class="mode-grid"><button class="btn primary" id="qAdaptive"><b>Adaptatif</b><span>erreurs + lenteur + maîtrise</span></button><button class="btn soft" id="qFormat"><b>Format concours</b><span>dossiers/questions liés</span></button><button class="btn soft" id="qExercise"><b>Dossier d’exercice</b><span>Physique · Biochimie · Bio cell</span></button><button class="btn" id="qBank"><b>Banque dérivée</b><span>questions sourcées</span></button><button class="btn" id="qTraining"><b>Entraînement isolé</b><span>QE / entraînements</span></button><button class="btn" id="qOriginal"><b>Originaux PDF</b><span>sujet + corrigé</span></button></div></div>`;
 const s=$('qSub'),c=$('qCh'),cnt=$('qCount'),stats=$('qStats'),fmt=$('qFormat'),tr=$('qTraining'),ex=$('qExercise');
 const upd=()=>{c.innerHTML=chapterOpts(s.value,false);refresh()};
 const refresh=()=>{const sid=s.value,chid=c.value||'all',all=bankPool(sid,chid),der=derivedPool(sid,chid),qr=qrocPool(sid,chid),linked=linkedExamPool(sid,chid),train=trainingPool(sid,chid),orig=(window.ORIGINAL_CORPUS||[]).filter(q=>q.chapterId===chid).length,exCount=window.AdaptiveExercises?.counts?.[sid]||0;stats.innerHTML=`<b>${all.length}</b> actives · ${der.length} dérivées · ${qr.length} QROC · ${linked.length} liées concours · ${train.length} entraînement · ${orig} originaux`;fmt.textContent=sid==='shs'?'QROC — format concours':linked.length?'Format concours lié':'Format concours indisponible';fmt.disabled=sid!=='shs'&&!linked.length;tr.disabled=!train.length;ex.disabled=!exCount;ex.querySelector('span').textContent=exCount?`${exCount} dossier(s) multiquestions disponibles`:'Aucun dossier validé pour cette matière'};
 s.onchange=upd;c.onchange=refresh;upd();
 const go=mode=>startSession(s.value,c.value,mode,Number(cnt.value||20));
 $('qAdaptive').onclick=()=>go(s.value==='shs'?'qroc':'adaptive');$('qBank').onclick=()=>go(s.value==='shs'?'qroc':'bank');$('qFormat').onclick=()=>go(s.value==='shs'?'qroc':'exam');$('qTraining').onclick=()=>go('training');$('qOriginal').onclick=()=>openOriginalCourse(c.value);$('qExercise').onclick=()=>startExercise(s.value)
}
function openQuizFor(sid,chid){nav('quiz');setTimeout(()=>{if(!$('qSub'))return;$('qSub').value=sid;$('qSub').dispatchEvent(new Event('change'));$('qCh').value=chid},0)}
function openCourseFor(chid){const c=chs[chid];if(!c)return;nav('course');setTimeout(()=>{if(!$('sumSub'))return;$('sumSub').value=c.subjectId;$('sumSub').dispatchEvent(new Event('change'));$('sumCh').value=chid;$('sumCh').dispatchEvent(new Event('change'))},0)}

function cleanTerm(t){return t.replace(/[?]+$/,'').replace(/^(Que|Qu'|Quel|Quelle|Quels|Quelles|Pourquoi|Comment|À quoi|Où|De quoi)\s+/i,'').trim()}
function factsFor(sid,chid){return C.facts.filter(f=>f.subjectId===sid&&(chid==='all'||f.chapterId===chid))}
function distractorFacts(f,limit=8){let arr=C.facts.filter(x=>x.id!==f.id&&x.chapterId===f.chapterId&&x.category===f.category);if(arr.length<3)arr=C.facts.filter(x=>x.id!==f.id&&x.chapterId===f.chapterId);if(arr.length<3)arr=C.facts.filter(x=>x.id!==f.id&&x.subjectId===f.subjectId);return shuffle(arr).slice(0,limit)}
function remember(sig){S.seenGenerated=S.seenGenerated||[];S.seenGenerated.push(sig);if(S.seenGenerated.length>500)S.seenGenerated=S.seenGenerated.slice(-350)}
function pickVariant(f){
 const possible=['direct','direct','direct'];
 if(['definition','mapping','formula','number','rule','trend'].includes(f.category))possible.push('reverse');
 if(f.category==='sequence')possible.push('sequence','sequence');
 const seen=new Set(S.seenGenerated||[]),fresh=possible.filter(v=>!seen.has(f.id+'|'+v));
 return shuffle(fresh.length?fresh:possible)[0]
}
function directQuestion(f){
 const ds=distractorFacts(f,6).slice(0,3),opts=shuffle([{txt:f.answer,ok:true},...ds.map(x=>({txt:x.answer,ok:false}))]),sig=f.id+'|direct';remember(sig);
 return QBase(f,f.term,opts.map(x=>x.txt),[opts.findIndex(x=>x.ok)],'QCU',sig)
}
function reverseQuestion(f){
 const ds=distractorFacts(f,6).slice(0,3),opts=shuffle([{txt:cleanTerm(f.term),ok:true},...ds.map(x=>({txt:cleanTerm(x.term),ok:false}))]),stem=`Quelle notion correspond le mieux à l’énoncé suivant ?\n« ${f.answer} »`,sig=f.id+'|reverse';remember(sig);
 return QBase(f,stem,opts.map(x=>x.txt),[opts.findIndex(x=>x.ok)],'QCU',sig)
}
function associationQuestion(f){
 const others=distractorFacts(f,6).slice(0,3),correct=`${cleanTerm(f.term)} — ${f.answer}`,wrong=others.map(x=>`${cleanTerm(f.term)} — ${x.answer}`),opts=shuffle([{txt:correct,ok:true},...wrong.map(txt=>({txt,ok:false}))]),sig=f.id+'|association';remember(sig);
 return QBase(f,'Quelle association est correcte ?',opts.map(x=>x.txt),[opts.findIndex(x=>x.ok)],'QCU',sig)
}
function contextQuestion(f){
 const lead={bio:'Dans le cadre du raisonnement biochimique,',biocell:'Dans l’interprétation d’une expérience de biologie cellulaire,',histo:'En histologie,',sp:'En santé publique,',chimie:'En chimie,',phys:'En physique,',shs:'Dans le cadre du cours de SHS,'}[f.subjectId]||'Dans ce chapitre,';
 const ds=distractorFacts(f,6).slice(0,3),opts=shuffle([{txt:f.answer,ok:true},...ds.map(x=>({txt:x.answer,ok:false}))]),stem=`${lead} quelle proposition répond correctement à : « ${f.term} »`,sig=f.id+'|context';remember(sig);
 return QBase(f,stem,opts.map(x=>x.txt),[opts.findIndex(x=>x.ok)],'QCU',sig)
}
function sequenceQuestion(f){
 let parts=f.answer.split(/\s*(?:→|;)\s*/).filter(Boolean);if(parts.length<3)return directQuestion(f);
 let perms=[parts,[parts[1],parts[0],...parts.slice(2)],[...parts].reverse(),[parts[0],...parts.slice(2),parts[1]]].map(a=>a.join(' → '));
 perms=[...new Set(perms)];while(perms.length<4)perms.push(shuffle(parts).join(' → '));perms=[...new Set(perms)].slice(0,4);
 const opts=shuffle(perms.map(x=>({txt:x,ok:x===parts.join(' → ')}))),sig=f.id+'|sequence';remember(sig);
 return QBase(f,f.term,opts.map(x=>x.txt),[opts.findIndex(x=>x.ok)],'QCU',sig)
}
function QBase(f,stem,options,correct,format,sig){return{id:'gen_'+Date.now()+'_'+Math.random().toString(36).slice(2,7),subjectId:f.subjectId,chapterId:f.chapterId,conceptId:f.conceptId,format,stem,options,correct,explanation:f.answer,source:f.source,difficulty:1,provenance:'GENERATED_RUNTIME',timeTargetSec:60,signature:sig}}
function fromFact(f){const v=pickVariant(f);return v==='reverse'?reverseQuestion(f):v==='sequence'?sequenceQuestion(f):directQuestion(f)}

function entitiesFor(sid,chid){return (C.entities||[]).filter(e=>e.subjectId===sid&&(chid==='all'||e.chapterId===chid))}
function entityQCM(sid,chid){
 const pool=entitiesFor(sid,chid);if(!pool.length)return null;
 const e=shuffle(pool)[0],same=(C.entities||[]).filter(x=>x.entityType===e.entityType&&x.id!==e.id),props=shuffle(e.properties||[]);
 const nTrue=Math.min(props.length,Math.max(2,Math.min(3,props.length))),trueProps=props.slice(0,nTrue),options=trueProps.map(p=>({txt:`${p.label} : ${p.value}`,ok:true}));
 const wanted=5-options.length;for(let i=0;i<wanted;i++){
   const labelSource=props[(nTrue+i)%props.length]||props[0];let candidates=[];
   same.forEach(x=>(x.properties||[]).forEach(p=>{if(!labelSource||p.label===labelSource.label)candidates.push(p)}));
   if(!candidates.length)same.forEach(x=>candidates.push(...(x.properties||[])));
   const p=shuffle(candidates)[0];if(p)options.push({txt:`${p.label} : ${p.value}`,ok:false});
 }
 const shuffled=shuffle(options),correct=[];shuffled.forEach((o,i)=>{if(o.ok)correct.push(i)});
 const explanation=`${e.name} — `+(e.properties||[]).map(p=>`${p.label} : ${p.value}`).join(' ; ');
 const sig='entity|'+e.id+'|'+shuffled.map(x=>x.txt).join('|');remember(sig);
 const optionRationales=shuffled.map(o=>o.ok?`Vrai — cette propriété appartient à ${e.name}.`:`Faux — cette association ne correspond pas à ${e.name}. Les propriétés à retenir sont : ${(e.properties||[]).map(p=>p.label+' : '+p.value).join(' ; ')}`);
 return{id:'ent_'+Date.now()+'_'+Math.random().toString(36).slice(2,6),subjectId:e.subjectId,chapterId:e.chapterId,conceptId:'entity:'+e.id,format:'QCM',stem:`Concernant ${e.name}, quelle(s) proposition(s) est/sont exacte(s) ?`,options:shuffled.map(x=>x.txt),correct,optionRationales,explanation,source:e.source,difficulty:2,provenance:'GENERATED_RUNTIME',timeTargetSec:90,signature:sig}
}
function generatedQCM(sid,chid){
 const eq=entityQCM(sid,chid);if(eq&&Math.random()<.78)return eq;
 let base=uniqueFacts(factsFor(sid,chid)).sort((a,b)=>priorityFact(b)-priorityFact(a));if(base.length<5)return base.length?fromFact(base[0]):eq;
 const anchor=base[0],same=base.filter(f=>f.category===anchor.category&&f.id!==anchor.id);let chosen=[anchor,...same.slice(0,4)];if(chosen.length<5)chosen.push(...base.filter(f=>!chosen.some(x=>x.id===f.id)).slice(0,5-chosen.length));
 const nTrue=2+Math.floor(Math.random()*3),trueSet=new Set(shuffle([0,1,2,3,4]).slice(0,nTrue)),options=[],correct=[],optionRationales=[];
 chosen.forEach((f,i)=>{if(trueSet.has(i)){options.push(f.answer);correct.push(i);optionRationales.push(`Vrai — ${f.term} : ${f.answer}`)}else{const alt=(distractorFacts(f,14).filter(x=>x.category===f.category).find(x=>normTxt(x.answer)!==normTxt(f.answer))||distractorFacts(f,14).find(x=>normTxt(x.answer)!==normTxt(f.answer))||base.find(x=>x.id!==f.id));options.push(alt?alt.answer:'Proposition non soutenue par le cours');optionRationales.push(`Faux — pour « ${f.term} », le cours donne : ${f.answer}`)}});
 const chapterTitle=chid==='all'?subs[sid].name:chs[chid].title,sig='qcm38|'+chosen.map(x=>x.id).join(',')+'|'+[...trueSet].join(',');remember(sig);
 return{id:'qcm_'+Date.now(),subjectId:sid,chapterId:anchor.chapterId,conceptId:anchor.conceptId||('qcm_'+(chid==='all'?sid:chid)),format:'QCM',stem:`Concernant ${chapterTitle}, quelle(s) proposition(s) est/sont exacte(s) ?`,options,correct,optionRationales,explanation:'Les propositions sont construites à partir de points de cours proches afin d’éviter les QCM artificiellement hétérogènes.',source:{kind:'Génération locale sourcée',title:chapterTitle},difficulty:3,provenance:'GENERATED_RUNTIME',timeTargetSec:90,signature:sig}
}
function numericQuestion(sid,chid){
 const gs=C.generators.filter(g=>g.subjectId===sid&&(chid==='all'||g.chapterId===chid));if(!gs.length)return null;const g=shuffle(gs)[0],rnd=(a,b,st=1)=>Math.round((a+Math.random()*(b-a))/st)*st;
 if(g.handler==='bio_mass_aa'){const n=rnd(80,900,10),ans=n*110/1000;return{id:'num'+Date.now(),subjectId:sid,chapterId:g.chapterId,conceptId:g.conceptId,format:'NUMERIC',stem:`Une protéine contient ${n} acides aminés. En utilisant l’approximation du cours (110 Da par AA), estimer sa masse moléculaire.`,numericAnswer:ans,tolerance:.015,unit:'kDa',explanation:`${n} × 110 Da = ${n*110} Da = ${ans.toFixed(1)} kDa.`,source:g.source,difficulty:2,provenance:'GENERATED_RUNTIME',timeTargetSec:70}}
 if(g.handler==='phys_delta_epg'){const m=rnd(50,90,5),dz=rnd(5,40,5),ans=m*9.81*dz;return{id:'num'+Date.now(),subjectId:sid,chapterId:g.chapterId,conceptId:g.conceptId,format:'NUMERIC',stem:`Une masse de ${m} kg s’élève de ${dz} m. Calculer la variation d’énergie potentielle de pesanteur avec g = 9,81 m·s⁻².`,numericAnswer:ans,tolerance:.015,unit:'J',explanation:`ΔEp = mgΔz ≈ ${ans.toFixed(0)} J.`,source:g.source,difficulty:2,provenance:'GENERATED_RUNTIME',timeTargetSec:90}}
 if(g.handler==='phys_ec'){const m=rnd(200,800,50)/1000,v=rnd(2,12,1),ans=.5*m*v*v;return{id:'num'+Date.now(),subjectId:sid,chapterId:g.chapterId,conceptId:g.conceptId,format:'NUMERIC',stem:`Un objet de masse ${m.toFixed(2).replace('.',',')} kg possède une vitesse de ${v} m·s⁻¹. Calculer son énergie cinétique.`,numericAnswer:ans,tolerance:.02,unit:'J',explanation:`Ec = 1/2 mv² ≈ ${ans.toFixed(2)} J.`,source:g.source,difficulty:2,provenance:'GENERATED_RUNTIME',timeTargetSec:90}}
 if(g.handler==='phys_cap_field'){const dv=rnd(20,120,5),h=rnd(4,12,1),ans=(dv*1e-3)/(h*1e-9);return{id:'num'+Date.now(),subjectId:sid,chapterId:g.chapterId,conceptId:g.conceptId,format:'NUMERIC',stem:`Une membrane de ${h} nm présente une différence de potentiel de ${dv} mV. Estimer la norme du champ électrique à travers la membrane.`,numericAnswer:ans,tolerance:.025,unit:'V/m',explanation:`|E| = |ΔV|/h ≈ ${ans.toExponential(2)} V/m.`,source:g.source,difficulty:2,provenance:'GENERATED_RUNTIME',timeTargetSec:95}}
 if(g.handler==='phys_delta_electric'){const z=[1,2][Math.floor(Math.random()*2)],dv=rnd(-100,100,10),ans=z*dv/1000;return{id:'num'+Date.now(),subjectId:sid,chapterId:g.chapterId,conceptId:g.conceptId,format:'NUMERIC',stem:`Un ion de charge +${z}e traverse une différence de potentiel ΔV = ${dv} mV. Donner la variation d’énergie potentielle en eV.`,numericAnswer:ans,tolerance:.015,unit:'eV',explanation:`ΔEp = z·ΔV(V) = ${ans.toFixed(3)} eV.`,source:g.source,difficulty:2,provenance:'GENERATED_RUNTIME',timeTargetSec:90}}
 return null
}
function priorityFact(f){
 const st=S.concepts[f.subjectId+':'+f.conceptId],m=mastery(st),days=st?.last?(now()-st.last)/DAY:30;
 const wrong=clamp((st?.wrongStreak||0)/2,0,1),slow=clamp(((st?.timeRatioEMA||1)-1)/.55,0,1),high=clamp((st?.highWrong||0)/2,0,1);
 return .42*(1-m)+.23*wrong+.17*slow+.08*high+.06*clamp(days/9,.2,1)+.04*Math.random();
}
function questionPriority(q){
 const st=S.concepts[q.subjectId+':'+q.conceptId],m=mastery(st),wrong=clamp((st?.wrongStreak||0)/2,0,1),slow=clamp(((st?.timeRatioEMA||1)-1)/.55,0,1);
 return .5*(1-m)+.28*wrong+.18*slow+.04*Math.random();
}
function bankPool(sid,chid){return C.questions.filter(q=>q.subjectId===sid&&(chid==='all'||q.chapterId===chid))}
function derivedPool(sid,chid){return bankPool(sid,chid).filter(q=>{const p=String(q.provenance||'');return p.startsWith('DERIVED_PDF')||p.startsWith('PDF_DERIVED')||p==='DERIVED_ANNAL'})}
function trainingPool(sid,chid){return derivedPool(sid,chid).filter(q=>/TRAINING/.test(String(q.provenance||''))||q.exerciseMode==='TRAINING_ISOLATED')}
function linkedExamPool(sid,chid){return bankPool(sid,chid).filter(q=>q.exerciseMode==='EXAM_LINKED'&&q.exerciseGroupId)}
function linkedExerciseSession(sid,chid,count){const pool=linkedExamPool(sid,chid),groups=new Map();for(const q of pool){if(!groups.has(q.exerciseGroupId))groups.set(q.exerciseGroupId,[]);groups.get(q.exerciseGroupId).push(q)}const gs=[...groups.values()].sort((a,b)=>questionPriority(b[0])-questionPriority(a[0]));let out=[];for(const g of gs){g.sort((a,b)=>String(a.id).localeCompare(String(b.id),undefined,{numeric:true}));if(out.length&&out.length+g.length>count)break;out.push(...g);if(out.length>=count)break}return out.slice(0,Math.max(count,out.length))}
function annalPool(sid,chid){return bankPool(sid,chid).filter(q=>q.provenance==='ORIGINAL_ANNAL'||q.provenance==='ORIGINAL_QE'||q.provenance==='TRAINING_QROC'||(q.provenance==='SOURCE_VISUAL'&&q.source?.kind==='Annale'))}
function originalPool(sid,chid){return bankPool(sid,chid)}
function qrocPool(sid,chid){
 return C.questions
  .filter(q=>q.format==='QROC'&&q.subjectId===sid&&(chid==='all'||q.chapterId===chid))
  .sort((a,b)=>{
    const pa=a.trainingPriority==='prioritaire'?1:0,pb=b.trainingPriority==='prioritaire'?1:0;
    if(pa!==pb)return pb-pa;
    return questionPriority(b)-questionPriority(a);
  });
}
function buildSession(sid,chid,mode,count){
 let out=[],all=bankPool(sid,chid).slice().sort((a,b)=>questionPriority(b)-questionPriority(a)),annals=annalPool(sid,chid).slice().sort((a,b)=>questionPriority(b)-questionPriority(a)),derived=derivedPool(sid,chid).slice().sort((a,b)=>questionPriority(b)-questionPriority(a)),visuals=visualPool(sid,chid).slice().sort((a,b)=>questionPriority(b)-questionPriority(a)),qrocs=qrocPool(sid,chid);
 const sessionSemanticKey=q=>q.format==='QROC'?(q.detailSignature||((q.basisFactIds||[]).slice().sort().join('|'))||q.conceptId||q.id):(q.conceptId||q.id);
 const uniqueConceptSlice=(arr,n)=>{const out=[],seen=new Set();for(const q of arr){const key=sessionSemanticKey(q);if(seen.has(key))continue;seen.add(key);out.push(q);if(out.length>=n)return out}if(out.length<n){for(const q of arr){if(out.some(x=>x.id===q.id))continue;out.push(q);if(out.length>=n)break}}return out};
 if(mode==='qroc')return uniqueConceptSlice(qrocs,count);
 if(mode==='visual')return uniqueConceptSlice(visuals,count);
 if(mode==='annals')return uniqueConceptSlice(annals,count);
 if(mode==='training')return uniqueConceptSlice(trainingPool(sid,chid).sort((a,b)=>questionPriority(b)-questionPriority(a)),count);
 if(mode==='exam')return linkedExerciseSession(sid,chid,count);
 if(mode==='bank')return uniqueConceptSlice(derived,count);
 const used=new Set();
 const pushUnique=(arr,n)=>{const seenConcept=new Set(out.map(sessionSemanticKey).filter(Boolean));const passes=[arr.filter(q=>!seenConcept.has(sessionSemanticKey(q))),arr];for(const pass of passes){for(const q of pass){if(out.length>=count||n<=0)break;if(used.has(q.id))continue;const key=sessionSemanticKey(q);if(pass===passes[0]&&seenConcept.has(key))continue;out.push(q);used.add(q.id);seenConcept.add(key);n--}if(n<=0||out.length>=count)break}};
 if(mode==='adaptive'&&sid==='shs'){
   pushUnique(qrocs,Math.min(Math.ceil(count*.35),qrocs.length));
   pushUnique(annals,Math.min(Math.ceil(count*.15),annals.length));
   pushUnique(derived,count-out.length);
 }else if(mode==='adaptive'){
   const visualN=Math.min(visuals.length,Math.ceil(count*(['histo','sp','biocell'].includes(sid)?.28:.15)));
   pushUnique(visuals,visualN);
   pushUnique(annals,Math.min(Math.ceil(count*.16),annals.length));
   pushUnique(derived,count-out.length);
 }
 pushUnique(all,count-out.length);
 // v3.18 final: sessions use only the materialized, audited bank. No runtime-generated
 // fallback is permitted for the 22 available courses; if a caller requests more
 // questions than the bank can provide, return the available audited questions only.
 return out.slice(0,count)
}
function generateExercise(sid){
 const engine=window.AdaptiveExercises;
 if(!engine||engine.auditStatus!=='PDF_AND_ANNAL_MODEL_ONLY'||typeof engine.generate!=='function')return null;
 return engine.generate(sid);
}
function startExercise(sid){
 const ex=generateExercise(sid);
 if(!ex)return toast('Module exercice indisponible pour cette matière.');
 session={list:ex.questions,i:0,score:0,max:0,conf:2,qStart:now(),answered:false,timing:[],results:[],exercise:ex};
 pushQuizHistory();renderQuestion();
}
function startSession(sid,chid,mode,count,fromQuick=false){if(fromQuick){sid=priorities()[0]?.c.subjectId||sid;chid='all'}const list=buildSession(sid,chid,mode,count);if(!list.length){toast(mode==='annals'?'Aucun QE/annale original transcrit dans ce filtre.':'Pas assez de contenu intégré pour ce filtre.');return}session={list,i:0,score:0,max:0,conf:2,qStart:now(),answered:false,timing:[]};pushQuizHistory();renderQuestion()}

function provenanceLabel(q){const p=String(q?.provenance||'');if(p==='ORIGINAL_ANNAL')return'Annale originale';if(p==='ORIGINAL_QE')return'QE original';if(p==='TRAINING_QROC')return'QROC entraînement';if(p.includes('DERIVED')&&p.includes('TRAINING'))return'Entraînement';if(p.includes('DERIVED')&&p.includes('EXAM'))return q?.format==='QROC'?'QROC dérivée':'Dérivée concours';if(p==='DERIVED_ANNAL')return'Dérivée d’annale/QE';if(p==='GENERATED_EXERCISE')return'Exercice';if(p==='SOURCE_VISUAL')return'Document source';return'Question sourcée'}
function renderQuestion(){
 const q=session.list[session.i];if(!q)return finishSession();
 let answer='';
 if(q.format==='QCM'||q.format==='QCU'){answer=`<div id="answerList" style="display:grid;gap:7px">${q.options.map((o,i)=>`<label class="choice" data-i="${i}"><input ${q.format==='QCU'?'type="radio" name="ans"':'type="checkbox"'} value="${i}"><span class="choice-letter">${String.fromCharCode(65+i)}</span><span>${esc(o)}</span></label>`).join('')}</div>`}
 else if(q.format==='NUMERIC')answer=`<input id="numAns" class="field" inputmode="decimal" placeholder="Valeur numérique ${esc(q.unit||'')}">`;
 else if(q.format==='QROC')answer=`<textarea id="qrocAns" class="field" placeholder="Rédige ta réponse"></textarea><div id="lineCount" class="small" style="margin-top:4px"></div>`;
 const ex=session.exercise;
 const exMedia=ex?.media?mediaHtml({media:ex.media}):'';
 const sharedMedia=ex?`<div class="exercise-context"><div class="row"><span class="badge accent">Contexte complet</span><span class="badge warn">${esc(ex.level||'avancé')}</span><b>${esc(ex.title)}</b></div><div class="exercise-stem">${esc(ex.context)}</div>${exMedia}</div>`:'';
 const qMedia=mediaHtml(q);
 $('quizContent').innerHTML=`<div class="card">${sharedMedia}<div class="quiz-session-top"><button id="leaveSession" class="btn soft compact">← Choix du quiz</button><div id="questionClock" class="question-clock"></div></div><div class="row"><div class="question-meta grow"><span class="badge accent">${session.i+1}/${session.list.length}</span><span class="badge">${esc(subs[q.subjectId]?.name||'')}</span><span class="badge">${esc(chs[q.chapterId]?.title||'')}</span><span class="badge ${['ORIGINAL_ANNAL','ORIGINAL_QE'].includes(q.provenance)?'ok':''}">${esc(provenanceLabel(q))}</span>${q.format==='QCM'?'<span class="badge warn">1 à 5 réponses exactes</span>':''}</div><span class="small">${Math.round(100*session.score/Math.max(1,session.max))}%</span></div><div class="progress" style="margin-top:9px"><div style="width:${100*session.i/session.list.length}%"></div></div><div class="qtext">${esc(q.stem).replace(/\n/g,'<br>')}</div>${qMedia}<div class="small">Confiance avant réponse</div><div class="conf"><button data-conf="1">Hasard</button><button data-conf="2" class="active">Moyenne</button><button data-conf="3">Sûr</button></div>${answer}<div id="feedback" class="feedback hidden"></div><div class="sticky-actions"><button id="leaveSessionBottom" class="btn ghost">← Choix du quiz</button><span class="grow"></span><button id="validate" class="btn primary">Valider</button><button id="nextQ" class="btn primary hidden">Suivante</button></div></div>`;
 document.querySelectorAll('.choice input').forEach(inp=>inp.onchange=()=>{if(q.format==='QCU')document.querySelectorAll('.choice').forEach(l=>l.classList.remove('selected'));inp.closest('.choice').classList.toggle('selected',inp.checked)});
 document.querySelectorAll('[data-conf]').forEach(b=>b.onclick=()=>{if(session.answered)return;session.conf=Number(b.dataset.conf);document.querySelectorAll('[data-conf]').forEach(x=>x.classList.toggle('active',x===b))});
 if(q.format==='QROC')$('qrocAns').oninput=e=>{const n=e.target.value.trim()?e.target.value.trim().split(/\n+/).length:0;$('lineCount').textContent=`${n} ligne(s)${q.maxLines?' / '+q.maxLines+' max':''}`};
 $('validate').onclick=()=>submit(q);
 $('leaveSession').onclick=()=>leaveQuizSession(true);
 const leaveBottom=$('leaveSessionBottom');if(leaveBottom)leaveBottom.onclick=()=>leaveQuizSession(true);
 bindQuestionMedia();preloadNextMedia();session.qStart=now();initQuestionTiming(q)
}
function getAns(q){if(q.format==='QCU'){const x=document.querySelector('input[name=ans]:checked');return x?Number(x.value):null}if(q.format==='QCM')return [...document.querySelectorAll('#answerList input:checked')].map(x=>Number(x.value));if(q.format==='NUMERIC')return $('numAns').value;if(q.format==='QROC')return $('qrocAns').value}
function normQroc(t){return String(t??'').toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g,'').replace(/[’'‐‑–—-]/g,' ').replace(/\s+/g,' ').trim()}
function qrocScore(q,text){
 const low=normQroc(text),groups=q.keywordGroups||[];
 const hits=groups.map(g=>g.some(k=>low.includes(normQroc(k))));
 const lines=text.trim()?text.trim().split(/\n+/).length:0;
 let sc=hits.length?hits.filter(Boolean).length/hits.length:0;
 if(q.maxLines&&lines>q.maxLines)sc=Math.max(0,sc-.1*(lines-q.maxLines));
 return{score:sc,errors:hits.filter(x=>!x).length,hits,lines}
}
function score(q,a){
 if(q.format==='QCU'){const ok=Number(a)===q.correct[0];return{score:ok?1:0,errors:ok?0:1}}
 if(q.format==='QCM'){const S1=new Set(a),C1=new Set(q.correct),e=[...S1].filter(x=>!C1.has(x)).length+[...C1].filter(x=>!S1.has(x)).length;return{score:e===0?1:e===1?.7:e===2?.1:0,errors:e}}
 if(q.format==='NUMERIC'){const v=Number(String(a).replace(',','.')),t=Number(q.numericAnswer),ok=Number.isFinite(v)&&Math.abs(v-t)<=Math.max(Math.abs(t)*(q.tolerance||.03),q.absoluteTolerance||0);return{score:ok?1:0,errors:ok?0:1}}
 return qrocScore(q,a)
}
function updateLearning(q,res,sec,answer){
 const st=cs(q.subjectId,q.conceptId),target=questionTargetSec(q),ratio=target?sec/target:1,baseW=(.9+.2*(q.difficulty||1))*(session.conf===3?1.12:session.conf===1?.92:1),timeFactor=res.score>=.7?clamp(1.08-.12*Math.max(0,ratio-.75),.86,1.08):clamp(1-.05*Math.max(0,ratio-1),.92,1),w=baseW*timeFactor;
 st.n++;st.last=now();st.times.push(sec);
 const tr=target?sec/target:1;st.timeRatioEMA=st.n<=1?tr:(.72*(st.timeRatioEMA||1)+.28*tr);
 if(tr>1.15)st.slowCount=(st.slowCount||0)+1;
 if(res.score<.7)st.lowScoreCount=(st.lowScoreCount||0)+1;
 if(res.score>=.7){st.c++;st.a+=w*Math.max(.7,res.score);st.wrongStreak=0}else{st.b+=w*(session.conf===3?1.3:1);st.wrongStreak++;if(session.conf===3)st.highWrong++}
 S.daily.attempts++;
 const key=q.subjectId+':'+q.conceptId;
 if(res.score<1){const old=S.errors[key];const supp=courseSupportFor(q,answer).map(f=>({term:f.term,answer:f.answer,source:f.source}));
 S.errors[key]={id:key,subjectId:q.subjectId,chapterId:q.chapterId,conceptId:q.conceptId,question:q.stem,correction:q.explanation,courseSupport:supp,optionRationales:q.optionRationales||[],source:q.source,count:(old?.count||0)+1,open:true,last:new Date().toISOString(),confidence:session.conf,time:sec,targetSec:questionTargetSec(q),score:res.score};
 const supportBack=[q.explanation,...supp.map(x=>x.term+' — '+x.answer)].filter(Boolean).join('\n\n');
 S.cards['err:'+key]=Object.assign(S.cards['err:'+key]||{interval:0,ease:2,reps:0},{due:now(),custom:true,front:q.stem,back:supportBack,subjectId:q.subjectId,chapterId:q.chapterId,source:{kind:'Erreur personnelle'}})}
 save()
}
function submit(q){
 const a=getAns(q);if((q.format==='QCU'&&a===null)||(q.format==='QCM'&&!a.length)||(q.format==='NUMERIC'&&!String(a).trim())||(q.format==='QROC'&&!String(a).trim()))return toast('Choisis ou saisis une réponse.');
 session.answered=true;const sec=Math.max(1,Math.round(activeElapsedMs()/1000)),targetSec=questionTargetSec(q);stopQuestionTimer();const r=score(q,a);session.score+=r.score;session.max++;session.timing=session.timing||[];const kind=session.exercise?'exercise':['ORIGINAL_ANNAL','ORIGINAL_QE'].includes(q.provenance)?'annal':q.provenance==='SOURCE_VISUAL'?'visual':'quiz';
 const itemResult={subjectId:q.subjectId,chapterId:q.chapterId,questionId:q.id,conceptId:q.conceptId,sec,targetSec,ratio:targetSec?sec/targetSec:null,score:r.score,valid:true,activeOnly:true,kind,format:q.format};
 session.timing.push(itemResult);session.results=session.results||[];session.results.push(itemResult);updateLearning(q,r,sec,a);
 if(['QCM','QCU'].includes(q.format))document.querySelectorAll('.choice').forEach((lab,i)=>{const sel=lab.querySelector('input').checked,cor=q.correct.includes(i);lab.querySelector('input').disabled=true;if(cor)lab.classList.add('correct');if(sel&&!cor)lab.classList.add('wrong');if(cor&&!sel)lab.classList.add('missed')});
 let detail='';
 if(q.format==='NUMERIC')detail=`<div style="margin-top:5px">Réponse attendue : <b>${Number(q.numericAnswer).toLocaleString('fr-FR')} ${esc(q.unit||'')}</b></div>`;
 if(q.format==='QROC')detail=`<div class="callout" style="margin-top:7px"><b>Auto-évaluation indicative</b><div class="small">Le repérage automatique cherche les idées-clés et ne remplace pas la comparaison avec le corrigé.</div></div><div style="margin-top:7px">${(q.expectedPoints||[]).map((p,i)=>`${r.hits[i]?'✓':'○'} ${esc(p)}`).join('<br>')}</div><div class="small">${r.lines} ligne(s)</div>`;
 $('feedback').classList.remove('hidden');
 const timeClass=timingStatus(sec,targetSec),timeFeedback=targetSec?`<div class="timing-feedback ${timeClass}"><b>Temps : ${fmtSec(sec)}</b><span>repère moyen concours ${fmtSec(targetSec)} · ${sec<=targetSec?'dans le repère':`dépassement de ${fmtSec(sec-targetSec)}`}</span><small>Le temps ne modifie pas le score brut ; il module légèrement la maîtrise. Le temps passé en arrière-plan n’est pas compté.</small></div>`:'';
 const explanationBlock=q.explanation?`<div class="correction-main"><b>Correction</b><div>${esc(q.explanation)}</div><div class="source">${esc(sourceText(q.source))}</div></div>`:'';
 $('feedback').innerHTML=`<strong class="score">${Math.round(100*r.score)}%</strong>${timeFeedback}${detail}${explanationBlock}${rationaleHtml(q)}${correctionMediaHtml(q)}${supportHtml(q,a)}`;
 bindQuestionMedia();
 $('validate').classList.add('hidden');$('nextQ').classList.remove('hidden');$('nextQ').onclick=()=>{stopQuestionTimer();session.i++;session.conf=2;session.answered=false;renderQuestion()}
}
function finishSession(){
 stopQuestionTimer();
 const pct=Math.round(100*session.score/Math.max(1,session.max));
 const tSum=sessionTimingSummary(session.timing||[]);
 S.sessions.push({date:new Date().toISOString(),score:session.score,max:session.max,timing:session.timing||[],results:session.results||session.timing||[],timingSummary:tSum,exercise:!!session.exercise,subjectId:(session.results||session.timing||[])[0]?.subjectId||null});
 save();
 const timingBlock=tSum?`<div class="session-timing-report"><div class="timing-kpis"><div><b>${fmtSec(tSum.avg)}</b><span>moyenne / question</span></div><div><b>${fmtSec(tSum.avgTarget)}</b><span>repère concours moyen</span></div><div><b>${tSum.onTime}/${tSum.total}</b><span>dans le repère</span></div></div><div class="callout ${tSum.ratio<=1?'ok':tSum.ratio<=1.25?'warn':'bad'}" style="margin-top:8px"><b>${tSum.ratio<=1?'Gestion du temps dans le repère':tSum.ratio<=1.25?'Léger dépassement moyen':'Dépassement moyen important'}</b><div class="small">Ratio moyen : ${Math.round(tSum.ratio*100)} % du temps moyen disponible par question. Cette donnée est séparée de ta maîtrise et de ton score.</div></div></div>`:'';
 $('quizContent').innerHTML=`<div class="card"><h2>Session terminée</h2><div class="kpi" style="margin-top:5px">${pct}%</div><div class="small">Score calculé avec le barème correspondant au format de chaque question.</div>${timingBlock}<div class="row" style="margin-top:10px"><button id="newSession" class="btn primary">Retour aux réglages</button><button id="toErrors" class="btn">Voir mes erreurs</button><button id="toTiming" class="btn">Analyse du temps</button></div></div>`;
 session=null;try{history.replaceState({adaptiveQuizSession:false},'',location.pathname+location.search)}catch(_){}
 $('newSession').onclick=renderQuizSetup;
 $('toErrors').onclick=()=>{currentMore='errors';nav('more')};
 $('toTiming').onclick=()=>{currentMore='timing';nav('more')};
}


function isQuestionLike(s){
 const t=String(s||'').trim();
 return /\?$/.test(t)||/^(quel|quelle|quels|quelles|comment|pourquoi|qu['’']est|que |à quoi|dans quel|où |quand |combien|peut-on|faut-il|cite|définis|explique)/i.test(t);
}
function cleanTopic(s){return String(s||'').replace(/[?.:]+$/,'').trim()}
function naturalFactFront(f){
 const t=String(f.term||'').trim();if(isQuestionLike(t))return t;
 const map={definition:`Définis précisément : ${t}.`,mapping:`À quoi correspond ${t} ?`,formula:`Quelle formule faut-il utiliser pour ${t} ?`,number:`Quelle valeur ou quel repère faut-il connaître pour ${t} ?`,rule:`Quelle règle faut-il appliquer concernant ${t} ?`,trend:`Comment évolue ${t} ?`,sequence:`Dans quel ordre se déroule ${t} ?`,list:`Quels éléments faut-il citer pour ${t} ?`,algorithm:`Quelle démarche faut-il appliquer pour ${t} ?`,trap:`Quel piège ou quelle nuance faut-il connaître concernant ${t} ?`,explanation:`Explique brièvement ${t}.`,example:`Quel exemple du cours illustre ${t} ?`,flashcard:`Que faut-il retenir sur ${t} ?`};
 return map[f.category]||`Que faut-il retenir sur ${t} ?`;
}
function shortAnswerForReverse(f){const a=String(f.answer||'').trim(),words=a.split(/\s+/).filter(Boolean).length;return a.length<=110&&words<=18&&!/[.;].*[.;]/.test(a)}
function naturalReverseFront(f){
 const a=String(f.answer||'').trim();if(!shortAnswerForReverse(f))return null;
 if(f.category==='definition')return `Quel terme ou concept désigne : « ${a} » ?`;
 if(f.category==='mapping')return `Quelle notion est associée à : « ${a} » ?`;
 if(f.category==='formula')return `Quelle relation du cours est donnée par : ${a} ?`;
 if(f.category==='number')return `À quel repère du cours associer : « ${a} » ?`;
 return null;
}
function sequenceMicroCards(f){
 if(f.category!=='sequence')return[];const raw=String(f.answer||'');let parts=raw.includes('→')?raw.split(/\s*→\s*/):raw.split(/\s*;\s*/);parts=parts.map(x=>x.trim()).filter(x=>x.length>=2&&x.length<=100);if(parts.length<3||parts.length>9)return[];
 const topic=cleanTopic(f.term),cards=[{id:`seq0:${f.id}`,front:`Quelle est la première étape de « ${topic} » ?`,back:parts[0],subjectId:f.subjectId,chapterId:f.chapterId,conceptId:f.conceptId,source:f.source,kind:'Séquence',importance:f.importance||1}];
 for(let i=0;i<parts.length-1;i++)cards.push({id:`seq:${f.id}:${i}`,front:`Dans « ${topic} », quelle étape vient après « ${parts[i]} » ?`,back:parts[i+1],subjectId:f.subjectId,chapterId:f.chapterId,conceptId:f.conceptId,source:f.source,kind:'Séquence',importance:f.importance||1});
 return cards;
}
function qrocFlashcards(sid,chid){
 const out=[];C.questions.filter(q=>q.format==='QROC'&&(sid==='all'||q.subjectId===sid)&&(chid==='all'||q.chapterId===chid)).forEach(q=>{const pts=q.expectedPoints||[];if(!pts.length)return;out.push({id:`qroc:${q.id}`,front:q.stem,back:pts.map((p,i)=>`${i+1}. ${p}`).join('\n'),subjectId:q.subjectId,chapterId:q.chapterId,conceptId:q.conceptId,source:q.source,kind:'QROC',importance:q.trainingPriority==='prioritaire'?1.35:1.15});pts.forEach((p,i)=>{const m=String(p).match(/^([^:]{3,65})\s*:\s*(.+)$/);if(!m)return;out.push({id:`qrocp:${q.id}:${i}`,front:`Dans la QROC « ${cleanTopic(q.stem)} », que faut-il mentionner à propos de « ${m[1].trim()} » ?`,back:m[2].trim(),subjectId:q.subjectId,chapterId:q.chapterId,conceptId:q.conceptId,source:q.source,kind:'QROC — point attendu',importance:q.trainingPriority==='prioritaire'?1.3:1.1})})});return out;
}
function cardKindForFact(f){const names={definition:'Définition',rule:'Règle',formula:'Formule',number:'Valeur',mapping:'Association',sequence:'Séquence',algorithm:'Méthode',trend:'Évolution',list:'Liste',explanation:'Compréhension',example:'Exemple',trap:'Piège / nuance',flashcard:'Notion-clé'};return names[f.category]||'Cours'}
function explicitFlashcardKind(c){
 const names={definition:'Définition',list:'Liste',mapping:'Association',mechanism:'Mécanisme',sequence:'Séquence',function:'Fonction',description:'Description',comparison:'Comparaison',number:'Valeur',exception:'Exception',fact:'Repère'};
 return names[c.category]||'Cours';
}
function cardPool(sid='all',chid='all'){
 let arr=(C.flashcards||[]).filter(c=>(sid==='all'||c.subjectId===sid)&&(chid==='all'||c.chapterId===chid)).map(c=>({
   id:c.id,front:c.question,back:c.answer,subjectId:c.subjectId,chapterId:c.chapterId,conceptId:c.conceptId||'',source:flashcardSource(c),kind:explicitFlashcardKind(c),importance:c.priority===2?1.3:1,category:c.category,cardLevel:c.cardLevel||'detail'
 }));
 // Fallback legacy uniquement si aucune banque explicite n'existe dans ce build.
 if(!(C.flashcards||[]).length){
   const reverseCats=new Set();
   C.facts.filter(f=>(sid==='all'||f.subjectId===sid)&&(chid==='all'||f.chapterId===chid)).forEach(f=>{arr.push({id:'f:'+f.id,front:naturalFactFront(f),back:f.answer,subjectId:f.subjectId,chapterId:f.chapterId,conceptId:f.conceptId,source:f.source,kind:cardKindForFact(f),importance:f.importance||1,category:f.category});if(reverseCats.has(f.category)){const rf=naturalReverseFront(f);if(rf)arr.push({id:'fr:'+f.id,front:rf,back:f.term,subjectId:f.subjectId,chapterId:f.chapterId,conceptId:f.conceptId,source:f.source,kind:'Rappel inversé',importance:f.importance||1,category:f.category})}arr.push(...sequenceMicroCards(f))});
   (C.entities||[]).filter(e=>(sid==='all'||e.subjectId===sid)&&(chid==='all'||e.chapterId===chid)).forEach(e=>(e.properties||[]).forEach((p,i)=>{const label=String(p.label||'propriété').trim(),val=String(p.value||'').trim();const l=label.toLowerCase();let front;if(l==='usage')front=`Quel est l’usage principal de ${e.name} ?`;else if(l.includes('principe'))front=`Quel est le principe de ${e.name} ?`;else if(l.includes('mesure'))front=`Que mesure ${e.name} ?`;else if(l.includes('localisation'))front=`Où se situe ${e.name} ?`;else if(l.includes('fonction')||l.includes('rôle'))front=`Quel est le rôle de ${e.name} ?`;else front=`Pour ${e.name}, que faut-il retenir concernant « ${label} » ?`;arr.push({id:`ep:${e.id}:${i}`,front,back:val,subjectId:e.subjectId,chapterId:e.chapterId,conceptId:`entity:${e.id}`,source:e.source,kind:'Comparaison',importance:p.importance||1})}));
   arr.push(...qrocFlashcards(sid,chid));
 }
 Object.entries(S.cards).forEach(([id,c])=>{if(c.custom&&(sid==='all'||c.subjectId===sid)&&(chid==='all'||c.chapterId===chid))arr.push({id,front:c.front,back:c.back,subjectId:c.subjectId,chapterId:c.chapterId,conceptId:c.conceptId||'',source:c.source,kind:'Erreur personnelle',importance:1.4})});
 const seenId=new Set(),seenContent=new Set(),seenFront=new Set();return arr.filter(x=>{const nf=normTxt(x.front),ck=nf+'|'+normTxt(x.back);if(seenId.has(x.id)||seenContent.has(ck)||seenFront.has(nf))return false;seenId.add(x.id);seenContent.add(ck);seenFront.add(nf);return true});
}
function cardPriority(c){const st=c.conceptId?S.concepts[c.subjectId+':'+c.conceptId]:null,m=mastery(st),wrong=clamp((st?.wrongStreak||0)/2,0,1),slow=clamp(((st?.timeRatioEMA||1)-1)/.55,0,1),due=S.cards[c.id]?.due&&S.cards[c.id].due<=now()?1:0,unseen=!(S.cards[c.id]?.reps>0)?1:0,kindBoost=/Erreur|Piège|Méthode|QROC|Règle/i.test(c.kind||'')?.12:0;return .38*(1-m)+.22*wrong+.16*slow+.10*due+.06*unseen+.05*clamp((c.importance||1)-1,0,.5)+kindBoost+.03*Math.random()}
function renderCards(){
 const total=cardPool('all','all').length,due=dueCount(),fresh=newCardCount();
 $('cardsContent').innerHTML=`<div class="grid"><div class="card c4"><div class="section-title"><h2 class="grow">Flashcards</h2><span class="badge accent">${total} cartes utiles</span></div><div class="flash-stats"><div><b>${due}</b><span>dues</span></div><div><b>${fresh}</b><span>nouvelles</span></div></div><label class="lbl">Matière</label><select id="cardSub" class="field"><option value="all">Toutes les matières</option>${subOpts()}</select><label class="lbl">Chapitre</label><select id="cardCh" class="field"><option value="all">Tous les chapitres</option></select><label class="lbl">Taille de la session</label><select id="cardCount" class="field"><option>20</option><option selected>50</option><option>100</option><option>200</option></select><div class="card-mode-grid"><button id="cardDue" class="btn primary">Cartes dues</button><button id="cardTarget" class="btn soft">Ciblées faiblesses</button><button id="cardNew" class="btn">Nouvelles cartes</button><button id="cardRandom" class="btn">Révision libre</button></div></div><div class="card c8" id="cardBox"><div class="section-title"><h2 class="grow">Récupération active</h2><span class="badge">Q ↔ R</span></div><div class="callout ok"><b>Flashcards validées cours par cours</b><div class="small">${(C.flashcards||[]).length} cartes validées explicitement depuis les FC PDF. Chaque question est rédigée pour le rappel actif ; la source et la page restent attachées à la carte sans apparaître dans sa formulation.</div></div><div class="small" style="margin-top:9px">Les cartes ciblées privilégient les notions mal maîtrisées, les erreurs répétées et les notions où tu dépasses souvent le temps attendu.</div></div></div>`;
 const sub=$('cardSub'),ch=$('cardCh'),upd=()=>{if(sub.value==='all'){ch.innerHTML='<option value="all">Tous les chapitres</option>';ch.disabled=true}else{ch.disabled=false;ch.innerHTML=chapterOpts(sub.value,true)}};sub.onchange=upd;upd();$('cardDue').onclick=()=>startCards('due');$('cardTarget').onclick=()=>startCards('target');$('cardNew').onclick=()=>startCards('new');$('cardRandom').onclick=()=>startCards('free');
}
function startCards(mode='target'){const sid=$('cardSub')?.value||'all',chid=$('cardCh')?.value||'all',n=Number($('cardCount')?.value||50);let pool=cardPool(sid,chid);if(mode==='due')pool=pool.filter(c=>S.cards[c.id]?.reps>0&&S.cards[c.id]?.due<=now()).sort((a,b)=>cardPriority(b)-cardPriority(a));else if(mode==='new')pool=pool.filter(c=>!(S.cards[c.id]?.reps>0)).sort((a,b)=>cardPriority(b)-cardPriority(a));else if(mode==='target')pool=pool.sort((a,b)=>cardPriority(b)-cardPriority(a));else pool=shuffle(pool);review={pool:pool.slice(0,n),i:0,side:'front',revealed:false};showCard()}
function startChapterCards(chid,n=50){const c=chs[chid];if(!c)return;nav('cards');setTimeout(()=>{let pool=cardPool(c.subjectId,chid).sort((a,b)=>cardPriority(b)-cardPriority(a));review={pool:pool.slice(0,n),i:0,side:'front',revealed:false};showCard()},0)}
function showCard(){const box=$('cardBox');if(!review||review.i>=review.pool.length){box.innerHTML='<div class="empty">Révision terminée.</div>';return}const c=review.pool[review.i];review.side='front';review.revealed=false;box.innerHTML=`<div class="row"><span class="badge">${esc(subs[c.subjectId]?.name||'')}</span><span class="badge">${esc(chs[c.chapterId]?.title||'')}</span><span class="badge soft">${esc(c.kind||'Cours')}</span><span id="sideBadge" class="badge accent">Question</span><span class="small right">${review.i+1}/${review.pool.length}</span></div><div class="flash-wrap" style="margin-top:9px"><div id="flash" class="flash" tabindex="0"><div><div class="front">${esc(c.front)}</div><div class="flash-hint">Touchez pour voir la réponse</div></div></div></div><div id="grades" class="review-actions hidden"><button class="btn bad" data-grade="again">À revoir</button><button class="btn warn" data-grade="hard">Difficile</button><button class="btn good" data-grade="good">Bien</button><button class="btn primary" data-grade="easy">Facile</button></div><div class="small" style="margin-top:7px">Tu peux revenir à la question avant de noter la carte.</div>`;$('flash').onclick=()=>flipCard(c);$('flash').onkeydown=e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();flipCard(c)}}}
function flipCard(c){if(review.side==='front'){review.side='back';review.revealed=true;$('sideBadge').textContent='Réponse';$('flash').innerHTML=`<div><div class="back">${esc(c.back)}</div><div class="source">${esc(sourceText(c.source))}</div><div class="flash-hint">Touchez pour relire la question</div></div>`;$('grades').classList.remove('hidden');document.querySelectorAll('[data-grade]').forEach(b=>b.onclick=()=>gradeCard(c,b.dataset.grade))}else{review.side='front';$('sideBadge').textContent='Question';$('flash').innerHTML=`<div><div class="front">${esc(c.front)}</div><div class="flash-hint">Touchez pour revoir la réponse</div></div>`}}
function gradeCard(c,g){let x=S.cards[c.id]||{interval:0,ease:2.3,reps:0},days;if(g==='again'){days=.2;x.interval=.2;x.ease=Math.max(1.5,x.ease-.2)}else if(g==='hard'){days=Math.max(1,x.interval?x.interval*1.35:1);x.interval=days;x.ease=Math.max(1.5,x.ease-.1)}else if(g==='good'){days=x.interval?Math.max(2,x.interval*x.ease):2;x.interval=days}else{days=x.interval?Math.max(4,x.interval*(x.ease+.45)):4;x.interval=days;x.ease+=.08}x.reps++;x.due=now()+days*DAY;S.cards[c.id]=Object.assign(x,S.cards[c.id]||{});save();review.i++;showCard()}

const catNames={
 definition:'Définitions et concepts',
 rule:'Règles et principes',
 formula:'Formules',
 number:'Valeurs numériques',
 mapping:'Associations à connaître',
 sequence:'Ordres et démarches',
 algorithm:'Méthodes / algorithmes',
 trend:'Évolutions / tendances',
 list:'Listes structurées',
 explanation:'Compréhension et mécanismes',
 example:'Exemples',
 trap:'Pièges et nuances',
 flashcard:'Notions-clés'
};
const catOrder=['definition','rule','list','mapping','sequence','algorithm','formula','number','trend','explanation','example','trap','flashcard'];

function useText(f){
 const x={
  definition:'Définition à restituer précisément.',
  rule:'Règle à savoir appliquer.',
  formula:'Connaître la formule, les unités et ses conditions d’utilisation.',
  number:'Valeur / ordre de grandeur à mémoriser.',
  mapping:'Association à reconnaître dans les deux sens.',
  sequence:'Ordre à restituer sans inversion.',
  algorithm:'Démarche de résolution à automatiser.',
  trend:'Sens d’évolution à reconnaître.',
  list:'Ensemble à restituer sans omission.',
  explanation:'Mécanisme à comprendre et expliquer.',
  example:'Exemple à rattacher à la notion.',
  trap:'Piège / nuance à vérifier avant de répondre.',
  flashcard:'Notion à automatiser.'
 };
 return x[f.category]||'À connaître et à mobiliser.';
}
function toneForFact(f){
 if(f.category==='trap')return'red';
 if(f.category==='number'||f.category==='formula')return'cyan';
 if(f.category==='example')return'blue';
 if((f.importance||1)>=1.2)return'green';
 if((f.importance||1)<.9)return'pink';
 return'neutral';
}
function toneLabel(t){
 return {green:'MAJEUR',pink:'SECONDAIRE',blue:'EXEMPLE',cyan:'VALEUR / FORMULE',red:'PIÈGE / NUANCE',neutral:'COURS'}[t]||'COURS';
}
function sheetFact(f){
 const tone=toneForFact(f);
 return `<div class="sheet-fact tone-${tone}">
   <div class="sheet-fact-head">
     <span class="tone-chip tone-${tone}">${toneLabel(tone)}</span>
     <div class="sheet-term">${esc(f.term)}</div>
   </div>
   <div class="sheet-answer">${esc(f.answer)}</div>
   <div class="sheet-foot"><span>${esc(useText(f))}</span><span class="source">${esc(sourceText(f.source))}</span></div>
 </div>`;
}
function sheetSection(title,items,tone='neutral',open=true){
 if(!items||!items.length)return'';
 return `<details class="sheet-section section-${tone}" ${open?'open':''}>
   <summary><span class="section-bar"></span><span class="section-name">${esc(title)}</span><span class="badge">${items.length}</span></summary>
   <div class="sheet-section-body">${items.join('')}</div>
 </details>`;
}
function factSection(title,fs,open=false){
 if(!fs.length)return'';
 const dominant=fs.some(f=>f.category==='trap')?'red':
                fs.some(f=>f.category==='number'||f.category==='formula')?'cyan':
                fs.some(f=>f.category==='example')?'blue':
                fs.some(f=>(f.importance||1)>=1.2)?'green':'neutral';
 return sheetSection(title,fs.map(sheetFact),dominant,open);
}
function entitySection(es,mode){
 if(!es.length)return'';
 const rows=es.map(e=>{
   const props=(e.properties||[]).filter(p=>mode!=='high'||(p.importance||1)>=1.1);
   return `<div class="compare-block">
     <div class="compare-title">${esc(e.name)}</div>
     <div class="compare-grid">${props.map(p=>`<div class="compare-label">${esc(p.label)}</div><div class="compare-value">${esc(p.value)}</div>`).join('')}</div>
     <div class="source">${esc(sourceText(e.source))}</div>
   </div>`;
 });
 return sheetSection('Tableaux comparatifs du cours',rows,'blue',mode==='all');
}

function closeCourseReader(){
 const chid=readerState?.chid,el=$('courseReaderOverlay');if(el)el.remove();readerState=null;
 const panel=document.querySelector('.course-pages-panel');if(chid&&panel&&$('sumCh')?.value===chid){panel.outerHTML=coursePageGallery(chid);bindCourseGallery(chid)}
}
function courseReadingState(chid){
 try{return JSON.parse(localStorage.getItem('adaptive-course-reading:'+chid)||'{}')||{}}catch(_){return{}}
}
function saveCourseReadingState(chid,patch){
 try{localStorage.setItem('adaptive-course-reading:'+chid,JSON.stringify({...courseReadingState(chid),...patch}))}catch(_){}
}
function coursePageLabel(chid,i){
 const start=C.courseMeta?.[chid]?.addendumStartPage;
 return start&&i+1>=start?`Addendum p. ${i+2-start}`:`p. ${i+1}`;
}
function coursePageGallery(chid){
 const pages=C.coursePages?.[chid]||[];
 if(!pages.length)return '<div class="empty">Les pages de cette FC ne sont pas encore installées dans cette version.</div>';
 const state=courseReadingState(chid),last=clamp(Number(state.page)||0,0,pages.length-1),saved=(state.saved||[]).filter(n=>Number.isInteger(n)&&n>=0&&n<pages.length);
 const tiles=pages.map((path,i)=>`<button class="course-page-tile" type="button" data-page-jump="${i}" aria-label="Lire ${coursePageLabel(chid,i)}"><img loading="lazy" src="${esc(readerPageUrl(path))}" alt="Aperçu ${coursePageLabel(chid,i)}"><span>${coursePageLabel(chid,i)}${saved.includes(i)?' ★':''}</span></button>`).join('');
 return `<section class="course-pages-panel"><div class="course-pages-head"><div><h3>Parcourir la FC</h3><p class="small">Aperçus des pages originales. Touchez une page pour lire tous ses détails.</p></div><span class="badge">${pages.length} pages</span></div><div class="course-quick-actions"><button class="btn primary" data-page-jump="${last}">Reprendre ${coursePageLabel(chid,last)}</button>${saved.length?`<label class="course-saved-label">Favoris <select id="courseSavedPage" class="field"><option value="">Choisir une page</option>${saved.map(i=>`<option value="${i}">${coursePageLabel(chid,i)}</option>`).join('')}</select></label>`:''}<label class="course-page-number">Aller à la page <input id="coursePageNumber" type="number" min="1" max="${pages.length}" placeholder="1–${pages.length}" class="field"></label></div><div class="course-page-grid">${tiles}</div></section>`;
}
function bindCourseGallery(chid){
 document.querySelectorAll('[data-page-jump]').forEach(b=>b.onclick=()=>openCourseReader(chid,Number(b.dataset.pageJump)));
 const pageInput=$('coursePageNumber');if(pageInput)pageInput.onchange=()=>{const n=Number(pageInput.value),length=C.coursePages?.[chid]?.length||0;if(Number.isInteger(n)&&n>=1&&n<=length)openCourseReader(chid,n-1)};
 const saved=$('courseSavedPage');if(saved)saved.onchange=()=>{if(saved.value!=='')openCourseReader(chid,Number(saved.value))};
}
function readerPageUrl(path){return new URL('./'+path,location.href).href}
async function ensureReaderPage(path){
 const url=readerPageUrl(path);
 try{
   const cached=await caches.match(url);
   if(cached)return url;
 }catch(_){}
 try{
   const resp=await fetch(url,{cache:'reload'});
   if(resp&&resp.ok){
     try{const c=await caches.open('adaptive-pages-v3-25-1-content');await c.put(url,resp.clone())}catch(_){}
     return url;
   }
 }catch(_){}
 return null;
}
async function renderReaderPage(){
 if(!readerState)return;
 const pages=C.coursePages?.[readerState.chid]||[];if(!pages.length)return;
 readerState.page=clamp(readerState.page,0,pages.length-1);
 saveCourseReadingState(readerState.chid,{page:readerState.page});
 const img=$('readerImage'),counter=$('readerCounter'),range=$('readerRange'),status=$('readerPageStatus');
 if(counter)counter.textContent=`${coursePageLabel(readerState.chid,readerState.page)} · ${readerState.page+1}/${pages.length}`;
 if(range)range.value=readerState.page+1;
 const mark=$('readerBookmark');if(mark){const saved=courseReadingState(readerState.chid).saved||[];mark.textContent=saved.includes(readerState.page)?'★ Enregistrée':'☆ Garder';mark.setAttribute('aria-pressed',saved.includes(readerState.page)?'true':'false')}
 if(status){status.className='reader-page-status';status.innerHTML='Chargement de la page…'}
 if(img){
   img.style.display='none';img.alt=coursePageLabel(readerState.chid,readerState.page);img.style.width=`${readerState.zoom}%`;
   const path=pages[readerState.page],url=await ensureReaderPage(path);
   if(!readerState)return;
   if(!url){
     if(status){status.className='reader-page-status error';status.innerHTML=`Cette page n’est pas encore disponible hors ligne.<br><button id="readerRetry" class="btn primary compact">Réessayer</button> <button id="readerSyncNow" class="btn compact">Synchroniser la fiche</button>`;setTimeout(()=>{const r=$('readerRetry'),s=$('readerSyncNow');if(r)r.onclick=renderReaderPage;if(s)s.onclick=()=>cacheCoursePages(readerState.chid,true)},0)}
     return;
   }
   img.onload=()=>{if(status)status.innerHTML='';img.style.display='block'};
   img.onerror=()=>{if(status){status.className='reader-page-status error';status.innerHTML=`Impossible d’afficher la page. <button id="readerRetry" class="btn compact">Réessayer</button>`;setTimeout(()=>{const r=$('readerRetry');if(r)r.onclick=renderReaderPage},0)}};
   img.src=url+(url.includes('?')?'&':'?')+'reader=353&p='+readerState.page;
 }
 // Preload adjacent pages without blocking the UI.
 [readerState.page-1,readerState.page+1].filter(i=>i>=0&&i<pages.length).forEach(i=>ensureReaderPage(pages[i]));
}
let mindMapOwnFullscreen=false;
function closeMindMap(){const el=$('mindMapOverlay');if(el)el.remove();try{screen.orientation?.unlock?.()}catch(_){}if(mindMapOwnFullscreen&&document.fullscreenElement){document.exitFullscreen?.().catch(()=>{})}mindMapOwnFullscreen=false}
async function mindMapLandscape(){try{screen.orientation?.unlock?.()}catch(_){}try{if(!document.fullscreenElement&&document.documentElement.requestFullscreen){await document.documentElement.requestFullscreen();mindMapOwnFullscreen=true}if(screen.orientation?.lock)await screen.orientation.lock('landscape');toast('Mode paysage activé.')}catch(_){toast('Active la rotation automatique du téléphone puis tourne-le en paysage.')}}
function openMindMap(chid){
 const m=C.mindMaps?.[chid];if(!m)return toast('Carte mentale non encore disponible pour ce cours.');
 closeMindMap();
 const maps=[{title:m.title,path:m.path},...(Array.isArray(m.subMaps)?m.subMaps:[])].filter(x=>x&&x.path),overlay=document.createElement('div');let active=0;
 overlay.id='mindMapOverlay';overlay.className='mindmap-overlay';
 overlay.innerHTML=`<div class="mindmap-top"><button id="mindMapClose" class="btn ghost compact">← Retour au cours</button><div class="grow"><b id="mindMapTitle">${esc(maps[0].title)}</b><div class="small">Carte mentale paysage · zoom et déplacement${maps.length>1?' · '+maps.length+' vues':''}</div></div><button id="mindMapLandscape" class="btn soft compact">↔ Paysage</button><span id="mindMapZoomLabel" class="badge">100%</span></div>${maps.length>1?`<div class="mindmap-pages">${maps.map((x,i)=>`<button class="btn ${i===0?'primary':'soft'} compact" data-mindmap-page="${i}">${i===0?'Vue globale':'Sous-carte '+i}</button>`).join('')}</div>`:''}<div class="mindmap-tools"><button id="mindMapMinus" class="btn">−</button><input id="mindMapZoom" type="range" min="25" max="240" value="100" step="10"><button id="mindMapPlus" class="btn">+</button><button id="mindMapFit" class="btn soft">Ajuster</button></div><div id="mindMapCanvas" class="mindmap-canvas"><img id="mindMapImage" src="./${maps[0].path}" alt="Carte mentale ${esc(maps[0].title)}"></div>`;
 document.body.appendChild(overlay);
 const img=$('mindMapImage'),range=$('mindMapZoom'),lab=$('mindMapZoomLabel'),canvas=$('mindMapCanvas'),title=$('mindMapTitle');
 const setZoom=v=>{v=clamp(Number(v)||100,25,240);range.value=v;lab.textContent=v+'%';img.style.width=(19.2*v)+'px';};
 const showMap=i=>{active=clamp(Number(i)||0,0,maps.length-1);const x=maps[active];title.textContent=x.title;img.src='./'+x.path;img.alt='Carte mentale '+x.title;document.querySelectorAll('[data-mindmap-page]').forEach(b=>{const on=Number(b.dataset.mindmapPage)===active;b.className='btn '+(on?'primary':'soft')+' compact';b.setAttribute('aria-pressed',on?'true':'false')});setZoom(Number(range.value)||100);canvas.scrollTo({left:0,top:0})};
 $('mindMapClose').onclick=closeMindMap;const land=$('mindMapLandscape');if(land)land.onclick=mindMapLandscape;$('mindMapMinus').onclick=()=>setZoom(Number(range.value)-10);$('mindMapPlus').onclick=()=>setZoom(Number(range.value)+10);range.oninput=e=>setZoom(e.target.value);$('mindMapFit').onclick=()=>{const v=Math.max(25,Math.min(100,Math.floor((canvas.clientWidth/1920)*100)));setZoom(v);canvas.scrollTo({left:0,top:0})};document.querySelectorAll('[data-mindmap-page]').forEach(b=>b.onclick=()=>showMap(Number(b.dataset.mindmapPage)));
 setZoom(100);
}
function openCourseReader(chid,page){
 const pages=C.coursePages?.[chid]||[];
 if(!pages.length){toast('Lecteur interne non disponible pour cette fiche. Utilise le téléchargement du PDF.');return}
 closeCourseReader();
 readerState={chid,page:clamp(Number.isInteger(page)?page:(Number(courseReadingState(chid).page)||0),0,pages.length-1),zoom:100};
 const title=chs[chid]?.title||'Fiche de cours';
 const overlay=document.createElement('div');overlay.id='courseReaderOverlay';overlay.className='course-reader-overlay';
 overlay.innerHTML=`<div class="reader-top"><button id="readerClose" class="btn ghost compact">← Retour au cours</button><div class="reader-title grow">${esc(title)}</div><span id="readerCounter" class="badge"></span></div><div class="reader-tools"><button id="readerPrev" class="btn">‹</button><input id="readerRange" type="range" min="1" max="${pages.length}" value="1"><button id="readerNext" class="btn">›</button><button id="readerBookmark" class="btn soft" aria-pressed="false">☆ Garder</button><button id="readerZoomOut" class="btn">−</button><span id="readerZoomLabel" class="badge">100%</span><button id="readerZoomIn" class="btn">+</button><button id="readerCache" class="btn soft">Synchroniser</button></div><div id="readerCanvas" class="reader-canvas"><div id="readerPageStatus" class="reader-page-status">Chargement de la page…</div><img id="readerImage" draggable="false"></div>`;
 document.body.appendChild(overlay);
 $('readerClose').onclick=closeCourseReader;
 $('readerPrev').onclick=()=>{readerState.page--;renderReaderPage()};
 $('readerNext').onclick=()=>{readerState.page++;renderReaderPage()};
 $('readerRange').oninput=e=>{readerState.page=Number(e.target.value)-1;renderReaderPage()};
 $('readerBookmark').onclick=()=>{const old=courseReadingState(chid).saved||[],set=new Set(old);set.has(readerState.page)?set.delete(readerState.page):set.add(readerState.page);saveCourseReadingState(chid,{saved:[...set].sort((a,b)=>a-b)});renderReaderPage()};
 $('readerZoomOut').onclick=()=>{readerState.zoom=clamp(readerState.zoom-25,75,250);$('readerZoomLabel').textContent=readerState.zoom+'%';renderReaderPage()};
 $('readerZoomIn').onclick=()=>{readerState.zoom=clamp(readerState.zoom+25,75,250);$('readerZoomLabel').textContent=readerState.zoom+'%';renderReaderPage()};
 $('readerCache').onclick=()=>cacheCoursePages(chid,true);
 let sx=0;$('readerCanvas').addEventListener('pointerdown',e=>{sx=e.clientX});$('readerCanvas').addEventListener('pointerup',e=>{const dx=e.clientX-sx;if(Math.abs(dx)>70){readerState.page+=dx<0?1:-1;renderReaderPage()}});
 renderReaderPage();
}
async function cacheCoursePages(chid,show=true){
 const pages=C.coursePages?.[chid]||[];if(!pages.length)return toast('Pages de cours non disponibles.');
 const btn=$('readerCache');if(btn&&show){btn.disabled=true;btn.textContent='0/'+pages.length}
 let done=0,failed=0;
 const queue=[...pages];
 async function worker(){
   while(queue.length){
     const path=queue.shift(),url=readerPageUrl(path);
     try{
       const cached=await caches.match(url);
       if(!cached){const resp=await fetch(url,{cache:'reload'});if(!resp.ok)throw new Error('HTTP');const c=await caches.open('adaptive-pages-v3-25-1-content');await c.put(url,resp.clone())}
     }catch(e){failed++}
     done++;if(btn&&show)btn.textContent=`${done}/${pages.length}`;
   }
 }
 await Promise.all(Array.from({length:Math.min(6,pages.length)},worker));
 if(btn&&show){btn.disabled=false;btn.textContent='Synchroniser'}
 if(show)toast(failed?`${pages.length-failed}/${pages.length} pages synchronisées. Laisse Termux ouvert et réessaie pour les autres.`:'Fiche complète disponible hors ligne.');
 renderReaderPage();
}
async function warmAllCoursePages(){
 // Keep startup light; full offline copies remain an explicit action in the reader.
 const all=Object.values(C.coursePages||{}).flatMap(pages=>pages.slice(0,1));if(!all.length)return;
 let cursor=0;const workers=Array.from({length:6},async()=>{while(cursor<all.length){const path=all[cursor++],url=readerPageUrl(path);try{if(!(await caches.match(url))){const r=await fetch(url,{cache:'reload'});if(r.ok){const c=await caches.open('adaptive-pages-v3-25-1-content');await c.put(url,r.clone())}}}catch(_){} }});
 await Promise.all(workers);
 try{localStorage.setItem('adaptive-study-course-cache-3243-content','ready')}catch(_){}
}
async function cacheCourseAsset(chid){const u=C.courseAssets?.[chid];if(!u)return toast('Fiche originale non disponible dans ce paquet.');try{const c=await caches.open('adaptive-course-assets-v3-25-0');await c.add('./'+u);toast('Fiche originale enregistrée hors ligne.')}catch(e){toast('Échec du cache. Laisse Termux ouvert et réessaie.') }}
function originalCourseBlock(chid){
 const meta=C.courseMeta?.[chid],pages=C.coursePages?.[chid]||[],st=chs[chid]?.auditStatus,nFacts=chapterFacts(chid).length,nCards=cardPool(chs[chid]?.subjectId||'all',chid).length;
 const audited=nCards>0?`<button class="btn soft" data-course-cards="${chid}">Flashcards du cours (${nCards})</button>`:'';
 const mind=C.mindMaps?.[chid]?`<button class="btn mindmap-btn" data-mindmap="${chid}">Carte mentale</button>`:'';
 if(!pages.length)return `<div class="course-original"><div class="row"><div class="grow"><b>PDF source fourni — non embarqué localement</b><div class="small">${nFacts} point(s) ont été recertifiés contre le document fourni. Le texte source complet n’est simplement pas inclus dans cette archive locale.</div></div></div><div class="source-actions">${mind}${audited}</div></div>`;
 const pc=pages.length||meta?.pages||'',pageLabel=pc?` · ${pc} pages`:'';
 return `<div class="course-original"><div class="row"><div class="grow"><b>PDF source${pageLabel}</b><div class="small">Source exhaustive. ${nFacts} point(s) de révision actifs après vérification PDF ; le PDF reste la référence complète.</div></div></div><div class="source-actions"><button class="btn primary" data-open-course="${chid}">Lire le PDF</button>${mind}${audited}<button class="btn" data-cache-pages="${chid}">Hors ligne</button></div></div>`;
}
function trainingAssetsBlock(chid){
 const a=C.trainingAssets?.[chid];if(!a)return'';
 const detail=(a.textActiveCount!=null)?`${a.count||0} QCM fournis · ${a.textActiveCount||0} textuels actifs · ${a.visualExcludedCount||0} documentaires désactivés dans ce build.`:`${a.count||0} QROC · ${a.priorityCount||0} prioritaires · ${a.complementaryCount||0} complémentaires.`;
 return `<div class="course-original training-assets"><div class="row"><div class="grow"><b>${esc(a.title)}</b><div class="small">${detail} Les questions et corrections actives sont intégrées directement dans l’application ; les PDF originaux sont dans l’archive documentaire.</div></div></div></div>`;
}
function sourceDetailsFor(chid){return (C.sourceDetails?.[chid]||[])}
function sourceDetailTagLabel(c){return ({formula:'formule/relation',number:'valeur',indicator:'indicateur/classement',molecule:'molécule/structure',method:'méthode',mechanism:'mécanisme',ultrastructure:'ultrastructure',definition:'définition',example:'exemple',detail:'détail'})[c]||c}
function sourceDetailsHtml(chid,mode='all'){
 const all=sourceDetailsFor(chid),arr=mode==='high'?all.filter(x=>(x.priority||1)>=1.5):all;
 if(!arr.length)return'';
 const by={};arr.forEach(x=>(by[x.page]??=[]).push(x));
 const pages=Object.keys(by).map(Number).sort((a,b)=>a-b);
 const title=mode==='high'?'Détails PDF prioritaires':'Registre détaillé du PDF';
 const note=mode==='high'?'Valeurs, molécules, mécanismes, ultrastructures, indicateurs ou relations littérales priorisés selon la matière. Le reste reste accessible dans la synthèse complète.':'Couverture page par page issue exclusivement du PDF. Ce registre complète les points structurés et empêche que les détails secondaires disparaissent.';
 return `<div class="sheet-section tone-cyan"><div class="sheet-section-title">${title} <span class="badge accent">${arr.length}/${all.length}</span></div><div class="callout"><b>Index détaillé du PDF</b><div class="small">${note} Le PDF affiché dans le lecteur reste l’autorité pour toute formule, valeur ou ligne dont la transcription paraît dégradée.</div></div>${pages.map(p=>`<details class="source-detail-page"><summary>Page ${p} <span class="badge">${by[p].length}</span></summary><div class="source-detail-list">${by[p].map(x=>`<div class="source-detail-row"><div>${esc(x.text)}</div><div class="row detail-tags">${(x.categories||[]).slice(0,3).map(c=>`<span class="badge">${esc(sourceDetailTagLabel(c))}</span>`).join('')}<span class="source right">PDF p.${p}</span></div></div>`).join('')}</div></details>`).join('')}</div>`;
}
function guideSection(chid,section,mode){
 const entries=(section.items||[]).filter(item=>mode==='all'||(item.priority||0)>=2);
 if(!entries.length)return'';
 const sourceButton=item=>Number.isInteger(item.page)?`<button class="guide-source" data-guide-page="${item.page-1}" title="Voir la FC originale page ${item.page}">FC p. ${item.page} ↗</button>`:'';
 const evidence=item=>item.evidence?`<div class="guide-evidence"><span class="badge">Piège observé</span> ${esc(item.evidence)}</div>`:'';
 const cell=item=>`<div class="guide-entry"><div class="guide-entry-title">${esc(item.label||'')}</div><div class="guide-entry-body">${esc(item.value||'')}</div>${evidence(item)}${sourceButton(item)}</div>`;
 let body='';
 if(section.type==='table')body=`<div class="guide-table"><div class="guide-table-head"><span>${esc(section.columns?.[0]||'Élément')}</span><span>${esc(section.columns?.[1]||'À retenir')}</span></div>${entries.map(item=>`<div class="guide-table-row"><strong>${esc(item.label||'')}</strong><div>${esc(item.value||'')}${evidence(item)} ${sourceButton(item)}</div></div>`).join('')}</div>`;
 else if(section.type==='steps')body=`<ol class="guide-steps">${entries.map(item=>`<li>${cell(item)}</li>`).join('')}</ol>`;
 else body=`<div class="guide-card-grid">${entries.map(cell).join('')}</div>`;
 return `<section class="guide-section guide-${esc(section.type||'list')}"><div class="guide-section-heading"><h3>${esc(section.title)}</h3><span class="badge">${entries.length}</span></div>${body}</section>`;
}
function chapterSummary(chid,mode='high'){
 const c=chs[chid],subject=subs[c.subjectId],pages=C.coursePages?.[chid]||[],guide=C.courseGuides?.[chid];
 const version=C.courseMeta?.[chid]?.sourceVersion==='ANTICIPEE_AUTORISEE'?' · FC anticipée autorisée':'';
 const heading=`<div class="course-visual-hero"><div class="row"><span class="badge accent">${esc(subject.name)}</span><span class="badge">${pages.length} pages${version}</span></div><h2>${esc(c.title)}</h2><p>${mode==='visual'?'Pages de la FC originale.':'Synthèse réorganisée à partir des pages du cours. Chaque élément renvoie à sa page originale.'}</p><div class="course-hero-actions"><button class="btn primary" data-course-quiz="${esc(chid)}">S’entraîner</button><button class="btn soft" data-course-cards="${esc(chid)}">Flashcards</button>${pages.length?`<button class="btn soft" data-open-course="${esc(chid)}">Lire la FC originale</button>`:''}${C.mindMaps?.[chid]?`<button class="btn" data-mindmap="${esc(chid)}">Carte mentale</button>`:''}</div></div>`;
 if(mode==='visual')return `<div class="study-sheet course-visual">${heading}${coursePageGallery(chid)}</div>`;
 if(!guide)return `<div class="study-sheet course-visual">${heading}<div class="callout warn"><b>Synthèse structurée en cours de vérification</b><div class="small">Les pages de la FC sont disponibles. Aucun tableau ou détail n’est affiché ici tant que sa transcription et sa source n’ont pas été contrôlées.</div></div>${coursePageGallery(chid)}</div>`;
 const count=(guide.sections||[]).flatMap(x=>x.items||[]).filter(x=>mode==='all'||(x.priority||0)>=2).length;
 return `<div class="study-sheet course-visual">${heading}<div class="guide-intro"><b>${mode==='high'?'À revoir en priorité':'Cours réorganisé · tous les détails vérifiés'}</b><span class="badge">${count} éléments</span><p>${mode==='high'?'Les détails non prioritaires restent dans « Complet ».':'La FC originale reste accessible pour le texte et les figures dans leur mise en page.'}</p></div>${(guide.sections||[]).map(section=>guideSection(chid,section,mode)).join('')}</div>`;
}
function renderCourse(){
 $('courseContent').innerHTML=`<div class="summary-toolbar"><div class="card flat"><div class="grid"><div class="c5"><label class="lbl">Matière</label><select id="sumSub" class="field">${subOpts()}</select></div><div class="c7"><label class="lbl">Cours</label><select id="sumCh" class="field"></select></div></div><div class="course-view-tabs" role="group" aria-label="Vue du cours"><button id="sumHigh" class="btn primary" aria-pressed="true">Essentiel</button><button id="sumFull" class="btn soft" aria-pressed="false">Complet</button><button id="sumVisual" class="btn soft" aria-pressed="false">PDF original</button></div></div></div><div id="summaryOut"></div>`;
 const subject=$('sumSub'),chapter=$('sumCh'),upd=()=>chapter.innerHTML=chapterOpts(subject.value,false);subject.onchange=()=>{upd();show('high')};upd();
 const buttons={high:$('sumHigh'),all:$('sumFull'),visual:$('sumVisual')};
 const show=mode=>{
  Object.entries(buttons).forEach(([key,button])=>{button.className='btn '+(key===mode?'primary':'soft');button.setAttribute('aria-pressed',key===mode?'true':'false')});
  const id=chapter.value;if(!id){$('summaryOut').innerHTML='<div class="empty">Aucune FC installée pour cette matière.</div>';return}
  $('summaryOut').innerHTML=chapterSummary(id,mode);bindCourseGallery(id);
  document.querySelectorAll('[data-guide-page]').forEach(b=>b.onclick=()=>openCourseReader(id,Number(b.dataset.guidePage)));
  document.querySelectorAll('[data-open-course]').forEach(b=>b.onclick=()=>openCourseReader(b.dataset.openCourse));
  document.querySelectorAll('[data-mindmap]').forEach(b=>b.onclick=()=>openMindMap(b.dataset.mindmap));
  document.querySelectorAll('[data-course-quiz]').forEach(b=>b.onclick=()=>openQuizFor(chs[b.dataset.courseQuiz].subjectId,b.dataset.courseQuiz));
  document.querySelectorAll('[data-course-cards]').forEach(b=>b.onclick=()=>startChapterCards(b.dataset.courseCards,50));
 };
 chapter.onchange=()=>show('high');Object.entries(buttons).forEach(([mode,button])=>button.onclick=()=>show(mode));show('high');
}
function openOriginalCourse(chid){
 const list=(window.ORIGINAL_CORPUS||[]).filter(q=>q.chapterId===chid);
 if(!list.length){toast('Aucune question originale appariée pour ce cours.');return}
 let pos=0,revealed=false;
 let overlay=document.getElementById('originalOverlay');
 if(!overlay){overlay=document.createElement('div');overlay.id='originalOverlay';overlay.style.cssText='position:fixed;inset:0;z-index:9999;background:#0b1016;overflow:auto;color:#f2f5fc;padding:10px';document.body.appendChild(overlay)}
 const render=()=>{
  const q=list[pos],imgs=arr=>arr.map(src=>`<img src="./${esc(src)}" alt="Page originale du document" style="width:100%;max-width:1050px;height:auto;display:block;margin:12px auto;border-radius:8px" loading="lazy">`).join('');
  overlay.innerHTML=`<div style="max-width:1080px;margin:auto"><div class="row" style="position:sticky;top:0;background:#0b1016;padding:8px 0;z-index:1"><button id="originalClose" class="btn soft">← Cours</button><span class="grow"></span><span class="badge accent">${pos+1}/${list.length}</span></div><h2>${esc(chs[chid]?.title||chid)}</h2><p class="small">${esc(q.subjectType)} n°${q.number} · ${esc(q.subjectName)} · sujet p. ${q.subjectPages.join(', ')}</p><div class="callout">Repérer la question n°${q.number} dans la page originale ci-dessous.</div>${imgs(q.questionImages)}<div class="row" style="position:sticky;bottom:0;background:#0b1016;padding:9px 0;gap:8px"><button id="originalPrev" class="btn" ${pos===0?'disabled':''}>Précédente</button><button id="originalReveal" class="btn primary grow">${revealed?'Masquer le corrigé':'Voir le corrigé'}</button><button id="originalNext" class="btn" ${pos===list.length-1?'disabled':''}>Suivante</button></div>${revealed?`<h3>Corrigé original · p. ${q.correctionPages.join(', ')}</h3>${imgs(q.correctionImages)}`:''}<p class="small">La notation automatique est désactivée : chaque réponse reste vérifiable sur le corrigé original.</p></div>`;
  overlay.querySelector('#originalClose').onclick=()=>overlay.remove();
  overlay.querySelector('#originalPrev').onclick=()=>{pos=Math.max(0,pos-1);revealed=false;render();overlay.scrollTop=0};
  overlay.querySelector('#originalNext').onclick=()=>{pos=Math.min(list.length-1,pos+1);revealed=false;render();overlay.scrollTop=0};
  overlay.querySelector('#originalReveal').onclick=()=>{revealed=!revealed;render();if(revealed)overlay.scrollTop=overlay.scrollHeight};
 };
 render();
}

function renderMore(){
 $('moreContent').innerHTML=`<div class="more-grid"><button class="btn ${currentMore==='errors'?'soft':''}" data-more="errors"><b>Erreurs</b><div class="small">carnet et remédiation</div></button><button class="btn ${currentMore==='timing'?'soft':''}" data-more="timing"><b>Temps</b><div class="small">gestion par matière</div></button><button class="btn ${currentMore==='subjects'?'soft':''}" data-more="subjects"><b>Matières</b><div class="small">couverture du corpus</div></button><button class="btn ${currentMore==='data'?'soft':''}" data-more="data"><b>Données</b><div class="small">sauvegarde et import</div></button></div><div id="moreBody" style="margin-top:10px"></div>`;document.querySelectorAll('[data-more]').forEach(b=>b.onclick=()=>{currentMore=b.dataset.more;renderMore()});if(currentMore==='errors')renderErrors();else if(currentMore==='timing')renderTiming();else if(currentMore==='subjects')renderSubjects();else renderData()
}
function renderErrors(){
 const es=Object.values(S.errors).sort((a,b)=>(Number(b.open)-Number(a.open))||((b.count||0)-(a.count||0))||String(b.last).localeCompare(String(a.last)));
 $('moreBody').innerHTML=`<div class="card"><div class="section-title"><h2 class="grow">Carnet d’erreurs</h2><span class="badge">${es.filter(e=>e.open).length} ouvertes</span></div><div class="error-filters"><select id="errSub" class="field"><option value="all">Toutes les matières</option>${subOpts()}</select><select id="errStatus" class="field"><option value="open">Ouvertes</option><option value="all">Toutes</option><option value="closed">Résolues</option></select><input id="errSearch" class="field" placeholder="Rechercher une notion"></div><div id="errList"></div></div>`;
 const rerender=()=>{const sid=$('errSub').value,status=$('errStatus').value,q=$('errSearch').value.toLowerCase();const arr=es.filter(e=>(sid==='all'||e.subjectId===sid)&&(status==='all'||(status==='open'?e.open:!e.open))&&(!q||(`${e.conceptId} ${e.question} ${e.correction}`).toLowerCase().includes(q)));$('errList').innerHTML=arr.length?arr.map(e=>`<div class="error-card"><div class="row"><span class="badge accent">${esc(subs[e.subjectId]?.name||'')}</span><span class="badge">${esc(chs[e.chapterId]?.title||'')}</span><span class="badge ${e.open?'bad':'ok'}">${e.open?'à revoir':'résolue'}</span><span class="badge">×${e.count}</span><span class="small right">${String(e.last||'').slice(0,10)}</span></div><div class="question">${esc(e.question)}</div><details open><summary class="small">Correction et point du cours</summary><div class="correction" style="margin-top:6px"><b>Correction</b><div>${esc(e.correction||'')}</div><div class="source">${esc(sourceText(e.source))}</div></div>${(e.courseSupport&&e.courseSupport.length?e.courseSupport:courseSupportFor({chapterId:e.chapterId,subjectId:e.subjectId,conceptId:e.conceptId,stem:e.question,explanation:e.correction,correct:[],options:[]},[])).slice(0,3).map(x=>`<div class="error-support"><b>${esc(x.term)}</b><div>${esc(x.answer)}</div><div class="source">${esc(sourceText(x.source))}</div></div>`).join('')}</details><div class="small" style="margin-top:7px">Confiance : ${e.confidence===3?'sûr':e.confidence===1?'hasard':'moyenne'} · temps ${e.time?fmtSec(e.time):'—'}${e.targetSec?` / repère ${fmtSec(e.targetSec)}`:''} · score ${Math.round(100*(e.score??0))}%</div><div class="error-actions"><button class="btn soft" data-retry="${e.id}">Revoir</button><button class="btn" data-card="${e.id}">Flashcard</button><button class="btn ${e.open?'good':'warn'}" data-toggle="${e.id}">${e.open?'Marquer résolue':'Rouvrir'}</button></div></div>`).join(''):'<div class="empty">Aucune erreur dans ce filtre.</div>';document.querySelectorAll('[data-toggle]').forEach(b=>b.onclick=()=>{S.errors[b.dataset.toggle].open=!S.errors[b.dataset.toggle].open;save();renderErrors()});document.querySelectorAll('[data-card]').forEach(b=>b.onclick=()=>{const e=S.errors[b.dataset.card];const supp=(e.courseSupport&&e.courseSupport.length?e.courseSupport:courseSupportFor({chapterId:e.chapterId,subjectId:e.subjectId,conceptId:e.conceptId,stem:e.question,explanation:e.correction,correct:[],options:[]},[]));const back=[e.correction,...supp.slice(0,3).map(x=>x.term+' — '+x.answer)].filter(Boolean).join('\n\n');S.cards['err:'+e.id]=Object.assign(S.cards['err:'+e.id]||{interval:0,ease:2,reps:0},{due:now(),custom:true,front:e.question,back,subjectId:e.subjectId,chapterId:e.chapterId,source:{kind:'Erreur personnelle'}});save();toast('Flashcard créée / remise à zéro.')});document.querySelectorAll('[data-retry]').forEach(b=>b.onclick=()=>{const e=S.errors[b.dataset.retry],pool=originalPool(e.subjectId,e.chapterId),q=pool.find(x=>x.conceptId===e.conceptId)||pool[0];nav('quiz');setTimeout(()=>{session={list:[q].filter(Boolean),i:0,score:0,max:0,conf:2,qStart:now(),answered:false};renderQuestion()},0)})};
 $('errSub').onchange=rerender;$('errStatus').onchange=rerender;$('errSearch').oninput=rerender;rerender()
}

function renderTiming(){
 const all=(S.sessions||[]).flatMap(se=>se.timing||[]);
 const rows=C.subjects.map(s=>{
   const xs=all.filter(x=>x.subjectId===s.id&&x.sec>0),target=examTargetSec(s.id);
   const avg=xs.length?xs.reduce((a,x)=>a+x.sec,0)/xs.length:0;
   const med=xs.length?median(xs.map(x=>x.sec)):0;
   const on=xs.length?xs.filter(x=>x.sec<=target).length:0;
   const ratio=avg&&target?avg/target:null;
   return{s,xs,target,avg,med,on,ratio};
 });
 $('moreBody').innerHTML=`<div class="card"><div class="section-title"><h2 class="grow">Gestion du temps</h2><span class="badge accent">non pénalisant</span></div><div class="callout"><b>Principe</b><div class="small">Le repère est calculé par matière : durée de l’épreuve ÷ nombre approximatif de questions. Il n’entre jamais dans le score brut. Il contribue légèrement à l’estimation de maîtrise lorsqu’un temps actif valide est disponible.</div></div><div class="timing-subject-list">${rows.map(r=>`<div class="timing-subject"><div class="row"><b class="grow">${esc(r.s.name)}</b><span class="badge">repère ${fmtSec(r.target)}/q.</span></div><div class="small">${esc(`${r.s.exam.durationMin} min / ≈${r.s.exam.approxItems} questions`)}</div>${r.xs.length?`<div class="timing-kpis compact"><div><b>${fmtSec(r.avg)}</b><span>moyenne</span></div><div><b>${fmtSec(r.med)}</b><span>médiane</span></div><div><b>${r.on}/${r.xs.length}</b><span>dans le repère</span></div><div><b>${Math.round(r.ratio*100)}%</b><span>du budget moyen</span></div></div>`:`<div class="small" style="margin-top:6px">Pas encore assez de données chronométrées.</div>`}</div>`).join('')}</div></div>`;
}
function renderSubjects(){const cards=C.subjects.map(s=>`<div class="card c6"><div class="row"><h2 class="grow">${esc(s.name)}</h2><span class="badge">coef ${s.coefficient}</span></div><div class="small">${esc(s.exam.mode)} · ${s.exam.durationMin} min</div>${C.chapters.filter(c=>c.subjectId===s.id).map(c=>{const n=(window.ORIGINAL_CORPUS||[]).filter(q=>q.chapterId===c.id).length;return `<div class="chapter-row"><div class="row"><b class="grow">${esc(c.title)}</b><span class="badge">${n} questions originales</span></div></div>`}).join('')}</div>`).join('');$('moreBody').innerHTML=`<div class="grid">${cards}</div>`}
function renderData(){
 const arc=C.documentArchive,a=C.auditPolicy||{};
 $('moreBody').innerHTML=`<div class="grid"><div class="card c6"><h2>Sauvegarde</h2><div class="small">La progression est locale à cet appareil.</div><div class="row" style="margin-top:9px"><button id="export" class="btn primary">Exporter</button><label class="btn">Importer<input id="import" type="file" class="hidden" accept=".json"></label><button id="reset" class="btn bad">Réinitialiser</button></div></div><div class="card c6"><h2>État du corpus</h2><div class="callout"><b>${(window.ORIGINAL_CORPUS||[]).length} questions et QROC originales consultables</b><div class="small">Sujets et corrigés reproduits en images depuis les PDF fournis. Aucun ancien QCM ou flashcard généré n’est actif. Notation automatique suspendue.</div></div></div>${arc?`<div class="card c12"><div class="row"><div class="grow"><h2>Archive documentaire</h2><div class="small">${arc.pdfCount} PDF regroupés dans un ZIP (${Math.round((arc.sizeBytes||0)/1024/1024)} Mo).</div></div><a class="btn soft" href="./${arc.path}" download>Archive PDF</a></div></div>`:''}</div>`;
 $('export').onclick=()=>{const blob=new Blob([JSON.stringify(S,null,2)],{type:'application/json'}),a=document.createElement('a');a.href=URL.createObjectURL(blob);a.download='adaptive_study_v3_25_1_progression.json';a.click();setTimeout(()=>URL.revokeObjectURL(a.href),500)};
 $('import').onchange=async e=>{try{S=Object.assign(base(),JSON.parse(await e.target.files[0].text()));save();toast('Progression importée.')}catch(_){toast('Fichier invalide.')}};
 $('reset').onclick=()=>{if(confirm('Réinitialiser toute la progression ?')){S=base();save();toast('Progression réinitialisée.')}};
}

renderHome();window.__ADAPTIVE_BOOT_OK=true;try{localStorage.removeItem('adaptive-study-booting')}catch(_){};setTimeout(()=>warmAllCoursePages(),1500);
})();