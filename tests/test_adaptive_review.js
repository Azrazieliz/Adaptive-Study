const fs=require('fs'),vm=require('vm'),assert=require('assert');
const path=require('path');const file=path.join(__dirname,'..','app','adaptive_review.js');
const data=new Map(),schedules=[];
let clock=Date.UTC(2026,9,28,10,0,0);
const realDate=Date;
class TestDate extends Date{constructor(...args){super(...(args.length?args:[clock]))}static now(){return clock}}
const sandbox={console,Date:TestDate,localStorage:{getItem:k=>data.get(k)||null,setItem:(k,v)=>data.set(k,v)},
 window:{NativeStudy:{setReviewSchedule:s=>schedules.push(JSON.parse(s)),requestNotifications:()=>{}}}};
vm.createContext(sandbox);vm.runInContext(fs.readFileSync(file,'utf8'),sandbox);
const a=sandbox.window.AdaptiveReview;
const list=[{id:'A',title:'A',subjectId:'phys',available:true,coefficient:5},{id:'B',title:'B',subjectId:'shs',available:true,coefficient:3}];
a.scheduleNative(list);assert.strictEqual(schedules.at(-1).masteryThreshold,75,'Native reminder threshold must match user setting');assert.strictEqual(schedules.at(-1).entries.length,2,'All chapters including unseen must be scheduled');
const id=a.startSet('A','questions',12);
for(let i=0;i<11;i++){const v=a.record('A','q'+i,.8,60,60,'questions',id,12);assert.strictEqual(v.completed,false)}
assert.strictEqual(a.snapshot('A').completedSets,0,'Full set must require all planned items');
let z=a.record('A','q11',.8,60,60,'questions',id,12);
assert(z.completed);assert.strictEqual(z.completedSets,1);assert(z.mastery>60&&z.mastery<75);
assert.strictEqual(z.daysSinceFull,0);assert.strictEqual(z.reviewNeeded,false);
clock+=2*86400000;
assert(a.snapshot('A').reviewNeeded,'Low mastery must become due early');
const slowScore=a.record('B','shsq',1,600,300,'questions','shs1',1);
assert(slowScore.completed&&slowScore.mastery<100,'Slow answer must lower mastery');
clock+=8*86400000;
assert(a.chapterTargets(list).find(x=>x.id==='A').reviewNeeded,'7-day overdue detection');
assert(schedules.length>2,'Native schedule must refresh as answers arrive');
a.setThreshold(85);a.scheduleNative(list);assert.strictEqual(schedules.at(-1).masteryThreshold,85,'Changed user threshold must be sent to Android');
const shortId=a.startSet('SHORT','questions',3);
for(let i=0;i<2;i++)assert.strictEqual(a.record('SHORT','s'+i,1,45,60,'questions',shortId,3).completed,false);
const shortResult=a.record('SHORT','s2',1,45,60,'questions',shortId,3);
assert.strictEqual(shortResult.completed,true,'A full three-item chapter session must be completable');
assert.strictEqual(a.snapshot('SHORT').completedSets,1);
assert(shortResult.mastery<70,'Three correct answers cannot imply complete mastery');
console.log('ADAPTIVE_TEST_PASS',JSON.stringify({completedSets:a.snapshot('A').completedSets,mastery:a.snapshot('A').mastery,due:a.snapshot('A').nextDue,bridgeUpdates:schedules.length,shsMastery:a.snapshot('B').mastery}));
