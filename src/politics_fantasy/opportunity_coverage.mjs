/** PFL aggregate opportunity coverage audit. No named-person scoring. */
export function auditOpportunity(records,coverage){
 if(!Array.isArray(records)||!Array.isArray(coverage))throw Error("ARRAYS_REQUIRED");
 const weekRE=/^\d{4}-W(?:0[1-9]|[1-4]\d|5[0-3])$/;
 const count=new Map(),complete=new Map(),ids=new Set();
 for(const c of coverage){
  if(!c||typeof c!=="object"||Object.keys(c).some(k=>!["week","verified_complete","evidence_id"].includes(k))||!weekRE.test(c.week)||typeof c.verified_complete!=="boolean")throw Error("INVALID_COVERAGE");
  if(complete.has(c.week))throw Error("DUPLICATE_WEEK");
  if(c.verified_complete&&(typeof c.evidence_id!=="string"||!c.evidence_id.trim()))throw Error("MISSING_EVIDENCE");
  complete.set(c.week,c);count.set(c.week,0);
 }
 for(const r of records){
  if(!r||typeof r!=="object"||Object.keys(r).some(k=>!["division_id","week"].includes(k))||!Number.isSafeInteger(r.division_id)||r.division_id<=0||!weekRE.test(r.week))throw Error("INVALID_EVENT");
  if(ids.has(r.division_id))throw Error("DUPLICATE_EVENT");
  if(!count.has(r.week))throw Error("UNKNOWN_WEEK");
  ids.add(r.division_id);count.set(r.week,count.get(r.week)+1);
 }
 const weeks=[...complete.keys()].sort().map(week=>{
  const n=count.get(week),c=complete.get(week);
  return Object.freeze({week,observed_events:n,status:c.verified_complete?(n===0?"VERIFIED_ZERO_EVENTS":"EVENTS_VERIFIED"):"COVERAGE_UNKNOWN",evidence_id:c.verified_complete?c.evidence_id:null});
 });
 return Object.freeze({schema:"pfl.opportunity.coverage.v1",total_observed_events:ids.size,weeks:Object.freeze(weeks),unknown_weeks:weeks.filter(w=>w.status==="COVERAGE_UNKNOWN").length,verified_zero_weeks:weeks.filter(w=>w.status==="VERIFIED_ZERO_EVENTS").length});
}
