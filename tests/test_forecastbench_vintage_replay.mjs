/**
 * Pure adversarial replay tests, no human forecasts. The same cases execute
 * directly against the exact frozen core in V8 and via native Node.
 */
export function runReplayTests(api){
 const {selectVintage,planVintagePair,inspectPublicCohort,replayOriginalPair}=api;
 let passed=0;
 function ok(label,fn){fn();passed++;}
 const eq=(a,b)=>{if(a!==b)throw Error('EXPECTED '+JSON.stringify(b)+' GOT '+JSON.stringify(a));};
 const throws=(fn,needle)=>{let m='';try{fn()}catch(e){m=e.message;}if(!m.includes(needle))throw Error('EXPECTED_THROW '+needle+' GOT '+m);};
 const q=(cohort,id='a',source='metaculus',p='0.8')=>({source,id,freeze_datetime_value:p,
   freeze_datetime:cohort==='2026-10-11'?'2026-10-05T00:00:00Z':'2026-09-01T00:00:00Z'});
 const rr=(cohort,id='a',y=1,source='metaculus')=>({source,id,resolved:true,resolved_to:y,
   resolution_date:cohort==='2026-10-11'?'2026-10-23':'2026-10-07'});
 const dat=(cohort,items=[q(cohort)],out=[rr(cohort)])=>({
   questions:{forecast_due_date:cohort,question_set:cohort+'-llm.json',questions:items},
   resolutions:{forecast_due_date:cohort,question_set:cohort+'-llm.json',resolutions:out}
 });
 const old='2026-10-08T00:00:00Z',mid='2026-10-24T00:00:00Z',late='2026-10-29T16:00:00Z';
 ok('reject before first original Git vintage',()=>throws(()=>selectVintage('2026-10-01T23:59:59Z'),'NO_VERIFIED_PUBLIC_VINTAGE'));
 ok('Oct8 selects published Oct7 version',()=>eq(selectVintage(old).commit,'4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110'));
 ok('Oct20 still selects Oct7 not future Oct23',()=>eq(selectVintage('2026-10-20T00:00:00Z').commit,'4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110'));
 ok('Oct24 selects Oct23 original version',()=>eq(selectVintage(mid).commit,'f3d8a4f83754f6c26990c67c69185f91f214c30c'));
 ok('one second before Oct29 commit still selects Oct23',()=>eq(selectVintage('2026-10-29T07:30:16Z').commit,'f3d8a4f83754f6c26990c67c69185f91f214c30c'));
 ok('Oct29 exact commit accepted',()=>eq(selectVintage('2026-10-29T07:30:17Z').commit,'027ba0b3017a60e0e64602d724284ac6b2d91134'));
 ok('invalid UTC offsets and impossible day rejected',()=>{
  for(const s of ['2026-10-29','2026-10-29T16:00:00+01:00','2026-10-40T16:00:00Z'])throws(()=>selectVintage(s),s.includes('40')?'INVALID_INSTANT':'NONCANONICAL_INSTANT');
 });
 ok('reject reversed or equal time',()=>{throws(()=>planVintagePair(late,mid),'INVALID_REPLAY_ORDER');throws(()=>planVintagePair(mid,mid),'INVALID_REPLAY_ORDER');});
 ok('reject two instants with same source vintage',()=>throws(()=>planVintagePair(old,'2026-10-18T00:00:00Z'),'NO_DISTINCT_VERIFIED_SOURCE_VERSION'));
 ok('Oct8 only Sept27 question set available',()=>{const v=selectVintage(old);eq(Object.keys(v.cohorts).length,1);eq(Object.hasOwn(v.cohorts,'2026-10-11'),false);});
 ok('Oct24 has two question cohorts',()=>eq(Object.keys(selectVintage(mid).cohorts).length,2));
 ok('simple original-source cohort acceptance',()=>{const x=inspectPublicCohort(dat('2026-09-27').questions,dat('2026-09-27').resolutions,{cohort:'2026-09-27',as_of_instant:old});eq(x.report.accepted,1);eq(x.accepted.size,1);});
 ok('source dated numeric quantity despite p in range vetoed',()=>{const c='2026-09-27',d=dat(c,[q(c,'a','fred','0.4')],[rr(c,'a',1,'fred')]);eq(inspectPublicCohort(d.questions,d.resolutions,{cohort:c,as_of_instant:old}).report.accepted,0);});
 ok('ambiguous multiple resolution remains unresolved',()=>{const c='2026-09-27',d=dat(c,[q(c)],[rr(c),rr(c,'a',0)]);const x=inspectPublicCohort(d.questions,d.resolutions,{cohort:c,as_of_instant:old});eq(x.report.accepted,0);eq(x.report.unresolved,1);});
 ok('not yet published event date conservatively excluded',()=>{const c='2026-09-27',x=rr(c);x.resolution_date='2026-10-08';const d=dat(c,[q(c)],[x]);eq(inspectPublicCohort(d.questions,d.resolutions,{cohort:c,as_of_instant:old}).report.not_known_by_cutoff,1);});
 ok('duplicate source plus ID fails rather than selecting survivor',()=>{const c='2026-09-27',d=dat(c,[q(c),q(c)],[rr(c)]);throws(()=>inspectPublicCohort(d.questions,d.resolutions,{cohort:c,as_of_instant:old}),'DUPLICATE_QUESTION_KEY');});
 ok('cohort mismatch rejected',()=>{const d=dat('2026-09-27');throws(()=>inspectPublicCohort(d.questions,d.resolutions,{cohort:'2026-10-11',as_of_instant:old}),'COHORT_MISMATCH');});
 ok('two-vintage early-to-late measured as one common cohort + new cohort',()=>{
  const a=dat('2026-09-27'),z=dat('2026-09-27');
  const result=replayOriginalPair({from:{'2026-09-27':a},to:{'2026-09-27':z,'2026-10-11':dat('2026-10-11')},from_instant:old,to_instant:late});
  eq(result.cohorts.length,1);eq(result.newly_available_cohorts[0],'2026-10-11');eq(result.cohorts[0].retained_known,1);
 });
 ok('cohort outcome flip detected without exposing individual ID',()=>{
  const c='2026-09-27',a=dat(c,[q(c)],[rr(c,'a',0)]),z=dat(c,[q(c)],[rr(c,'a',1)]);
  const x=replayOriginalPair({from:{[c]:a},to:{[c]:z},from_instant:old,to_instant:late});
  eq(x.cohorts[0].outcome_flips_among_retained,1);eq(JSON.stringify(x).includes('"id"'),false);eq(JSON.stringify(x).includes('"a"'),false);
 });
 ok('dropped past outcome is an explicit negative',()=>{
  const c='2026-09-27',a=dat(c),z=dat(c,[q(c)],[]);
  const x=replayOriginalPair({from:{[c]:a},to:{[c]:z},from_instant:old,to_instant:late});
  eq(x.cohorts[0].previously_known_no_longer_valid,1);eq(x.cohorts[0].newly_known,0);
 });
 ok('newly known event distinguished from carried prior event',()=>{
  const c='2026-09-27',a=dat(c,[q(c,'a'),q(c,'b')],[rr(c,'a')]),z=dat(c,[q(c,'a'),q(c,'b')],[rr(c,'a'),rr(c,'b')]);
  const x=replayOriginalPair({from:{[c]:a},to:{[c]:z},from_instant:old,to_instant:late});
  eq(x.cohorts[0].retained_known,1);eq(x.cohorts[0].newly_known,1);
 });
 ok('missing source in either side does not become zero',()=>{
  throws(()=>replayOriginalPair({from:{},to:{'2026-09-27':dat('2026-09-27')},from_instant:old,to_instant:late}),'MISSING_COHORT_FOR_REPLAY');
 });
 ok('both Oct24 and Oct29 common source cohorts replay',()=>{
  const a={'2026-09-27':dat('2026-09-27'),'2026-10-11':dat('2026-10-11')};
  const x=replayOriginalPair({from:a,to:a,from_instant:mid,to_instant:late});
  eq(x.cohorts.length,2);eq(x.newly_available_cohorts.length,0);
 });
 ok('no causal or release-ready claims',()=>{
  const a={'2026-09-27':dat('2026-09-27')};
  const x=replayOriginalPair({from:a,to:a,from_instant:old,to_instant:late});
  eq(x.personal_rows_processed,0);eq(x.release_ready,false);eq(x.per_record_first_public_at_verified,false);
 });
 return passed;
}
