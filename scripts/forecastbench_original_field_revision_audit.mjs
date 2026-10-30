/** Field-level change accounting of original PUBLIC NON-PERSON forecast-resolution snapshots. */
const K=['id','source','direction','resolution_date','resolved_to','resolved'];
function keyed(doc){
 if(!doc||!Array.isArray(doc.resolutions)||typeof doc.forecast_due_date!=='string'||!doc.question_set)throw Error('PUBLIC_SCHEMA_REQUIRED');
 const m=new Map();
 for(const r of doc.resolutions){if(!r||typeof r!=='object'||Array.isArray(r)||!K.every(x=>Object.hasOwn(r,x))||Object.keys(r).some(x=>!K.includes(x))||typeof r.id!=='string'||!r.id||typeof r.source!=='string'||!r.source)throw Error('INVALID_OR_UNEXPECTED_PUBLIC_FIELDS');
  const k=JSON.stringify([r.source,r.id]);if(m.has(k))throw Error('DUPLICATE_PUBLIC_KEY');m.set(k,r);
 }
 return m;
}
export function auditPublicResolutionFieldRevisions(a,b){
 if(a.forecast_due_date!==b.forecast_due_date||a.question_set!==b.question_set)throw Error('CROSS_COHORT_OR_QUESTION_SET');
 const before=keyed(a),after=keyed(b),changes=Object.fromEntries(['direction','resolution_date','resolved_to','resolved'].map(x=>[x,0]));
 let unchanged=0,mutated=0,removed=0,added=0,date_only=0,outcome_changed=0,paired_outcome_date_change=0;
 for(const [key,row] of before){const next=after.get(key);if(!next){removed++;continue;}
  const ch=['direction','resolution_date','resolved_to','resolved'].filter(k=>JSON.stringify(row[k])!==JSON.stringify(next[k]));
  if(!ch.length){unchanged++;continue;}
  mutated++;for(const x of ch)changes[x]++;
  if(ch.length===1&&ch[0]==='resolution_date')date_only++;
  if(ch.includes('resolved_to')||ch.includes('resolved'))outcome_changed++;
  if(ch.includes('resolution_date')&&(ch.includes('resolved_to')||ch.includes('resolved')))paired_outcome_date_change++;
 }
 for(const key of after.keys())if(!before.has(key))added++;
 const result={schema:'pfl.forecastbench.original_public_field_revisions.v1',before_rows:before.size,after_rows:after.size,unchanged,mutated,removed,added,fields_changed:changes,date_only,outcome_changed,paired_outcome_date_change,bookkeeping_identity:before.size-removed+added===after.size,private_person_rows_processed:false,individual_source_ids_disclosed:false,first_public_time_verified:false,scientific_grade:'0/3'};
 if(unchanged+mutated+removed!==before.size||!result.bookkeeping_identity)throw Error('MUTATION_ACCOUNTING_IDENTITY_FAILED');
 return result;
}
