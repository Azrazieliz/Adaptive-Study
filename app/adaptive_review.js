/* Adaptive Study — source-first adaptive review v1.
   All measurements come from real attempts, never content counts. */
(function(global){
'use strict';
const KEY='adaptive-study-mastery-v1', DAY=86400000, MIN_SET=10, PASS=75;
let state;
let currentCatalogue=[];
function load(){try{const x=JSON.parse(localStorage.getItem(KEY)||'null');if(x&&x.version===1&&x.chapters)return x}catch(_){}
 return {version:1,created:Date.now(),chapters:{},preferences:{notificationEnabled:true,masteryThreshold:PASS}};}
state=load();
const now=()=>Date.now(),clamp=(n,lo,hi)=>Math.min(hi,Math.max(lo,n));
const safe=s=>String(s??'').replace(/[&<>"']/g,x=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[x]));
function save(){try{localStorage.setItem(KEY,JSON.stringify(state))}catch(e){console.error('Mastery state save',e)}}
function row(id){if(!state.chapters[id])state.chapters[id]={attempts:[],fullSets:[],activeSets:{}};return state.chapters[id]}
function scoreAttempt(a){const accuracy=clamp(Number(a.correctness)||0,0,1);
 const target=Number(a.targetSec)||0,sec=Number(a.seconds)||0;
 const timeFactor=target&&sec>0?clamp(target/sec,.65,1):1;
 return accuracy*(.85+.15*timeFactor);
}
function snapshot(id){
 const r=row(id),history=r.attempts||[],use=history.slice(-60);
 const n=use.length;
 // Rolling recent attempts are favored, without pretending one answer = full mastery.
 const weighted=use.reduce((a,x,i)=>{const w=.4+.6*(i+1)/n;return {sum:a.sum+w*scoreAttempt(x),weight:a.weight+w}}, {sum:0,weight:0});
 const mean=weighted.weight?weighted.sum/weighted.weight:0;
 const mastery=n?Math.round(100*mean*clamp(.35+(.65*n/16),.35,1)):null;
 const full=(r.fullSets||[]),lastFull=full.length?full[full.length-1].at:0;
 const interval=mastery===null?7:mastery<40?1:mastery<60?2:mastery<75?3:mastery<90?5:7;
 const reviewInterval=Math.min(7,interval)*DAY;
 const lowMasteryDue=lastFull&&mastery!==null&&mastery<state.preferences.masteryThreshold?lastFull+DAY:Infinity;
 const due=lastFull?Math.min(lastFull+reviewInterval,lowMasteryDue):(n&&mastery!==null&&mastery<state.preferences.masteryThreshold?history[history.length-1].at+DAY:state.created+7*DAY);
 const days=lastFull?Math.floor((now()-lastFull)/DAY):null;
 const threshold=state.preferences.masteryThreshold;
 return {id,mastery,attempts:r.attempts.length,completedSets:full.length,lastFull,nextDue:due,intervalDays:interval,
    daysSinceFull:days,reviewNeeded:!lastFull||now()>=due||(mastery!==null&&mastery<threshold&&now()-lastFull>=DAY),
    reason:!lastFull?'Jamais de session complète':now()>=due?'Rappel de révision':mastery!==null&&mastery<threshold?'Maîtrise sous le seuil':'À jour'};
}
function chapterTargets(catalogue){
 return (catalogue||[]).filter(c=>c&&c.id&&c.available!==false).map(c=>{
 const m=snapshot(c.id),coef=Number(c.coefficient)||6,lateDays=Math.max(0,(now()-m.nextDue)/DAY);
 return {...m,title:c.title||c.id,subjectId:c.subjectId,
 priority:(m.mastery==null?80:100-m.mastery)+Math.min(40,lateDays*5)+(m.completedSets===0?8:0)+coef*.65}
 }).sort((a,b)=>b.priority-a.priority);
}
function scheduleNative(catalogue){
 currentCatalogue=catalogue;
 const entries=chapterTargets(catalogue).sort((a,b)=>a.nextDue-b.nextDue).slice(0,100);
 const payload={version:1,enabled:state.preferences.notificationEnabled,entries:entries.map(x=>({id:x.id,title:x.title,due:x.nextDue,mastery:x.mastery,subjectId:x.subjectId}))};
 try{global.NativeStudy?.setReviewSchedule?.(JSON.stringify(payload))}catch(e){console.warn('Native reminder',e)}
 return payload;
}
function completedSet(chapterId,kind,records){
 const r=row(chapterId);const at=now(),n=records.length;
 const correctness=n?records.reduce((s,x)=>s+x.correctness,0)/n:0;
 r.fullSets.push({at,kind,count:n,accuracy:correctness});
 if(r.fullSets.length>200)r.fullSets=r.fullSets.slice(-200);
 save();return snapshot(chapterId);
}
function record(chapterId,questionId,correctness,seconds,targetSec,kind='questions',setId='default',planned=20){
 if(!chapterId||!questionId)throw Error('Must identify chapter and studied item');
 const r=row(chapterId),session=r.activeSets[setId]||(r.activeSets[setId]={kind,planned,items:{},at:now()});
 const a={id:String(questionId),correctness:clamp(Number(correctness)||0,0,1),seconds:clamp(Number(seconds)||0,0,36000),targetSec:clamp(Number(targetSec)||0,0,36000),kind,at:now()};
 const old=session.items[a.id];session.items[a.id]=a;
 if(!old){r.attempts.push(a);if(r.attempts.length>300)r.attempts=r.attempts.slice(-300)}
 else {const idx=r.attempts.findLastIndex(x=>x.id===a.id&&x.at===old.at);if(idx>=0)r.attempts[idx]=a}
 const answered=Object.keys(session.items).length,minimum=Math.max(1,Number(session.planned)||MIN_SET);
 let completed=false;
 if(answered>=minimum){completedSet(chapterId,kind,Object.values(session.items));delete r.activeSets[setId];completed=true}
 // Prune ancient incomplete sessions; visiting a course is not studying.
 for(const [k,x] of Object.entries(r.activeSets))if(now()-x.at>3*DAY)delete r.activeSets[k];
 save();if(currentCatalogue.length)scheduleNative(currentCatalogue);return {completed,answered,required:minimum,...snapshot(chapterId)};
}
function startSet(chapterId,kind='questions',planned=20){
 if(!Number.isInteger(Number(planned))||Number(planned)<1)throw Error('Set length must be positive');
 const r=row(chapterId),id=String(now())+'-'+String(Math.floor(Math.random()*100000));
 r.activeSets[id]={kind,planned,at:now(),items:{}};save();return id;
}
function renderDashboard(catalogue){
 currentCatalogue=catalogue;
 const a=chapterTargets(catalogue),focus=a.slice(0,5),due=a.filter(x=>x.reviewNeeded);
 const fmt=x=>x.mastery==null?'Non évaluée':x.mastery+' %';
 const html='<section class="card adaptive-dashboard"><div class="section-title"><h2 class="grow">Révisions adaptatives</h2><span class="badge accent">'+due.length+' cours prioritaires</span></div>'+
 '<p class="small">Seules les sessions complètes de questions ou de flashcards comptent comme travail du chapitre. Les réponses correctes et leur temps actif ajustent la maîtrise en direct. Seuil actuel : '+state.preferences.masteryThreshold+' % ; rappel au plus tard après 7 jours.</p>'+
 '<div class="adaptive-priorities">'+focus.map(x=>'<button class="adaptive-priority" data-ar-course="'+safe(x.id)+'"><b>'+safe(x.title)+'</b><span>'+fmt(x)+' · '+safe(x.reason)+(x.completedSets?' · '+x.completedSets+' session(s)':'')+'</span></button>').join('')+'</div>'+
 '<div class="adaptive-threshold"><label for="arThreshold">Seuil de maîtrise</label><input type="range" id="arThreshold" min="60" max="95" step="5" value="'+state.preferences.masteryThreshold+'"><b id="arThresholdValue">'+state.preferences.masteryThreshold+' %</b></div><div class="clean-actions"><button id="arNotify" class="btn soft">Activer les notifications Android</button><button id="arReview" class="btn primary">Questions du cours prioritaire</button></div></section>';
 const host=document.querySelector('#homeContent');if(!host)return;
 host.insertAdjacentHTML('afterbegin',html);
 host.querySelectorAll('[data-ar-course]').forEach(b=>b.onclick=()=>global.__AR_NAV_COURSE?.(b.dataset.arCourse));
 host.querySelector('#arReview').onclick=()=>{if(focus[0])global.__AR_NAV_QUIZ?.(focus[0].id)};
 host.querySelector('#arNotify').onclick=()=>{global.NativeStudy?.requestNotifications?.();scheduleNative(catalogue)};
 if(!global.NativeStudy)host.querySelector('#arNotify').style.display='none';
 host.querySelector('#arThreshold').oninput=e=>{host.querySelector('#arThresholdValue').textContent=e.target.value+' %'};
 host.querySelector('#arThreshold').onchange=e=>{state.preferences.masteryThreshold=clamp(Number(e.target.value),60,95);save();scheduleNative(catalogue);host.querySelector('.adaptive-dashboard')?.remove();renderDashboard(catalogue)};
 scheduleNative(catalogue);
}
function chapterNote(id){
 const m=snapshot(id),name=m.mastery===null?'Non évaluée':m.mastery+' %',d=m.daysSinceFull==null?'Jamais terminé de session':'Dernière session complète il y a '+m.daysSinceFull+' j';
 return '<div class="adaptive-course-note"><b>Maîtrise : '+name+'</b><span>'+d+' · '+safe(m.reason)+'</span></div>';
}
global.AdaptiveReview={snapshot,chapterTargets,record,startSet,chapterNote,renderDashboard,scheduleNative,
 getState:()=>JSON.parse(JSON.stringify(state)),setThreshold:v=>{state.preferences.masteryThreshold=clamp(Math.round(Number(v)||PASS),40,95);save()},
 resetForTests:()=>{state={version:1,created:now(),chapters:{},preferences:{notificationEnabled:true,masteryThreshold:PASS}};save()}};
})(window);
